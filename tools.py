import configparser
import json

from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
from markdown import markdown
import re

from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains

config = configparser.ConfigParser()
config.read('config.ini')
badWordDictionaryLocation = config["General"]["BadWordDictionaryLocation"]


def markdown_to_text(markdown_string) -> str:
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    html = re.sub(r'~~(.*?)~~', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return text


def text_sanitizer(text) -> str:
    # Cleans text of any links
    cleanString = re.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        " ", text)

    badWordDictionary = json.load(open(badWordDictionaryLocation, 'r'))

    for badWord in badWordDictionary.keys():
        cleanString = cleanString.replace(badWord, badWordDictionary[badWord])

    return cleanString


def scroll_to_element(driver, element_locator):
    actions = ActionChains(driver)
    try:
        actions.move_to_element(element_locator).perform()
    except MoveTargetOutOfBoundsException as e:
        print(e)
        driver.execute_script("arguments[0].scrollIntoView(true);", element_locator)


def add_corners(image, rad) -> Image:
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    image.putalpha(alpha)
    return image


def add_transparency(image, a) -> Image:
    A = image.getchannel('A')
    image.putalpha(A.point(lambda i: a if i > 0 else 0))
    return image
