# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-28 18:22:27
"""
File: test_media.py
Project: GailBot GUI
File Created: Saturday, 21st January 2023 11:01:59 am
Author: Siara Small  & Vivian Li
-----
Last Modified: Wednesday, 25th January 2023 6:47:31 am
Modified By:  Siara Small  & Vivian Li
-----
"""
from typing import List
from gailbot.core.utils import media
from gailbot.core.utils import general
from tests.test_data.path import PATH
import shutil
import pytest
import os
import json

""" global file path for testing  """
# TEST_BASE =  f"{os.getcwd()}/data/test_file/"
# INPUT_DIR = f"{os.getcwd()}/data/test_file/audio_file_input"
# STEREO_DIR = f"{os.getcwd()}/data/test_file/stereo_file"
# OUTPUT_DIR = f"{os.getcwd()}/data/test_file/audio_file_output"

TEST_BASE = os.path.join(PATH.TEST_ROOT, "gbtest")
INPUT_DIR = PATH.INPUTROOT
STEREO_DIR = os.path.join(TEST_BASE, "stereo_file")
OUTPUT_DIR = PATH.OUTPUT_ROOT


def test_setup():
    """
    helper function to create an output directory if such a directory does not
    exist
    """
    if not general.is_directory(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)


@pytest.fixture
def handlers() -> media.AudioHandler:
    """
    initialize and return media and audio handlers
    """
    audio_handler = media.AudioHandler()
    media_handler = media.MediaHandler()
    return [audio_handler, media_handler]


def test_support_format(handlers: List[media.AudioHandler]):
    """
    Purpose:            Checking the fields for supported media
                        file formats
    Expected Output:    Assertion true
    """
    for handler in handlers:
        assert handler.supported_formats == handler._SUPPORTED_FORMATS


def test_is_supported(handlers: List[media.MediaHandler]):
    """
    Purpose:            Checking that media types are supported
    Expected Output:    Assertions met that formats are supported
    """
    for handler in handlers:
        basename = "test"
        print(handler.supported_formats)
        for format in handler.supported_formats:
            assert media.MediaHandler.is_supported(f"{basename}.{format}")
            assert not media.MediaHandler.is_supported(f"{basename}.not {format}")


def test_read_write_stream(handlers):
    """
    Purpose:            Testing read_file() and write_stream()
    Expected Output:    Assertions met that files are read properly
    """
    output = f"{OUTPUT_DIR}/write_stream"
    if general.is_directory(output):
        shutil.rmtree(output)
    os.mkdir(output)
    for handler in handlers:
        files = general.filepaths_in_dir(INPUT_DIR)
        for file in files:
            stream: media.AudioStream = handler.read_file(file)
            assert stream
            format = general.get_extension(file)
            handler.write_stream(stream, output, format=format)


def test_get_info(handlers):
    """
    Purpose:            Test info() functionality on each file
    Expected Output:    Files with results from info() wrriten in
                        an info output directory
    """
    output = f"{OUTPUT_DIR}/info"
    if general.is_directory(output):
        shutil.rmtree(output)
    os.mkdir(output)
    for handler in handlers:
        files = general.filepaths_in_dir(INPUT_DIR)
        for file in files:
            stream: media.AudioStream = handler.read_file(file)
            info = handler.info(stream)
            with open(f"{output}/{stream.name}", "w+") as f:
                f.write(json.dumps(info))


def test_change_volume(handlers):
    """
    Purpose:            Test change_volume() functionality
    Expected Output:    A new audio stream after volume has been
                        changed
    """
    for handler in handlers:
        files = general.filepaths_in_dir(INPUT_DIR)
        output = f"{OUTPUT_DIR}/volume"
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        for file in files:
            stream: media.AudioStream = handler.read_file(file)
            assert stream
            after_change: media.AudioStream = handler.change_volume(stream, 10)
            format = general.get_extension(file)
            handler.write_stream(after_change, output, format=format)


def test_stereo_mono_convert(handlers):
    """
    Purpose:            Test stereo_to_mono() functionality
    Expected Output:    Original stereo file as well as left and right
                        audio files in mono_stereo output directory
    """
    for handler in handlers:
        files = general.filepaths_in_dir(STEREO_DIR)
        # files = general.filepaths_in_dir(PATH.MANY_SMALL_FILES_DIR)
        output = f"{OUTPUT_DIR}/mono_stereo"
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        for file in files:
            stream: media.AudioStream = handler.read_file(file)
            assert stream.segment.channels == 2
            mono_left, mono_right = handler.stereo_to_mono(stream)
            assert mono_left, mono_right
            assert mono_left.segment.channels == 1
            assert mono_right.segment.channels == 1
            stereo: media.AudioStream = handler.mono_to_stereo(mono_left, mono_right)
            assert stereo
            assert stereo.segment.channels == 2
            format = general.get_extension(file)
            handler.write_stream(mono_right, output, format=format)
            handler.write_stream(mono_left, output, format=format)
            handler.write_stream(stereo, output, format=format)


def test_concat(handlers):
    """
    Purpose:            Test concat() functionality
    Expected Output:    Assertion met that audio streams are concatenated
                        and resultant audio file is in output directory
    """
    for handler in handlers:
        output = f"{OUTPUT_DIR}/concat"
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        files = general.filepaths_in_dir(INPUT_DIR)
        for file in files:
            stream1 = handler.read_file(file)
            stream2 = handler.read_file(file)
            concated = handler.concat([stream1, stream2])
            assert concated
            format = general.get_extension(file)
            handler.write_stream(concated, output, format=format)


def test_overlay(handlers):
    """
    Purpose:            Test overlay() functionality
    Expected Output:    A resultant overlay audio file in output directory
    """
    for handler in handlers:
        output = f"{OUTPUT_DIR}/overlay"
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        audio_files = general.filepaths_in_dir(INPUT_DIR)
        music_files = general.filepaths_in_dir(STEREO_DIR)
        for audio, music in zip(audio_files, music_files):
            audio_stream = handler.read_file(audio)
            music_stream = handler.read_file(music)
            overlayed = handler.overlay(audio_stream, music_stream)
            assert overlayed
            handler.write_stream(overlayed, output, format=general.get_extension(audio))


def test_reverse(handlers):
    """
    Purpose:            Test reverse() functionality
    Expected Output:    Resultant reversed audio file in output directory
    """
    output = f"{OUTPUT_DIR}/reverse"
    for handler in handlers:
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        files = general.filepaths_in_dir(INPUT_DIR)
        for file in files:
            stream = handler.read_file(file)
            reversed = handler.reverse(stream)
            # assert reversed
            format = general.get_extension(file)
            handler.write_stream(reversed, output, format=format)


def test_chunck(handlers):
    """
    Purpose:            Test chunk() functionality
    Expected Output:    Series of chunked audio files in output directory
    """
    output = f"{OUTPUT_DIR}/chunck"
    for handler in handlers:
        if general.is_directory(output):
            shutil.rmtree(output)
        os.mkdir(output)
        # files = general.filepaths_in_dir(INPUT_DIR)
        files = general.filepaths_in_dir(PATH.MEDIUM_AUDIO)

        for file in files:
            stream = handler.read_file(file)
            assert stream.segment.duration_seconds > 2.0
            chunks = handler.chunk(stream, 2.0)
            format = general.get_extension(file)
            for chunk in chunks:
                handler.write_stream(chunk, output, format=format)
