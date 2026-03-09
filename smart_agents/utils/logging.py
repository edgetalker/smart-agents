import logging
import sys

def setup_logger(
    name: str = "smart_agents",
    level: str = "INFO",
    format_string: str | None = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            format_string or
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def get_logger(name: str = "smart_agents") -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)