# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-30 01:42:39
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-30 03:35:13

import pytest
from gailbot.plugins.suite import (
    PluginComponent,
    PluginSuite,
    ComponentResult,
    ComponentState,
)
from gailbot.plugins.plugin import Plugin, Methods
from gailbot.plugins.manager import PluginManager, ERROR
from typing import Dict, Any, List
from gailbot.core.utils.logger import makelogger
from tests.test_data.path import PATH
from tests.plugins.plugin_data import Invalid

logger = makelogger("test_plugins")
TEST_CONFIG_SRC = "/Users/yike/Documents/GitHub/GailBot/data/test_suite/conf.toml"
TEST_DIR_SRC = "/Users/yike/Documents/GitHub/GailBot/data/test_suite"
HIL_CONFIG_SRC = "/Users/yike/Documents/GitHub/GailBot/HiLabSuite/config.toml"
HIL_DIR_SRC = "/Users/yike/Documents/GitHub/GailBot/HiLabSuite"
SUCCESS_RESULT = ComponentResult(ComponentState.SUCCESS)
FAILURE_RESULT = ComponentResult(ComponentState.FAILED)

TEST_SUITE_NAME = "test_suite"
HIL_LAB_SUITE_NAME = "HiLabSuite"


@pytest.fixture
def plugin_manager() -> PluginManager:
    """
    Driver function for creating an instance of PluginManager for testing
    """
    return PluginManager(
        workspace=PATH.OUTPUT_ROOT, load_existing=False, over_write=True
    )


def test_plugin_init():
    """
    Purpose: Very simple test testing the initialization of a Plugin
    Expected Output: assert existence of testPlugin
    """
    testPlugin = Plugin()
    assert testPlugin


def test_register_suite_invalid_input(plugin_manager: PluginManager):
    """
    Purpose: Test registering a plugin suite with an invalid URL.
    Expected Output: The result should be ERROR.INVALID_URL.
    """
    result = plugin_manager.register_suite("invalid_url")
    assert result == ERROR.INVALID_INPUT


def _test_register_suite_missing_config(plugin_manager: PluginManager):
    """
    Purpose: Test registering a plugin suite without a config file.
    Expected Output: The result should be ERROR.MISSING_CONFIG.
    """
    result = plugin_manager.register_suite("path/to/plugin/suite/without/config")
    assert result == ERROR.MISSING_CONFIG


def _test_get_all_suites_name(plugin_manager: PluginManager):
    """
    Purpose: Test getting the names of all registered plugin suites.
    Expected Output: The result should be a list of strings.
    """
    plugin_manager.register_suite("path/to/a/valid/plugin/suite")
    result = plugin_manager.get_all_suites_name()
    assert isinstance(result, list)


def _test_is_suite(plugin_manager: PluginManager):
    """
    Purpose: Test checking if a plugin suite exists.
    Expected Output: The result should be a boolean indicating whether the plugin suite exists or not.
    """
    plugin_manager.register_suite("path/to/plugin/suite/called/example_suite")
    result = plugin_manager.is_suite("example_suite")
    assert result == True


def _test_reset_workspace(plugin_manager: PluginManager):
    """
    Purpose: Test resetting the plugin workspace.
    Expected Output: The plugin manager should have no registered plugin
                     suites after resetting the workspace.
    """
    plugin_manager.register_suite("path/to/a/valid/plugin/suite")
    plugin_manager.reset_workspace()
    result = plugin_manager.get_all_suites_name()
    assert len(result) == 0


def _test_delete_suite(plugin_manager: PluginManager):
    """
    Purpose: Test deleting a plugin suite.
    Expected Output: The result should be True if the deletion is successful, otherwise False.
    """
    plugin_manager.register_suite("path/to/plugin/suite/called/example_suite")
    result = plugin_manager.delete_suite("example_suite")
    assert result == True


def _test_get_suite(plugin_manager: PluginManager):
    """
    Purpose: Test getting a specific plugin suite.
    Expected Output: The result should be the PluginSuite object associated with the given suite name.
    """
    plugin_manager.register_suite("path/to/plugin/suite/called/example_suite")
    suite = plugin_manager.get_suite("example_suite")
    assert suite is not None
    assert isinstance(suite, PluginSuite)


def _test_get_suite_dependency_graph(plugin_manager: PluginManager):
    """
    Purpose: Test getting the dependency graph of a plugin suite.
    Expected Output: The result should be a dictionary representing the
                     dependency graph of the plugin suite.
    """
    plugin_manager.register_suite("path/to/plugin/suite/called/example_suite")
    result = plugin_manager.get_suite_dependency_graph("example_suite")
    assert isinstance(result, dict)


def _test_validate_valid_plugin(plugin_manager: PluginManager):
    """
    Purpose: Test validating a valid plugin suite
    Expected Output: result from validate_plugin_structure asserted to be true
    """
    expected = "dictionary/storing/expected/structure/of/config/file"
    plugin_manager.register_suite("path/to/a/valid/plugin/suite")
    result = plugin_manager.validate_plugin_structure(
        user_suite="path/to/config/file/for/registered/suite", expected=expected
    )
    assert result == True


def _test_validate_invalid_plugin(plugin_manager: PluginManager):
    """
    Purpose: Test validating an invalid plugin suite
    Expected Output: result from validate_plugin_structure asserted not True
    """
    expected = "dictionary/storing/expected/structure/of/config/file"
    plugin_manager.register_suite("path/to/an/invalid/plugin/suite")
    result = plugin_manager.validate_plugin_structure(
        user_suite="path/to/config/file/for/registered/suite", expected=expected
    )
    assert not result == True


@pytest.mark.parametrize(
    "source", [[Invalid.InvalidConf, Invalid.InvalidConf2, Invalid.InvalidConf3]]
)
def _test_invalid_configuration(source):
    """
    Purpose: Testing with invalid configuration sources
    """
    test = PluginManager(
        plugin_sources=source,
        load_existing=False,
    )
