import os

# Import UI modules
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton ,QHBoxLayout
from PyQt5.QtGui import QFont


class Playlist(QVBoxLayout):
    def __init__(self, window):
        super().__init__()


class PlaylistThumbnail(QPushButton):
    def __init__(self, main_window, root_dir_plib, med, scale):
        super().__init__()
        self.setFixedSize(int(192 * scale), int(108 * scale))
        if os.path.exists(os.path.join(root_dir_plib, "_Thumbnails_Small", f"{med.code}.png")):
            self.setStyleSheet(fr"border-image : url({root_dir_plib}/_Thumbnails_Small/{med.code}.png);" f"border : none")
        else:
            self.setStyleSheet(f"border-image : url(../bin/png/empty_thumbnail.png);")
        self.clicked.connect(lambda: main_window.select_media(med.code))


class PlaylistText(QPushButton):
    def __init__(self, main_window, font_light, med, scale):
        super().__init__()
        self.setFixedSize(int(460*scale), int(92*scale))
        self.setText(f'{med.title.upper()} \n- {med.studio}')
        self.setStyleSheet("text-align:left; color: #cccccc;")
        self.setFont(QFont(font_light, int(20*scale)))
        self.clicked.connect(lambda: main_window.select_media(med.code))


class PlaylistElement(QWidget):
    def __init__(self, main_window, font_light, root_dir_plib, med, scale):
        super().__init__()

        self.setAutoFillBackground(True)
        self.setFixedSize(int(716*scale), int(128*scale))
        scrollLayout = QHBoxLayout()

        self.setLayout(scrollLayout)

        thumbnail = PlaylistThumbnail(main_window, root_dir_plib, med, scale)
        text = PlaylistText(main_window, font_light, med, scale)

        scrollLayout.addWidget(thumbnail)
        scrollLayout.addWidget(text)
