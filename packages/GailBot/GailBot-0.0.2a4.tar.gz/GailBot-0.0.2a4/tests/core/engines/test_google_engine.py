# -*- coding: utf-8 -*-
# @Author: Muhammad Umair
# @Date:   2023-06-20 09:38:58
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-30 14:15:09
from gailbot.core.utils.logger import makelogger
from gailbot.core.engines.google.google import Google
from gailbot.core.engines.google.core import GoogleCore
from gailbot.core.utils.media import MediaHandler
from .data import AudioPath
from tests.test_data import PATH
import pytest

logger = makelogger("pytest_google_engine")


def test_init_google():
    """
    test_init_google()
    Purpose:            Test functionality of Google engine's init function using
                        given Google API Key and a small audio wav file.
    Expected Output:    An instance of Google engine is initialized and able to
                        transcribe a small audio file.
    """
    google_engine = Google(PATH.GOOGLE_API)
    assert not google_engine.transcribe_success
    google_engine.transcribe(AudioPath.SMALL_AUDIO_WAV, PATH.GOOGLE_OUT)


@pytest.mark.parametrize(
    "audio_path", [AudioPath.SMALL_AUDIO_WAV, AudioPath.SMALL_AUDIO_MP3]
)
def test_core_run_engine(audio_path):
    """
    test_core_run_engine()
    Purpose:            Test that Google core's engine is able to run with
                        audio input.
    Expected Output:    Response from Google STT engine for the given input
                        files.
    """
    core = GoogleCore(PATH.GOOGLE_API)
    core._run_engine(audio_path, PATH.GOOGLE_OUT)


@pytest.mark.parametrize("audio_path", [AudioPath.SMALL_AUDIO_WAV])
def test_core_transcribe(audio_path):
    """
    test_core_transcribe()
    Purpose:            Test functionality of Google engine's transcribe function
                        with audio inputs
    Expected Output:    Response from Google STT engine
    """
    core = GoogleCore(PATH.GOOGLE_API)
    core.transcribe(audio_path, PATH.GOOGLE_OUT)


@pytest.mark.parametrize(
    "audio_path", [AudioPath.SMALL_AUDIO_MP3, AudioPath.SMALL_AUDIO_WAV]
)
def test_small_file(audio_path):
    """
    test_small_file()
    Purposes:           Test that the Google engine can transcribe small audio
                        input files.
    Expected Output:    Response from Google STT engine for input audio files
    """
    core = Google(PATH.GOOGLE_API)
    assert not core.transcribe_success
    core.transcribe(audio_path, PATH.GOOGLE_OUT)
    assert core.transcribe_success


@pytest.mark.parametrize("audio_path", [AudioPath.LARGE_AUDIO_MP3])
def _test_chunking_large_audio(audio_path):
    """
    test_chunking_large_audio()
    Purpose:            Test that Google engine is able to chunk large input
                        audio files. Use mediaHandler to get audio length (secs)
                        and chunk duration (secs) and call chunk_aduio_to_outpath
                        with given audio path, output path, and chunk duration.
    Expected Output:    Able to get chunk duration for given large input
                        and get chunked files in specified output path
    """
    core = GoogleCore(PATH.GOOGLE_API)
    mediaHandler = MediaHandler()
    audio_len_sec = (mediaHandler.info(mediaHandler.read_file(audio_path)))[
        "duration_seconds"
    ]
    chunk_duration = core._get_chunk_duration(audio_path, audio_len_sec)

    files = mediaHandler.chunk_audio_to_outpath(
        audio_path, PATH.GOOGLE_OUT, chunk_duration
    )
    for file in files:
        logger.info(file)


@pytest.mark.parametrize("audio_path", [AudioPath.LARGE_AUDIO_MP3])
def _test_large_audio(audio_path):
    """
    test_large_audio()
    Purpose:            Test to make sure Google engine can transcribe a large audio
                        input successfully
    Expected Output:    Transcription status unsuccessful before calling
                        transcribe(); successful after transcription
    """
    core = GoogleCore(PATH.GOOGLE_API)
    assert not core.transcribe_success
    core.transcribe(audio_path, PATH.GOOGLE_OUT)
    assert core.transcribe_success


@pytest.mark.parametrize("audio_path", [AudioPath.MEDIUM_AUDIO_MP3])
def test_medium_audio(audio_path):
    """
    test_medium_audio()
    Purpose:            Test to make sure Google engine can transcribe a medium
                        length audio
    Expected Output:    Transcription status unsuccessful before calling
                        transcribe(); successful after transcription; print out
                        transcription result
    """
    core = GoogleCore(PATH.GOOGLE_API)
    assert not core.transcribe_success
    res = core.transcribe(audio_path, PATH.GOOGLE_OUT)
    assert core.transcribe_success
    logger.info("the final result of the utterance")
    logger.info(res)


@pytest.mark.parametrize("audio_path", [AudioPath.CHUNK_60])
def test_60_sec_audio(audio_path):
    """
    test_60_sec_audio()
    Purpose:            Test to make sure Google engine can transcribe a 60
                        sec audio file
    Expected Output:    Transcription status unsuccessful before calling
                        transcribe(); successful after transcription; print out
                        transcription result
    """
    core = GoogleCore(PATH.GOOGLE_API)
    assert not core.transcribe_success
    res = core.transcribe(audio_path, PATH.GOOGLE_OUT)
    assert core.transcribe_success
    logger.info("the final result of the utterance")
    logger.info(res)
