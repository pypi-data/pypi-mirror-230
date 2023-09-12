# -*- coding: utf-8 -*-
# @Author: Muhammad Umair
# @Date:   2023-01-30 22:25:13
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-06 14:10:39
import json
import time
from .data import AudioPath
from gailbot.core.engines.whisperEngine import WhisperEngine
from gailbot.core.utils.general import write_json
import pytest
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future
from typing import List
from gailbot.core.utils.logger import makelogger
import logging

logger = makelogger("test_whisper.py")


def whisper_test(audio_path, detect_speaker: bool, output_path):
    """
    whispher_test()
    Purpose:            driver function that gets called in file size-specific
                        test functions. Takes in input audio file path
                        configuration, speaker detection configuration, and
                        output path
    Expected Output:    logger messages of what is being tested and relevant
                        information
    """
    # engine = WhisperEngine(AudioPath.RESULT_OUTPUT)
    engine = WhisperEngine()
    print(engine)
    print(engine.get_supported_formats())
    print(engine.get_available_models())
    # print(engine.get_supported_languages())

    start = time.time()
    result = engine.transcribe(
        audio_path=audio_path,
        payload_workspace=output_path,
        language="English",
        detect_speakers=detect_speaker,
    )
    print(f"Time taken for transcription: {time.time() - start}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    write_json(f"{AudioPath.WHISPER_OUT_PATH}/{output_path}", {"data": result})


@pytest.mark.parametrize(
    "audio_path, detect_speaker, output_path",
    [(AudioPath.SHORT_AUDIO, False, "short_phone_call.json")],
)
def test_short(audio_path, detect_speaker, output_path):
    """
    test_short()
    Purpose:            Test the functionality for whisper engine using a small
                        input audio file
    Expected Output:    Transcription sucessful with output files in the specified
                        output directory
    """
    whisper_test(audio_path, detect_speaker, output_path)


@pytest.mark.parametrize(
    "audio_path, detect_speaker, output_path",
    [(AudioPath.SHORT_AUDIO, True, "short_phone_call.json")],
)
def test_detect_speaker_short(audio_path, detect_speaker, output_path):
    """
    test_detect_speaker_short()
    Purpose:            Test functionality of whisper engine using a small input
                        audio file with speaker detection on
    Expected Output:    Transcription sucess with output files in specified output
                        directory. Output should have different speakers
    """
    whisper_test(audio_path, detect_speaker, output_path)


@pytest.mark.parametrize(
    "audio, detect_speaker, output", [(AudioPath.FORTY_MIN, False, "long_audio.json")]
)
def _test_long_audio(audio, detect_speaker, output):
    """
    test_long_audio()
    Purpose:            Test the functionality for whisper engine using a long
                        input audio file
    Expected Output:    Transcription sucessful with output files in the specified
                        output directory
    """
    whisper_test(audio, detect_speaker, output)


@pytest.mark.parametrize(
    "audio_path, detect_speaker, output_path",
    [(AudioPath.LONG_PHONE_CALL, True, "long_phone_call.json")],
)
def _test_detect_speaker_long(audio_path, detect_speaker, output_path):
    """
    test_detect_speaker_long()
    Purpose:            Test functionality of whisper engine using a long input
                        audio file with speaker detection on
    Expected Output:    Transcription sucess with output files in specified output
                        directory. Output should have different speakers
    """
    whisper_test(audio_path, detect_speaker, output_path)


def test_single_whisper():
    """
    test_single_whisper()
    Purpose:            Test a single transcription using whisper engine.
    Expected Output:    Transcription successful with utterance data in the
                        specified output path. Utterance result also printed
    """
    # whisper = WhisperEngine(AudioPath.RESULT_OUTPUT)
    whisper = WhisperEngine()
    utt = whisper.transcribe(AudioPath.SineWaveMinus16, AudioPath.WHISPER_OUT_PATH)
    logging.info(utt)


def test_threading_whisper():
    """
    test_threading_whisper()
    Purpose:            Test concurrent running multiple transcriptions on the Whisper
                        engine using multithreading.
    Expected Output:    All transcriptions run successfully get transcription results
    """
    whisper = WhisperEngine()
    futures: List[Future] = list()
    audios = [
        AudioPath.SHORT_AUDIO,
        AudioPath.HELLO_1,
        AudioPath.HELLO_2,
        AudioPath.HELLO_3,
        AudioPath.HELLO_4,
    ]
    output_path = AudioPath.WHISPER_OUT_PATH
    with ThreadPoolExecutor(max_workers=5) as executor:
        for audio in audios:
            future = executor.submit(
                whisper.transcribe, audio_path=audio, payload_workspace=output_path
            )
            futures.append(future)
        for f in futures:
            if f.exception():
                print(f.exception())
            print(f.result())
