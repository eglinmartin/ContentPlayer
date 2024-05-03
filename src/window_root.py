# Import general modules
import os
import pathlib
import random
import subprocess
import shutil
import traceback, sys
from PIL import Image

# Import local modules
import main
import gui
import playlist

# Import UI modules
import PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QListWidget, QFileDialog, QVBoxLayout, QWidget, QPushButton, QScrollArea,\
    QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QPalette, QColor, QFont

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook


class RootWindow(QMainWindow):
    def __init__(self, input_media, root_dir, vlc_path, handler, tags_json, window_size):
        super().__init__()
        self.main = main
        self.handler = handler
        self.input_media = input_media
        self.root_dir = root_dir
        self.root_dir_plib = root_dir.replace('\\', '/')
        self.vlc_path = vlc_path
        self.window_size = window_size.split(',')

        self.font = 'Bahnschrift Semibold'
        self.font_light = 'Bahnschrift Light'
        self.setWindowTitle('Media Viewer')

        self.window_dimensions = {'width': int(self.window_size[0]), 'height': int(self.window_size[1])}

        self.setFixedWidth(self.window_dimensions['width'])
        self.setFixedHeight(self.window_dimensions['height'])
        self.scale = (self.window_dimensions['width'] / 1920)

        if self.window_dimensions['width'] == 1920:
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.base_media = input_media
        # self.base_media = [med for med in input_media if os.path.exists(fr"{self.root_dir}\_Thumbnails_Small\{med.code}.png")]
        # self.base_media.sort(key=lambda media: random.random())
        self.base_media.sort(key=lambda media: (media.studio, media.title))
        self.media = self.base_media
        self.media_category = 'All Media'

        self.selected_media = None
        self.create_ui_elements()
        self.create_buttons()
        self.create_searchbar()

        self.listbox_elements = []
        self.draw_playlist()

        self.draw_adder()
        self.show_playlist()

        self.shuffle_media()

    def set_media_category(self):
        media_categories = ['All Media', 'Video', 'Imageset']

        for i in range(len(media_categories)):
            if i == len(media_categories)-1:
                self.media_category = media_categories[0]
                break
            elif self.media_category == media_categories[i]:
                self.media_category = media_categories[i+1]
                break

        if self.media_category == 'All Media':
            self.media = self.base_media
        else:
            self.media = [med for med in self.base_media if med.media_type == self.media_category]

        self.create_searchbar()

        self.gui_listbox.clear()
        for i, med in enumerate(self.media):
            listbox_entry = f"| {med.title} ({med.studio})                                         #{med.code}"
            self.gui_listbox.insertItem(i, listbox_entry)

        self.shuffle_media()

    def create_searchbar(self):
        self.searchbar = gui.GuiTextEntry(self)
        self.searchbar.draw('none', '#cccccc', '#1B1C1E', self.font, int(32 * self.scale),
                            width=int(640 * self.scale), height=int(100 * self.scale),
                            x=int(1150*self.scale), y=int(264*self.scale), default_text='Playlist')
        self.searchbar.gui_searchbar.textChanged.connect(self.filter_media)

    def filter_media(self):
        if self.searchbar.get_text():
            self.media = [med for med in self.base_media if self.searchbar.get_text() in med.tags]
        else:
            self.media = self.base_media
        self.media.sort(key=lambda media: (media.studio, media.title))

        for item in self.listbox_elements:
            self.scrollLayout.removeWidget(item)

        self.listbox_elements = [playlist.PlaylistElement(self, self.font_light, self.root_dir_plib, med, self.scale) for med in self.media]
        for item in self.listbox_elements:
            self.scrollLayout.addWidget(item)

    def create_ui_elements(self):
        self.background = gui.GuiImage(window=self, width=self.window_dimensions['width'], height=self.window_dimensions['height'], x=0, y=0)
        self.background.set_image(fr"../bin/png/root_window.png")

        self.image_preview = gui.GuiImage(window=self, width=int((1920*self.scale)/2), height=int((1080*self.scale)/2),
                                          x=int((self.window_dimensions['height']/10)/2),
                                          y=int((self.window_dimensions['height']/10)/2))

        # Draw title text
        self.text_title = gui.GuiText(window=self, width=int((1920*self.scale)/2), height=int(80*self.scale), alignment='left',
                                      x=int((self.window_dimensions['height']/10)/2), y=int(642*self.scale))
        self.text_title.set_font(font=self.font, font_size=int(32*self.scale), font_colour='#ffffff')

        # Draw studio text
        self.text_studio = gui.GuiText(window=self, width=int((1920*self.scale)/2), height=int(80*self.scale), alignment='left',
                                      x=int((self.window_dimensions['height']/10)/2), y=int(710*self.scale))
        self.text_studio.set_font(font=self.font, font_size=int(24*self.scale), font_colour='#ffffff')

        # Draw actor text
        self.text_actors = gui.GuiText(window=self, width=int((1280*self.scale)/2), height=int(80*self.scale), alignment='left',
                                       x=int((self.window_dimensions['height']/10)/2), y=int(766*self.scale))
        self.text_actors.set_font(font=self.font, font_size=int(24*self.scale), font_colour='#ffffff')

        # Draw duration text
        self.text_duration = gui.GuiText(window=self, width=int((1920*self.scale)/2), height=int(80*self.scale), alignment='right',
                                         x=int((self.window_dimensions['height']/10)/2), y=int(642*self.scale))
        self.text_duration.set_font(font=self.font, font_size=int(32*self.scale), font_colour='#ffffff')

        # Draw date text
        self.text_date = gui.GuiText(window=self, width=int((1920*self.scale)/2), height=int(80*self.scale), alignment='right',
                                      x=int((self.window_dimensions['height']/10)/2), y=int(710*self.scale))
        self.text_date.set_font(font=self.font, font_size=int(24*self.scale), font_colour='#ffffff')

        # Draw tags text
        self.text_tags = gui.GuiText(window=self, width=int((1920*self.scale)/2), height=int(80*self.scale), alignment='right',
                                      x=int((self.window_dimensions['height']/10)/2), y=int(766*self.scale))
        self.text_tags.set_font(font=self.font, font_size=int(24*self.scale), font_colour='#ffffff')

        # Draw add media heading, but hide initially
        self.text_add = gui.GuiText(window=self, width=int(640*self.scale), height=int(100*self.scale), alignment='left',
                                      x=int(1152*self.scale), y=int(288*self.scale))
        self.text_add.set_font(font=self.font, font_size=int(32*self.scale), font_colour='#cccccc')
        self.text_add.set_text('Add Media')
        self.text_add.gui_text.hide()

        # Draw settings heading, but hide initially
        self.text_settings = gui.GuiText(window=self, width=int(640*self.scale), height=int(100*self.scale), alignment='left',
                                      x=int(1152*self.scale), y=int(288*self.scale))
        self.text_settings.set_font(font=self.font, font_size=int(32*self.scale), font_colour='#cccccc')
        self.text_settings.set_text('Settings')
        self.text_settings.gui_text.hide()

    def create_buttons(self):
        self.button_shuffle = gui.GuiButton(window=self, cmd=self.shuffle_media, width=int(128*self.scale),
                                            height=int(128*self.scale), x=int(54*self.scale), y=int(898*self.scale))
        self.button_shuffle.set_image(fr"../bin/png/button_shuffle.png")

        self.button_prev = gui.GuiButton(window=self, cmd=self.prev_media, width=int(128*self.scale),
                                         height=int(128*self.scale), x=int(262*self.scale), y=int(898*self.scale))
        self.button_prev.set_image(fr"../bin/png/button_prev.png")

        self.button_play = gui.GuiButton(window=self, cmd=self.play_media, width=int(128*self.scale),
                                         height=int(128*self.scale), x=int(470*self.scale), y=int(898*self.scale))
        self.button_play.set_image(fr"../bin/png/button_play.png")

        self.button_next = gui.GuiButton(window=self, cmd=self.next_media, width=int(128*self.scale),
                                         height=int(128*self.scale), x=int(678*self.scale), y=int(898*self.scale))
        self.button_next.set_image(fr"../bin/png/button_next.png")

        self.button_playlist = gui.GuiButton(window=self, cmd=self.show_playlist, width=int(128*self.scale),
                                                      height=int(128*self.scale), x=int(1150*self.scale), y=int(54*self.scale))
        self.button_playlist.set_image(fr"../bin/png/button_playlist.png")

        self.button_add_media = gui.GuiButton(window=self, cmd=self.show_add_menu, width=int(128*self.scale),
                                                      height=int(128*self.scale), x=int(1346*self.scale), y=int(54*self.scale))
        self.button_add_media.set_image(fr"../bin/png/button_add.png")

        self.button_settings = gui.GuiButton(window=self, cmd=self.show_settings, width=int(128*self.scale),
                                                      height=int(128*self.scale), x=int(1542*self.scale), y=int(54*self.scale))
        self.button_settings.set_image(fr"../bin/png/button_settings.png")

        self.button_exit = gui.GuiButton(window=self, cmd=self.exit, width=int(128*self.scale),
                                                      height=int(128*self.scale), x=int(1738*self.scale), y=int(54*self.scale))
        self.button_exit.set_image(fr"../bin/png/button_exit.png")

    def exit(self):
        self.close()

    def show_settings(self):
        self.scroll.hide()
        self.searchbar.gui_searchbar.hide()
        self.text_add.gui_text.hide()
        self.text_settings.gui_text.show()

    def show_add_menu(self):
        self.scroll.hide()
        self.searchbar.gui_searchbar.hide()
        self.text_add.gui_text.show()
        self.text_settings.gui_text.hide()

        self.adder_scroll.show()

    def show_playlist(self):
        self.scroll.show()
        self.searchbar.gui_searchbar.show()
        self.text_add.gui_text.hide()
        self.text_settings.gui_text.hide()

        self.adder_scroll.hide()

    # def create_add_menu(self):

    def display_selected_media(self):
        for med in self.media:
            if med.code == self.selected_media:
                self.text_title.set_text(med.title)
                self.text_studio.set_text(str(med.studio))
                self.text_actors.set_text(f"👩 {', '.join(med.actors)}")
                self.text_duration.set_text(str(med.duration).replace('-', '/'))
                self.text_date.set_text(str(med.date).replace('-', '/'))
                self.text_tags.set_text(f"🏷 {len(str(med.tags).split('#'))-3}")
                self.image_preview.set_image(fr"{self.root_dir_plib}/_Thumbnails_Med/{self.selected_media}.png")

    def shuffle_media(self):
        prev_choice = self.selected_media
        self.selected_media = random.choice([med.code for med in self.media])
        if len(self.media) > 1:
            if self.selected_media == prev_choice:
                self.shuffle_media()
        self.display_selected_media()

    def prev_media(self):
        for i, med in enumerate(self.media):
            if med.code == self.selected_media:
                if i > 0:
                    self.selected_media = self.media[i-1].code
                    self.display_selected_media()
                    break

    def next_media(self):
        for i, med in enumerate(self.media):
            if med.code == self.selected_media:
                if i < len(self.media)-1:
                    self.selected_media = self.media[i+1].code
                    self.display_selected_media()
                    break

    def play_media(self):
        for i, med in enumerate(self.media):
            if med.code == self.selected_media:
                # med.views +=1
                # fav_sql_query = f'UPDATE media SET views={med.views} where id={self.selected_media}'
                # self.handler.sql_query(fav_sql_query)
                self.display_selected_media()

        media_path = str(os.path.join(self.root_dir.replace('/', '\\'), 'Videos', f"{self.selected_media}.mp4"))
        subprocess.Popen([self.vlc_path, media_path])

    def draw_playlist(self):
        # Draw the album listbox
        self.playlist = playlist.Playlist(self)
        self.setLayout(self.playlist)

        self.scroll = QScrollArea(self)
        self.scroll.resize(int(746*self.scale), int(656*self.scale))
        self.scroll.move(int(1120*self.scale), int(370*self.scale))
        self.scroll.setStyleSheet('background-color: #1B1C1E; border: none;')
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # scroll.verticalScrollBar().hide()
        self.playlist.addWidget(self.scroll)

        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scrollContent.setLayout(self.scrollLayout)

        self.listbox_elements = [playlist.PlaylistElement(self, self.font_light, self.root_dir_plib, med, self.scale) for med in self.media]
        for item in self.listbox_elements:
            self.scrollLayout.addWidget(item)
        self.scroll.setWidget(self.scrollContent)
        self.scroll.setWidgetResizable(True)

    def draw_adder(self):
        self.adder_window = QVBoxLayout(self)
        self.setLayout(self.adder_window)

        self.adder_scroll = QScrollArea(self)
        self.adder_scroll.resize(int(708*self.scale), int(646*self.scale))
        self.adder_scroll.move(int(1142*self.scale), int(380*self.scale))
        self.adder_scroll.setStyleSheet('background-color: #1B1C1E; border: none;')
        self.adder_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.adder_window.addWidget(self.adder_scroll)

        self.adder_scrollContent = QWidget(self.adder_scroll)
        self.adder_scrollLayout = QVBoxLayout(self.adder_scrollContent)
        self.adder_scrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.adder_scrollContent.setLayout(self.adder_scrollLayout)

        self.video_selector = QLabel(self)
        self.video_selector.setFixedSize(int(288), int(162))
        self.video_selector.setStyleSheet('background-color: #2B2D30; border: none;')
        self.adder_scrollLayout.addWidget(self.video_selector)

        self.title_entry = QLineEdit(self)
        self.title_entry.setFixedSize(int(670), int(72))
        self.title_entry.setStyleSheet('background-color: #2B2D30; border: none; color: #ffffff')
        self.title_entry.setContentsMargins(0, 20, 0, 0)
        self.title_entry.setFont(QFont(self.font, int(24 * self.scale)))
        self.adder_scrollLayout.addWidget(self.title_entry)

        self.studio_entry = QLineEdit(self)
        self.studio_entry.setFixedSize(int(670), int(72))
        self.studio_entry.setStyleSheet('background-color: #2B2D30; border: none; color: #ffffff')
        self.studio_entry.setContentsMargins(0, 20, 0, 0)
        self.studio_entry.setFont(QFont(self.font, int(24 * self.scale)))
        self.adder_scrollLayout.addWidget(self.studio_entry)

        self.actors_entry = QLineEdit(self)
        self.actors_entry.setFixedSize(int(670), int(72))
        self.actors_entry.setStyleSheet('background-color: #2B2D30; border: none; color: #ffffff')
        self.actors_entry.setContentsMargins(0, 20, 0, 0)
        self.actors_entry.setFont(QFont(self.font, int(24 * self.scale)))
        self.adder_scrollLayout.addWidget(self.actors_entry)

        self.adder_scroll.setWidget(self.adder_scrollContent)

    def select_media(self, code):
        self.selected_media = code
        self.display_selected_media()

    def edit_thumbnail(self):
        thumbnail_path, _ = QFileDialog.getOpenFileName(self, 'Search for thumbnail', os.path.join(self.root_dir, 'Screenshots'), "Image Files (*.png)")

        if thumbnail_path:
            for med in self.media:
                if med.code == self.selected_media:

                    fullres_thumbnail_path = os.path.join(self.root_dir, '_Thumbnails', f'{med.code}.png')
                    midres_thumbnail_path = os.path.join(self.root_dir, '_Thumbnails_Med', f'{med.code}.png')
                    smallres_thumbnail_path = os.path.join(self.root_dir, '_Thumbnails_Small', f'{med.code}.png')
                    shutil.copy(thumbnail_path, fullres_thumbnail_path)

                    # Resize to mid-scale
                    im = Image.open(fullres_thumbnail_path)
                    imResize = im.resize((960, 540), Image.LANCZOS)
                    imResize.save(os.path.join(midres_thumbnail_path), 'PNG', quality=90)

                    # Resize to small-scale
                    imResize = im.resize((192, 108), Image.LANCZOS)
                    imResize.save(os.path.join(smallres_thumbnail_path), 'PNG', quality=90)

                    self.display_selected_media()
