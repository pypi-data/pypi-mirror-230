# log_helper.py
import os
import logging

class CustomLogger():
    # Logging levels encapsulated
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


    def __init__(self, model_name='',log_filename="./Logs/simple_log_helper.log", level=INFO):
        self.model_name = model_name
        self.log_filename = log_filename
        self.level = level
        self._initialize_logger()

    def _initialize_logger(self):
        if self.model_name == "__main__":
            folder = os.path.dirname(self.log_filename)
            path_exists = os.path.exists(folder)
            if path_exists == False:
                os.makedirs(folder)
            if self.log_filename[-4:] != '.log':
                self.log_filename = folder + '/' + 'default.log'
                
            # This script is being run directly, so configure logging
            logging.basicConfig(level=self.level,  
                                format='%(asctime)s [%(levelname)s] "%(name)s" %(message)s', 
                                datefmt='%Y-%m-%d %H:%M:%S',
                                handlers=[logging.FileHandler(self.log_filename), 
                                          logging.StreamHandler()])
        self.logger = logging.getLogger(self.model_name)

    def set_level(self, level):
        self.level = level
        self.logger.setLevel(level)

# If this module is imported, it will provide a default logger.
# If this module is the main script, it will also configure the logger.
logger = CustomLogger(model_name=__name__).logger

