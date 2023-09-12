# -*- coding: utf-8 -*-
# @Author: Muhammad Umair
# @Date:   2023-01-12 14:26:59
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-22 11:31:31
from gailbot import GailBot
from tests.test_data import PATH
from tests.test_data import SETTING_DATA
import logging
import os


def transcribe(
    files,
    setting_name="test",
    setting_data=SETTING_DATA.WHISPER_PROFILE,
    output=PATH.OUTPUT_ROOT,
    fail_test=False,
    google_engine=SETTING_DATA.GOOGLE_SETTING,
):
    gb = GailBot(output)
    input = [(f, output) for f in files]

    gb.add_sources(input)

    assert gb.add_new_engine(
        SETTING_DATA.WHISPER_NAME, SETTING_DATA.WHISPER_SETTING, overwrite=True
    )
    assert gb.add_new_engine(SETTING_DATA.GOOGLE_NAME, google_engine, overwrite=True)
    assert gb.add_new_engine(
        SETTING_DATA.WATSON_NAME, SETTING_DATA.WATSON_SETTING, overwrite=True
    )
    assert gb.add_new_engine(
        SETTING_DATA.WHISPER_SP_NAME, SETTING_DATA.WHISPER_SPEAKER, overwrite=True
    )

    if not gb.is_profile(setting_name):
        assert gb.create_new_profile(setting_name, setting_data)
    for file in files:
        # second arg need to be a SettingObj
        setting_object_for_file = gb.settingManager.profiles[setting_name]

        # second arg need to be a SettingObj
        assert gb.apply_setting_profile_to_source(file, setting_object_for_file, True)

    source_names = gb.get_all_source_names()

    for file in files:
        for source in source_names:
            assert gb.get_src_setting_name(source) == setting_name
        assert gb.is_source(file)
    fails, invalid = gb.transcribe()
    logging.info(fails)
    logging.info(invalid)
    if not fail_test:
        assert not (fails or invalid)
    return fails, invalid


## demo for testing plugin ##
# def test_test_suite():
#     use_test_suite = {
#         "engine_setting_name": "whisper",
#         "plugin_setting": ["HiLabSuite"],
#     }
#     gb = GailBot(PATH.USER_ROOT)
#     test_suite_path = "/Users/hannahshader/Desktop/HiLabSuite"
#     gb.register_plugin_suite(test_suite_path)
#     gb.create_new_profile("HiLabSuite", use_test_suite)
#     gb.add_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test/hello1.wav",
#         "/Users/hannahshader/Desktop/output",
#     )

#     gb.apply_setting_profile_to_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test/hello1.wav",
#         gb.settingManager.profiles["HiLabSuite"],
#     )
#     gb.transcribe()
#     gb.remove_profile("HiLabSuite")
#     gb.delete_plugin_suite("HiLabSuite")


# def test_gailbot():
#     """
#     Purpose: Test overall functionality of the Gailbot program
#     Expected Output: a running Gailbot
#     """
#     gb = GailBot(PATH.USER_ROOT)


# #####################  test for whisper #####################


# def test_whisper_hello():
#     """
#     Purpose: Test the whisper transcription with the WAV suite
#     Expected Output: No failures or invalid transcriptions
#     """

#     use_test_suite = {
#         "engine_setting_name": "whisper",
#         "plugin_setting": ["HiLabSuite"],
#     }
#     gb = GailBot(PATH.USER_ROOT)
#     test_suite_path = "/Users/hannahshader/Desktop/HiLabSuite"
#     gb.register_plugin_suite(test_suite_path)
#     gb.create_new_profile("HiLabSuite", use_test_suite)
#     gb.add_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         "/Users/hannahshader/Desktop/output",
#     )
#     gb.apply_setting_profile_to_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         gb.settingManager.profiles["HiLabSuite"],
#     )

#     # figure out what names are
#     print("source names are")
#     print(gb.get_all_source_names())

