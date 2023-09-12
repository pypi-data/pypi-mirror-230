# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-08-06 13:32:05
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-06 14:06:25
import os
from typing import List, Dict

import whisperx
from gailbot.core.utils.logger import makelogger

from gailbot.core.utils.media import MediaHandler

from gailbot.core.utils.general import get_extension
from ..engine import Engine

logger = makelogger("whisperX")


class WhisperX(Engine):
    def __init__(self):
        super().__init__()
        self._successful = False

    def __str__(self):
        return "whisperX"

    def __repr__(self):
        return "whisperX"

    def transcribe(
        self, audio_path, payload_workspace, language="en", *args, **kwargs
    ) -> List[Dict[str, str]]:
        path_copy = audio_path
        try:
            new_path = os.path.join(payload_workspace, os.path.basename(audio_path))
            audio_path = MediaHandler.convert_to_16bit_wav(audio_path, new_path)
        except Exception as e:
            logger.error(e, exc_info=e)
            audio_path = path_copy

        # TODO: either store in config or passed in by user
        device = "cpu"
        batch_size = 4
        compute_type = "int8"
        model = whisperx.load_model(
            "base", device, compute_type=compute_type, language=language
        )
        audio = whisperx.load_audio(audio_path)
        result = model.transcribe(audio, batch_size=batch_size, language=language)
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], device=device
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False,
        )
        res = []
        segments = result["segments"]
        nxt_timestamp = 0
        for segment in segments:
            for word in segment["words"]:
                res.append(
                    {
                        "start": word.get("start", nxt_timestamp),
                        "end": word.get("end", nxt_timestamp),
                        "text": word.get("word", "null"),
                        "speaker": "0",
                    }
                )
                nxt_timestamp = word.get("end", nxt_timestamp) + 0.00001
        return res

    def was_transcription_successful(self) -> bool:
        return self._successful

    def get_engine_name(self) -> str:
        """
        Obtain the name of the current engine.
        """
        return "whisperX"

    def get_supported_formats(self) -> List[str]:
        """
        Obtain a list of audio file formats that are supported.
        """
        return ["wav"]

    def is_file_supported(self, filepath: str) -> bool:
        """
        Determine if the given file is supported by the engine.
        """
        return get_extension(filepath) in self.get_supported_formats()
