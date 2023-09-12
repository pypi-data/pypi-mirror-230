"""
Main script for Circadian Desktops app.
Settings file and logo images are stored locally.
Contains MainWindow class and script to run app.
"""

import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from . import custom_qt
from . import functions
from .ui_mainwindow import Ui_MainWindow

settingsFile = "settings.json"
logoFile = "Icons\\logo.png"


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    MainWindow class for the UI.
    Inherits from Ui_MainWindow, which contains the layout of the widgets.
    """

    def __init__(self, parent=None, settings=None):
        # setup
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.settingsPath = settings
        self.isClosedFromTray = False
        self.settings = functions.get_settings(settings)
        self.activeImage = ""

        # connect widgets to methods
        self.btnSelectDayImg.clicked.connect(lambda: self.get_image(self.labelDayImg))
        self.btnSelectDDImg.clicked.connect(lambda: self.get_image(self.labelDDImg))
        self.btnSelectNightImg.clicked.connect(
            lambda: self.get_image(self.labelNightImg)
        )
        self.comboBox.currentIndexChanged.connect(self.set_background_style)
        self.spinShuffleTime.valueChanged.connect(self.set_shuffle_time)

        self.timeDawn.timeChanged.connect(self.set_desktop)
        self.timeDay.timeChanged.connect(self.set_desktop)
        self.timeDusk.timeChanged.connect(self.set_desktop)
        self.timeNight.timeChanged.connect(self.set_desktop)

        self.radioDefaultTimes.clicked.connect(self.default_times)
        self.radioCustomTimes.clicked.connect(self.custom_times)

        self.boxDark.stateChanged.connect(self.set_palette)
        self.boxMinimize.stateChanged.connect(self.minimize_behaviour)
        self.boxStartup.stateChanged.connect(self.startup_behaviour)

        # tray icon
        self.trayIcon = QtWidgets.QSystemTrayIcon()
        self.trayIcon.setIcon(QtGui.QIcon(logoFile))
        self.trayIcon.setToolTip("Circadian Desktops")
        self.trayIcon.activated.connect(self.__icon_activated)
        self.trayIcon.show()

        self.trayMenu = QtWidgets.QMenu()
        self.trayMenu.addAction("Open Circadian Desktops", self.show_window)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction("Exit Circadian Desktops", self.close_from_tray)

        self.trayIcon.setContextMenu(self.trayMenu)

        # timers
        self.mainTimer = QtCore.QTimer()
        self.mainTimer.timeout.connect(self.set_desktop)
        self.shuffleTimer = QtCore.QTimer()
        self.shuffleTimer.timeout.connect(self.shuffle_images)

        # populate data
        self.set_image(self.settings["labelDayImg"], self.labelDayImg)
        self.set_image(self.settings["labelDDImg"], self.labelDDImg)
        self.set_image(self.settings["labelNightImg"], self.labelNightImg)
        self.load_times()
        self.load_preferences()
        self.set_desktop()
        self.set_background_style()

    def set_image(self, fileName: str, imageLbl: QtWidgets.QLabel):
        if self.settings["isSlideshow"]:
            fileName = functions.random_image(fileName)
        pixmap = QtGui.QPixmap(fileName)
        pixmap = pixmap.scaled(
            imageLbl.width(), imageLbl.height(), QtCore.Qt.KeepAspectRatio
        )
        imageLbl.setPixmap(pixmap)
        imageLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.settings[imageLbl.objectName()] = fileName

    def get_image(self, imageLbl: QtWidgets.QLabel):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select image", "", "Image files (*.png *.jpg *.jpeg *.bmp)"
        )
        if fileName:
            self.set_image(fileName, imageLbl)
            self.set_desktop()

    def shuffle_images(self):
        self.set_image(self.settings["labelDayImg"], self.labelDayImg)
        self.set_image(self.settings["labelDDImg"], self.labelDDImg)
        self.set_image(self.settings["labelNightImg"], self.labelNightImg)
        self.shuffleTimer.start(self.settings["shuffleTime"] * 60000)
        self.set_desktop()

    def set_desktop(self):
        now = QtCore.QTime.currentTime()
        nextChange: QtCore.QTime
        if self.timeDawn.time() < now <= self.timeDay.time():
            imageFile = self.settings["labelDDImg"]
            nextChange = self.timeDay.time()
        elif self.timeDay.time() < now <= self.timeDusk.time():
            imageFile = self.settings["labelDayImg"]
            nextChange = self.timeDusk.time()
        elif self.timeDusk.time() < now <= self.timeNight.time():
            imageFile = self.settings["labelDDImg"]
            nextChange = self.timeNight.time()
        else:
            imageFile = self.settings["labelNightImg"]
            nextChange = self.timeDawn.time()
        if imageFile != self.activeImage:
            functions.set_desktop(imageFile)
            self.activeImage = imageFile
        timeToChange = nextChange.msec() - now.msec() + 10
        if timeToChange <= 0:
            timeToChange += 2_073_600  # ms in a day
        self.mainTimer.start(timeToChange)

    def set_background_style(self):
        if self.comboBox.currentText() == "single image":
            self.shuffleTimer.stop()
            self.settings["isSlideshow"] = 0
            self.spinShuffleTime.setReadOnly(True)
        elif self.comboBox.currentText() == "slideshow from folders":
            self.shuffleTimer.start(self.settings["shuffleTime"] * 60000)
            self.settings["isSlideshow"] = 1
            self.spinShuffleTime.setReadOnly(False)

    def set_shuffle_time(self):
        newTime = self.spinShuffleTime.value() * 60000
        if self.shuffleTimer.remainingTime() > newTime:
            self.shuffleTimer.start(newTime)
        self.settings["shuffleTime"] = self.spinShuffleTime.value()

    def load_times(self):
        if int(self.settings["isCustomTimes"]):
            self.timeDawn.setTime(
                QtCore.QTime(
                    int(self.settings["dawnhour"]), int(self.settings["dawnmin"]), 0
                )
            )
            self.timeDay.setTime(
                QtCore.QTime(
                    int(self.settings["dayhour"]), int(self.settings["daymin"]), 0
                )
            )
            self.timeDusk.setTime(
                QtCore.QTime(
                    int(self.settings["duskhour"]), int(self.settings["duskmin"]), 0
                )
            )
            self.timeNight.setTime(
                QtCore.QTime(
                    int(self.settings["nighthour"]), int(self.settings["nightmin"]), 0
                )
            )
            self.custom_times()
            self.radioCustomTimes.setChecked(True)
        else:
            self.default_times()

    def custom_times(self):
        self.timeDawn.setReadOnly(False)
        self.timeDay.setReadOnly(False)
        self.timeDusk.setReadOnly(False)
        self.timeNight.setReadOnly(False)

    def default_times(self):
        d = functions.get_times()
        self.timeDawn.setTime(QtCore.QTime(d["dawn"].hour, d["dawn"].minute, 0))
        self.timeDay.setTime(QtCore.QTime(d["sunrise"].hour, d["sunrise"].minute, 0))
        self.timeDusk.setTime(QtCore.QTime(d["sunset"].hour, d["sunset"].minute, 0))
        self.timeNight.setTime(QtCore.QTime(d["dusk"].hour, d["dusk"].minute, 0))
        self.timeDawn.setReadOnly(True)
        self.timeDay.setReadOnly(True)
        self.timeDusk.setReadOnly(True)
        self.timeNight.setReadOnly(True)

    def load_preferences(self):
        if self.settings["isSlideshow"]:
            self.comboBox.setCurrentIndex(1)
        else:
            self.spinShuffleTime.setReadOnly(True)
        self.spinShuffleTime.setValue(self.settings["shuffleTime"])
        if self.settings["isDarkMode"]:
            self.boxDark.setChecked(True)
            self.set_palette()
        if self.settings["minimizeToTray"]:
            self.boxMinimize.setChecked(True)
        else:
            self.isClosedFromTray = True
        if self.settings["runOnStartup"]:
            self.boxStartup.setChecked(True)

    def set_palette(self):
        if self.boxDark.isChecked():
            self.setPalette(custom_qt.DarkPalette())
            self.settings["isDarkMode"] = 1
        else:
            self.setPalette(QtGui.QPalette())
            self.settings["isDarkMode"] = 0

    def startup_behaviour(self):
        if self.boxStartup.isChecked():
            functions.run_on_startup(True)
            self.settings["runOnStartup"] = 1
        else:
            functions.run_on_startup(False)
            self.settings["runOnStartup"] = 0

    def minimize_behaviour(self):
        if self.boxMinimize.isChecked():
            self.isClosedFromTray = False
            self.settings["minimizeToTray"] = 1
        else:
            self.isClosedFromTray = True
            self.settings["minimizeToTray"] = 0

    def show_window(self):
        functions.set_background_priority(False)
        getattr(self, "raise")()
        self.activateWindow()
        self.setWindowState(QtCore.Qt.WindowNoState)
        self.show()

    def close_from_tray(self):
        self.isClosedFromTray = True
        self.close()

    def closeEvent(self, event):
        if self.radioCustomTimes.isChecked():
            self.settings["isCustomTimes"] = 1
            self.settings["dawnhour"] = self.timeDawn.time().hour()
            self.settings["dawnmin"] = self.timeDawn.time().minute()
            self.settings["dayhour"] = self.timeDay.time().hour()
            self.settings["daymin"] = self.timeDay.time().minute()
            self.settings["duskhour"] = self.timeDusk.time().hour()
            self.settings["duskmin"] = self.timeDusk.time().minute()
            self.settings["nighthour"] = self.timeNight.time().hour()
            self.settings["nightmin"] = self.timeNight.time().minute()
        else:
            self.settings["isCustomTimes"] = 0
        functions.write_settings(self.settingsPath, self.settings)
        if self.isClosedFromTray:
            event.accept()
        else:
            event.ignore()
            self.hide()
            functions.set_background_priority(True)

    def __icon_activated(self, reason):
        if (
            reason == QtWidgets.QSystemTrayIcon.DoubleClick
            or reason == QtWidgets.QSystemTrayIcon.Trigger
        ):
            self.show_window()


def main():
    """
    Main function for launching the app
    """
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # To pick up settings & images
    functions.set_process_explicit()  # So Windows uses logo icon
    app = QtWidgets.QApplication([])
    ui = MainWindow(settings=settingsFile)
    app.setStyle("fusion")
    if "/noshow" in sys.argv:
        functions.set_background_priority(True)
    else:
        ui.show()
    app.setWindowIcon(QtGui.QIcon(logoFile))
    ui.setWindowIcon(QtGui.QIcon(logoFile))
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
