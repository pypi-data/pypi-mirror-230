# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-07-07 13:59:42
import os
from dataclasses import dataclass
from pathlib import Path

# path the app will be initialized
APP_ROOT = "/Users/yike"
# APP_ROOT = "/Users/jasonycwu/Documents/GitHub"
# path of the parent directory of gbtest directory
TEST_ROOT = "/Users/yike/Desktop"
# TEST_ROOT = "/Users/jasonycwu/Desktop"


@dataclass
class PATH:
    APP_ROOT = APP_ROOT
    TEST_ROOT = TEST_ROOT
    # SETTING_ROOT = os.path.join(APP_ROOT, "GailBot/Backend/gailbot_workspace/gailbot_data/setting_source")
    SETTING_ROOT = os.path.join(APP_ROOT, "GailBot/interface/gui/config_backend")
    # USER_ROOT = os.path.join(APP_ROOT, "GailBot/Backend")
    USER_ROOT = os.path.join(APP_ROOT, "GailBot/interface/gui")
    OUTPUT_ROOT = os.path.join(TEST_ROOT, "gbtest/output")
    GOOGLE_OUT = os.path.join(OUTPUT_ROOT, "google")
    WATSON_OUT = os.path.join(OUTPUT_ROOT, "watson")
    WHISPER_OUT = os.path.join(OUTPUT_ROOT, "whisper")
    INPUTROOT = os.path.join(TEST_ROOT, "gbtest/input")

    INVALID_DATA_DIR = os.path.join(INPUTROOT, "invalidFile")
    DUMMY_AUDIO = os.path.join(INPUTROOT, "invalidaudio")
    EMPTY = os.path.join(INPUTROOT, "empty")
    MIX = os.path.join(INPUTROOT, "mix")
    TRANSCRIBED = os.path.join(INPUTROOT, "medium_transcribed")
    SMALL_AUDIO_MP3 = os.path.join(INPUTROOT, "all/test.mp3")
    CHUNK_60 = os.path.join(INPUTROOT, "all/60sec.mp3")
    MEDIUM_AUDIO_MP3 = os.path.join(INPUTROOT, "all/mediumtest.mp3")
    SHORT_PHONE_CALL = os.path.join(INPUTROOT, "all/short_phone_call.wav")
    LARGE_AUDIO_WAV = os.path.join(INPUTROOT, "all/largetest.wav")
    LARGE_AUDIO_MP3 = os.path.join(INPUTROOT, "all/largetest.mp3")
    OPUS_AUDIO = os.path.join(INPUTROOT, "all/test.opus")
    WATSON_OUT_PATH = os.path.join(OUTPUT_ROOT, "Watson")
    GOOGLE_OUT_PATH = os.path.join(OUTPUT_ROOT, "Google")
    WHISPER_OUT_PATH = os.path.join(OUTPUT_ROOT, "Whisper")
    CONVERSATION_DIR = os.path.join(INPUTROOT, "small_dir")
    TRANSCRIBED_DIR = os.path.join(INPUTROOT, "medium_transcribed")
    FORTY_MIN = os.path.join(INPUTROOT, "long/forty.mp3")
    SHORT_AUDIO = os.path.join(INPUTROOT, "small_dir/test1.wav")
    SMALL_AUDIO_WAV = os.path.join(INPUTROOT, "all/shorttest.wav")
    MEDIUM_AUDIO = os.path.join(INPUTROOT, "all/mediumtest.wav")
    LONG_PHONE_CALL = os.path.join(INPUTROOT, "all/long_phone_call.wav")
    SMALL_CONVERSATION_DIR = os.path.join(INPUTROOT, "small_dir")
    LIB_RECORD_DIR = os.path.join(INPUTROOT, "librecord")
    LONG_LIB_RECORD = os.path.join(INPUTROOT, "3speakersLibrecord.wav")
    LARGE_CONVERSATION_DIR = os.path.join(INPUTROOT, "all")
    MANY_FILES_DIR = os.path.join(INPUTROOT, "many_files_dir")
    MANY_SMALL_FILES_DIR = os.path.join(INPUTROOT, "many_small_files_dir")
    HELLO_1 = os.path.join(INPUTROOT, "small_test/hello1.wav")
    HELLO_2 = os.path.join(INPUTROOT, "small_test/hello2.wav")
    HELLO_3 = os.path.join(INPUTROOT, "small_test/hello3.wav")
    HELLO_4 = os.path.join(INPUTROOT, "small_test/hello4.wav")
    MANY_HELLO = os.path.join(INPUTROOT, "small_test")
    TWO_MIN_10 = os.path.join(INPUTROOT, "many_small_files_dir/test10.wav")
    TWO_MIN_9 = os.path.join(INPUTROOT, "many_small_files_dir/test9.wav")
    TWO_MIN_8 = os.path.join(INPUTROOT, "many_small_files_dir/test8.wav")
    TWO_MIN_7 = os.path.join(INPUTROOT, "many_small_files_dir/test7.wav")
    TEST_2b = os.path.join(INPUTROOT, "wav/test2b.wav")
    TEST_2a = os.path.join(INPUTROOT, "wav/test2a.wav")
    TEST_2a_trim = os.path.join(INPUTROOT, "wav/test2a_trim.wav")
    TEST_2aa = os.path.join(INPUTROOT, "wav/test2aa.wav")
    TEST__ = os.path.join(INPUTROOT, "wav/test.wav")
    TEST_OUTPUT_AUDIO = os.path.join(INPUTROOT, "wav/test_output.wav")
    SineWaveMinus16 = os.path.join(INPUTROOT, "wav/SineWaveMinus16.wav")
    assassination1 = os.path.join(INPUTROOT, "wav/07assassination1.wav")
    WAV_DIR = os.path.join(INPUTROOT, "wav")
    ICC_DIR = os.path.join(INPUTROOT, "ICC")
    # DIR_4157 = os.path.join(INPUTROOT, "4157")
    DIR_4157 = os.path.join(INPUTROOT, "4157Google")
    DIR_4156 = os.path.join(INPUTROOT, "4156")
    DIR_4145 = os.path.join(INPUTROOT, "4145")
    DIR_4112 = os.path.join(INPUTROOT, "4112")
    DIR_4104 = os.path.join(INPUTROOT, "4104")
    DIR_4093 = os.path.join(INPUTROOT, "4093")
    DIR_4092 = os.path.join(INPUTROOT, "4092")
    DIR_2ab = os.path.join(INPUTROOT, "test2ab")
    TEST_COPY_SRC = os.path.join(OUTPUT_ROOT, "test_copy_src")
    TEST_COPY_DES = os.path.join(OUTPUT_ROOT, "test_copy_des")
    WAV_SUITE = [
        TEST_OUTPUT_AUDIO,
        TEST__,
        TEST_2a,
        TEST_2b,
        assassination1,
        SineWaveMinus16,
    ]
    DEMO1 = os.path.join(INPUTROOT, "demo-folder/demo1")
    DEMO2 = os.path.join(INPUTROOT, "demo-folder/demo2")
    DEMO3 = os.path.join(INPUTROOT, "demo-folder/demo3")
    GOOGLE_API = os.path.join(INPUTROOT, "googleApi/gailbot_key.json")

    TEST_DATA_DIR = os.path.join(APP_ROOT, "GailBot/tests/test_data")
    TEST_SUITE_DIR = os.path.join(TEST_DATA_DIR, "test_suite")
    SAMPLE_SUITE_DIR = os.path.join(TEST_DATA_DIR, "sample_suite")

    @dataclass
    class LINK:
        HIL_LAB_GITHUB = (
            "https://github.com/YikeLi-Vivi/hillab/archive/refs/heads/main.zip"
        )
        HIL_LAB_AWS = (
            "https://gailbot-plugin.s3.us-east-2.amazonaws.com/gb_hilab_suite.zip"
        )


def assert_dataclass_paths():
    """
    Asserts that all values in a dataclass are valid file or directory paths.
    """
    for field, value in PATH.__dict__.items():
        if isinstance(value, str) and not (
            Path(value).is_file() or Path(value).is_dir()
        ):
            print(f"Invalid path for field {field}")


assert_dataclass_paths()