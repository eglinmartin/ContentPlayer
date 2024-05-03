from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon, QCursor
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QLabel, QListWidget, QLineEdit, QComboBox, QCheckBox


class GuiImage:
    def __init__(self, window, width, height, x, y):
        self.gui_image = QLabel(window)
        self.gui_image.resize(width, height)
        self.gui_image.move(int(x), int(y))

    def set_image(self, image):
        self.gui_image.setStyleSheet(f"border-image : url({image});" f"border : none")

    def set_size(self, width, height):
        self.gui_image.resize(int(width), int(height))

    def set_xy(self, x, y):
        self.gui_image.move(int(x), int(y))


class GuiButton:
    def __init__(self, window, cmd, width, height, x, y):
        self.gui_toggle = QPushButton(window)
        self.gui_toggle.resize(int(width), int(height))
        self.gui_toggle.setCheckable(True)
        self.gui_toggle.clicked.connect(cmd)
        self.gui_toggle.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.gui_toggle.move(int(x), int(y))

    def set_image(self, image):
        self.gui_toggle.setStyleSheet(f"border-image : url({image}); border : none; background-color: rgba(255, 255, 255, 0);")


class GuiText:
    def __init__(self, window, width, height, x, y, alignment):
        self.gui_text = QLabel(window)
        self.gui_text.resize(width, height)
        self.gui_text.setWordWrap(True)
        self.gui_text.move(x, y)

        if alignment == 'left':
            self.gui_text.setAlignment(QtCore.Qt.AlignLeft)
        if alignment == 'centre':
            self.gui_text.setAlignment(QtCore.Qt.AlignCenter)
        if alignment == 'right':
            self.gui_text.setAlignment(QtCore.Qt.AlignRight)

    def set_text(self, text):
        self.gui_text.setText(text)

    def set_font(self, font, font_size, font_colour):
        self.gui_text.setFont(QFont(font, font_size))
        self.gui_text.setStyleSheet(f"background-color: rgba(255, 255, 255, 0); color: {font_colour}")


class GuiTextEntry:
    def __init__(self, window):
        self.gui_searchbar = QLineEdit(window)
        self.window = window
        self.selection = ''

    def draw(self, border, fgcolour, bgcolour, font, font_size, width, height, x, y, default_text):
        self.gui_searchbar.setStyleSheet(f"border: {border};"
                                         f"background-color: {bgcolour};"
                                         f"color: {fgcolour}")
        self.gui_searchbar.setFont(QFont(font, font_size))
        self.gui_searchbar.setAlignment(QtCore.Qt.AlignLeft)
        self.gui_searchbar.resize(width, height)
        self.gui_searchbar.move(x, y)
        self.gui_searchbar.setPlaceholderText(default_text)

    def get_text(self):
        return self.gui_searchbar.text()


class GuiComboBox:
    def __init__(self, window, input_list, name, output_cmd):
        self.gui_combobox = QComboBox(window)
        self.window = window
        self.input_list = input_list.copy()
        self.name = name
        self.output_cmd = output_cmd

    def draw(self, border, bgcolour, fgcolour, font, font_size, width, height, x, y, default, adder):
        self.default = default

        self.gui_combobox.setStyleSheet(f"border: {border};"
                                        f"background-color: {bgcolour};"
                                        f"color: {fgcolour}")
        self.gui_combobox.setFont(QFont(font, font_size))
        self.gui_combobox.resize(width, height)
        self.gui_combobox.move(x, y)

        if adder:
            self.input_list.insert(0, adder)
        if default:
            self.input_list.insert(0, default)
        self.gui_combobox.addItems(self.input_list)

        if str(self.gui_combobox.currentText()) == str(self.default):
            self.selection = 'No Filter'
        else:
            self.selection = str(self.gui_combobox.currentText())

        self.gui_combobox.activated[str].connect(self.on_changed)
        self.gui_combobox.wheelEvent = lambda event: None

    def on_changed(self):
        if str(self.gui_combobox.currentText()) == str(self.default):
            self.selection = 'No Filter'
        else:
            self.selection = str(self.gui_combobox.currentText())

        self.output_cmd(self.selection)

