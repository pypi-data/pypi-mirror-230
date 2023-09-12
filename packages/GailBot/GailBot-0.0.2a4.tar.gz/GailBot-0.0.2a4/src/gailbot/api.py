# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-08-04 13:59:52
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-09-10 11:24:35
from typing import List, Dict, Union, Tuple, Callable
from gailbot.workspace import WorkspaceManager
from .core.engines.engineManager import EngineManager
from .plugins.suite import PluginSuite
from gailbot.core.utils.logger import makelogger
from gailbot.plugins.manager import PluginManager
from gailbot.services.organizer.source import SourceManager
from gailbot.plugins.suite import PluginSuite, MetaData
from gailbot.services.organizer.settings import SettingManager
from gailbot.services.converter import Converter
from gailbot.services.organizer.settings import SettingManager
from gailbot.services.organizer.settings.objects.settingObject import SettingObject
from gailbot.services.organizer.settings.objects.settingObject import SettingDict
from gailbot.services.organizer.source import SourceManager
from gailbot.services.pipeline import PipelineService
from gailbot.configs import default_setting_loader

CONFIG = default_setting_loader()
DEFAULT_SETTING_NAME = CONFIG.profile_name

logger = makelogger("gb_api")


class GailBot:
    """
    Class for API wrapper
    """

    ###########################################################################
    # Init                                                                    #
    ###########################################################################

    # Done
    def __init__(self, ws_root: str):
        """
        initialize a gailbot object that provides a suite of functions
            to interact with gailbot

        Args:
            ws_root (str): the path to workspace root
        """
        self.ws_manager: WorkspaceManager = WorkspaceManager(ws_root)
        self._init_workspace()
        self.source_manager = SourceManager()
        self.plugin_manager = PluginManager(self.ws_manager.plugin_src)
        self.settingManager: SettingManager = SettingManager(
            workspace=self.ws_manager.setting_src, load_exist=True
        )
        self.source_manager = SourceManager()

        # self.pipeline_service = PipelineService(
        #    self.plugin_manager, num_threads=CONFIG.thread.transcriber_num_threads
        # )
        self.pipeline_service = PipelineService(self.plugin_manager, 5)  # why is it 5?

        self.transcribed = set()
        self.converter = Converter(self.ws_manager)
        self.__init_default_setting()

    def _init_workspace(self) -> bool:
        """
        Resets the workspace: clears the old workspace and initializes a new one.

        Returns
        -------
        True if the workspace is initialized successful, false otherwise
        """
        try:
            self.ws_manager.clear_gb_temp_dir()
            self.ws_manager.init_workspace()
            return True
        except Exception as e:
            logger.error(f"failed to reset workspace due to the error {e}", exc_info=e)
            return False

    def clear_workspace(self) -> bool:
        """
        Clears current workspace

        Returns
        -------
        True if the workspace is cleared, false otherwise
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

        Returns
        -------
        True if workspace successfully reset; false otherwise
        """
        return self.ws_manager.reset_workspace()

    ###########################################################################
    # Sources                                                                 #
    ###########################################################################

    def apply_setting_profile_to_source(
        self, source: str, setting: SettingObject, overwrite: bool = True
    ) -> bool:
        """
        Applies the given settings to the given source

        Parameters
        ----------
        source: str: given source to update
        setting: SettingObject: setting object to apply
        overwrite: bool: whether or not to overwrite

        Returns
        -------
        bool: True if successfully applied, false if not
        """
        return self.source_manager.apply_setting_profile_to_source(
            source, setting, overwrite
        )

    def add_source(self, source_path: str, output_dir: str) -> Union[str, bool]:
        """
        Adds a given source

        Parameters
        ----------
        source_path: str: Source path of the given source
        output_dir: str: Path to the output directory of the given source

        Returns
        -------
        Union[str, bool]: return the name if successfully added, false if not
        """
        logger.info(f"add source {source_path}")
        logger.info(f"source_path: {source_path}, output: {output_dir}")
        try:
            name = self.source_manager.add_source(source_path, output_dir)
            self.source_manager.apply_setting_profile_to_source(
                name,
                self.settingManager.get_setting(
                    self.get_default_profile_setting_name()
                ),
            )
            assert name
            return name
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def add_sources(self, src_output_pairs: List[Tuple[str, str]]) -> bool:
        """
        Adds a given list of sources

        Parameters
        ----------
        src_output_pairs: List [Tuple [str, str]]: List of Tuples of strings;
        string pair representing the source path and output path

        Returns
        -------
        Bool: True if each given source was successfully added, false if not
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

    def is_source(self, name: str) -> bool:
        """
        Determines if a given name corresponds to an existing source

        Parameters
        ----------
        name: str: Name of the source to look for; or path

        Returns
        -------
        Bool: True if the given name corresponds to an existing source,
        false if not
        """
        return self.source_manager.is_source(name)

    def get_source_output_directory(self, source: str) -> Union[bool, str]:
        """
        Accesses source output directory with a given name

        Parameters
        ----------
        source_name: str: source name (without extension) to access

        Returns
        -------
        str: a string stores the output path of the source
        if inaccessible, returns false
        """
        return self.source_manager.get_source_outdir(source)

    def remove_source(self, source_name: str) -> bool:
        """
        Removes the given source

        Parameters
        ----------
        source_name: str: Name of the existing source to remove; without extension

        Returns
        -------
        Bool: True if source was successfully removed, false if not
        """
        return self.source_manager.remove_source(source_name)

    def remove_sources(self, source_names: List[str]) -> bool:
        """
        Removes the given list of sources

        Parameters
        ----------
        source_names : List[str] : list of names of the existing sources to remove

        Returns
        -------
        Bool: True if all sources were successfully removed, false if not
        """
        for source_name in source_names:
            if not self.source_manager.remove_source(source_name):
                return False
        return True

    def get_source_profile_dict(self, source_name) -> Union[bool, SettingDict]:
        """
        Given a source, returns its setting content as a dictionary

        Parameters
        ----------
        source_name (str): the name of the source; or path

        Returns
        -------
        SettingDict:  if the source is found, returns its setting
        content stored in a SettingDict structure, else returns false
        """
        return self.source_manager.get_source_setting(source_name).data

    def clear_source_memory(self) -> bool:
        """
        Clears source memory

        Parameters
        ----------
        None

        Returns
        ----------
        bool: True if successfully cleared, False if not
        """
        logger.info("clear source memory")
        try:
            for src in self.transcribed:
                self.source_manager.remove_source(src)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)

    def get_all_source_names(self) -> List[str]:
        """
        Returns list of all source names

        Parameters
        ----------
        None

        Returns
        -------
        Returns: List[str] : list of source names
        """
        return self.source_manager.source_names()

    ## CHANGED BY HANNAH
    def get_src_profile_name(self, source_name: str) -> Union[bool, str]:
        """
        Given a source name, return the setting name applied to the source

        Parameters
        ----------
        source_name (str): the name the source file; without extensions

        Returns
        ----------
        Union[bool, str]: if the source is found, return the setting name
        applied to the source, else return false
        """
        if not self.source_manager.is_source(source_name):
            return False
        return self.source_manager.get_source_setting(source_name).name

    ###########################################################################
    # Transcribe                                                              #
    ###########################################################################

    def transcribe(self, sources: List[str] = None) -> Tuple[List[str], List[str]]:
        """
        Given a list of the source names, transcribe the sources

        Parameters
        ----------
        sources (List[str], optional): a list of source name, which \
        can be either a list of source paths or the file name of the \
        source file without the file extension.
        if sources is None, the default is to transcribe all sources
        that have been configured

        Returns
        -------
        Tuple[List[str], List[str]]:
            returns a tuple of two lists of string
            the first lists consist of files that are not valid input
            the second lists consist of files that it failed to process.
            However, if getting sources fails, then it instead returns 
            the sources.
        """

        invalid, fails = [], []

        # Get configured sources
        try:
            if not sources:
                source_objs = self.source_manager.get_configured_sources(sources)
            else:
                source_objs = [self.source_manager.get_source(name) for name in sources]
            # Load to converter
            # this sets payloads, invalid to None
            payloads, invalid = self.converter(source_objs)

            if len(source_objs) != 0:
                logger.info(payloads)
                # Put the payload to the pipeline
                fails = self.pipeline_service(payloads=payloads)
                logger.info(f"the failed transcriptions are {fails}")
                logger.info(f"the invalid files are {invalid}")

            if sources:
                for source in sources:
                    self.transcribed.add(source)

            return invalid, fails
        except Exception as e:
            logger.error(e, exc_info=e)
            return invalid, sources

    ###########################################################################
    # Profile (Setting)                                                      #
    ###########################################################################

    def create_new_profile(
        self, name: str, profile: Dict[str, str], overwrite: bool = True
    ) -> bool:
        """
        Create a new Profile

        Parameters
        ----------
        name (str): The name of the profile
        profile (Dict[str, str]): The profile content
        overwrite (bool): whether or not to override an existing profile, \
        defaults to True
                                
        Returns
        -------
        bool: return true if the profile can be created. If the profile uses
        an existing name, the profile cannot be created
        """
        return self.settingManager.add_new_profile(name, profile, overwrite)

    def save_profile(self, profile_name: str) -> Union[bool, str]:
        """
        Saves the given profile

        Parameters
        ----------
        profile_name: str: Name of the setting to save

        Returns
        -------
        Union[bool, str]: Returns the path if setting was successfully saved,
        otherwise false
        """
        return self.settingManager.save_profile(profile_name)

    def get_profile_dict(self, profile_name: str) -> Union[bool, SettingDict]:
        """
        Given a profile name, returns the profile content in a dictionary

        Parameters
        ----------
        profile_name (str): name that identifies a profile

        Returns
        -------
        Union[bool, SettingDict]: if the profile is found, returns its profile
        content stored in a dictionary, else returns false
        """
        return self.settingManager.get_profile_dict(profile_name)

    def get_all_profiles_data(self) -> Dict[str, SettingDict]:
        """
        Given a setting name, return the setting content in a dictionary format

        Returns
        -------
        Dict[str, SettingDict]: a dictionary that maps the setting name to
        a setting content
        """
        return self.settingManager.get_all_profiles_data()

    def get_all_profile_names(self) -> List[str]:
        """
        Get the names of available profiles

        Returns
        -------
        List[str]: a list of available setting names
        """
        return self.settingManager.get_profile_names()

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        Renames a given profile to a given new name

        Parameters
        ----------
        old_name: str: original name of the profile to rename
        new_name: str: name to rename the profile to

        Returns
        -------
        Bool: True if profile was successfully renamed, false if not
        """
        return self.settingManager.rename_profile(old_name, new_name)

    def update_profile(self, profile_name: str, new_profile: Dict[str, str]) -> bool:
        """
        Updates a given setting to a newly given structure

        Parameters
        ----------
        profile_name: str: name of the setting to update
        new_profile: Dict[str, str]: dictionary representation of
        the new structure of the setting

        Returns
        -------
        Bool: true if setting was successfully updated, false if not
        """
        return self.settingManager.update_profile(profile_name, new_profile)

    def get_plugin_profile(self, profile_name: str) -> Union[bool, List[str]]:
        """
        Accesses the plugin setting of a given setting

        Parameters
        ----------
        profile_name: str: name of the setting to get the plugin setting of

        Returns
        -------
        Union[bool, List[str]]: dictionary representation of the plugin setting,
        else false
        """
        setting: SettingObject = self.settingManager.get_setting(profile_name)
        if setting:
            return setting.get_plugin_setting()
        else:
            return False

    def remove_profile(self, profile_name: str) -> bool:
        """
        Removes the given profile

        Parameters
        ----------
        profile_name: str: name of the setting to remove

        Returns
        -------
        Bool: True if setting was successfully removed, false if not
        """
        if not self.settingManager.is_profile(profile_name):
            return False
        try:
            assert self.settingManager.remove_profile(profile_name)
            sources = self.source_manager.get_sources_with_setting(profile_name)
            for source in sources:
                self.source_manager.apply_setting_profile_to_source(
                    source, self.settingManager.get_setting(DEFAULT_SETTING_NAME), True
                )
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def remove_multiple_profiles(self, profile_names: List[str]) -> bool:
        """
        Removes the given list of profiles

        Parameters
        ----------
        profile_names: List[str]: names of the profiles to remove

        Returns
        -------
        Bool: True if all profiles were successfully removed, false if not
        """
        for profile_name in profile_names:
            if not self.remove_profile(profile_name):
                return False
        return True

    def is_profile(self, name: str) -> bool:
        """
        Determines if a given setting name corresponds to an existing setting

        Parameters
        ----------
        name: str: name of the setting to search fort

        Returns
        -------
        Bool: True if given setting is an existing setting, false if not
        """
        return self.settingManager.is_profile(name)

    def apply_profile_to_source(
        self, source: str, profile_name: str, overwrite: bool = True
    ) -> bool:
        """
        Applies a given setting to a given source

        Parameters
        ----------
        source: str: name of the source to which to apply the given setting profile
        setting: str: name of the setting to apply to the given source
        overwrite: bool: determines if it should overwrite from an existing setting
        Defaults to true

        Returns
        ------
        Bool: true if setting was successfully applied, false if not
        """
        return self.source_manager.apply_setting_profile_to_source(
            source, self.settingManager.get_setting(profile_name), overwrite
        )

    def apply_profile_to_sources(
        self, sources: List[str], profile_name: str, overwrite: bool = True
    ) -> bool:
        """
        Applies a given setting to a given list of sources

        Parameters
        ----------
        sources: List[str]: list of names of the sources to which to apply the given setting profile
        setting: str: name of the setting to apply to the given sources
        overwrite: bool: determines if it should overwrite from an existing setting
        Defaults to true

        Returns
        -------
        Bool: true if setting was successfully applied, false if not
        """
        try:
            for source in sources:
                logger.info(f"organizer change {source} setting to {profile_name}")
                assert self.apply_profile_to_source(source, profile_name, overwrite)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def is_profile_in_use(self, profile_name: str) -> bool:
        """
        Checks if a setting is being used by any source

        Parameters
        ----------
        profile_name (str): the name of the setting

        Returns
        ------
        bool: return true if the setting is being used, false otherwise
        """
        src_with_set = self.source_manager.get_sources_with_setting(profile_name)
        if len(src_with_set) == 0:
            return False
        else:
            return True

    def get_default_profile_setting_name(self) -> str:
        """
        Get the name of current default profile

        Returns
        -------
        str: the name of current default profile
        """
        return self.settingManager.get_default_profile_setting_name()

    def set_default_profile(self, profile_name) -> bool:
        """
        Set the default setting to setting name

        Parameters
        ----------
        profile_name (str): the name of the default setting

        Returns
        -------
        bool: true if default setting is set correctly
        """
        return self.settingManager.set_to_default_setting(profile_name)

    ###########################################################################
    # Plugin Suite                                                            #
    ###########################################################################

    def register_plugin_suite(self, plugin_source: str) -> Union[List[str], str]:
        """
        Registers a gailbot plugin suite

        Parameters
        ----------
        plugin_source : str: Path of the plugin suite to register

        Returns
        -------
        return  a list of plugin name if the plugin is registered,
        return the string that stores the error message if the plugin suite
        is not registered
        """
        return self.plugin_manager.register_suite(plugin_source)

    def get_plugin_suite(self, suite_name) -> PluginSuite:
        """
        Gets the plugin suite with a given name

        Parameters
        ----------
        suite_name: string name of the given plugin suite

        Returns
        -------
        PluginSuite with the given name
        """
        return self.plugin_manager.get_suite(suite_name)

    def is_plugin_suite(self, suite_name: str) -> bool:
        """
        Determines if a given plugin suite is an existing plugin suite

        Parameters
        ----------
        suite_name: str: name of the plugin suite of which to determine existence

        Returns
        -------
        Bool: true if given plugin suite exists, false if not
        """
        return self.plugin_manager.is_suite(suite_name)

    def delete_plugin_suite(self, suite_name: str) -> bool:
        """
        Removes the given plugin suite

        Parameters
        ----------
        suite_name: str: name of the plugin suite to delete

        Returns
        -------
        Bool: true if plugin suite was successfully removed, false if not
        """
        return self.plugin_manager.delete_suite(suite_name)

    def delete_plugin_suites(self, suite_names: List[str]) -> bool:
        """
        Removes the given list of plugin suites

        Parameters
        ----------
        suite_names: List[str]: list of names of the plugin suites to delete

        Returns
        -------
        Bool: true if all plugin suites were successfully removed, false if not
        """
        return self.plugin_manager.delete_suites(suite_names)

    def add_progress_display(self, source: str, displayer: Callable) -> bool:
        """
        Add a function displayer to track for the progress of source,

        Parameters
        ----------
        source (str): the name of the source
        displayer (Callable): displayer is a function that takes in a string as
                                argument, and the string encodes the progress of
                                the source

        Returns
        -------
        bool: return true if the displayer is added, false otherwise
        """
        return self.source_manager.add_progress_display(source, displayer)

    def get_all_plugin_suites(self) -> List[str]:
        """
        Get names of available plugin suites

        Returns
        -------
        List[str]: a list of available plugin suites name
        """
        return self.plugin_manager.get_all_suites_name()

    def get_plugin_suite_metadata(self, suite_name: str) -> MetaData:
        """
        Get the metadata of a plugin suite identified by suite name

        Parameters
        ----------
        suite_name (str): the name of the suite

        Returns
        -------
        MetaData: a MetaData object that stores the suite's metadata,
        """
        return self.plugin_manager.get_suite_metadata(suite_name)

    def get_plugin_suite_dependency_graph(
        self, suite_name: str
    ) -> Dict[str, List[str]] | None:
        """
        Get the dependency map of the plugin suite identified by suite_name

        Parameters
        ----------
        suite_name (str): the name of the suite

        Returns
        -------
        Dict[str, List[str]]: the dependency graph of the suite
        Returns None if the suite does not exist
        """
        return self.plugin_manager.get_suite_dependency_graph(suite_name)

    def get_plugin_suite_documentation_path(self, suite_name: str) -> str | None:
        """
        Get the path to the documentation map of the plugin suite identified
        by suite_name

        Parameters
        ----------
        suite_name (str): the name of the suite

        Returns
        -------
        str: the path to the documentation file
        Returns None if the suite does not exist
        """
        return self.plugin_manager.get_suite_documentation_path(suite_name)

    def is_suite_in_use(self, suite_name: str) -> bool:
        """
        Given a suite_name, check if this suite is used in any of the settings

        Args:
        suite_name (str): the name of the plugin suite

        Returns:
        bool: return true if the suite is used in any of the setting,
        false otherwise
        """
        return self.settingManager.is_suite_in_use(suite_name)

    def is_official_suite(self, suite_name: str) -> bool | None:
        """
        Given a suite_name, check if the suite identified by the suite_name
        is official

        Parameters
        ----------
        suite_name (str): the name of the suite

        Returns
        -------
        bool: true if the suite is official false otherwise
        Returns None if the suite does not exist
        """
        return self.plugin_manager.is_official_suite(suite_name)

    def get_suite_source_path(self, suite_name: str) -> str | None:
        """
        Given the name of the  suite , return the path to the source
        code of the suite
        if the suite name doesn't correspond to a valid directory,
        the key value pair is erased from the list of suite names
        and corresponding PluginSuite objects

        Parameters
        ----------
        suite_name (str): the name of the suite

        Returns
        -------
        string: string representing path to the source
        Returns None if the suite does not exist
        """
        return self.plugin_manager.get_suite_path(suite_name)

    ###########################################################################
    # Engines                                                                 #
    ###########################################################################

    def get_engine_setting_names(self) -> List[str]:
        """
        Get a list of all available engine setting name

        Returns
        ----------
        List[str]: a list of all available engine setting names
        """
        return self.settingManager.get_engine_setting_names()

    def add_new_engine(self, name, setting, overwrite=False) -> bool:
        """
        Add a new engine setting

        Parameters
        ----------
        name(str):                 the name of the engine setting
        setting(Dict[str, str]):   the setting data stored in a dictionary
        overwrite(bool, optional): if True, overwrite the existing
                                    engine setting with the same name. Defaults to False.

        Returns
        ----------
        bool: return True if the engine setting is successfully created
                false otherwise
        """
        return self.settingManager.add_new_engine(name, setting, overwrite)

    def remove_engine_setting(self, name) -> bool:
        """
        Remove the engine setting identified by name

        Parameters
        ----------
        name (str): the name of the engine setting to be removed

        Returns
        ----------
        bool:  return True if the engine setting is successfully removed
        """
        return self.settingManager.remove_engine_setting(name)

    def update_engine_setting(self, name, setting_data: Dict[str, str]) -> bool:
        """
        Update the engine setting identified by name

        Parameters
        ----------
        name (str): the name of the engine setting to be updated
        setting_data (Dict[str, str]): the content of the new setting

        Returns
        ----------
        bool:  return True if the engine setting is successfully updated
        """
        return self.settingManager.update_engine_setting(name, setting_data)

    def get_engine_setting_data(self, name: str) -> Union[bool, Dict[str, str]]:
        """get the engine setting data

        Parameters
        ----------
        name (str): the name of the engine setting

        Returns
        ----------
        Union[bool, Dict[str, str]]: if the engine setting name is available
        return the engine setting data as stored in a dictionary, else return False
        """
        return self.settingManager.get_engine_setting_data(name)

    def is_engine_setting_in_use(self, name: str) -> bool:
        """check if the engine setting identified by name is in use

        Parameters
        ----------
        name (str): the name of the engine setting

        Returns
        ----------
        bool: return true if the engine setting is in use, false otherwise
        """
        return self.settingManager.is_engine_setting_in_use(name)

    def is_engine_setting(self, name: str) -> bool:
        """check if the given engine name is engine setting

        Parameters
        ----------
        name (str): the name of the engine setting

        Returns
        ----------
        bool: true if provided engine name is a valid engine setting
        """
        return self.settingManager.is_engine_setting(name)

    def get_default_engine_setting_name(self) -> str:
        """
        Get the default engine setting name

        Returns
        -------
        str: a string that represent the default engine setting
        """
        return self.settingManager.get_default_engine_setting_name()

    def __init_default_setting(self):
        # add default engine setting
        if not self.is_engine_setting(CONFIG.engine_name):
            self.add_new_engine(CONFIG.engine_name, CONFIG.engine_data)
        self.settingManager.set_to_default_engine_setting(CONFIG.engine_name)
        # add default profile setting
        if not self.is_profile(CONFIG.profile_name):
            plugin_suites = CONFIG.profile_data["plugin_setting"]
            for suite in plugin_suites:
                if not self.plugin_manager.is_suite(suite):
                    self.create_new_profile(
                        CONFIG.profile_name, CONFIG.profile_data_no_plugin
                    )
                    self.set_default_profile(CONFIG.profile_name)
                    return
            self.create_new_profile(CONFIG.profile_name, CONFIG.profile_data)
        self.set_default_profile(CONFIG.profile_name)

    @staticmethod
    def available_engine() -> List[str]:
        return EngineManager.available_engines()
