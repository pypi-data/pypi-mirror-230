import os
from pathlib import Path
from typing import Dict, Tuple

import numpy.typing as npt
from pympi.Praat import TextGrid


def detect_clipping(
    samples_array: npt.NDArray, max_threshold=0.995, min_threshold=0.995
) -> Tuple[Dict[str, int], int]:
    """
    Somewhat informed from https://www.sciencedirect.com/science/article/pii/S0167639321000832
    but without the sample-by-sample tagging. Intended to catch cases where clipped values have
    been normalized away.

    Returns the tagged clipped samples and the total number of clipped samples
    """
    if len(samples_array.shape) != 1:
        raise ValueError(
            "You must pass just the samples without any channel information"
        )
    max_sample = samples_array.max()
    min_sample = samples_array.min()
    max_threshold *= max_sample
    min_threshold *= min_sample
    clipping_sections = []
    total_clipped_samples = 0
    clip_end = 0
    for i, sample in enumerate(samples_array):
        if i > clip_end and sample in [max_sample, min_sample]:
            clipping_count = 0
            for new_sample in samples_array[i:]:
                if new_sample >= max_threshold or new_sample <= min_threshold:
                    clipping_count += 1
                else:
                    clipping_sections.append({"start": i, "end": i + clipping_count})
                    total_clipped_samples += clipping_count
                    clip_end = i + clipping_count
                    break
    return clipping_sections, total_clipped_samples


def create_textgrid_from_clipped_sections(
    clipping_sections: Dict[str, int], samples_array: npt.NDArray, sample_rate: int
):
    tg = TextGrid(xmax=len(samples_array) / sample_rate)
    clipping_tier = tg.add_tier("clipping")
    for section in clipping_sections:
        clipping_tier.add_interval(
            section["start"] / sample_rate, section["end"] / sample_rate, "clipped"
        )
    return tg


def get_data_from_audio(audio: npt.NDArray) -> npt.NDArray:
    """Get raw data from audio file

    Args:
        audio (npt.NDArray): A 1D or 2D (samples, channels) array representing the audio

    Raises:
        ValueError: Audio has too many dimensions

    Returns:
        npt.NDArray: Just the sample array, averaged if stereo.
    """
    audio_dims = len(audio.shape)
    if audio_dims == 1:
        return audio
    if audio_dims == 2:
        # if mono
        if audio.shape[1] == 1:
            return audio[0]
        # if stereo
        elif audio.shape[1] == 2:
            return (audio[:, 0] + audio[:, 1]) / 2
        else:
            raise ValueError(
                "Audio has too many dimensions. Please pass only a single audio file at a time."
            )
    if audio_dims > 2:
        raise ValueError(
            "Audio has too many dimensions. Please pass only a single audio file at a time."
        )


def process_audio_file_from_path(audio_path: Path):
    from scipy.io.wavfile import read as read_wav  # Heavy import so loading it here

    if not audio_path.suffix.endswith("wav"):
        raise ValueError(
            f"Path at {audio_path} is not a wav file, please choose another file."
        )
    sr, data = read_wav(audio_path)
    return (audio_path, sr, data)
