from scripts.handler import download
from scripts.handler import MediaEditor
import os

if __name__ == "__main__":
    cases = [("https://www.youtube.com/shorts/QAfet1z-FJo", "mp3", 0, 5),
             ("https://www.youtube.com/watch?v=XB5Lj_Qe76E", "mp4", 0, 5),             
             ("https://www.youtube.com/watch?v=iYYRH4apXDo", "gif", 0, 5),
             ("https://x.com/i/status/1816632274160341237", "mp3", 0, 10),
             ("https://x.com/i/status/1816632274160341237", "mp4", 0, 10),
             ("https://x.com/i/status/1816632274160341237", "gif", 0, 10)
]

    generated_files = []

    for url, format, start, end in cases:
        generated_files.append(download(url, format, start, end))

    print(generated_files)

    