import os
import shutil

from moviepy.editor import AudioFileClip
from datetime import datetime

import tools
import voiceover

MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
MIN_DURATION = 20
MAX_DURATION = 58


class Video():
    title = ""
    postId = ""
    titleSCFile = ""
    url = ""
    totalDuration = 0
    frames = []

    def __init__(self, url, title, postId) -> None:
        self.postId = postId
        self.url = url
        self.title = title

        self.__prepare_post_directory()

        self.titleAudioClip = self.__create_voice_over("title", title)

    def can_be_finished(self) -> bool:
        return (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (self.totalDuration > MIN_DURATION)

    def can_quick_finish(self):
        return (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (self.totalDuration > MIN_DURATION)

    def add_comment_scene(self, text, commentId) -> bool:
        wordCount = len(text.split())
        if wordCount > MAX_WORDS_PER_COMMENT:
            return True
        frame = ScreenshotScene(text, commentId)
        frame.audioClip = self.__create_voice_over(commentId, text)
        if frame.audioClip is None:
            return True
        self.frames.append(frame)

    def get_duration(self):
        return self.totalDuration

    def get_file_name(self):
        return f"{datetime.today().strftime('%Y-%m-%d')}-{self.postId}"

    def __create_voice_over(self, name, dirtyText):
        text = tools.text_sanitizer(dirtyText)
        file_path = voiceover.create(f"{self.postId}-{name}",f"posts/{self.postId}", text)
        audioClip = AudioFileClip(file_path)
        if self.totalDuration + audioClip.duration > MAX_DURATION:
            return None
        self.totalDuration += audioClip.duration
        return audioClip

    def __prepare_post_directory(self):
        try:
            os.mkdir(f"posts/{self.postId}")
        except FileExistsError:
            print("Post directory already exists. Clearing it and starting fresh!")
            shutil.rmtree(f"posts/{self.postId}")
            os.mkdir(f"posts/{self.postId}")

        os.mkdir(f"posts/{self.postId}/voiceovers")
        os.mkdir(f"posts/{self.postId}/screenshots")


class ScreenshotScene:
    text = ""
    screenShotFile = ""
    commentId = ""

    def __init__(self, text, commentId) -> None:
        self.text = text
        self.commentId = commentId