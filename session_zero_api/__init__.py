import logging
import pathlib


def get_logger(name: str) -> logging.Logger:
    # setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    
    # add stream handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
                      
    # add file handler
    log_path = pathlib.Path(__file__).parent.parent / "logs" / f"{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    fh = logging.FileHandler(filename=log_path, mode='a', encoding='utf-8')
    fh.setLevel(logging.WARNING)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger