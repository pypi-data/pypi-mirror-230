# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 14:30:48
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-04 15:18:14
from typing import Dict, List, Tuple, Union, Callable

from gailbot.api import GailBotInterface
from gailbot.core.engines.engineManager import EngineManager
from gailbot.services.organizer import Organizer, SettingDict
from gailbot.services.converter import Converter
from gailbot.services.pipeline import PipelineService
from gailbot.plugins import PluginManager, PluginSuite
from gailbot.core.utils.logger import makelogger
from gailbot.workspace.manager import WorkspaceManager
from gailbot.configs import service_config_loader, default_setting_loader
from userpaths import get_profile

CONFIG = service_config_loader()
DEFAULT_SETTING = default_setting_loader()
logger = makelogger("service_controller")


class GailBot(GailBotInterface):
    def __init__(self, ws_root: str = get_profile(), load_exist_setting: bool = True) -> None:
        super().__init__(ws_root)
        self.ws_manager = WorkspaceManager(ws_root)
        self._init_workspace()
        self.organizer = Organizer(self.ws_manager.setting_src, load_exist_setting)
        self.converter = Converter(self.ws_manager)
        self.plugin_manager = PluginManager(self.ws_manager.plugin_src)
        self.pipeline_service = PipelineService(
            self.plugin_manager, num_threads=CONFIG.thread.transcriber_num_threads
        )
        self.transcribed = set()
        self._init_default_profile()

    def _init_workspace(self) -> bool:
        """
        Resets the workspace: clears the old workspace and initializes a new one.

        Returns: True if the workspace is initialized successful, false otherwise
        """
        try:
            self.ws_manager.clear_gb_temp_dir()
            self.ws_manager.init_workspace()
            return True
        except Exception as e:
            logger.error(f"failed to reset workspace due to the error {e}", exc_info=e)
            return False

    def _init_default_profile(self):
        # add default engine setting
        if not self.organizer.is_engine_setting(DEFAULT_SETTING.engine_name):
            self.organizer.add_new_engine(
                DEFAULT_SETTING.engine_name, DEFAULT_SETTING.engine_data
            )
        self.organizer.set_default_engine(DEFAULT_SETTING.engine_name)

        # add default profile setting
        if not self.organizer.is_profile(DEFAULT_SETTING.profile_name):
            plugin_suites = DEFAULT_SETTING.profile_data["plugin_setting"]
            for suite in plugin_suites:
                if not self.plugin_manager.is_suite(suite):
                    self.organizer.create_new_profile(
                        DEFAULT_SETTING.profile_name,
                        DEFAULT_SETTING.profile_data_no_plugin,
                    )
                    self.organizer.set_default_profile(DEFAULT_SETTING.profile_name)
                    return
            self.organizer.create_new_profile(
                DEFAULT_SETTING.profile_name, DEFAULT_SETTING.profile_data
            )
        self.organizer.set_default_profile(DEFAULT_SETTING.profile_name)

    def clear_workspace(self) -> bool:
        """
        Clears current workspace

        Returns: true if the workspace is cleared, false otherwise
        """
        try:
            self.ws_manager.clear_gb_temp_dir()
            return True
        except Exception as e:
            logger.error(f"failed to reset workspace due to the error {e}", exc_info=e)
            return False

    def reset_workspace(self) -> bool:
        """
        Reset the gailbot workspace

        Returns: True if workspace successfully reset; false otherwise
        """
        return self.ws_manager.reset_workspace()

    def add_sources(self, src_output_pairs: List[Tuple[str, str]]):
        """add a list of sources

        Args:
            src_output_pairs (List[Tuple [str, str]]): a list of pairs that
            stores the input path and the output path

        Returns:
            bool : return true of the sources are added correctly
        """
        logger.info(src_output_pairs)
        try:
            for src_pair in src_output_pairs:
                (source_path, out_path) = src_pair
                logger.debug(source_path)
                logger.debug(out_path)
                assert self.add_source(source_path, out_path)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def add_source(self, src_path: str, out_path: str) -> bool:
        """add a single source

        Args:
            src_path (str): path to the input source
            out_path (str): path to where the output will be stored

        Returns:
            Union[str, bool]: return the name if successfully added, false if not
        """
        logger.info(f"add source {src_path}")
        return self.organizer.add_source(src_path, out_path)

    def remove_source(self, name: str) -> bool:
        """remove the source

        Args:
            name (str): the name of the source, which can be either the
                        full path to the source or the filename


        Returns:
            bool: return true if the source can be deleted correctly
        """
        return self.organizer.remove_source(name)

    def remove_sources(self, names: List[str]) -> bool:
        """Remove the list of sources

        Args:
            names (List[str]): the names of the sources, which can be either the
                        full path to the source or the filename


        Returns:
            bool: True if all sources have been successfully removed, False if not
        """
        for source_name in names:
            if not self.organizer.remove_source(source_name):
                return False
        return True

    def is_source(self, name: str) -> bool:
        """check if a source exists

        Args:
            name (str): either the name of the source or the path to the source

        Returns:
            bool: return true if the source exists
        """
        return self.organizer.is_source(name)

    def get_source_output_directory(self, name: str) -> str:
        """
        Accesses source output directory with a given name

        Args:
            name: str: source name to access

        Returns:
            a string stores the output of the source
        """
        return self.organizer.get_source_output_directory(name)

    def create_new_profile(self, name: str, profile: SettingDict, overwrite: bool = True) -> bool:
        """create a new setting

        Args:
            name (str): the name of the setting
            profile (Dict[str, str]): the setting content
            overwrite (bool)

        Returns:
            bool: return true if the setting can be created, if the setting uses
                  an existing name, the setting cannot be created
        """
        return self.organizer.create_new_profile(name, profile, overwrite)

    def save_profile(self, profile_name: str) -> str | bool:
        """save the setting locally on the disk

        Args:
            profile_name (str): the setting name of the setting

        Returns:
            str | bool : return the saved path if the setting is saved else return false
        """
        return self.organizer.save_profile(profile_name)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """rename a setting

        Args:
            old_name (str): the old name that identifies the setting
            new_name (str): the new name of the setting

        Returns:
            bool: return true if the setting can be renamed correctly,
                  return false if the new setting name has been taken
        """
        return self.organizer.rename_profile(old_name, new_name)

    def update_profile(self, profile_name: str, new_profile: SettingDict) -> bool:
        """updating the setting with new setting content

        Args:
            profile_name (str): the setting name that identifies the setting
            new_profile (SettingDict): the content of the new settings

        Returns:
            bool: return true if the setting can be updated correctly
        """
        return self.organizer.update_profile(profile_name, new_profile)

    def get_all_profile_data(self) -> Dict[str, SettingDict]:
        """return all settings data in a dictionary

        Returns:
            Dict[str, SettingDict]: a dictionary that maps the setting name to
                a setting content
        """
        return self.organizer.get_all_profile_data()

    def get_all_profile_names(self) -> List[str]:
        """get the names fo available settings

        Returns:
            List[str]: a list of available setting names
        """
        return self.organizer.get_all_profile_names()

    def get_src_profile_name(self, source_name: str) -> Union[bool, str]:
        """given a source, return its setting name

        Args:
            source_name (str): the name of the source

        Returns:
            Union[bool, str]: if the source is found, return its setting name,
                              else, return false

        """
        if not self.organizer.is_source(source_name):
            return False
        return self.organizer.get_source_setting(source_name).name

    def get_profile_plugin_setting(self, setting_name: str) -> bool | List[str]:
        """returns the plugin setting of the setting

        Args:
            setting_name (str): name that identifies a setting

        Returns:
            Union[bool, Dict[str, str]]: if the setting is found, return the
            list of string that identifies which plugins are used, else return
            false
        """
        return self.organizer.get_profile_plugin_setting(setting_name)

    def get_profile_dict(self, setting_name: str) -> bool | SettingDict:
        """given a setting name, return the setting content in a dictionary

        Args:
            setting_name (str): name that identifies a setting

        Returns:
            Union[bool, SettingDict]: if the setting is found, returns its setting
            content stored in a dictionary, else returns false
        """
        return self.organizer.get_profile_dict(setting_name)

    def get_source_profile_dict(
            self, source_name: str
    ) -> bool | Dict[str, Union[str, Dict]]:

        """given a source name, return the setting content of the source
            in a dictionary

        Args:
            source_name (str): name that identifies a source

        Returns:
            Union[bool, SettingDict]: if the source is found, returns its setting
            content stored in a dictionary, else returns false
        """
        return self.organizer.get_source_setting(source_name).data

    def remove_profile(self, setting_name: str) -> bool:
        """remove a setting

        Args:
            setting_name (str): the name of the setting that will be removed

        Returns:
            bool: true if the setting is removed, false otherwise
        """
        return self.organizer.remove_profile(setting_name)

    def remove_profiles(self, profile_names: List[str]) -> bool:
        """
        Removes the given list of settings

        Args:
            profile_names: List[str]: names of the setting to remove

        Returns:
            Bool: True if all settings were successfully removed, false if not
        """
        for setting_name in profile_names:
            if not self.organizer.remove_profile(setting_name):
                return False
        return True

    def is_profile(self, name: str) -> bool:
        """check if a setting exists or not

        Args:
            name (str): names that identifies the settings

        Returns:
            bool: return true if the setting exists, false otherwise
        """
        return self.organizer.is_profile(name)

    def get_default_engine_setting_name(self) -> str:
        """get the default setting name

        Returns:
            str: a string that represent the default setting
        """
        return self.organizer.get_default_engine_setting_name()

    def get_default_profile_setting_name(self) -> str:
        """
        Accesses an object's default setting name

        Returns:
            string containing the default name
        """
        return self.organizer.get_default_profile_setting_name()

    def set_default_profile(self, profile_name: str) -> bool:
        """
        Updates an object's default setting to the given setting name

        Args:
            profile_name:str: new setting name

        Returns:
            bool: True if successfully set, false if not
        """
        return self.organizer.set_default_profile(profile_name)

    def apply_profile_to_sources(
            self, sources: List[str], profile: str, overwrite: bool = True
    ) -> bool:
        """apply setting to a list of sources

        Args:
            sources (List[str]): a list of string that identifies the sources
            profile (str): the setting name
            overwrite (bool, optional): if true, overwrites  the existing setting
            . Defaults to True.

        Returns:
            bool: return true if settings can be applied
        """
        return self.organizer.apply_profile_to_sources(sources, profile, overwrite)

    def apply_profile_to_source(
            self, source: str, profile: str, overwrite: bool = True
    ) -> bool:
        """apply setting to a source

        Args:
            source (str): a string that identifies the source
            profile (str): the setting name
            overwrite (bool, optional): if true, overwrites  the existing setting
            . Defaults to True.

        Returns:
            bool: return true if settings can be applied
        """
        return self.organizer.apply_profile_to_source(source, profile, overwrite)

    def is_profile_in_use(self, profile_name: str) -> bool:
        """check if a setting is being used by any source

        Args:
            profile_name (str): the name of the setting

        Returns:
            bool: return true if the setting is being used, false otherwise
        """
        return self.organizer.is_profile_in_use(profile_name)

    def add_progress_callback(self, source: str, callback: Callable):
        """add a displayer function to the source to track the progress of the
            source in the pipeline

        Args:
            source (str): the name of the source
            callback (Callable): a callable function that only takes in
                                  one argument that stores the progress message
                                  as a string

        Returns:
            bool: true if the displayer is added correctly, false otherwise
        """
        return self.organizer.add_progress_callback(source, callback)

    def transcribe(self, sources: List[str] = None) -> Tuple[List[str], List[str]]:
        """return a list of file that was not able to transcribe,
            and the transcription result of the rest of the file

        Args:
            sources (List[str], optional): a list of file names. Defaults to None.

        Returns:
           Tuple [List[str], List[str]]: return a tuple of two list,
                                         the first list stores a list of invalid files,
                                         the second list stores a list of files that
                                         fail to be transcribed
        """
        invalid, fails = [], []

        # get configured sources
        try:
            if not sources:
                source_objs = self.organizer.get_configured_sources(sources)
            else:
                source_objs = [self.organizer.get_source(name) for name in sources]
            # load to converter
            payloads, invalid = self.converter(source_objs)

            if len(source_objs) != 0:
                logger.info(payloads)
                # put the payload to the pipeline
                fails = self.pipeline_service(payloads=payloads)
                logger.info(f"the failed transcriptions are {fails}")
                logger.info(f"the invalid files are {invalid}")

            # remove source from organizer
            if sources:
                for source in sources:
                    self.transcribed.add(source)

            return invalid, fails
        except Exception as e:
            logger.error(e, exc_info=e)
            return invalid, sources

    def clear_source_memory(self) -> bool:
        """clear the memory related with transcribed files,"""
        logger.info("clear source memory")
        try:
            for src in self.transcribed:
                self.organizer.remove_source(src)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)

    def get_all_source_names(self) -> List[str]:
        """
        Returns list of all source names

        Returns: List[str] : list of source names
        """
        return self.organizer.get_all_source_names()

    def register_plugin_suite(self, plugin_source: str) -> Union[List[str], str]:
        """
        Registers a plugin suite to the object's plugin manager

        Args:
            plugin_source: str: plugin suite to register

        Returns:
            Union[str, bool]: return the plugin name if successfully registered,
                              return the string that stores the error message if
                              the plugin is not registered
        """
        return self.plugin_manager.register_suite(plugin_source)

    def get_plugin_suite(self, suite_name) -> PluginSuite:
        """
        Accesses the plugin suite object associated with a given name

        Args:
            suite_name: name of the suite to search for

        Returns:
            PluginSuite: found plugin suite object
        """
        return self.plugin_manager.get_suite(suite_name)

    def get_all_plugin_suites(self) -> set[str]:
        """get names of available plugin suites

        Returns:
            List[str]: a list of available plugin suites name
        """
        return self.plugin_manager.get_all_suites_name()

    def is_plugin_suite(self, suite_name: str) -> bool:
        """
        Determines if a given name is associated with a plugin suite object in the
            plugin manager

        Args:
            suite_name: str: name of the suite to search for

        Returns:
            bool: True if name is associated with an existing plugin suite in the
                manager, false if not
        """
        return self.plugin_manager.is_suite(suite_name)

    def delete_plugin_suite(self, suite_name: str) -> bool:
        """
        Deletes the plugin suite with the given name from the object's plugin manager

        Args:
            suite_name: str: name of the plugin suite to delete

        Returns:
            bool: True if successfully deleted, false if not
        """
        return self.plugin_manager.delete_suite(suite_name)

    def delete_plugin_suites(self, suite_names: List[str]) -> bool:
        """
        Removes the given list of plugin suites

        Args:
            suite_names: List[str]: list of names of the plugin suites to delete

        Returns:
            Bool: true if all plugin suites were successfully removed, false if not
        """
        for suite_name in suite_names:
            if not self.plugin_manager.delete_suite(suite_name):
                return False
        return True

    def get_plugin_suite_metadata(self, suite_name: str):
        """get the metadata of a plugin suite identified by suite name

        Args:
            suite_name (str): the name of the suite

        Returns:
            MetaData: a MetaData object that stores the suite's metadata,

        """
        return self.plugin_manager.get_suite_metadata(suite_name)

    def get_plugin_suite_dependency_graph(self, suite_name: str):
        """get the dependency map of the plugin suite identified by suite_name

        Args:
            suite_name (str): the name of the suite

        Returns:
            Dict[str, List[str]]: the dependency graph of the suite
        """
        return self.plugin_manager.get_suite_dependency_graph(suite_name)

    def get_plugin_suite_documentation_path(self, suite_name: str):
        """get the path to the documentation map of the plugin suite identified by suite_name

        Args:
            suite_name (str): the name of the suite

        Returns:
            str: the path to the documentation file
        """
        return self.plugin_manager.get_suite_documentation_path(suite_name)

    def is_suite_in_use(self, suite_name: str) -> bool:
        """given a suite_name, check if this suite is used
           in any of the setting

        Args:
            suite_name (str): the name of the plugin suite

        Returns:
            bool: return true if the suite is used in any of the setting,
                  false otherwise
        """
        return self.organizer.is_suite_in_use(suite_name)

    def is_official_suite(self, suite_name: str) -> bool:
        """given a suite_name, check if the suite identified by the suite_name
           is official

        Args:
            suite_name (str): the name of the suite

        Returns:
            bool: true if the suite is official false otherwise
        """
        return self.plugin_manager.is_official_suite(suite_name)

    def get_suite_path(self, suite_name):
        """

        Return:
            (str): the path to the source code of the plugin suite
                              identified by suite name
        """
        return self.plugin_manager.get_suite_path(suite_name)

    def get_engine_setting_names(self) -> List[str]:
        """get a list of available engine setting name

        Returns:
            List[str]: the list of engine setting name
        """
        return self.organizer.get_engine_setting_names()

    def add_new_engine(self, name, setting, overwrite=False) -> bool:
        """add a new engine setting

        Args:
            name (str): the name of the engine setting
            setting (Dict[str, str]): the setting data stored in a dictionary
            overwrite (bool, optional): if True, overwrite the existing
                                        engine setting with the same name. Defaults to False.

        Returns:
            bool: return True if the engine setting is successfully created
        """
        return self.organizer.add_new_engine(name, setting, overwrite)

    def remove_engine_setting(self, name) -> bool:
        """remove the engine setting identified by name

        Args:
            name (str): the name of the engine setting to be removed

        Returns:
            bool:  return True if the engine setting is successfully removed
        """
        return self.organizer.remove_engine_setting(name)

    def update_engine_setting(self, name, setting_data: Dict[str, str]) -> bool:
        """update the engine setting identified by name

        Args:
            name (str): the name of the engine setting to be updated
            setting_data (Dict[str, str]): the content of the new setting

        Returns:
            bool:  return True if the engine setting is successfully updated
        """
        return self.organizer.update_engine_setting(name, setting_data)

    def get_engine_setting_data(self, name: str) -> Union[bool, Dict[str, str]]:
        """get the engine setting data

        Args:
            name (str): the name of the engine setting

        Returns:
            Union[bool, Dict[str, str]]: if the engine setting name is available
            return the engine setting data as stored in a dictionary, else return False
        """
        return self.organizer.get_engine_setting_data(name)

    def is_engine_setting_in_use(self, name: str) -> bool:
        """check if the engine setting identified by name is in use

        Args:
            name (str): the name of the engine setting

        Returns:
            bool: return true if the engine setting is in use, false otherwise
        """
        return self.organizer.is_engine_setting_in_use(name)

    def is_engine_setting(self, name: str):
        """check if the given engine name is engine setting

        Args:
            name (str): the name of the engine setting
        """
        return self.organizer.is_engine_setting(name)

    def get_profile_src_path(self, name: str):
        """get the  path to the profile setting source

        Args:
            name (str): the name of the profile
        """
        return self.organizer.get_profile_src_path(name)

    def get_engine_src_path(self, name: str):
        """get the  path to the engine setting source

        Args:
            name (str): the name of the engine
        """
        return self.organizer.get_engine_src_path(name)

    @staticmethod
    def available_engine_api() -> List[str]:
        return EngineManager.available_engines()
