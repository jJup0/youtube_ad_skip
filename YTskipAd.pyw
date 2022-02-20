import os
from pydub.playback import play
from pydub import AudioSegment
import timeit
import numpy as np
import cv2
import mss
import pyautogui as pauto
import time
import winsound

# PYAUTOGUI DOESNT SCREENSHOT ON SECOND MONITOR

# GLOBALS ###########################
SLEEPTIMER = 1
sourceCodePath = "C:/Users/Jakob/OneDrive/Desktop/Programming/Python/myenv38progs/WebAutomation/YT/"
CUTOFF_Y = 800
CUTOFF_X = 1720
exitSoundFile = sourceCodePath + "Soundfiles/Speech Sleep.wav"
startingSoundFile = sourceCodePath + "Soundfiles/Windows Startup.wav"
LOG_DATA = False


def getMonitor(monitorNr):
    mon = mss.mss().monitors[monitorNr]

    # The screen part to capture
    return {
        "top": mon["top"],
        "left": mon["left"],
        "width": mon["width"],
        "height": mon["height"],
        "mon": monitorNr,
    }


def screenshot_templateMatch(monitorNr):
    # ripped from https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html

    # methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    template = cv2.imread(sourceCodePath + "/ScreenShots/AdScreenShots/skipButton.png", 0)

    method = cv2.TM_CCOEFF_NORMED    # method to template match, TM_CCOEFF_NORMED seems to work the best

    screenshot = np.array(mss.mss().grab(getMonitor(monitorNr)))                                              # get screenshot
    screenshot = np.dot(screenshot[..., :4], [0.2989, 0.5870, 0.1140, 0]).astype(np.uint8)      # convert rgba to grayscale

    screenshot = screenshot[CUTOFF_Y:1080, CUTOFF_X:1920]                # crop screen shot for efficiency
    res = cv2.matchTemplate(screenshot, template, method)       # Apply template Matching

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)     # get best matching
    top_left = max_loc                                          # for cv2.TM_CCOEFF_NORMED the max_loc is location of best matching

    if (LOG_DATA):
        template_h, template_w = template.shape
        print(f"{method}: max val = {max_val} at position {top_left}")
        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
        cv2.rectangle(screenshot, top_left, bottom_right, 255, 2)
        cv2.imwrite(sourceCodePath + f"Screenshots/result_{method}.png", screenshot)

    return max_val, top_left


def changeVolume(soundFile, diff) -> str:
    song = AudioSegment.from_wav(soundFile)
    # change volume by diff dB
    louder_song = song + diff
    # save louder song
    outPath = sourceCodePath + f"Soundfiles/vol_changed_{diff:+}_" + soundFile[soundFile.rfind("/") + 1:]
    if (not os.path.exists(outPath)):
        louder_song.export(outPath, format='wav')
    else:
        print(outPath+" already exists")
    return outPath


if __name__ == '__main__':
    startingSoundFile = changeVolume(startingSoundFile, 20)
    exitSoundFile = changeVolume(exitSoundFile, -5)

    for _ in range(0):
        # t1 = timeit.timeit(screenShotSecondMonitor, number=1)
        # print(f"Screengrab time: {t1:.3f}, ", end=""
        t2 = timeit.timeit(screenshot_templateMatch, number=1)
        print(f"Template matching: {t2:.3f}")

    print('Starting Skip Ad Procedure')
    winsound.PlaySound(startingSoundFile, winsound.SND_FILENAME)  # i guess supposed to maybe use SND_ALIAS  instead

    while True:
        print("Running main")
        # rn monitor 1 is actually left monitor
        for monitorNr in (1, 2):
            matchingPercentage, coords = screenshot_templateMatch(monitorNr)
            if matchingPercentage > 0.9:
                print(f"Found skip button with {(matchingPercentage*100):.1f}% certainty")
                x, y = coords
                x += CUTOFF_X + (1920 * (monitorNr == 1))
                y += CUTOFF_Y
                print((x, y))
                prevPos = pauto.position()
                pauto.click(x, y)
                pauto.moveTo(*prevPos)

        for i in range(10):
            time.sleep(1/10)
            # exit if mouse in top left corner
            if sum(pauto.position()) < 5:
                # print(sum(pauto.position()))
                print("playing sound")
                winsound.PlaySound(exitSoundFile, winsound.SND_FILENAME)  # i guess supposed to maybe use SND_ALIAS  instead
                exit()


# def screenshotMonitor(monitorNr):
#     # ripped from https://stackoverflow.com/questions/63737476/screenshot-on-multiple-monitor-setup-pyautogui
#     with mss.mss() as sct:

#         # Grab the data
#         sct_img = sct.grab(getMonitor(monitorNr))

#         # Save to the picture file
#         mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_file_name)

# # OLD
# from PIL import Image
# scrshdirAd = sourceCodePath + "ScreenShots/AdScreenShots/"
# output_file_name = sourceCodePath + "yt_screenshot.png"
# skipAdRegion = (1805, 940, 100, 45)
# skipAdImg = Image.open(scrshdirAd + 'skipButton.png')
# pressSmallxRegion = (1165, 953, 15, 15)
# smallxImg = Image.open(scrshdirAd + 'pressXonAd.png')
# def clickToRemoveAd(adType, adImg, adRegion):
#     adButtonPos = pauto.locateCenterOnScreen(image=adImg, confidence=0.8, region=adRegion, grayscale=True)
#     if adButtonPos:
#         prevx, prevy = pauto.position()
#         pauto.moveTo(adButtonPos[0], adButtonPos[1], 0.1,  pauto.easeOutQuad)
#         pauto.click()
#         pauto.moveTo(prevx, prevy)
#         print('\nClicked ' + adType)
#     else:
#         print('No ' + adType + ', ', end='')


# def myMain():
#     try:
#         while True:
#             clickToRemoveAd('Skip', skipAdImg, skipAdRegion)
#             clickToRemoveAd('Small x', smallxImg, pressSmallxRegion)
#             print()
#             time.sleep(SLEEPTIMER)
#     except KeyboardInterrupt:  # press ctrl + c to stop
#         print('STOPPED')
