# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 19:21:51
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-08-17 12:27:33
"""
# -*- coding: utf-8 -*-
@Author  :   Vivian Li , Siara Small 
@Date    :   2023/05/17
@Last Modified By :   Vivian, Siara Small
@Last Modified Time :   2023/05/17 19:50:58
"""

from typing import Dict, Union, List
import os

from .objects import SettingDict, SettingObject, PluginSuiteSetObj, EngineSetObj
from gailbot.core.utils.general import (
    is_file,
    is_directory,
    read_toml,
    get_name,
    make_dir,
    delete,
    filepaths_in_dir,
)
from gailbot.core.utils.logger import makelogger

logger = makelogger("setting_manager")


class ExistingSettingName(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(*args)
        self.name = name

    def __str__(self) -> str:
        return f"the setting name {self.name} already exist"


class SettingManager:
    """
    Manages all available settings
    """

    profiles: Dict[str, SettingObject] = dict()
    engine_settings: Dict[str, EngineSetObj] = dict()

    def __init__(self, workspace: str, load_exist: bool = True) -> None:
        """constructing the setting manager

        Args:
            workspace (str): the path to the directory stores all the
                             setting files
            load_exist (bool, optional): if true , load existing setting in
                             workspace. Defaults to True.
        """
        self.workspace = workspace
        self.engine_set_space = os.path.join(workspace, "engine_setting")
        self.default_setting = None
        self.default_engine_setting = None

        if not is_directory(self.workspace):
            make_dir(self.workspace)

        if not is_directory(self.engine_set_space):
            make_dir(self.engine_set_space)

        if load_exist:
            engine_files = filepaths_in_dir(self.engine_set_space, ["toml"])
            for file in engine_files:
                self.load_set_from_file(file, self.add_new_engine, overwrite=True)

            setting_files = filepaths_in_dir(self.workspace, ["toml"])
            for file in setting_files:
                self.load_set_from_file(file, self.add_new_profile, overwrite=True)

    def load_set_from_file(self, file_path, addfun, overwrite: bool = False) -> bool:
        """load the setting from local file

        Args:
            file_path (str): the file path
            overwrite (bool, optional): if true, the loaded
            file will overwrite existing setting with same name. Defaults to False.

        Returns:
            bool: return true if the loading is successful, false if the file
            cannot be loaded
        """
        if is_file(file_path):
            data = read_toml(file_path)
            try:
                name = get_name(file_path)
                data = read_toml(file_path)
                return addfun(name, data, overwrite)
            except Exception as e:
                logger.error(e, exc_info=e)
                return False

    #####################################################################
    #               Functions for managing engine setting               #
    #####################################################################
    def get_engine_setting_names(self) -> List[str]:
        """
        Return a list of available engine setting name

        Returns
        -------
        List[str]: a list of engine setting names
        """
        return list(self.engine_settings.keys())

    def add_new_engine(self, name, engine: Dict[str, str], overwrite: bool = False):
        """
        Add a new engine setting

        Parameters
        ----------
        name (str): the name of the engine setting
        engine (Dict[str, str]): the data of the engine setting,
            one required field is the type of the engine
        overwrite (bool, optional): if True, overwrite the existing engine
            setting with the same name. Defaults to False.

        Returns
        -------
        bool: return true if the setting is successfully added, false otherwise

        Raises
        ------
        ExistingSettingName: if the engine setting name has been taken, and overwrite is set to False

        """
        if self.is_engine_setting(name) and (not overwrite):
            raise ExistingSettingName(name)
        try:
            setting: EngineSetObj = EngineSetObj(engine, name)
            assert setting.engine_setting
            self.engine_settings[name] = setting
            self.save_engine_setting(name)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def remove_engine_setting(self, name):
        """
        Remove the engine setting from the disk

        Parameters
        ----------
        name (str): the name of the engine setting

        Returns
        -------
        bool: return true if the engine setting is removed successfully
        """
        try:
            assert self.is_engine_setting(name)
            assert not self.engine_settings[name].is_in_use()
            del self.engine_settings[name]
            if is_file(self.get_engine_src_path(name)):
                delete(self.get_engine_src_path(name))
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def is_engine_setting_in_use(self, name) -> bool:
        """
        Checks if the engine setting is in use

        Parameters
        ----------
        name (str): the name of the engine setting

        Returns
        -------
        bool: whether or not the name is currently in use
        """
        return self.engine_settings[name].is_in_use()

    def is_engine_setting(self, name):
        """check if the given setting is engine setting

        Parameters
        ----------
        name (str): the name that identify the engine setting

        Returns
        -------
        bool: true if the setting is engine setting false otherwise
        """
        return name in self.engine_settings

    def save_engine_setting(self, name: str) -> Union[bool, str]:
        """save the setting as a local file

        Parameters
        ----------
        name (str): the setting name

        Returns
        -------
        Union[bool, str]: return the saved file path if the setting is
            saved successfully, return false otherwise
        """
        try:
            out_path = self.get_engine_src_path(name)
            if is_file(out_path):
                delete(out_path)
            self.engine_settings[name].save_profile(out_path)
            return out_path
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def update_engine_setting(self, name: str, setting_data: Dict[str, str]) -> bool:
        """
        Update the engine setting

        Parameters
        ----------
        name: str: the name of the engine to update
        setting_data: Dict[str, str]: the data to update the engine with

        Returns
        ------
        bool: whether or not the data was updated successfully
        """
        if self.is_engine_setting(name):
            try:
                engine_setting = self.engine_settings[name]
                assert engine_setting.update_profile(setting_data)
                assert self.save_engine_setting(name)
                for profile in engine_setting.applied_in_profiles:
                    ## update the engine setting on the disk
                    self.save_profile(profile)
                return True
            except Exception as e:
                logger.error(e, exc_info=e)
                return False

    def get_engine_src_path(self, name: str) -> str:
        """
        Given a engine setting name, return its path

        Parameters
        ----------
        name (str): the engine setting name

        Returns
        -------
        str: a path to store the setting file

        Note
        ----
        This is a function to form a path to the local setting file
        in a unified format, the path does not guaranteed to indicate
        an existing setting file
        """
        return os.path.join(self.engine_set_space, name + ".toml")

    def get_engine_setting_data(self, name: str) -> Union[bool, Dict[str, str]]:
        """
        Get the setting data of the engine setting

        Parameters
        ----------
        name (str): the name of the engine

        Returns
        -------
        Union[bool, Dict[str, str]]: return the dictionary that stores the
            the engine data if the data engine
            name is a valid engine in the setting
            manager, else return false
        """
        if self.is_engine_setting(name):
            return self.engine_settings[name].get_profile_dict()
        else:
            return False

    def _get_profile_engine(self, profile_name: str) -> EngineSetObj:
        """
        Return the engine used in the profile identifies by profile name

        Parameters
        ----------
        profile_name (str): the name of the profile to be queried

        Returns
        -------
        EngineSetObj: the engine object
        """
        profile_obj = self.profiles[profile_name]
        engine_obj = self.engine_settings[profile_obj.engine_setting_name]
        return engine_obj

    def set_to_default_engine_setting(self, setting_name: str) -> bool:
        """
        Set one setting to be the default setting

        Parameters
        ----------
        name (str): the name of the setting

        Returns
        -------
        bool: return true if the default setting can be set,
            false otherwise
        """
        if setting_name in self.profiles:
            self.default_engine_setting = setting_name
            return True
        else:
            return False

    def get_default_engine_setting_name(self) -> str:
        """
        Get the default engine setting name

        Returns
        -------
        str: a string that represent the default engine setting
        """
        return self.default_engine_setting

    #####################################################################
    #               Functions for managing profile setting              #
    #####################################################################
    def get_profile_names(self) -> List[str]:
        """
        Return a list of available setting names

        Returns
        -------
        List[str]: a list of setting names
        """
        return list(self.profiles.keys())

    def remove_profile(self, name: str) -> bool:
        """
        given the setting name, remove the setting and the local
        setting file

        Parameters
        ----------
        name (str): the name that identify the setting

        Returns
        -------
        bool: return true if the removal is successful, else false
        """
        if self.is_profile(name):
            settingObj = self.profiles.pop(name)
            self.engine_settings[settingObj.engine_setting_name].remove_applied_profile(
                name
            )
            if is_file(self.get_profile_src_path(name)):
                delete(self.get_profile_src_path(name))
            return True
        else:
            return False

    def get_setting(self, name: str) -> Union[SettingObject, bool]:
        """
        Given the profile name, return the corresponding setting

        Parameters
        ----------
        name (str): a name that identifies the setting

        Returns
        -------
        Union [SettingObject, bool]: return the setting object if the
        setting is found, return false if the setting does not exist
        """
        if self.is_profile(name):
            return self.profiles[name]
        else:
            return False

    def add_new_profile(
        self, name: str, data: SettingDict, overwrite: bool = True
    ) -> Union[bool, str]:
        """
        Makes a new profile

        Parameters
        ----------
            name (str): The name of the profile
            setting (Dict[str, str]): The profile content
            overwrite (bool): whether or not to override an existing profile, \
                                defaults to True
                                
        Returns
        -------
            bool: return true if the profile can be created. If the profile uses
                  an existing name, the profile cannot be created
        
        Raises
        ------
            ExistingSettingName: raised when the setting name already exists
            and the overwrite option is set to false. Will not occur.
        """
        logger.info(f"get engine {data}")
        if self.is_profile(name):
            if overwrite:
                self.remove_profile(name)
            else:
                raise ExistingSettingName(name)
        try:
            engine_set_name = data["engine_setting_name"]
            # HANNAH CHANGED: Issue with Watson vs watson, put to lower
            # engine_obj = self.engine_settings[engine_set_name.lower()]
            engine_obj = self.engine_settings[engine_set_name]
            plugin_obj = PluginSuiteSetObj(data["plugin_setting"])
            profile: SettingObject = SettingObject(
                engine_setting=engine_obj,
                engine_setting_name=engine_set_name,
                plugin_setting=plugin_obj,
                name=name,
            )
            self.engine_settings[engine_set_name].add_applied_profile(name)
            assert profile and profile.engine_setting
            self.profiles[name] = profile
            self.save_profile(name)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

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
        return name in self.profiles

    def update_profile(self, name: str, setting_data: SettingDict) -> bool:
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
        if self.is_profile(name):
            try:
                profile_setting = self.profiles[name]
                orig_engine = profile_setting.engine_setting.name
                engine_set_name = setting_data["engine_setting_name"]
                engine_obj = self.engine_settings[engine_set_name]
                plugin_obj = PluginSuiteSetObj(setting_data["plugin_setting"])
                assert profile_setting.update_profile(
                    engine_setting=engine_obj, plugin_setting=plugin_obj
                )
                assert self.save_profile(name)
                return True
            except Exception as e:
                logger.error(e, exc_info=e)
        else:
            return False

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        Renames a profile

        Parameters
        ----------
        old_name (str): the old name that identifies the profile
        new_name (str): the new name of the profile

        Returns
        -------
        bool: return true if the profile can be renamed correctly,
        return false if the new profile name has been taken
        """
        if self.is_profile(old_name):
            if self.is_profile(new_name):
                logger.error(f"new name{new_name} has been taken")
                return False

            temp = self.profiles.pop(old_name)
            engine_applied = self._get_profile_engine(old_name)
            engine_applied.remove_applied_profile(old_name)

            temp.name = new_name
            engine_applied.add_applied_profile(new_name)
            self.profiles[new_name] = temp
            self.save_profile(new_name)

            if is_file(self.get_profile_src_path(old_name)):
                delete(self.get_profile_src_path(old_name))
            logger.info("update_profile")
            return self.profiles[new_name] != None
        else:
            logger.error("the setting is not found")
            return False

    def save_profile(self, name: str) -> Union[bool, str]:
        """
        Saves the profile as a local file

        Parameters
        ----------
        name (str): the profile name

        Returns
        -------
        Union[bool, str]: return the saved file path if the setting
        is saved successfully, return false otherwise
        """
        try:
            out_path = self.get_profile_src_path(name)
            if is_file(out_path):
                delete(out_path)
            self.profiles[name].save_profile(out_path)
            return out_path
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def get_profile_dict(self, profile_name: str) -> Union[bool, SettingDict]:
        """
        Return the setting data as a dictionary

        Parameters
        ----------
        profile_name (str): the name that identifies the profile

        Returns
        -------
        Union[bool, SettingDict]: if the profile exists, return the profile
        data, else return false
        """
        if profile_name in self.profiles:
            return self.profiles[profile_name].get_data()
        else:
            return False

    def get_profile_src_path(self, name: str) -> str:
        """
        Given a profile name, return its path

        Parameters
        ----------
        name (str): the profile name

        Returns
        -------
        str: a path to store the profile file

        Note
        ----
        This is a function to form a path to the local profile file
        in a unified format, the path does not guaranteed to indicate
        an existing profile file
        """
        return os.path.join(self.workspace, name + ".toml")

    def delete_all_settings(self) -> bool:
        """
        Delete all settings

        Returns
        -------
        bool: True if the deletion is successful, false if not
        """
        try:
            for setting in self.get_profile_names():
                if setting != "default":
                    self.remove_profile(setting)
            return True
        except Exception as e:
            logger.error(e, exc_info=e)
            return False

    def get_all_profiles_data(self) -> Dict[str, SettingDict]:
        """
        Returns a dictionary that stores all available setting data

        Returns
        -------
        Dict[str, SettingDict]: a dictionary that maps the setting name to
        a setting content
        """
        setting_dict = dict()
        for key, setting_object in self.profiles.items():
            setting_dict[key] = setting_object.data

        logger.info(f"setting data {setting_dict}")
        return setting_dict

    def set_to_default_setting(self, profile_name: str) -> bool:
        """
        Set the default setting to setting name

        Parameters
        ----------
        profile_name (str): the name of the default setting

        Returns
        -------
        bool: true if default setting is set correctly
        """
        if profile_name in self.profiles:
            self.default_setting = profile_name
            return True
        else:
            return False

    def get_default_profile_setting_name(self) -> str:
        """
        Get the name of current default profile

        Returns
        -------
        str: the name of current default profile
        """
        return self.default_setting

    #####################################################################
    #       function for managing plugin setting                        #
    #####################################################################

    def is_suite_in_use(self, suite_name: str) -> bool:
        """
        Given a suite_name, check if this suite is used in any of the setting

        Parameters
        ----------
        suite_name (str): the name of the plugin suite

        Returns
        --------
        bool: return true if the suite is used in any of the setting,
        false otherwise
        """
        for setting_obj in self.profiles.values():
            if suite_name in setting_obj.get_plugin_setting():
                return True
        return False
