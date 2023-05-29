import configparser
import random

from moviepy.editor import *
import time
from os import listdir
from os.path import isfile, join

import reddit
import screenshot


def create_video():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    video = reddit.get_content(outputDir)

    fileName = video.get_file_name()

    screenshot.get_post_screenshots(video)

    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)
    bgIndex = random.randint(0, bgCount - 1)
    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4",
        audio=False).subclip(0, video.get_duration())
    w, h = backgroundVideo.size

    def __create_clip(screenShotFile, audioClip, marginSize):
        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
        ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w - marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    clips.append(__create_clip(video.titleSCFile, video.titleAudioClip, marginSize))
    for comment in video.frames:
        clips.append(__create_clip(comment.screenShotFile, comment.audioClip, marginSize))

    # Merge clips into single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay],
        size=backgroundVideo.size).set_audio(contentOverlay.audio)
    final.duration = video.get_duration()
    final.set_fps(backgroundVideo.fps)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4"
    final.write_videofile(
        outputFile,
        threads=threads,
        bitrate=bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

if __name__ == "__main__":
    create_video()
