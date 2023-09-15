import csv
import os
from datetime import datetime
from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm

app = typer.Typer()


@app.command()
def main(
    audio_path: Path = typer.Argument(None, exists=True, file_okay=True, dir_okay=True),
    export_textgrids: bool = typer.Option(False, "--textgrid", "-t"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """
    Detect clipping at a provided path. Path must be pointed to a wav file or a folder containing wav files.
    """
    from clipdetect import (
        create_textgrid_from_clipped_sections,
        detect_clipping,
        get_data_from_audio,
        process_audio_file_from_path,
    )

    if audio_path.is_file():
        audio_to_process = [process_audio_file_from_path(audio_path)]
    if audio_path.is_dir():
        logger.info(f"Reading Audio from {audio_path}")
        audio_to_process = [
            process_audio_file_from_path(audio)
            for audio in tqdm(audio_path.glob("*.wav"))
        ]
    if not audio_to_process:
        raise FileNotFoundError(f"Sorry, no wav files found at {audio_path}")
    logger.info("Detecting Clipping in Audio")
    results = []
    for path, sr, audio in tqdm(audio_to_process):
        samples_array = get_data_from_audio(audio)
        samples_array_len = len(samples_array)
        clipping_sections, total_clipped_samples = detect_clipping(samples_array)
        results.append(
            {
                "path": path,
                "clipped_samples": total_clipped_samples,
                "sr": sr,
                "number_of_samples": samples_array_len,
            }
        )
        if total_clipped_samples and verbose:
            logger.info(
                f"Audio at path {path} has {total_clipped_samples} clipped samples out of {samples_array_len}"
            )
        if export_textgrids:
            tg = create_textgrid_from_clipped_sections(clipping_sections, samples_array, sr)
            fn, _ = os.path.splitext(path)
            tg.to_file(f"{fn}.textgrid")
    if len(results) > 1:
        dt = datetime.now()
        with open(
            f"clipdetect-log-{int(datetime.timestamp(dt))}.csv", "w", encoding="utf8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            for line in results:
                writer.writerow(line)
    else:
        logger.info(
            f"Audio at path {path} has {total_clipped_samples} clipped samples out of {samples_array_len}. Re-run command with --textgrid to output clipped sections to textgrid."
        )


if __name__ == "__main__":
    app()
