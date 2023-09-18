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
        self.supported_char = self.__detect_supported_char()
        self._initialize_logger()

    def __detect_supported_char(self):
        try:
            print("\r█", end="", flush=True)
            print("\r ", end="", flush=True)  # clear the line
            return '█'
        except Exception:
            return '#'

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
    
    def show_progress(self, progress, bar_length=50):
        # calculate the percentage
        filled_length = int(round(bar_length * progress / 100))

        # fill the bar with '█' character
        bar = self.supported_char * filled_length + '-' * (bar_length - filled_length)

        # print the bar
        print(f"\r processing: [{bar}] {progress}%", end="", flush=True)

# If this module is imported, it will provide a default logger.
# If this module is the main script, it will also configure the logger.
logger = CustomLogger(model_name=__name__).logger