#     # HANNAH note: when you're transcribing just one file,
#     # you have to put it as an item in a list
#     fails, invalid = gb.transcribe(["hello1"])
#     assert not fails
#     assert not invalid
#     assert invalid == []


# def test_whisper_hello_multiple():
#     """
#     Purpose: Test the whisper transcription with the WAV suite
#     Expected Output: No failures or invalid transcriptions
#     """

#     use_test_suite = {
#         "engine_setting_name": "whisper",
#         "plugin_setting": ["HiLabSuite"],
#     }
#     gb = GailBot(PATH.USER_ROOT)
#     test_suite_path = "/Users/hannahshader/Desktop/HiLabSuite"
#     gb.register_plugin_suite(test_suite_path)
#     gb.create_new_profile("HiLabSuite", use_test_suite)
#     gb.add_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         "/Users/hannahshader/Desktop/output",
#     )
#     gb.add_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello2.wav",
#         "/Users/hannahshader/Desktop/output",
#     )
#     gb.apply_setting_profile_to_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         gb.settingManager.profiles["HiLabSuite"],
#     )
#     gb.apply_setting_profile_to_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello2.wav",
#         gb.settingManager.profiles["HiLabSuite"],
#     )

#     # figure out what names are
#     print("source names are")
#     print(gb.get_all_source_names())

#     # HANNAH note: when you're transcribing just one file,
#     # you have to put it as an item in a list
#     fails, invalid = gb.transcribe(["hello1", "hello2"])
#     assert not fails
#     assert not invalid
#     assert invalid == []


# def test_watson_hello():
#     """
#     Purpose: Test the whisper transcription with the WAV suite
#     Expected Output: No failures or invalid transcriptions
#     """
#     gb = GailBot(PATH.USER_ROOT)
#     print("avliable settings names are: ")
#     print(gb.get_engine_setting_names())

#     use_test_suite = {
#         "engine_setting_name": "watson",
#         "plugin_setting": ["HiLabSuite"],
#     }
#     test_suite_path = "/Users/hannahshader/Desktop/HiLabSuite"
#     gb.register_plugin_suite(test_suite_path)
#     gb.create_new_profile("WatsonProfile", use_test_suite)
#     gb.add_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         "/Users/hannahshader/Desktop/output",
#     )
#     gb.apply_setting_profile_to_source(
#         "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",
#         gb.settingManager.profiles["WatsonProfile"],
#     )

#     # figure out what names are
#     print("source names are")
#     print(gb.get_all_source_names())

#     # HANNAH note: when you're transcribing just one file,
#     # you have to put it as an item in a list
#     fails, invalid = gb.transcribe(["hello1"])
#     assert not fails
#     assert not invalid
#     assert invalid == []


# def test_google_hello():
#     """
#     Purpose: Test the whisper transcription with the WAV suite
#     Expected Output: No failures or invalid transcriptions
#     """
#     gb = GailBot(PATH.USER_ROOT)
#     print("avliable settings names are: ")
#     print(gb.get_engine_setting_names())

#     use_test_suite = {
#         "engine_setting_name": "google",
#         "plugin_setting": ["HiLabSuite"],
#     }
#     test_suite_path = "/Users/jasonycwu/Desktop/HiLabSuite"
#     gb.register_plugin_suite(test_suite_path)
#     gb.create_new_profile("HiLabSuite", use_test_suite)
#     gb.add_source(
#         "/Users/jasonycwu/Desktop/gbtest/input/small_test2/hello1.wav",
#         "/Users/jasonycwu/Desktop/output",
#     )
#     gb.apply_setting_profile_to_source(
#         "/Users/jasonycwu/Desktop/gbtest/input/small_test2/hello1.wav",
#         gb.settingManager.profiles["HiLabSuite"],
#     )

#     # figure out what names are
#     print("source names are")
#     print(gb.get_all_source_names())

#     # HANNAH note: when you're transcribing just one file,
#     # you have to put it as an item in a list
#     fails, invalid = gb.transcribe(["hello1"])
#     assert not fails
#     assert not invalid
#     assert invalid == []


