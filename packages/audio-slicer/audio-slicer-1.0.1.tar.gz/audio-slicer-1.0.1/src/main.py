import librosa  # Optional. Use any library you like to read audio files.
import soundfile  # Optional. Use any library you like to write audio files.
import re
from .slicer2 import Slicer
from .slicer_time import slicer_time
import argparse
import logging
import os
import glob
import numpy as np


logging.basicConfig(
    format="[autocut:%(filename)s:L%(lineno)d] %(levelname)-6s %(message)s")
logging.getLogger().setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Edit videos based on transcribed subtitles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        help="intpu files",
        type=str
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="Cutting mode, mute cuts audio by mute, time cuts by time period, default mute",
        type=str,
        default="mute",
        choices=[
            "mute",
            "time"
        ]
    )
    parser.add_argument(
        "-time_unit",
        "--time_unit",
        help="Cutting mode time by time,ms",
        type=int,
        default=20 * 1000,
    )
    parser.add_argument(
        "-t",
        "--threshold",
        help="The RMS threshold presented in dB. Areas where all RMS values are below this threshold will be regarded as silence. Increase this value if your audio is noisy. Defaults to -40",
        type=int,
        default=-40
    )
    parser.add_argument(
        "-ml",
        "--min_length",
        help="The minimum length required for each sliced audio clip, presented in milliseconds. Defaults to 5000",
        type=int,
        default=5000
    )

    parser.add_argument(
        "-mi",
        "--min_interval",
        help=("The minimum length for a silence part to be sliced, presented in milliseconds. Set this value smaller if your audio contains only short breaks. The smaller this value is, the more sliced audio clips this script is likely to generate. Note that this value must be smaller than min_length and larger than hop_size. Defaults to 300."),
        type=int,
        default=300
    )
    parser.add_argument(
        "-hs",
        "--hop_size",
        help=("Length of each RMS frame, presented in milliseconds. Increasing this value will increase the precision of slicing, but will slow down the process. Defaults to 10."),
        type=int,
        default=10
    )
    parser.add_argument(
        "-msk",
        "--max_sil_kept",
        help=("The maximum silence length kept around the sliced audio, presented in milliseconds. Adjust this value according to your needs. Note that setting this value does not mean that silence parts in the sliced audio have exactly the given length. The algorithm will search for the best position to slice, as described above. Defaults to 1000."),
        type=int,
        default=1000
    )
    args = parser.parse_args()

    input = args.input if isabs_path(
        args.input) else os.path.join(os.path.curdir, args.input)
    print(f"input={input} {args}")
    if os.path.isfile(input):
        handle(
            file=input,
            mode = args.mode,
            threshold=args.threshold,
            min_length=args.min_length,
            min_interval=args.min_interval,
            hop_size=args.hop_size,
            max_sil_kept=args.max_sil_kept,
            time_unit = args.time_unit
        )
    elif os.path.isdir(input):
        dir = input
        files = glob.glob(dir+"/*.(mp3|wav|flac)")
        print(f"files={files}")
        for i, name in files:
            handle(
                file=os.path.join(dir, name),
                mode = args.mode,
                threshold=args.threshold,
                min_length=args.min_length,
                min_interval=args.min_interval,
                hop_size=args.hop_size,
                max_sil_kept=args.max_sil_kept,
                time_unit = args.time_unit
            )


def handle(
    file: str,
    mode: str,
    threshold: int,
    min_length: int,
    min_interval: int,
    hop_size: int,
    max_sil_kept: int,
    time_unit: int = 20 * 1000
):
    print(f"handle==={file}")
    # Load an audio file with librosa.
   
    if mode == u"time":
        slicer_time(file=file, time_unit=20*1000)
    else:
        audio, sr = librosa.load(file, sr=None, mono=False)
        num_sections = np.ceil(len(audio) / sr)
        duration = librosa.get_duration(y=audio, sr=sr)
        print(f"num_sections={num_sections} {len(audio)} {sr} {duration}")
        slicer = Slicer(
            sr=sr,
            threshold=threshold,
            min_length=min_length,
            min_interval=min_interval,
            hop_size=hop_size,
            max_sil_kept=max_sil_kept
        )
        print("audio m1", audio, audio.shape)
        chunks = slicer.slice(audio)
        file = file.replace("\\", "/")
        name = re.split("/", file)[-1].split(".")[0]
        print(f"name={name}", chunks)
        for i, chunk in enumerate(chunks):
            if len(chunk.shape) > 1:
                chunk = chunk.T  # Swap axes if the audio is stereo.
            print(f"chunk={chunk} shape={chunk.shape}")

            # Save sliced audio files with soundfile.
            outdir = (f"clips_{name}")
            if os.path.exists(outdir) != True :
                print(f"create dir {os.path.join(outdir)}")
                os.mkdir(outdir)
            soundfile.write(f'{outdir}/{name}_{i}.wav', chunk, sr)


def isabs_path(path: str):
    if re.match(r"\d+:/?|\\?.*", path):
        return True
    return False


if __name__ == '__main__':
    main()