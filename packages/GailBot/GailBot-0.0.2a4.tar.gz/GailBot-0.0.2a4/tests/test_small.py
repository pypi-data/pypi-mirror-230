# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-28 18:22:29
"""
# -*- coding: utf-8 -*-
@Author  :   Vivian Li 
@Date    :   2023/06/19
@Last Modified By :   Vivian
@Last Modified Time :   2023/06/19 07:46:38
Description: include testing for small files, the input source is provided 
             in the same folder as the test script 
"""

import pytest
from dataclasses import dataclass
from tests.test_api import transcribe
from tests.test_data import SETTING_DATA
import os
import logging


@dataclass
class PATH:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    HELLO1 = os.path.join(ROOT, "small-test/hello1.wav")
    HELLO2 = os.path.join(ROOT, "small-test/hello2.wav")
    HELLODIR = os.path.join(ROOT, "small-test/hello-dir")
    EMPTY = os.path.join(ROOT, "small-test/empty")
    TRANSCRIBED = os.path.join(ROOT, "small-test/transcribed-input")
    INVALID = os.path.join(ROOT, "small-test/invalidFile")
    OUTPUT = os.path.join(ROOT, "small-test/output")
    GOOGLE_API = os.path.join(ROOT, "small-test/gailbot_key.json")


GOOGLE_SETTING = {"engine": "google", "google_api_key": PATH.GOOGLE_API}


@pytest.mark.parametrize(
    "input", [[PATH.HELLO1, PATH.HELLO2], [PATH.HELLODIR], [PATH.TRANSCRIBED]]
)
def test_whisper(input):
    """
    Purpose: Test the Whisper transcription with multiple input files or directories
    Expected Output: No failures or invalid transcriptions
    """
    logging.warn(input)
    fails, invalid = transcribe(
        input,
        "whisper",
        SETTING_DATA.WHISPER_PROFILE,
        PATH.OUTPUT,
        google_engine=GOOGLE_SETTING,
    )


@pytest.mark.parametrize(
    "input", [[PATH.HELLO1, PATH.HELLO2], [PATH.HELLODIR], [PATH.TRANSCRIBED]]
)
def test_watson(input):
    """
    Purpose: Test the Watson transcription with multiple input files or directories
    Expected Output: No failures or invalid transcriptions
    """
    fails, invalid = transcribe(
        input,
        "watson",
        SETTING_DATA.WATSON_PROFILE,
        PATH.OUTPUT,
        google_engine=GOOGLE_SETTING,
    )


@pytest.mark.parametrize(
    "input", [[PATH.HELLO1, PATH.HELLO2], [PATH.HELLODIR], [PATH.TRANSCRIBED]]
)
def test_google(input):
    """
    Purpose: Test the Google transcription with multiple input files or directories
    Expected Output: No failures or invalid transcriptions
    """
    fails, invalid = transcribe(
        input,
        "google",
        SETTING_DATA.GOOGLE_PROFILE,
        PATH.OUTPUT,
        google_engine=GOOGLE_SETTING,
    )


@pytest.mark.parametrize("input", [[PATH.EMPTY], [PATH.INVALID]])
def test_invalid(input):
    """
    Purpose: Test the behavior of transcribe function with invalid input files or directories
    Expected Output: At least one failure or invalid transcription
    """
    fails, invalid = transcribe(
        input,
        "watson",
        SETTING_DATA.WATSON_PROFILE,
        PATH.OUTPUT,
        google_engine=GOOGLE_SETTING,
        fail_test=True,
    )
    assert fails or invalid
    fails, invalid = transcribe(
        input,
        "whisper",
        SETTING_DATA.WHISPER_PROFILE,
        PATH.OUTPUT,
        fail_test=True,
        google_engine=GOOGLE_SETTING,
    )
    assert fails or invalid
