import logging

import pytest

from pubtools.sign.utils import set_log_level


def test_set_log_level():
    LOG = logging.getLogger()
    set_log_level(LOG, "DEBUG")
    assert LOG.level == logging.DEBUG
    set_log_level(LOG, "INFO")
    assert LOG.level == logging.INFO
    set_log_level(LOG, "WARNING")
    assert LOG.level == logging.WARNING
    set_log_level(LOG, "ERROR")
    assert LOG.level == logging.ERROR
    with pytest.raises(ValueError):
        set_log_level(LOG, "UNKNOWN")
