"""
Helper functions called by app.py.
Deals with getting information and making changes outside the GUI.
"""

import ctypes
import datetime
import json
import os
import random
import sys
import winreg

from astral import LocationInfo, sun
import geocoder

appname = "CircadianDesktops"


def get_times():
    """Get sunrise/sunset times for default values in app"""
    try:
        mylocation = geocoder.ip("me")
        mylatlng = mylocation.latlng
        mytimezone = mylocation.json["raw"]["timezone"]
        loc = LocationInfo(latitude=mylatlng[0], longitude=mylatlng[1])
        s = sun.sun(loc.observer, datetime.datetime.now(), tzinfo=mytimezone)

        # adjustment to widen dawn/dusk window (quite short by default)
        adjustment = datetime.timedelta(minutes=20)
        times = {
            "dawn": (s["dawn"] - adjustment).time(),
            "sunrise": (s["sunrise"] + adjustment).time(),
            "sunset": (s["sunset"] - adjustment).time(),
            "dusk": (s["dusk"] + adjustment).time(),
        }

    except:
        """For when no connection"""
        times = {
            "dawn": datetime.time(hour=5),
            "sunrise": datetime.time(hour=7),
            "sunset": datetime.time(hour=17),
            "dusk": datetime.time(hour=19),
        }

    return times


def get_settings(filePath: str):
    """Read settings file or create one when none exits"""

    try:
        with open(filePath, "r") as f:
            s = json.loads(f.read())

    except:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop") as key:
            imgPath = winreg.QueryValueEx(key, "WallPaper")[0]
        s = {
            "labelDayImg": imgPath,
            "labelDDImg": imgPath,
            "labelNightImg": imgPath,
            "isDarkMode": 0,
            "runOnStartup": 0,
            "isCustomTimes": 0,
            "minimizeToTray": 1,
            "isSlideshow": 0,
            "shuffleTime": 30,
        }

    return s


def write_settings(filePath: str, settings: dict):
    with open(filePath, "w") as f:
        json.dump(settings, f, indent=2)


def random_image(fullPath: str):
    folderPath = os.path.dirname(fullPath)  # Allows input to be file or folder
    image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]
    images = [
        f
        for f in os.listdir(folderPath)
        if any(f.endswith(s) for s in image_extensions)
    ]
    if images:
        return os.path.join(folderPath, random.choice(images))
    else:
        return ""


def set_desktop(imagePath: str):
    # SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(20, 0, imagePath, 0)


def run_on_startup(isRunOnStartup: bool):
    """Write to or delete from registry"""
    sub_key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
    if isRunOnStartup:
        if hasattr(sys, "frozen"):
            regString = f'"{os.path.abspath(os.path.basename(sys.executable))}" /noshow'
        else:
            regString = f'"{sys.executable}" "-m" "circadian_desktops" /noshow'
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, sub_key, 0, winreg.KEY_WRITE
        ) as key:
            winreg.SetValueEx(key, appname, 0, winreg.REG_SZ, regString)
    else:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, sub_key, 0, winreg.KEY_WRITE
        ) as key:
            winreg.DeleteValue(key, appname)


def set_process_explicit():
    # Tell Windows to treat app as it's own process so custom icons are used.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appname)


def set_background_priority(isBackground: bool):
    """Start or stop process as background prioity to ensure app does not interfer with performance"""
    processID = os.getpid()
    processHandle = ctypes.windll.kernel32.OpenProcess(
        ctypes.c_uint(0x0200 | 0x0400), ctypes.c_bool(False), ctypes.c_uint(processID)
    )
    if isBackground:
        # PROCESS_MODE_BACKGROUND_BEGIN = 0x00100000
        processMode = 0x00100000
    else:
        # PROCESS_MODE_BACKGROUND_END = 0x00200000
        processMode = 0x00200000
    ctypes.windll.kernel32.SetPriorityClass(processHandle, ctypes.c_uint(processMode))
    ctypes.windll.kernel32.CloseHandle(processHandle)
