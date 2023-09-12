# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-03 23:12:38
from gailbot.core.utils.logger import makelogger
from gailbot.configs import (
    log_config_loader,
    google_config_loader,
    watson_config_loader,
    whisper_config_loader,
)

logger = makelogger("pytest_config")


def test_engine_config_file():
    """
    test_engine_config_file()
    Purpose:            Tests to make sure that engine configuration files are properly
                        loaded. Loader functions for Watson, Google, and Whisper called
    Expected Result:    Configuration data loaded properly, not none
    """
    WATSON_CONFIG = watson_config_loader()
    GOOGLE_CONFIG = google_config_loader()
    WHISPER_CONFIG = whisper_config_loader()
    assert WATSON_CONFIG is not None
    assert GOOGLE_CONFIG is not None
    assert WHISPER_CONFIG is not None


def test_log_config_file():
    """
    test_log_config_file()
    Purpose:            Tests to make sure that log configurations are properly
                        loaded. Loader functions for log called
    Expected Result:    Configuration data loaded properly, not none
    """
    LOG_CONFIG = log_config_loader()
    assert LOG_CONFIG is not None
