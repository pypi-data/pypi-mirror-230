import logging
import sys
import traceback

#console log level to prevent logger from printing to console
console_log_level = 100

class Logger():
    def __init__(self, path):
        self.config_logger(path)
        sys.excepthook = self.handle_exception
        
    
    def config_logger(self, path):
        #Create and configure logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s [%(levelname)s] - %(message)s',
            filename=path,
            filemode='a')  # pass explicit filename here 
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)


    def log_error(self, msg):
        self.logger.error(msg)
    
    def log_info(self, msg):
        self.logger.info(msg)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.logger.error("Uncaught exception : ", exc_info=(exc_type, None, exc_traceback))