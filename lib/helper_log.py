import logging

EXTRA_DETAIL = 8
EXTRA_NOISY = 2


def setup_logging(verbosity_level=0):
    if verbosity_level == 1:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity_level == 2:
        logging.addLevelName(EXTRA_DETAIL, 'DETAIL')
        logging.basicConfig(level=EXTRA_DETAIL)
    elif verbosity_level > 2:
        logging.addLevelName(EXTRA_DETAIL, 'DETAIL')
        logging.addLevelName(EXTRA_NOISY, 'NOISE')
        logging.basicConfig(level=EXTRA_NOISY)
    else:
        logging.basicConfig(level=logging.INFO)
