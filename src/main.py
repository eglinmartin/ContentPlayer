import configparser
import argparse
import sys
import os
from PyQt5.QtWidgets import QApplication

import handler
import window_root


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_path', help="path to configuration file")
    args = parser.parse_args()
    config_path = str(args.config_path)

    return config_path


def main():
    config_path = parse_args()
    config = configparser.ConfigParser()
    config.read(config_path)

    MEDIA_DIR = config.get('paths', 'media_directory')
    DATABASE_PATH = os.path.join(MEDIA_DIR, 'media.db')
    VLC_PATH = config.get('paths', 'vlc_exe')
    TAGS_JSON = os.path.join(MEDIA_DIR, 'tags.json')
    WINDOW_SIZE = config.get('settings', 'resolution')

    data_handler = handler.Handler(DATABASE_PATH, MEDIA_DIR)
    tags_list = data_handler.parse_tags(TAGS_JSON)
    media = data_handler.load_from_db(tags_list)

    application = QApplication(sys.argv)
    main_window = window_root.RootWindow(media, MEDIA_DIR, VLC_PATH, data_handler, tags_list, WINDOW_SIZE)
    main_window.show()
    application.exec()


if __name__ == '__main__':
    main()
