# Import general modules
import sqlite3
import json
import re
import os
import datetime


class Media:
    def __init__(self, code, title, studio, actors, media_type, tags, date, duration):
        self.code = int(code)
        self.studio = str(studio)
        self.actors = actors.split(', ')
        self.title = str(title).replace("`", "'")
        self.media_type = media_type
        self.tags = tags
        self.date = date

        mins, secs = divmod(int(duration) , 60)
        self.duration = f"{mins}:{str(secs).zfill(2)}"


class Handler:
    def __init__(self, db, root_dir):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.root_dir = root_dir

    def manage_tags(self, input_tags, tags_json, studio, people):
        input_tags_list = input_tags.split(' ')

        for tag in input_tags_list:
            new_tag = None
            if tag in tags_json['blindfolds']:
                new_tag = '#blindfolded'
            if tag in tags_json['gags']:
                new_tag = '#gagged'
            if tag in tags_json['metal']:
                new_tag = '#metalbondage'
            if tag in tags_json['rope']:
                new_tag = '#ropebondage'

            if new_tag:
                input_tags_list.append(new_tag)

        people_list = people.split(',')
        number_of_people = len(people_list)
        if number_of_people == 2:
            input_tags_list.append('#couple')
        elif number_of_people > 2:
            input_tags_list.append('#group')
        for person in people_list:
            input_tags_list.append("#{}".format(re.sub('[\W_]+', '', person.lower().replace(' ', ''))))

        studio_tag = studio.lower().replace(' ', '')
        if studio_tag not in input_tags_list:
            input_tags_list.append("#{}".format(re.sub('[\W_]+', '', studio_tag)))

        input_tags_list = list(dict.fromkeys(input_tags_list))
        if '#unknown' in input_tags_list:
            input_tags_list.remove('#unknown')

        input_tags_list.sort()
        input_tags_final = ' '.join(input_tags_list)
        if input_tags_final:
            if input_tags_final[0] == ' ':
                input_tags_final = input_tags_final[1:]

        return input_tags_final

    def compile_all_media_tags(self, media_list):
        all_tags = []

        for media in media_list:
            med_tags = [tag for tag in str(media.tags).split(' ')]
            for tag in med_tags:
                all_tags.append(tag)

        all_tags = list(dict.fromkeys(all_tags))
        all_tags.sort()
        return all_tags

    def parse_tags(self, tags_json):
        f = open(tags_json, 'r')
        tags_list = json.loads(f.read())

        for key, value in tags_list.items():
            tags_list[key] = [f"#{tag}" for tag in value]

        return tags_list

    def load_from_db(self, tags_json):
        media_list = [Media(row[0], row[1], row[2], row[3], row[4], self.manage_tags(row[5], tags_json, row[2], row[3]), row[6], row[7])
                      for row in self.cursor.execute('SELECT * FROM media')]
        media_list.sort(key=lambda media: media.title)

        return media_list

    def sql_query(self, sql_command):
        self.cursor.execute(sql_command)
        self.connection.commit()