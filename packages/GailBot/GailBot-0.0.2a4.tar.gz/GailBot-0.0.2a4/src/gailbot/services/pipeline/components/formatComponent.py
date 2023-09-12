# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-17 19:21:51
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-01 05:53:27
from typing import List, Dict

from gailbot.core.pipeline import Component, ComponentState, ComponentResult
from gailbot.core.utils.logger import makelogger
from ...converter.payload import PayLoadObject

logger = makelogger("transcribeComponent")


class FormatComponent(Component):
    def __call__(self, dependency_outputs: Dict[str, ComponentResult], *args, **kwargs) -> ComponentResult:
        """
        Gets a source and the associated settings objects and transcribes it

        Args:
            dependency_outputs : Dict[str, Any]: output of the dependency map to search through

        Returns:
            ComponentResult: the result of the formatting process
        """
        try:
            dependency_res: ComponentResult = dependency_outputs["analysis"]
            payloads: List[PayLoadObject] = dependency_res.result
            logger.info(
                f"format component is run, {len(payloads)} result will be formatted"
            )
            logger.info(payloads)
            for payload in payloads:
                logger.info(f"saving {payload.name} result to {payload.out_dir}")
                payload.save()
                if not payload.failed:
                    payload.set_formatted()
                payload.clear_temporary_workspace()

            assert dependency_res.state == ComponentState.SUCCESS
            return ComponentResult(
                state=ComponentState.SUCCESS, result=payloads, runtime=0
            )

        except Exception as e:
            logger.error(e, exc_info=e)
            logger.error(f"error in formatting payload result {e}")
            return ComponentResult(state=ComponentState.FAILED, result=None, runtime=0)

    def __repr__(self):
        return "Format component"

    def emit_progress(self, payload: PayLoadObject, msg: str):
        if payload.progress_display:
            payload.progress_display(msg)
