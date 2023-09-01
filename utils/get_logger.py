import logging

class CustomExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        result = result.split('\n')
        formatted_result = ''.join([' ' * 8 + line + '\n' if result.index(line) != len(result)-1 else ' ' * 8 + line for line in result])
        return formatted_result

formatter = CustomExceptionFormatter(fmt="[%(levelname)s] %(asctime)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def get_logger(name, filename, logging_level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)
        
        logger.setLevel(logging_level)
        logger.addHandler(handler)

    return logger