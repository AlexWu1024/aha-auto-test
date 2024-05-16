import logging
import os

def check_folder(path):    
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, path)
    folder_path = os.path.dirname(full_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)    
        print(f"Create Folder: '{folder_path}'")
        
def setup_logger(logfile, log_type="execution", loglevel=logging.INFO):
    check_folder(logfile)
    logger = logging.getLogger(logfile)
    file_handler = logging.FileHandler(logfile, encoding='utf-8')
    
    if log_type == "execution":
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')       
    else:
        formatter = logging.Formatter('%(asctime)s - %(message)s')
  
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if log_type == "execution":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.setLevel(loglevel)
    return logger
    
def close_log(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()