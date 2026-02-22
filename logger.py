from logging import Formatter, StreamHandler, INFO, getLogger
from logging.handlers import RotatingFileHandler
from sys import stdout

def setup_logging() -> None:
    # Setup the Flask/Werkzeug logger.
    root_logger = getLogger()
    root_logger.setLevel(INFO)

    console_hdlr = StreamHandler(stdout)
    console_hdlr.setLevel(INFO)
    root_logger.addHandler(console_hdlr)

    app_logger = getLogger('app_logger')
    app_logger.propagate = False

    # Setup application-wide logger.
    hdlr = RotatingFileHandler('app.log', maxBytes = 1_000_000, backupCount = 5)
    hdlr.setLevel(INFO)
    hdlr.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    app_logger.addHandler(hdlr)
