import logging
import traceback

class Logger:

    def __init__(self, name: str, level: str) -> None:

        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.propagate = False
        set_level = logging._nameToLevel[level]
        self.logger.setLevel(set_level)
        if not self.logger.handlers:
            msg = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formats: str = msg
            formatter = logging.Formatter(formats)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None: 
        self.logger.debug(message)

    def info(self, message: str) -> None: 
        self.logger.info(message)

    def warning(self, message: str) -> None: 
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)
        print(traceback.format_exc())

    def critical(self, message: str) -> None:
        self.logger.critical(message)
        print(traceback.format_exc())