# def test_whisper_hello():
#     """
#     Purpose: Test the whisper transcription with the hello audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.HELLO_1], "whisper", SETTING_DATA.WHISPER_PROFILE)


# #      "/Users/hannahshader/Desktop/gbtest/input/small_test2/hello1.wav",


# def test_whisper_wav_dir():
#     """
#     Purpose: Test the whisper transcription with a directory containing WAV files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.WAV_DIR], "whisper", SETTING_DATA.WHISPER_PROFILE)


def test_whisper_one():
    """
    Purpose: Test the whisper transcription with a single audio file
    Expected Output: No failures or invalid transcriptions
    """
    fails, invalid = transcribe([PATH.HELLO_1], "whisper", SETTING_DATA.WHISPER_PROFILE)


# def test_whisper_dir():
#     """
#     Purpose: Test the whisper transcription with multiple directories
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [
#             PATH.MANY_FILES_DIR,
#             PATH.SMALL_CONVERSATION_DIR,
#             PATH.MANY_SMALL_FILES_DIR,
#         ]
#     )


# def test_with_speaker_one_file():
#     """
#     Purpose: Test the transcription with speaker separation using a single audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.LONG_LIB_RECORD], "speaker", SETTING_DATA.WHISPER_SPEAKER_PROFILE
#     )


# def test_with_speaker_empty():
#     """
#     Purpose: Test the transcription with speaker separation using an empty audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SineWaveMinus16], "speaker", SETTING_DATA.WHISPER_SPEAKER_PROFILE
#     )


# def test_with_speaker_seven():
#     """
#     Purpose: Test the transcription with speaker separation using a specific audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.assassination1], "speaker", SETTING_DATA.WHISPER_SPEAKER_PROFILE
#     )


# def test_with_speaker_short():
#     """
#     Purpose: Test the transcription with speaker separation using a short audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SHORT_AUDIO], "speaker", SETTING_DATA.WHISPER_SPEAKER_PROFILE
#     )


# def test_with_speaker_dir():
#     """
#     Purpose: Test the transcription with speaker separation using multiple directories
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SMALL_CONVERSATION_DIR, PATH.MANY_SMALL_FILES_DIR],
#         "speaker",
#         SETTING_DATA.WHISPER_SPEAKER_PROFILE,
#     )


# def test_invalid():
#     """
#     Purpose: Test the transcription with invalid inputs
#     Expected Output: At least one failure or invalid transcription
#     """
#     fails, invalid = transcribe(
#         [PATH.INVALID_DATA_DIR, PATH.DUMMY_AUDIO, PATH.EMPTY, PATH.MIX], fail_test=True
#     )
#     assert fails or invalid


# ###########################  test for watson #####################################
def test_watson():
    """
    Purpose: Test the Watson transcription with various inputs
    Expected Output: No failures or invalid transcriptions
    """
    fails, invalid = transcribe([PATH.HELLO_1], "watson", SETTING_DATA.WATSON_PROFILE)


# def test_watson_large():
#     """
#     Purpose: Test the Watson transcription with a large audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.LONG_PHONE_CALL], "watson", SETTING_DATA.WATSON_PROFILE
#     )


# def test_watson_large_two():
#     """
#     Purpose: Test the Watson transcription with another large audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.LONG_LIB_RECORD], "watson", SETTING_DATA.WATSON_PROFILE
#     )


# def test_watson_dir():
#     """
#     Purpose: Test the Watson transcription with a directory containing audio files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.MANY_SMALL_FILES_DIR], "watson", SETTING_DATA.WATSON_PROFILE
#     )


# def test_watson_many():
#     """
#     Purpose: Test the Watson transcription with multiple audio files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.HELLO_1, PATH.HELLO_2, PATH.HELLO_3, PATH.HELLO_4],
#         "watson",
#         SETTING_DATA.WATSON_PROFILE,
#     )


