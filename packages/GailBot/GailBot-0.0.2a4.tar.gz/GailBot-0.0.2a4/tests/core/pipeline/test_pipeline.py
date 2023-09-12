# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-28 18:22:50
from gailbot.core.pipeline import Pipeline, Component, ComponentResult, ComponentState
import pytest
from gailbot.core.utils.logger import makelogger
from typing import Dict, List, Any

logger = makelogger("test_pipeline")


class TestComponent(Component):
    """
    Defines a class for a test component
    Inherits Component class
    """

    def __init__(self, name: str, sleeptime: int):
        self.name = name
        self.sleeptime = sleeptime

    def __call__(
        self, dependency_outputs: Dict[str, ComponentResult], *args, **kwargs
    ) -> ComponentState:
        logger.info(self.name)
        logger.info(f"Dependency outputs: {dependency_outputs}")
        return ComponentResult(
            state=ComponentState.SUCCESS, result=self.name, runtime=self.sleeptime
        )

    def __repr__(self):
        return f"Component{self.name}"

    @property
    def __name__(self):
        return self.name


def test_pipeline_sequence():
    """
    test_pipeline_sequence()
    Purpose:            Test the basic functionality of a pipeline. Runs
                        sequential execution in a given dependency graph.

    Expected Output:    Logger information on the components being run in the
                        test pipeline.
    """
    components = {str(i): TestComponent(i, i) for i in range(1, 11)}
    pipeline = Pipeline(
        dependency_map={
            "1": [],
            "2": ["1"],
            "3": ["2"],
            "4": ["3"],
            "5": ["4"],
            "6": ["5"],
            "7": ["6"],
            "8": ["7"],
            "9": ["8"],
            "10": ["9"],
        },
        components=components,
        num_threads=10,
    )
    res = pipeline([], {})
    logger.info(res)


def test_pipeline_has_cylce():
    """
    test_pipeline_has_cycle()
    Purpose:            Test exception handling for cyclical graph
    Expected Output:    None
    """
    components = {str(i): TestComponent(i, 3 * i) for i in range(1, 6)}
    with pytest.raises(Exception) as e:
        pipeline = Pipeline(
            dependency_map={"1": ["2"], "2": ["1"], "3": ["1"], "4": ["1"], "5": ["1"]},
            components=components,
            num_threads=1,
        )
        pipeline._generate_dependency_graph(pipeline.dependency_graph)
        graph = pipeline.get_dependency_graph()
        pipeline._does_cycle_exist(graph)
        logger.info(e)


def test_component_info():
    """
    test_component_info()
    Purpose:            Test that component information are accessible
    Expected Output:    Logger output with component name, whether it is a
                        component, it's parent components, and its child
                        components.
    """
    components = {str(i): TestComponent(i, 3 * i) for i in range(1, 6)}
    pipeline = Pipeline(
        dependency_map={"1": [], "2": ["1"], "3": ["1"], "4": ["1", "3"], "5": ["2"]},
        components=components,
        num_threads=1,
    )
    for i in range(1, 6):
        logger.info(
            f"component {i}, is_component: {pipeline.is_component(str(i))}, component_parents: {pipeline.component_parents(str(i))}, component_children: {pipeline.component_children(str(i))}"
        )


def test_complex_dependency():
    """
    test_complex_dependency()
    Purpose:            Test pipeline with a complex dependency map
    Expected Output:    All components are in success state
    """
    components = {str(i): TestComponent(str(i), 1) for i in range(1, 17)}

    pipe = Pipeline(
        dependency_map={
            "2": [],
            "4": [],
            "6": [],
            "3": ["2", "4"],
            "15": ["3"],
            "1": ["2", "3", "4"],
            "5": ["1", "2"],
            "7": ["2", "5", "6"],
            "8": ["7", "6"],
            "9": ["2", "7", "8"],
            "10": ["1", "4"],
            "11": ["4", "1", "8"],
            "12": ["10", "2", "7", "3"],
            "13": ["10", "12", "11", "9", "8", "7", "6"],
            "14": ["13"],
            "16": ["15"],
        },
        components=components,
        num_threads=3,
    )

    res = pipe([], {})
    logger.info(res)
    for i in range(1, 17):
        assert res[str(i)] == ComponentState.SUCCESS
