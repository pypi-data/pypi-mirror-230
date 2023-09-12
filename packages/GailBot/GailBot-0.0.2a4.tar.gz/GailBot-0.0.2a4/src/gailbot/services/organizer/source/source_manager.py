# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 14:30:48
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-28 23:33:41
from typing import List, Dict, Union
import os
from .source_object import SourceObject
from ..settings import SettingObject
from gailbot.core.utils.general import get_name, is_file, is_directory, is_path
from gailbot.core.utils.logger import makelogger
from gailbot.configs import workspace_config_loader

OUTPUT_EXTENSION = workspace_config_loader().file_extension.output
logger = makelogger("source_manager")


class SourceManager:
    """
    Holds and handles all functionality for managing all sources
    """

    def __init__(self) -> None:
        self.sources: Dict[str, SourceObject] = dict()

    def add_source(self, source_path: str, output: str) -> Union[str, bool]:
        """
        Adds a source to the source manager object

        Parameters
        ----------
        source_path: str: path to the source object to add
        output: str: path to the output directory

        Returns
        -------
        Union[str, bool]: Name of the source if it is successfully added,
        false if it is not successfully added
        """
        try:
            logger.info("in try")
            name = get_name(source_path)
            i = 0
            while name in self.sources.keys():
                print(name)
                if i:
                    i += 1
                    name = name.replace("---" + str(i - 1), "---" + str(i))
                else:
                    i += 1
                    name = f"{name}---{i}"
            source = SourceObject(source_path, name, output)
            self.sources[name] = source
        except Exception as e:
            logger.info("in exception")
            logger.error(e, exc_info=e)
            return False
        else:
            logger.info("in else")
            return name

    def remove_source(self, source_name: str) -> bool:
        """
        Removes a given source from the source manager's sources

        Parameters
        ----------
        source_name: str: name to remove

        Returns
        ------
        True if given source was successfully removed, false if given
            source was not found
        """
        logger.info(f"source {source_name} is removed")
        if not self.is_source(source_name):
            return False
        self.sources.pop(source_name)
        return True

    def is_source(self, source: str) -> bool:
        """
        Determines if a given source is currently in the source manager's \
        sources

        Parameters
        ----------
        source: str: key of the source to search for

        Returns
        -------
        bool: True if given source was found, false if not
        """
        source_name = get_name(source) if is_path(source) else source
        if source_name in self.sources:
            return True
        else:
            return False

    def source_names(self) -> List[str]:
        """
        Obtains all source names as a list

        Returns
        -------
        List[str]: List of strings containing all source names
        """
        return list(self.sources.keys())

    def get_source(self, source: str) -> Union[bool, SourceObject]:
        """
        Gets the source associated with a given source name

        Parameters
        ----------
        source_name: str: string of name to search for

        Returns
        -------
            Source object associated with the given name
            Returns false if object with given name is not found
        """
        source_name = get_name(source) if is_path(source) else source
        if self.is_source(source_name):
            return self.sources[source_name]
        else:
            return False

    def get_source_outdir(self, source: str) -> Union[bool, str]:
        """
        Gets the source output directory associated with a given source name

        Parameters
        ----------
        source_name: str: string of name to search for

        Returns
        -------
        Source object associated with the given name
        Returns false if object with given name is not found
        """
        source_name = get_name(source) if is_path(source) else source
        if self.is_source(source_name):
            logger.info("is source")
            return self.sources[source_name].output
        else:
            logger.error(source_name)
            return False

    def get_source_setting(self, source: str) -> SettingObject:
        """
        Gets the object;s source settings

        Parameters
        ----------
        source: str: source object to look for

        Returns
        -------
        SettingObject of the current source's settings
        """
        source_name = get_name(source) if is_path(source) else source
        if self.is_source(source_name):
            return self.sources[source_name].source_setting()
        else:
            return False

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
        source_name = get_name(source) if is_path(source) else source
        logger.info(f"apply setting {setting} to {source_name}")
        if self.is_source(source_name):
            self.sources[source_name].apply_setting(setting, overwrite)
            return self.sources[source_name].configured
        logger.error(f"not a valid source")
        return False

    def add_progress_display(self, source: str, displayer: callable) -> bool:
        """
        Add function to display file progress

        Parameters
        ----------
        source (str): a string that identify the source
        displayer (callable): the function that check for file progress

        Returns
        -------
        bool: True if the displayer is applied, false otherwise
        """
        source_name = get_name(source) if is_path(source) else source
        if self.is_source(source_name):
            return self.sources[source_name].add_progress_display(displayer)
        return False

    def get_sources_with_setting(self, profile_name: str) -> List[str]:
        """
        Accesses all sources with a given settings profile

        Parameters
        ----------
        profile_name: string of the settings profile to look for

        Returns
        -------
        List[str]: list of strings of all source names with the settings profile
        Returns an empty list if
        """
        # changed v.setting.get_name() to v.name bc name is the settingObject's name
        return [
            k for k, v in self.sources.items() if v.setting and v.name == profile_name
        ]

    def get_configured_sources(self, sources: List[str] = None) -> List[SourceObject]:
        """
        given a list of source names, returns a list of the sourceObject
        that stores the source configured with setting
            
        Parameters
        ----------
        sources (List[str], optional): a list of source names. If not \
        given, returns a list of configured sources. Defaults to None.

        Returns
        -------
        List[SourceObject]: a list of source objects that stores the source 
        data
        """

        configured = []
        if not sources:
            for source in self.sources.values():
                if source.setting != None:
                    configured.append(source)
            return configured
        else:
            for source in sources:
                src = self.get_source(source)
                if src.setting != None:
                    configured.append(source)
            return configured  # TODO check if this is okay to add this line?

    def is_source_configured(self, source: str) -> bool:
        """
        Determines if given source has been configured with settings

        Args:
            self
            source_name: string of the source name

        Returns:
            True if configured, false if not
        """
        source_name = get_name(source) if is_path(source) else source
        return self.sources[source_name].configured

    def __repr__(self) -> str:
        return f"Source manager with sources {self.source_names}"

    @staticmethod
    def _is_path(source: str):
        """
        Determines if a string is a path

        Args:
            source: str: string to determine if is a path

        Returns:
            bool: true if given string is a path, false if not
        """
        return is_file(source) or is_directory(source)
