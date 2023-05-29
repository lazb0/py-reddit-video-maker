import os
import re

import praw
import configparser

import tools
from video import Video

config = configparser.ConfigParser()
config.read('config.ini')
CLIENT_ID = config["Reddit"]["CLIENT_ID"]
CLIENT_SECRET = config["Reddit"]["CLIENT_SECRET"]
USER_AGENT = config["Reddit"]["USER_AGENT"]
SUBREDDIT = config["Reddit"]["SUBREDDIT"]


def get_content(outputDir) -> Video:
    reddit = __get_reddit()
    usedPostIds = __get_used_post_ids(outputDir)

    post = {}
    for submission in reddit.subreddit(SUBREDDIT).top(time_filter="week", limit=20):
        if submission.id in usedPostIds:
            continue
        post = submission
        break

    if not post.id:
        print("Cannot find any good post :(")
        exit(1)

    return __get_content_from_post(post)


def __get_content_from_post(post) -> Video:
    content = Video(post.url, post.title, post.id)
    print(f"Creating video for post: {post.title}")
    print(f"Url: {post.url}")

    failed = 0
    for comment in post.comments:
        if comment.collapsed_reason_code == 'DELETED':
            continue
        if content.add_comment_scene(tools.markdown_to_text(comment.body), comment.id):
            failed += 1
        if content.can_quick_finish() or (failed > 2 and content.can_be_finished()):
            break

    return content


def __get_reddit():
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )


def __get_used_post_ids(outputDir):
    files = os.listdir(outputDir)
    # I'm sure anyone knowledgeable on python hates this. I had some weird
    # issues and frankly didn't care to troubleshoot. It works though...
    files = [f for f in files if os.path.isfile(outputDir + '/' + f)]
    return [re.sub('.mp4', '', re.sub(r'.*?-', '', file)) for file in files]



