# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-08-06 14:01:35
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-06 14:20:16
from gailbot.core.engines.whisperX.whisperX import WhisperX
import pytest
from .data import AudioPath


def whisperx_test(audio_path, detect_speaker: bool, output_path):
    engine = WhisperX()
    print(engine)
    print(engine.get_engine_name())
    print(engine.get_supported_formats())
    assert engine.is_file_supported(filepath=audio_path)
    result = engine.transcribe(
        audio_path=audio_path,
        payload_workspace=output_path,
        language="en",
    )


@pytest.mark.parametrize(
    "audio_path, detect_speaker, output_path",
    [(AudioPath.SHORT_AUDIO, False, "short_phone_call.json")],
)
def test_short(audio_path, detect_speaker, output_path):
    """
    test_short()
    Purpose:            Test the functionality for whisper engine using a small
                        input audio file
    Expected Output:    Transcription sucessful with output files in the specified
                        output directory
    """
    whisperx_test(audio_path, detect_speaker, output_path)
