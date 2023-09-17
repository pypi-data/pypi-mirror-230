from pydub import AudioSegment
from pydub.utils import make_chunks
import re
import os

# 按时间切换, 默认20s
def slicer_time(file:str, time_unit:int=20000):
    file = file.replace("\\", "/")
    audio = AudioSegment.from_file(file)
    chunks = make_chunks(audio, time_unit)  #将文件切割为10s一块
    names = re.split("/", file)[-1].split(".")
    name = names[0]
    ext = names[1]
    print(f"name={name}", chunks)
    outdir = (f"clips_{name}")
    if os.path.exists(outdir) != True :
        print(f"create dir {os.path.join(outdir)}")
        os.mkdir(outdir)
    for i, chunk in enumerate(chunks):
        chunk_name = f"{outdir}/{name}-{i}.wav"
        print(chunk_name)
        chunk.export(chunk_name, format="wav")
    