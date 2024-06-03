import logging

class Logger:
    def __init__(self, cls, level=logging.DEBUG):
        self.logger = logging.getLogger(cls.__name__)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger