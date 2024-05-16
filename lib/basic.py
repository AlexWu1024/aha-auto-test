import os, yaml, re
from datetime import datetime
from lib.log import setup_logger, close_log

class SYS:
    def setup_environment(setting_file, start_time):       
        with open(setting_file, 'r') as file:
            Setting = yaml.safe_load(file)

        Setting = SYS.setting_process(Setting, start_time)
        LOG_FOLDER = Setting['path']['Log_folder']
        SYS.create_log_folder(LOG_FOLDER)
        summary_logger = setup_logger(os.path.join(LOG_FOLDER, Setting['path']['Summary']), log_type="summary")   
        
        return Setting, LOG_FOLDER, summary_logger
        
    def create_log_folder(folder_path):        
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Create Log Folder: '{folder_path}'")
            else:
                print(f"Log Folder: '{folder_path}'")
        except Exception as e:
            print(f"Create Log Folder Error: '{e}'")
            
    def setting_process(setting, start_time):       
        project = setting['Info']['Project']
        station = setting['Info']['Station']
        version = get_version()

        start_time = start_time.strftime("%H%M%S")
        date = datetime.today().date()
        date = date.strftime("%Y%m%d")

        replacements = {
            "[version]": version,
            "[project]": project,
            "[station]": station,
            "[date]": date, 
            "[time]": start_time
        }

        for category in ['Version', 'path']:
            for key, value in setting[category].items():
                modified_value = value
                for placeholder, replacement in replacements.items():
                    modified_value = modified_value.replace(placeholder, replacement)
                setting[category][key] = modified_value  
                
        setting['Version']['Program'] = re.sub(r'\(.*?\)', '', setting['Version']['Program'])
        return setting
    
class LogHandler:
    def __init__(self, setting, start_time):
        self.setting = setting
        self.start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        self.log_folder = setting['path']['Log_folder'] 
        self.project = setting['Info']['Project']
        self.station = setting['Info']['Station']
        
        self.program_version = setting['Version']['Program']
        self.formatted_time = start_time.strftime("%Y%m%d_%H%M%S")

    def get_start_logger(self):
        self.log_file_name = self.setting['path']['Execution']
        self.log_file_name = self.log_file_name.replace("[time]", self.formatted_time)
            
        logger = setup_logger(os.path.join(self.log_folder, self.log_file_name), log_type="execution")
        
        logger.info("START!")
        logger.info(f"Start Time: {self.start_time}")
        logger.info(f"Program Version: {self.program_version}")
        logger.info(f"Project: {self.project}")
        logger.info(f"Station: {self.station}")
        logger.info(f"Log folder: {self.log_folder}")
        return logger    
    
    def rename_log(self, LOG_FOLDER, new_log_file_name, log):
        old_path = os.path.join(LOG_FOLDER, self.log_file_name)
        new_path = os.path.join(LOG_FOLDER, new_log_file_name)
        log.info(f"Rename log file: '{self.log_file_name}' to '{new_log_file_name}'")
        close_log(log)
        os.rename(old_path, new_path)
    
def get_version():
    version_file = "config/version.yaml"
    with open(version_file, 'r') as file:
        version_setting = yaml.safe_load(file)
    VERSION = version_setting['Version']
    return VERSION