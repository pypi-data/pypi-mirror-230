# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 14:30:48
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-04 15:23:04
from typing import Dict, List, Union, Callable

from .source import SourceObject, SourceManager
from gailbot.core.utils.logger import makelogger
from .settings import SettingManager, SettingObject, SettingDict
from gailbot.configs import default_setting_loader

logger = makelogger("organizer")
CONFIG = default_setting_loader()
DEFAULT_SETTING_NAME = CONFIG.profile_name
DEFAULT_SETTING = CONFIG.profile_data
DEFAULT_ENGINE_NAME = CONFIG.engine_name
DEFAULT_ENGINE_SETTING = CONFIG.engine_data


class Organizer:
    def __init__(
            self, setting_workspace: str, load_exist_setting: bool = False
    ) -> None:
        self.setting_manager = SettingManager(setting_workspace, load_exist_setting)
        self.source_manager = SourceManager()

    def add_source(self, source_path: str, output: str) -> bool | str:
        """
        Adds given source to the output directory

        Args:
            source_path: str: path to the source to add
            output: str: path to the output directory

        Returns:
            bool | str : return the name if successfully added, false if not
        """
        logger.info(f"source_path: {source_path}, output: {output}")
        try:
            name = self.source_manager.add_source(source_path, output)
            self.apply_profile_to_source(name, self.get_default_profile_setting_name())
            assert name
            return name
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def remove_source(self, source: str) -> bool:
        """
        Removes given source

        Args:
            source: str: path to the source to remove

        Returns:
            bool: True if successfully removed, false if not
        """
        return self.source_manager.remove_source(source)

    def is_source(self, source: str) -> bool:
        """
        Determines if given name corresponds to an existing source

        Args:
            source: str: name of potential source

        Returns:
            bool: true if the name corresponds to an existing source, false if not
        """
        return self.source_manager.is_source(source)

    def get_source(self, source: str) -> Union[bool, SourceObject]:
        """
        Accesses source with a given name

        Args:
            source: str: source name to access

        Returns:
            Source object associated with the given name or false if source object is not found
        """
        return self.source_manager.get_source(source)

    def get_all_source_names(self) -> List[str]:
        """
        Returns list of all source names

        Returns: List[str] : list of source names
        """
        return self.source_manager.source_names()

    def get_source_output_directory(self, source: str) -> Union[bool, str]:
        """
        Accesses source output directory with a given name

        Args:
            source: str: source name to access

        Returns:
            a string stores the output of the source
        """

        return self.source_manager.get_source_outdir(source)

    def get_source_setting(self, source: str) -> SettingObject:
        """
        Accesses the settings of a source with a given name

        Args:
            source: str: source name whose setting to access

        Returns:
            Source settings associated with the given name or false if source object is not found
        """
        return self.source_manager.get_source_setting(source)

    def is_profile_applied(self, source: str) -> bool:
        """
        Determines if a given source has configured settings

        Args:
            source: str: source name to access

        Returns:
            bool: True if given source is configured, false if not
        """
        return self.source_manager.is_source_configured(source)

    def apply_profile_to_source(
            self, source: str, profile: str, overwrite: bool = True
    ) -> bool:
        """apply setting to a source

        Args:
            source (str): either file name or file path that identifies the source
            profile (str): the profile name
            overwrite (bool, optional): if true, overwrites  the existing setting
            . Defaults to True.

        Returns:
            bool: return true if settings can be applied
        """
        return self.source_manager.apply_setting_profile_to_source(
            source, self.get_profile_obj(profile), overwrite
        )

    def apply_profile_to_sources(
            self, sources: List[str], profile: str, overwrite: bool = True
    ) -> bool:
        """apply setting to a list of sources

        Args:
            sources (List[str]): a list of string that identifies the sources
            profile (str): the profile name
            overwrite (bool, optional): if true, overwrites  the existing setting
            . Defaults to True.

        Returns:
            bool: return true if settings can be applied
        """
        try:
            for source in sources:
                logger.info(f"organizer change {source} setting to {profile}")
                assert self.apply_profile_to_source(source, profile, overwrite)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def add_progress_callback(self, source_name: str, callback: Callable):
        """add a displayer function to the source to track the progress of the
            source in the pipeline

        Args:
            source_name (str): the name of the source
            callback (Callable): a callable function that only takes in
                                  one argument that stores the progress message
                                  as a string

        Returns:
            bool: true if the displayer is added correctly, false otherwise
        """
        return self.source_manager.add_progress_display(source_name, callback)

    def create_new_profile(self, setting_name: str, setting: SettingDict, overwrite: bool = True) -> bool:
        """create a new setting

        Args:
            setting_name (str): the name of the setting
            setting (Dict[str, str]): the setting content
            overwrite (Boolean): if true, overwrite existing profile with the same name

        Returns:
            bool: return true if the setting can be created, if the setting uses
                  an existing name, the setting cannot be created
        """
        return self.setting_manager.add_new_setting(setting_name, setting, overwrite)

    def save_profile(self, setting_name: str) -> str | bool:
        """save the setting locally on the disk

        Args:
            setting_name (str): the setting name of the setting

        Returns:
            str | bool : return the saved path if the setting is saved else return false
        """
        return self.setting_manager.save_setting(setting_name)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """rename a setting

        Args:
            old_name (str): the old name that identifies the setting
            new_name (str): the new name of the setting

        Returns:
            bool: return true if the setting can be renamed correctly,
                  return false if the new setting name has been taken
        """
        try:
            self.setting_manager.rename_setting(old_name, new_name)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def remove_profile(self, profile: str) -> bool:
        """remove a setting

        Args:
            profile (str): the name of the setting that will be removed

        Returns:
            bool: true if the setting is removed, false otherwise
        """
        if not self.setting_manager.is_setting(profile):
            return False
        try:
            assert self.setting_manager.remove_setting(profile)
            sources = self.source_manager.get_sources_with_setting(profile)
            for source in sources:
                self.remove_profile_from_source(source)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def update_profile(self, profile: str, new_setting: Dict[str, str]) -> bool:
        """updating the setting with new setting content

        Args:
            profile (str): the setting name that identifies the setting
            new_setting (SettingDict): the content of the new settings

        Returns:
            bool: return true if the setting can be updated correctly
        """
        return self.setting_manager.update_setting(profile, new_setting)

    def get_profile_obj(self, profile: str) -> SettingObject:
        """get setting object that is identified by setting name

        Args:
            profile (str): the name that identifies the setting object

        Returns:
            SettingObject: a setting object that stores the setting data
        """
        return self.setting_manager.get_setting(profile)

    def get_profile_dict(self, profile: str) -> SettingObject | bool:
        """given a source name, return the setting content of the source
            in a dictionary

        Args:
            profile: (str): name that identifies a source

        Returns:
            Union[bool, SettingDict]: if the source is found, returns its setting
            content stored in a dictionary, else returns false
        """
        return self.setting_manager.get_setting_dict(profile)

    def is_profile(self, profile: str) -> bool:
        """check if a setting exists or not

        Args:
            profile (str): names that identifies the settings

        Returns:
            bool: return true if the setting exists, false otherwise
        """
        return self.setting_manager.is_setting(profile)

    def is_profile_in_use(self, profile: str) -> bool:
        """check if a setting is being used by any source

        Args:
            profile (str): the name of the setting

        Returns:
            bool: return true if the setting is being used, false otherwise
        """
        src_with_set = self.source_manager.get_sources_with_setting(profile)
        if len(src_with_set) == 0:
            return False
        else:
            return True

    def remove_profile_from_source(self, source_name: str) -> bool:
        """given a source name, remove the current setting from the source,
            set the setting of the source to default

        Args:
            source_name (str): the name that identifies the source

        Returns:
            bool: return true if the setting is removed successfully false otherwise
        """
        return self.apply_profile_to_source(source_name, DEFAULT_SETTING_NAME, True)

    def get_profile_plugin_setting(self, profile: str) -> List[str] | bool:
        """returns the plugin setting of the setting

        Args:
            profile (str): name that identifies a setting

        Returns:
            Union[bool, Dict[str, str]]: if the setting is found, return the
            list of string that identifies which plugins are used, else return
            false
        """
        setting: SettingObject = self.setting_manager.get_setting(profile)
        if setting:
            return setting.get_plugin_setting()
        else:
            return False

    def get_configured_sources(self, sources: List[str] = None) -> List[SourceObject]:
        """given a list of source name, return a list of the sourceObject
            that stores the source configured with setting
        Args:
            sources (List[str], optional): a list of source name, if not
            given, return a list of configured source. Defaults to None.

        Returns:
            List[SourceObject]: a list of source object that stores the source data
        """
        return self.source_manager.get_configured_sources(sources)

    def get_engine_setting_names(self) -> List[str]:
        """get a list of available engine setting name

        Returns:
            List[str]: the list of engine setting name
        """
        return self.setting_manager.get_engine_setting_names()

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
        return self.setting_manager.add_new_engine(name, setting, overwrite)

    def remove_engine_setting(self, name) -> bool:
        """remove the engine setting identified by name

        Args:
            name (str): the name of the engine setting to be removed

        Returns:
            bool:  return True if the engine setting is successfully removed
        """
        return self.setting_manager.remove_engine_setting(name)

    def update_engine_setting(self, name, setting_data: Dict[str, str]) -> bool:
        """update the engine setting identified by name

        Args:
            name (str): the name of the engine setting to be updated
            setting_data (Dict[str, str]): the content of the new setting

        Returns:
            bool:  return True if the engine setting is successfully updated
        """
        return self.setting_manager.update_engine_setting(name, setting_data)

    def is_engine_setting(self, name: str):
        """check if the given engine name is engine setting

        Args:
            name (str): the name of the engine setting
        """
        return self.setting_manager.is_engine_setting(name)

    def get_engine_setting_data(self, name: str) -> Union[bool, Dict[str, str]]:
        """get the engine setting data

        Args:
            name (str): the name of the engine setting

        Returns:
            Union[bool, Dict[str, str]]: if the engine setting name is available
            return the engine setting data as stored in a dictionary, else return False
        """
        return self.setting_manager.get_engine_setting_data(name)

    def is_engine_setting_in_use(self, name: str) -> bool:
        """check if the engine setting identified by name is in use

        Args:
            name (str): the name of the engine setting

        Returns:
            bool: return true if the engine setting is in use, false otherwise
        """
        return self.setting_manager.is_engine_setting_in_use(name)

    def remove_all_profiles(self) -> bool:
        """remove all settings except for the default setting

        Returns:
            bool: return true if the removal is successful
        """
        try:
            for setting in self.setting_manager.get_setting_names():
                if setting != DEFAULT_SETTING_NAME:
                    assert self.remove_profile(setting)
            for source in self.source_manager.get_configured_sources():
                assert source.setting_name() == DEFAULT_SETTING_NAME
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def get_profile_names(self) -> List[str]:
        """return a list of available setting names

        Returns:
            List[str]: a list of available setting names
        """
        return self.setting_manager.get_setting_names()

    def get_all_profile_data(self) -> Dict[str, SettingDict]:
        """
        return a dictionary that stores all setting data
        """
        return self.setting_manager.get_all_settings_data()

    def get_all_profile_names(self) -> List[str]:
        """
        return a list of string that stores all setting name
        """
        return self.setting_manager.get_setting_names()

    def get_default_engine_setting_name(self) -> str:
        """get the default setting name

        Returns:
            str: a string that represent the default setting
        """
        return self.setting_manager.get_default_engine_setting_name()

    def get_default_profile_setting_name(self) -> str:
        """get the default setting name

        Returns:
            str: a string that represent the default setting
        """
        return self.setting_manager.get_default_profile_setting_name()

    def set_default_profile(self, profile: str) -> bool:
        """set the default setting to setting_name

        Args:
            profile (str)

        Returns:
            bool:return true if the setting can be set, false otherwise
        """
        return self.setting_manager.set_to_default_setting(profile)

    def set_default_engine(self, engine_name: str) -> bool:
        """set the default setting to engine_name

        Args:
            engine_name (str)

        Returns:
            bool:return true if the setting can be set, false otherwise
        """
        return self.setting_manager.set_to_default_engine_setting(engine_name)

    def is_suite_in_use(self, suite_name: str) -> bool:
        """given a suite_name, check if this suite is used
           in any of the setting

        Args:
            suite_name (str): the name of the plugin suite

        Returns:
            bool: return true if the suite is used in any of the setting,
                  false otherwise
        """
        return self.setting_manager.is_suite_in_use(suite_name)

    def get_profile_src_path(self, name: str):
        """get the  path to the profile setting source

        Args:
            name (str): the name of the profile
        """
        return self.setting_manager.get_profile_src_path(name)

    def get_engine_src_path(self, name: str):
        """get the  path to the engine setting source

        Args:
            name (str): the name of the engine
        """
        return self.setting_manager.get_engine_src_path(name)
