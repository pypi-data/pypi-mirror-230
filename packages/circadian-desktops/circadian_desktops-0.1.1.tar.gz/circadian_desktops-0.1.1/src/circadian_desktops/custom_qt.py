from PyQt5 import QtCore, QtGui, QtWidgets


class DarkPalette(QtGui.QPalette):
    """DarkPalette class to be used with the 'fusion' style."""

    def __init__(self):
        super().__init__()
        self.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
        self.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(25, 25, 25))
        self.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))
        self.setColor(QtGui.QPalette.Active,
                      QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.setColor(QtGui.QPalette.Disabled,
                      QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
        self.setColor(QtGui.QPalette.Disabled,
                      QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
        self.setColor(QtGui.QPalette.Disabled,
                      QtGui.QPalette.Text, QtCore.Qt.darkGray)
        self.setColor(QtGui.QPalette.Disabled,
                      QtGui.QPalette.Light, QtGui.QColor(53, 53, 53))
