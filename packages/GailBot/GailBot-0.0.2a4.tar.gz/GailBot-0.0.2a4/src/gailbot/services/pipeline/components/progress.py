# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-31 16:21:27
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-01 05:52:58

from dataclasses import dataclass


@dataclass
class ProgressMessage:
    Start = "\u25B6 Start"
    Waiting = "\U0001F551 Waiting"
    Transcribing = "\u25CC Transcribing"
    Finished = "\u2705 Completed"
    Transcribed = "\u2705 Transcribed"
    Error = "\U0001F6AB Error"
    Analyzing = "\U0001F4AC Analyzing"
    Analyzed = "\u2705 Analyzed"
