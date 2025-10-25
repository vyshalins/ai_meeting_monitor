from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG, ERROR, FileHandler

logger = getLogger("AI Meeting Monitor")
logger.setLevel(DEBUG)

# Console handler
console_handler = StreamHandler()
console_handler.setLevel(INFO)
console_formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# File handler
file_handler = FileHandler("app.log")
file_handler.setLevel(ERROR)
file_formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)