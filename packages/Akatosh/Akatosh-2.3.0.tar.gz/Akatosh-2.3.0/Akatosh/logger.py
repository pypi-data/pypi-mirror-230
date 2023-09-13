import logging

logger = logging.getLogger("Akatosh")
formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(filename=".log", mode="w")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)