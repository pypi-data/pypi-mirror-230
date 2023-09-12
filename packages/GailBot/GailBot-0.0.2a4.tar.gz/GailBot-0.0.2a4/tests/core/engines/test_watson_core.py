# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-30 14:28:49
import os
from gailbot.core.engines.watson.core import WatsonCore
from gailbot.core.engines.watson.watson import Watson
from gailbot.core.utils.media import MediaHandler
from .data import AudioPath
from gailbot.core.utils.logger import makelogger
import pytest
from gailbot.core.utils.threads import ThreadPool
from tests.test_data.setting_data import SETTING_DATA

logger = makelogger("watsone_engine")


WATSON_API_KEY = SETTING_DATA.WATSON_SETTING["apikey"]
WATSON_LANG_CUSTOM_ID = SETTING_DATA.WATSON_LANG_CUSTOM_ID
WATSON_REGION = SETTING_DATA.WATSON_SETTING["region"]
WATSON_BASE_LANG_MODEL = SETTING_DATA.WATSON_SETTING["base_model"]


def test_watson_core():
    """
    Purpose: test to initialize a watson core and check for file extensio
    Expected Output: check that file supported by watson core is also
                    supported by mediaHandler
    """
    watson_core = Watson(WATSON_API_KEY, WATSON_REGION)
    assert set(watson_core.supported_formats) <= set(MediaHandler().supported_formats)
    for format in watson_core.supported_formats:
        assert watson_core.is_file_supported(f"test.{format}")


def test_on_invalid_api():
    """
    test_on_invalid_api()
    Purpose:            Test to see if Watson core recognizes an invalid API key
    Expected Output:    expect to raise an error showing that an invalid API was
                        given
    """
    with pytest.raises(Exception) as e:
        watson_core = WatsonCore(WATSON_API_KEY + "**", WATSON_REGION)
        logger.info(e)
        assert e


def test_on_invalid_region():
    """
    test_on_invalid_region()
    Purpose:            Test to see if Watson core recognizes an invalid region
    Expected Output:    An error raised showing that an invalid region was
                        provided
    """
    with pytest.raises(Exception) as e:
        watson_core = WatsonCore(WATSON_API_KEY, WATSON_REGION + "__")
        logger.info(e)
        assert e


@pytest.mark.parametrize("inpath", [AudioPath.MEDIUM_AUDIO])
def test_convert_to_opus(inpath):
    """
    test_convert_to_opus()
    Purpose:            Test that the Watson core is able to convert an audio
                        input into .opus format by calling the private function
                        _convert_to_opus() from Watson core
    Expected Output:    input file is compressed successfully; assert not false
    """
    watson = WatsonCore(WATSON_API_KEY, WATSON_REGION)
    assert watson._convert_to_opus(inpath, AudioPath.WATSON_OUT_PATH)


def watson_test(inpath):
    """
    watson_test()
    Purpose:            Driver function for running transcription using the
                        Watson core
    Expected Output:    Successful transcription and assert that the
                        transcription was successful
    """
    watson = Watson(WATSON_API_KEY, WATSON_REGION)
    assert set(watson.supported_formats) <= set(MediaHandler().supported_formats)
    for format in watson.supported_formats:
        assert watson.is_file_supported(f"test.{format}")
    assert not watson.was_transcription_successful()
    utterance = watson.transcribe(inpath, WATSON_BASE_LANG_MODEL, WATSON_LANG_CUSTOM_ID)
    logger.info(utterance)
    assert watson.was_transcription_successful()


@pytest.mark.parametrize(
    "inpath", [AudioPath.SMALL_AUDIO_MP3, AudioPath.SMALL_AUDIO_WAV]
)
def test_watson_small(inpath):
    """
    test_watson_small()
    Purpose:            Test the overall functionality of Watson core on a small
                        input file. Works by calling watson_test()
    Expected Output:    Transcription success with output files in the
                        specified output directory
    """
    logger.info("test watson small audio")
    watson_test(inpath)


@pytest.mark.parametrize("inpath", [AudioPath.MEDIUM_AUDIO])
def test_watson_medium(inpath):
    """
    test_watson_medium()
    Purpose:            Test the overall functionality of Watson core on a
                        medium input file. Works by calling watson_test()
    Expected Output:    Transcription success with output files in the
                        specified output directory
    """
    logger.info("test watson medium audio")
    watson_test(inpath)


@pytest.mark.parametrize("inpath", [AudioPath.LARGE_AUDIO_MP3])
def _test_watson_large(inpath):
    """
    test_watson_large()
    Purpose:            Test the overall functionality of Watson core on a large
                        input file. Works by calling watson_test()
    Expected Output:    Transcription success with output files in the
                        specified output directory
    """
    logger.info("test watson large audio")
    watson_test(inpath)


@pytest.mark.parametrize("inpath", [AudioPath.LARGE_AUDIO_WAV])
def _test_watson_large_wav(inpath):
    """
    test_watson_large_wav()
    Purpose:            Test the overall functionality of Watson core on a large
                        wav input file. Works by calling watson_test()
    Expected Output:    Transcription success with output files in the
                        specified output directory
    """
    logger.info("test watson large wav file")
    watson_test(inpath)


@pytest.mark.parametrize("inpath", [AudioPath.CHUNK_60])
def test_watson_60(inpath):
    """
    test_watson_60()
    Purpose:            Test the overall functionality of Watson core on a 60sec
                        input source
    Expected Output:    Transcription sucess with output files in the specified
                        output directory
    """
    logger.info("test watson 60 sec input file")
    watson_test(inpath)


def test_parallel_transcription():
    """
    test_parallel_transcription()
    Purpose:            run parallel transcription (watson core) tests on
                        medium length audio input files
    Expected Output:    transcription success and output the results
    """
    pool = ThreadPool(3)
    key1 = pool.add_task(watson_test, [AudioPath.MEDIUM_AUDIO])
    key2 = pool.add_task(watson_test, [AudioPath.MEDIUM_AUDIO_MP3])
    utt1 = pool.get_task_result(key1)
    utt2 = pool.get_task_result(key2)
    logger.info("first utterance result")
    logger.info(utt1)
    logger.info("second utterance result")
    logger.info(utt2)
    pool.wait_for_all_completion()
