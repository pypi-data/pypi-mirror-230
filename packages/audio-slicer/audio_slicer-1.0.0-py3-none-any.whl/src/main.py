import librosa  # Optional. Use any library you like to read audio files.
import soundfile  # Optional. Use any library you like to write audio files.
import re
from .slicer2 import Slicer
import argparse
import logging
import os
import glob


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
        type=str,
        default=-40
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
        help=("The minimum length for a silence part to be sliced, presented in milliseconds. Set this value smaller if your audio contains only short breaks. The smaller this value is, the more sliced audio clips this script is likely to generate. Note that this value must be smaller than min_length and larger than hop_size. Defaults to 100."),
        type=int,
        default=100
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
            threshold=args.threshold,
            min_length=args.min_length,
            min_interval=args.min_interval,
            hop_size=args.hop_size,
            max_sil_kept=args.max_sil_kept
        )
    elif os.path.isdir(input):
        dir = input
        files = glob.glob(dir+"/*.(mp3|wav|flac)")
        print(f"files={files}")
        for i, name in files:
            handle(
                file=os.path.join(dir, name),
                threshold=args.threshold,
                min_length=args.min_length,
                min_interval=args.min_interval,
                hop_size=args.hop_size,
                max_sil_kept=args.max_sil_kept
            )


def handle(
    file: str,
    threshold: int,
    min_length: int,
    min_interval: int,
    hop_size: int,
    max_sil_kept: int
):
    print(f"handle==={file}")
    # Load an audio file with librosa.
    audio, sr = librosa.load(file, sr=None, mono=False)
    slicer = Slicer(
        sr=sr,
        threshold=threshold,
        min_length=min_length,
        min_interval=min_interval,
        hop_size=hop_size,
        max_sil_kept=max_sil_kept
    )
    chunks = slicer.slice(audio)

    file = file.replace("\\", "/")
    name = re.split("/", file)[-1].split(".")[0]
    print(f"name={name}")
    for i, chunk in enumerate(chunks):
        if len(chunk.shape) > 1:
            chunk = chunk.T  # Swap axes if the audio is stereo.
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