# def test_watson_wav_suite():
#     """
#     Purpose: Test the Watson transcription with the WAV suite
#     Expected Output: At least one failure or invalid transcription
#     """
#     fails, invalid = transcribe(
#         PATH.WAV_SUITE, "watson", SETTING_DATA.WATSON_PROFILE, fail_test=True
#     )


# def test_watson_wav_dir():
#     """
#     Purpose: Test the Watson transcription with a directory containing WAV files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.WAV_DIR], "watson", SETTING_DATA.WATSON_PROFILE)


# def test_watson_wav_test2b():
#     """
#     Purpose: Test the Watson transcription with a specific WAV file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.TEST_2b], "watson", SETTING_DATA.WATSON_PROFILE)


# def test_watson_icc():
#     """
#     Purpose: Test the Watson transcription with the ICC directory
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.ICC_DIR], "watson", SETTING_DATA.WATSON_PROFILE)


# def test_watson_long():
#     """
#     Purpose: Test the Watson transcription with a long audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.LONG_PHONE_CALL], "watson", SETTING_DATA.WATSON_PROFILE
#     )


# def test_watson_empty():
#     """
#     Purpose: Test the Watson transcription with an empty audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SineWaveMinus16], "watson", SETTING_DATA.WATSON_PROFILE
#     )


# ################################### test for google ##################################
# def test_google():
#     """
#     Purpose: Test the Google transcription with various inputs
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.HELLO_1], "google", SETTING_DATA.GOOGLE_PROFILE)


# def test_google_many_hello():
#     """
#     Purpose: Test the Google transcription with multiple hello audio files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.HELLO_1, PATH.HELLO_2, PATH.HELLO_3, PATH.HELLO_4],
#         "google",
#         SETTING_DATA.GOOGLE_PROFILE,
#     )


# def test_google_two():
#     """
#     Purpose: Test the Google transcription with a specific audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.TWO_MIN_9], "google", SETTING_DATA.GOOGLE_PROFILE)


# def test_google_many_two():
#     """
#     Purpose: Test the Google transcription with multiple audio files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.TWO_MIN_10, PATH.TWO_MIN_7, PATH.TWO_MIN_9, PATH.TWO_MIN_8],
#         "google",
#         SETTING_DATA.GOOGLE_PROFILE,
#     )


# def test_google_dir():
#     """
#     Purpose: Test the Google transcription with a directory containing audio files
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.MANY_FILES_DIR], "google", SETTING_DATA.GOOGLE_PROFILE
#     )


# def test_google_long():
#     """
#     Purpose: Test the Google transcription with a long audio file
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.LONG_PHONE_CALL], "google", SETTING_DATA.GOOGLE_PROFILE
#     )


# def test_google_wav_suite():
#     """
#     Purpose: Test the Google transcription with the WAV suite
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(PATH.WAV_SUITE, "google", SETTING_DATA.GOOGLE_PROFILE)


# def test_google_icc():
#     """
#     Purpose: Test the Google transcription with the ICC directory
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.ICC_DIR], "google", SETTING_DATA.GOOGLE_PROFILE)


# def test_google_40_dirs():
#     """
#     Purpose: Test the Google transcription with multiple directories
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DIR_4092, PATH.DIR_4093, PATH.DIR_4112],
#         "google",
#         SETTING_DATA.GOOGLE_PROFILE,
#     )


# ################################## test for plugin ###########################################


# def test_auto_load():
#     """
#     Purpose: Test the auto-loading of plugin suites
#     Expected Output: The specified plugin suite is loaded
#     """
#     gb = GailBot(PATH.USER_ROOT)
#     assert gb.is_plugin_suite("HiLabSuite")


# def test_s3_bucket():
#     """
#     Purpose: Test the registration of a plugin suite from an S3 bucket
#     Expected Output: The specified plugin suite is registered
#     """
#     gb = GailBot(PATH.USER_ROOT)
#     gb.register_plugin_suite("gailbot-plugin-suite-official")


