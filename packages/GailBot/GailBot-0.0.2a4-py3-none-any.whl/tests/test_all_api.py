from unittest.mock import patch
from gailbot.api import GailBot
from tests.testdata.path import PATH
from tests.testdata.setting import SETTING_DATA
import logging
from gailbot.workspace import WorkspaceManager


class TestGailbot:
    WS_ROOT = "/Users/yike/Desktop/gbtest"

    gb = GailBot(PATH.OUTPUT_ROOT)

    assert gb.add_new_engine(
        SETTING_DATA.WHISPER_NAME, SETTING_DATA.WHISPER_SETTING, overwrite=True
    )
    assert gb.add_new_engine(SETTING_DATA.GOOGLE_NAME, SETTING_DATA.GOOGLE_SETTING, overwrite=True)
    assert gb.add_new_engine(
        SETTING_DATA.WATSON_NAME, SETTING_DATA.WATSON_SETTING, overwrite=True
    )
    assert gb.add_new_engine(
        SETTING_DATA.WHISPER_SP_NAME, SETTING_DATA.WHISPER_SPEAKER, overwrite=True
    )

    def transcribe(
            self,
            files,
            setting_name="test",
            setting_data=SETTING_DATA.WHISPER_PROFILE,
            output=PATH.OUTPUT_ROOT,
            fail_test=False,
    ):
        self.gb.add_sources([(f, output) for f in files])
        if not self.gb.is_profile(setting_name):
            assert self.gb.create_new_profile(setting_name, setting_data)
        assert self.gb.apply_profile_to_sources(files, setting_name)
        for file in files:
            assert self.gb.get_src_profile_name(file) == setting_name
            assert self.gb.is_source(file)
        fails, invalid = self.gb.transcribe()
        logging.info(fails)
        logging.info(invalid)
        if not fail_test:
            assert not (fails or invalid)
        return fails, invalid

    def test_clear_workspace(self):
        pass

    def test_reset_workspace(self):
        pass

    def test_add_source(self):
        pass

    def test_add_sources(self):
        pass

    def test_is_source(self):
        pass

    def test_get_source_output_directory(self):
        pass

    def test_remove_source(self):
        pass

    def test_remove_sources(self):
        pass

    def test_clear_source_memory(self):
        pass

    def test_get_src_profile_name(self):
        pass

    def test_get_source_profile_dict(self):
        pass

    def test_transcribe(self):
        pass

    def test_create_new_profile(self):
        pass

    def test_save_profile(self):
        pass

    def test_get_profile_dict(self):
        pass

    def test_get_all_profile_data(self):
        pass

    def test_get_all_profile_names(self):
        pass

    def test_rename_profile(self):
        pass

    def test_update_profile(self):
        pass

    def test_get_profile_plugin_setting(self):
        pass

    def test_remove_profile(self):
        pass

    def test_remove_profiles(self):
        pass

    def test_is_profile(self):
        pass

    def test_apply_profile_to_source(self):
        pass

    def test_apply_profile_to_sources(self):
        pass

    def test_is_profile_in_use(self):
        pass

    def test_get_default_profile_setting_name(self):
        pass

    def test_set_default_profile(self):
        pass

    def test_register_plugin_suite(self):
        pass

    def test_get_plugin_suite(self):
        pass

    def test_is_plugin_suite(self):
        pass

    def test_delete_plugin_suite(self):
        pass

    def test_delete_plugin_suites(self):
        pass

    def test_add_progress_display(self):
        pass

    def test_get_all_plugin_suites(self):
        pass

    def test_get_plugin_suite_metadata(self):
        pass

    def test_get_plugin_suite_dependency_graph(self):
        pass

    def test_get_plugin_suite_documentation_path(self):
        pass

    def test_is_suite_in_use(self):
        pass

    def test_is_official_suite(self):
        pass

    def test_get_suite_source_path(self):
        pass

    def test_get_engine_setting_names(self):
        pass

    def test_add_new_engine(self):
        pass

    def test_remove_engine_setting(self):
        pass

    def test_update_engine_setting(self):
        pass

    def test_get_engine_setting_data(self):
        pass

    def test_is_engine_setting_in_use(self):
        pass

    def test_is_engine_setting(self):
        pass

    def test_get_default_engine_setting_name(self):
        pass
