# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 19:21:51
# @Last Modified by:   Jacob Boyar
# @Last Modified time: 2023-08-15 15:53:01
from typing import Dict, List, Union, TypedDict

from ..interface import (
    load_watson_setting,
    load_whisper_setting,
    load_google_setting,
    EngineSettingInterface,
    PluginSettingsInterface,
)
from gailbot.core.utils.logger import makelogger
from gailbot.core.utils.general import write_toml
from gailbot.configs import default_setting_loader
from ..interface.whisperXInterface import load_whisperX_setting

logger = makelogger("engineObject")


class EngineSetObj:
    """
    store a single Engine setting

    """

    engine_setting: EngineSettingInterface = None
    name: str = None
    valid_interfaces = [load_whisper_setting, load_google_setting, load_watson_setting, load_whisperX_setting]

    def __init__(self, setting: Dict[str, str], name: str) -> None:
        """initializing an engine

        Args:
            setting (Dict[str, str]): engine setting data stored in a dictionary
            name (str): the name of the engine setting
        """
        self.applied_in_profiles = (
            set()
        )  # a set of profiles that applied this engine setting
        self.name = name
        logger.info("initialize the setting object")
        assert self._load_engine_setting(setting)
        self.data = setting
        self.engine = self.engine_setting.engine

    def get_init_kwargs(self):
        return self.engine_setting.get_init_kwargs()

    def get_transcribe_kwargs(self):
        return self.engine_setting.get_transcribe_kwargs()

    def get_name(self):
        """
        Accesses and returns the object's name
        """
        return self.name

    def change_name(self, name):
        """
        Changes the profile name to a given new name

        Args:
            name: name to change to
        """
        self.name = name

    def get_profile_dict(self) -> Dict[str, str]:
        """
        Accesses and returns the object's setting dict

        Returns
        -------
        Dict[str, str]: the object's setting dictionary
        """
        return self.data

    def update_profile(self, setting: Dict[str, str]) -> bool:
        """
        Updates the settings to a given dictionary

        Parameters
        ----------
        setting: Dict[str, str]: new setting

        Returns
        -------
        bool: True if successfully updated, false if not
        """
        logger.info(setting)
        self._load_engine_setting(setting)

        if self.engine_setting:
            self.data = setting
            return True
        else:
            return False

    def save_profile(self, output: str) -> bool:
        """
        Saves the settings to the output directory
        
        Parameters
        ----------
        output:str: output directory path

        Returns
        -------
        bool: True if successfully saved, false if not
        """
        logger.info(self.data)
        try:
            write_toml(output, self.data)
        except Exception as e:
            logger.error(e, exc_info=e)
            return False
        else:
            return True

    def is_in_use(self) -> bool:
        """
        Checks whether a given engine is in use
        
        Returns
        -------
        bool: true if in use, false otherwisie
        """
        return len(self.applied_in_profiles) != 0

    def remove_applied_profile(self, profile_name):
        """
        Removed an applied profile with the given profile name

        Parameters
        ----------
        profile_name : str: The name of the profile to add

        Returns
        -------
        None
        """
        if profile_name in self.applied_in_profiles:
            self.applied_in_profiles.remove(profile_name)

    def add_applied_profile(self, profile_name) -> None:
        """
        Adds an applied profile with the given profile name

        Parameters
        ----------
        profile_name : str: The name of the profile to add

        Returns
        -------
        None
        """
        self.applied_in_profiles.add(profile_name)

    def _load_engine_setting(self, setting: Dict[str, str]) -> bool:
        """
        Loads the engine settings

        Args:
            setting : List[str]: settings to load

        Returns:
            bool: true if successfully loaded, false if not
        """
        logger.info("initialize the engine setting")
        for option in self.valid_interfaces:
            logger.info(option)
            set_obj = option(setting)
            if isinstance(set_obj, EngineSettingInterface):
                self.engine_setting = set_obj
                return True
        logger.info(f"setting {setting} cannot be loaded")
        return False