# def test_2ab():
#     """
#     Purpose: Test the transcription with a specific audio file using the Watson plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe([PATH.DIR_2ab], "watson", SETTING_DATA.WATSON_PROFILE)


# def test_plugin_dir():
#     """
#     Purpose: Test the transcription with a directory containing audio files using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DIR_2ab], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_hello():
#     """
#     Purpose: Test the transcription with the hello audio file using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.HELLO_1], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_multiple_files():
#     """
#     Purpose: Test the transcription with multiple audio files using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.HELLO_2, PATH.HELLO_1, PATH.HELLO_3],
#         "plugin",
#         SETTING_DATA.PROFILE_WITH_PLUGIN,
#     )


# def test_plugin_short_phone():
#     """
#     Purpose: Test the transcription with a short phone call audio file using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SHORT_PHONE_CALL], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_assasination():
#     """
#     Purpose: Test the transcription with a specific audio file using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.assassination1], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_wav():
#     """
#     Purpose: Test the transcription with the WAV suite using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         PATH.WAV_SUITE, "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_empty():
#     """
#     Purpose: Test the transcription with an empty audio file using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SineWaveMinus16], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_wav_dir():
#     """
#     Purpose: Test the transcription with a directory containing WAV files using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.WAV_DIR], "plugin", SETTING_DATA.PROFILE_WITH_PLUGIN
#     )


# def test_plugin_multiple():
#     """
#     Purpose: Test the transcription with multiple audio files using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SHORT_AUDIO, PATH.SHORT_PHONE_CALL],
#         "plugin",
#         SETTING_DATA.PROFILE_WITH_PLUGIN,
#     )


# def test_plugin_with_spk():
#     """
#     Purpose: Test the transcription with a short phone call audio file using the plugin
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.SHORT_PHONE_CALL], "plugin", SETTING_DATA.WATSON_PROFILE
#     )


# ########## test for demo ############
# def test_demo_watson():
#     """
#     Purpose: Test the Watson transcription with multiple audio files in a demo scenario
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DEMO1, PATH.DEMO2, PATH.DEMO3],
#         "watson",
#         SETTING_DATA.WATSON_PROFILE,
#         output=PATH.GOOGLE_OUT_PATH,
#     )


# def test_demo_whisper():
#     """
#     Purpose: Test the Whisper transcription with multiple audio files in a demo scenario
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DEMO1, PATH.DEMO2, PATH.DEMO3],
#         "whisper",
#         SETTING_DATA.WHISPER_PROFILE,
#         output=PATH.WHISPER_OUT_PATH,
#     )


# def test_demo_google():
#     """
#     Purpose: Test the Google transcription with multiple audio files in a demo scenario
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DEMO1, PATH.DEMO2, PATH.DEMO3],
#         "google",
#         SETTING_DATA.GOOGLE_PROFILE,
#         output=PATH.GOOGLE_OUT_PATH,
#     )


# def test_google_demo_1():
#     """
#     Purpose: Test the Google transcription with a specific audio file in a demo scenario
#     Expected Output: No failures or invalid transcriptions
#     """
#     fails, invalid = transcribe(
#         [PATH.DEMO3], "google", SETTING_DATA.GOOGLE_PROFILE, output=PATH.GOOGLE_OUT_PATH
#     )


# def test_sample_suite():
#     use_sample_suite = {
#         "engine_setting_name": "whisper",
#         "plugin_setting": ["sample_suite"],
#     }
#     gb = GailBot(PATH.USER_ROOT)
#     sample_suite_path = PATH.SAMPLE_SUITE_DIR
#     print(sample_suite_path)
#     gb.register_plugin_suite(sample_suite_path)
#     gb.create_new_profile("sample_suite_test", use_sample_suite)
#     gb.add_source(PATH.HELLO_1, PATH.OUTPUT_ROOT)
#     gb.apply_setting_profile_to_source(PATH.HELLO_1, "sample_suite_test")
#     gb.transcribe()
#     gb.remove_profile("sample_suite_test")
#     gb.delete_plugin_suite("sample_test")
