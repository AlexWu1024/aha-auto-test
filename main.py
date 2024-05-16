from datetime import datetime
import schedule, time, os
import multiprocessing
import argparse
from lib.log import close_log, setup_logger
from lib.basic import SYS, LogHandler
from lib.AutoTest import Test
from lib.notify import Process_notify

def run_test(setting, testID, testItem, log):
    testItemStratTime = datetime.now()
    log.info(f"================ [RunTest] {testID}-{testItem} ================")
    test_instance = Test(setting, log)
    result = getattr(test_instance, testItem)()
    testItemEndTime = datetime.now()
    ELAPSED = round((testItemEndTime - testItemStratTime).total_seconds(), 3)
    log.info(f"================ {result} - {testID}-{testItem} ({ELAPSED}s) =================")
    summary_msg = f"{testID}|{testItem}|{result}|MESSAGE |ELAPSED {ELAPSED}"
    notify_msg = f"{result} - {testID}-{testItem} ({ELAPSED}s)\n"
    return result, summary_msg, notify_msg

def run_test_wrapper(args):
    Setting, TestID, Item, LOG_FOLDER, log_file = args
    item_log = setup_logger(os.path.join(LOG_FOLDER, log_file))
    result, summary_msg, notify_msg = run_test(Setting, TestID, Item, item_log)
    item_log.info(summary_msg)
    close_log(item_log)
    return result, notify_msg, summary_msg

def main(multi=False):
    try:
        StratTime = datetime.now()
        setting_file = "config/UI_TEST_setting_config.yaml"
        Setting, LOG_FOLDER, summary_logger = SYS.setup_environment(setting_file, StratTime)
        Station = Setting['Info']['Station']
        Sequence = Setting['Process']
        loghandler = LogHandler(Setting, StratTime)
        logger = loghandler.get_start_logger()  
        Test(Setting, logger).get_chromedriver_info()

        RESULTS = []
        NOTIFY = ""

        if multi:
            processes = []        
            with multiprocessing.Pool(processes=3) as pool:
                for i, TestID in enumerate(Sequence.keys()):
                    Process = Sequence[TestID]
                    log_file = f"{TestID}.log"
                    if Process["active"]:
                        args = (Setting, TestID, Process['Item'], LOG_FOLDER, log_file)
                        processes.append(pool.apply_async(run_test_wrapper, (args,)))
                    else:
                        logger.info(f"Skip {TestID}: {Process['Item']}")
                
                for process in processes:
                    result, notify_msg, summary_msg = process.get()
                    summary_logger.info(summary_msg) 
                    RESULTS.append(result)
                    NOTIFY += notify_msg
        else:
            for i, TestID in enumerate(Sequence.keys()):
                Process = Sequence[TestID]
                if Process["active"]:  
                    result, summary_msg, notify_msg = run_test(Setting, TestID, Process['Item'], logger)
                    summary_logger.info(summary_msg) 
                    RESULTS.append(result)
                    NOTIFY += notify_msg
                else:
                    logger.info(f"Skip {TestID}: {Process['Item']}")


        Result = "PASS" if all(res == "PASS" for res in RESULTS) else "FAIL"     
        EndTime = datetime.now()        
        new_log_file_name = loghandler.log_file_name.replace("[result]", Result)  
        ELAPSED = round((EndTime - StratTime).total_seconds(), 3) 
        Summary_msg = f"{Result} - {Station} ({ELAPSED}s)"
        logger.info(f"Total Elapsed Time: {ELAPSED}s")
        logger.info(f"================ {Summary_msg} =================")
        summary_logger.info(f"{Station}|{Result}|ELAPSED {ELAPSED}")
        NOTIFY = Summary_msg + '\n' + NOTIFY
        Process_notify(Setting, "UI-Test Summary", NOTIFY, logger)
        loghandler.rename_log(LOG_FOLDER, new_log_file_name, logger)
        close_log(summary_logger)
    except Exception as e:
        Process_notify(Setting, "UI-Test Test Program Exception", f"Error: {e}", logger)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-m', '--multi', action='store_true', help='Enable multi processing.')
    args = parser.parse_args()
    
    main(args.multi)

    schedule.every().day.at("09:00").do(main, args.multi)
    while True:
       schedule.run_pending()
       time.sleep(60) 