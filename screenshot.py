import time

from PIL import Image

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.webdriver import FirefoxProfile

import tools

# Config
screenWidth = 400
screenHeight = 800


def get_post_screenshots(video):
    print("Taking screenshots...")
    driver, wait = __setup_driver(video.url)
    video.titleSCFile = __take_screenshot(video.postId, driver, wait)
    for commentFrame in video.frames:
        commentFrame.screenShotFile = __take_screenshot(video.postId, driver, wait, f"t1_{commentFrame.commentId}")
    driver.quit()


def __take_screenshot(postDir, driver, wait, handle="Post"):
    method = By.CLASS_NAME if (handle == "Post") else By.ID
    element = wait.until(EC.presence_of_element_located((method, handle)))
    tools.scroll_to_element(driver, element)

    driver.execute_script("window.focus();")
    time.sleep(1)

    fileName = f"posts/{postDir}/screenshots/{handle}.png"
    fp = open(fileName, "wb")
    fp.write(element.screenshot_as_png)
    fp.close()
    __prettify_screenshot(fileName)
    return fileName


def __prettify_screenshot(fileName):
    image = Image.open(fileName)
    w, h = image.size
    croppedImage = image.crop((0, 2, w, h-4))
    tools.add_corners(croppedImage, 15)
    tools.add_transparency(croppedImage, 238)
    croppedImage.save(fileName)


def __setup_driver(url: str):
    options = webdriver.FirefoxOptions()
    options.headless = False
    options.enable_mobile = False
    profile = FirefoxProfile('/home/lazbo/.mozilla/firefox/drhqqgwg.selenium')
    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    wait = WebDriverWait(driver, 20)

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)

    return driver, wait
