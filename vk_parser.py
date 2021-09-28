import requests
import datetime
from datetime import date
from timeit import default_timer as timer
import time
import math
import sys
import os
import re
from rich.console import Console
import sqlite3
import csv
import unicodedata
from unidecode import unidecode
from transliterate import translit

def strip_emoji(text):
    returnString = ""

    for character in text:
        try:
            character.encode("ascii")
            returnString += character
        except UnicodeEncodeError:
            replaced = unidecode(str(character))
            if replaced != '':
                returnString += replaced
            else:
                # try:
                #      returnString += "[" + unicodedata.name(character) + "]"
                # except ValueError:
                #      returnString += "[x]"
                returnString += ' '
    return returnString

class parser():
    def __init__(self, user_id=None, limit=None, likes=None, subscribers=None, verified=None, key_word=None, stop_word=None, start_date=None, stop_date=None):
        create_table_1 = """CREATE TABLE IF NOT EXISTS "{}" (
                            url          VARCHAR (255)  NOT NULL,
                            title        VARCHAR (255)  NOT NULL,
                            date         VARCHAR (255)  NOT NULL,
                            likes        INTEGER        NOT NULL,
                            reposts      INTEGER        NOT NULL,
                            subscribers  INTEGER        NOT NULL,
                            text         VARCHAR (4000),
                            img_or_video VARCHAR (1000),
                            [index]      INTEGER        NOT NULL
                        );"""
        create_table_2 = """CREATE TABLE IF NOT EXISTS params (
                            info VARCHAR (255),
                            status VARCHAR (255)
                        );"""
        delete_table_1 = """DROP TABLE IF EXISTS "{}";"""
        delete_table_2 = """DROP TABLE IF EXISTS params;"""

        # try:
        self.connection = sqlite3.connect('db.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.cursor.execute(delete_table_1.format(user_id))
        self.connection.commit()
        self.cursor.execute(delete_table_2)
        self.connection.commit()
        self.cursor.execute(create_table_1.format(user_id))
        self.connection.commit()
        self.cursor.execute(create_table_2)
        self.connection.commit()
        self.cursor.execute("""INSERT INTO "params" ("info", "status") VALUES ('parser_status', 'False');""")
        self.connection.commit()
        self.cursor.execute("""INSERT INTO "params" ("info", "status") VALUES ('parser_post', '...');""")
        self.connection.commit()
        self.cursor.execute("""INSERT INTO "params" ("info", "status") VALUES ('parser_all_posts', '...');""")
        self.connection.commit()
        self.cursor.execute("""INSERT INTO "params" ("info", "status") VALUES ('parser_time', '...');""")
        self.connection.commit()

        print("SQLite connected")

        # except sqlite3.Error as error:
        #     print("Error connecting to sqlite\n" + str(error))
        #     return None

        with open('access_tokens.txt', 'r') as access_tokens_file:
            self.access_tokens = access_tokens_file.read().split('\n')

        self.access_token_index = 0
        self.console = Console()
        self.start_from = 0
        self.filters = 'post'
        self.v = '5.61'
        if start_date != '' and stop_date != '':
            print(start_date + ' ' + stop_date)
            start_date = start_date.split('-')
            stop_date = stop_date.split('-')
            start_date = round(int(time.mktime(date(int(start_date[0]), int(start_date[1]), int(start_date[2])).timetuple())))
            stop_date = round(int(time.mktime(date(int(stop_date[0]), int(stop_date[1]), int(stop_date[2])).timetuple())))
        else:
            start_date = ''
            stop_date = ''
        self.FILTERS = {'likes': [likes[0], likes[1], int(likes[2])], 'subscribers': [subscribers[0], subscribers[1], int(subscribers[2])], 'verified': verified, 'key_word': key_word, 'stop_word': stop_word, 'start_date': start_date, 'stop_date': stop_date}
        self.LIMIT = int(limit)
        self.posts = list()
        self.sorted_posts = list()
        self.all_timers = list()
        self.invalid_access_tokens = list()
        self.user_id = user_id

    def parser_function(self):
        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ?;""", (1, 'parser_status'))
        self.connection.commit()

        self.start = timer()
        _continue = True

        with self.console.status("[bold green]Parsind data...") as self.status:
            self.counter = 0
            self.end_date = self.FILTERS['stop_date']
            while True:
                self.counter += 1

                self.console.print(f'[yellow]Index: [bold]{self.counter}[/bold][yellow]')
                while True:
                    if self.FILTERS['start_date'] != '':
                        if self.end_date <= self.FILTERS['start_date']:
                            _continue = False
                            break

                    try:
                        if self.FILTERS['start_date'] != '':
                            response = requests.get(f"https://api.vk.com/method/newsfeed.search?lang=ru&access_token={self.access_tokens[self.access_token_index]}&q={self.FILTERS['key_word']}&end_time={self.end_date}&start_time={self.FILTERS['start_date']}&count=200&v=5.131")
                        else:
                            response = requests.get(f"https://api.vk.com/method/newsfeed.search?lang=ru&access_token={self.access_tokens[self.access_token_index]}&q={self.FILTERS['key_word']}&end_time={self.end_date}&start_time=1136073600&count=200&v=5.131")
                    except IndexError:
                        print('Index error')
                        self.access_token_index = 0
                        _continue = False
                        break

                    try:
                        if response.json()['response']['items'] == list():
                            self.access_token_index += 1
                            print('[red][bold]Access token index[/bold] - ' + str(self.access_token_index - 1) + '[/red]')
                            continue
                    except KeyError:
                        if response.json()['error']['error_msg'] == 'Too many requests per second':
                            continue
                        elif response.json()['error']['error_msg'] == 'User authorization failed: user is blocked.':
                            self.console.print(f'[red]{self.access_tokens[self.access_token_index]} - [bold]user is blocked.[/bold][/red]')
                            self.access_tokens.pop(self.access_token_index)
                            continue
                        elif response.json()['error']['error_msg'] == 'User authorization failed: invalid access_token (4).':
                            self.console.print(f'[red]{self.access_tokens[self.access_token_index]} - [bold]invalid access_token.[/bold][/red]')
                            self.invalid_access_tokens.append(self.access_tokens[self.access_token_index])
                            self.access_tokens.pop(self.access_token_index)
                            continue
                        else:
                            print(response.json())

                    print(response.url)

                    if len(self.posts) >= self.LIMIT:
                        _continue = False
                        break

                    response = response.json()['response']['items']
                    break

                if not _continue:
                    break

                print()
                for j in response:
                    self.posts.append(j)
                print(len(self.posts))

                self.end_date = self.posts[-1]['date'] - 1

        print()

        with open('access_tokens.txt', 'w') as access_tokens_file:
            access_tokens_file.write('\n'.join(self.access_tokens))

        with open('invalid_access_tokens.txt', 'w') as invalid_access_tokens_file:
            invalid_access_tokens_file.write('\n'.join(self.invalid_access_tokens))

        self.end = timer()
        self.console.print('[cyan]Parsing from VK completed successfully (', round(self.end - self.start, 2), '[bold cyan]sec[/bold cyan] [cyan])!')
        print()

        print(datetime.datetime.utcfromtimestamp(self.posts[-1]['date']))
        self.posts = self.posts[:self.LIMIT]
        self.start = timer()
        self._index = 0
        self.index = 0

        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ?;""", (str(len(self.posts)), 'parser_all_posts'))
        self.connection.commit()

        # sys.exit()
        self.access_token_index = 0

        with self.console.status("[bold green]Scaning data...") as self.status:
            for j in self.posts:
                self.start_time = timer()

                self.console.log(f"[yellow]Scaning post [bold]{self.index + 1}/{len(self.posts)}[/bold] complete[/yellow]")
                self.cursor.execute("""UPDATE params SET status = ? WHERE info = ?;""", (str(self.index + 1), 'parser_post'))
                self.connection.commit()
                self.index += 1

                if j['post_type'] != 'post':
                    continue

                self.text = j['text']

                self.date = j['date']

                self.likes = j['likes']['count']

                self.reposts = j['reposts']['count']

                self._id = int(j['owner_id'])
                if self._id < 0:
                    while True:
                        time.sleep(0.1)
                        response = requests.get(f'http://api.vk.com/method/groups.getById?lang=ru&group_id={abs(self._id)}&fields=members_count,verified&access_token={self.access_tokens[self.access_token_index]}&v={self.v}').json()
                        try:
                            self.subscribers = response['response'][0]['members_count']
                            self.verified = response['response'][0]['verified']
                            self.title = response['response'][0]['name']
                            break
                        except KeyError:
                            if response['error']['error_msg'] == 'Too many requests per second':
                                continue
                            elif response['error']['error_msg'] == 'Rate limit reached':
                                if self.access_token_index == len(self.access_tokens) - 1:
                                    self.access_token_index = 0
                                else:
                                    self.access_token_index += 1
                                continue
                            else:
                                print(response)
                                break
                else:
                    while True:
                        time.sleep(0.1)
                        response = requests.get(f'http://api.vk.com/method/users.get?lang=ru&fields=followers_count,verified&access_token={self.access_tokens[self.access_token_index]}&v={self.v}&user_ids={self._id}').json()
                        try:
                            self.subscribers = response['response'][0]['followers_count']
                            self.verified = response['response'][0]['verified']
                            self.title = response['response'][0]['first_name'] + response['response'][0]['last_name']
                            break
                        except KeyError:
                            if response['error']['error_msg'] == 'Too many requests per second':
                                continue
                            else:
                                print(response)
                                break


                if self.FILTERS['likes'][0]:
                    if self.FILTERS['likes'][1] == '>' and self.likes > self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '>=' and self.likes >= self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '=' and self.likes == self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '<=' and self.likes <= self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '<' and self.likes < self.FILTERS['likes'][2]:
                        pass
                    else:
                        continue

                if self.FILTERS['subscribers'][0]:
                    if self.FILTERS['subscribers'][1] == '>' and self.subscribers > self.FILTERS['subscribers'][2] or self.FILTERS['subscribers'][1] == '>=' and self.subscribers >= self.FILTERS['subscribers'][2] or self.FILTERS['subscribers'][1] == '=' and self.subscribers == self.FILTERS['subscribers'][2] or self.FILTERS['subscribers'][1] == '<=' and self.subscribers <= self.FILTERS['subscribers'][2] or self.FILTERS['subscribers'][1] == '<' and self.ubscribers < self.FILTERS['subscribers'][2]:
                        pass
                    else:
                        continue

                if self.FILTERS['stop_word'] != '':
                    if self.FILTERS['stop_word'].lower() in self.text.lower():
                        continue

                if not (self.FILTERS['start_date'] == '' or self.FILTERS['stop_date'] == ''):
                    if self.FILTERS['stop_date'] >= self.date >= self.FILTERS['start_date']:
                        pass
                    else:
                        continue

                if self.FILTERS['verified']:
                    if self.verified == 1:
                        pass
                    else:
                        continue

                # print(j)
                img_or_video = list()
                try:
                    for i in j['attachments']:
                        img_or_video.append(i['photo']['sizes'][2]['url'])
                except KeyError:
                    try:
                        for i in j['attachments']:
                            img_or_video.append(i['video']['image'][2]['url'])
                    except KeyError:
                        pass

                post = ['https://vk.com/wall' + str(j['owner_id']) + '_' + str(j['id']), str(datetime.datetime.utcfromtimestamp(int(j['date'])).strftime('%Y-%m-%d %H:%M:%S')), int(j['likes']['count']), int(j['reposts']['count']), int(self.subscribers), translit(strip_emoji(self.text), 'ru'), img_or_video, int(self._index + 1), self.title]
                # print(post)
                text = ''
                for j in post[5]:
                    if j == 'Ь':
                        text += j.lower()
                    else:
                        text += j
                post[5] = text
                self.cursor.execute("""INSERT INTO "{}" (url, title, date, likes, reposts, subscribers, text, img_or_video, [index]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""".format(self.user_id), (post[0], post[8], post[1], post[2], post[3], post[4], post[5], str(post[6]), post[7]))
                self.connection.commit()
                self.sorted_posts.append(post)

                # self.console.print(f'\n[bold white]Text:[/bold white] [white]{strip_emoji(self.text)}[/white]')
                # console.print(f'[bold blue]Date:[/bold blue] [blue]{date}[/blue]')
                # console.print(f'[bold red]Likes:[/bold red] [red]{likes}[/red]', end=', ')
                # console.print(f'[bold green]Reposts:[/bold green] [green]{reposts}[/green]', end=', ')
                # console.print(f'[bold yellow]Subscribers:[/bold yellow] [yellow]{subscribers}[/yellow]')
                # print()
                # print()

                self._index += 1

                self.end = timer()

                self.all_timers.append(self.end - self.start_time)

                self.primernoe_time = (sum(self.all_timers) / len(self.all_timers)) * self.LIMIT
                self.timer = self.primernoe_time - (self.end - self.start)

                print('≈' + str(round(self.timer, 2)))

                self.cursor.execute("""UPDATE params SET status = ? WHERE info = ?;""", (str(round(self.timer, 2)), 'parser_time'))
                self.connection.commit()

        print()
        self.console.print('[cyan]Parsing from VK completed successfully (', round(self.end - self.start, 2), '[bold cyan]sec[/bold cyan] [cyan])!')
        print()

        self.console.print('[bold green]All posts:', len(self.sorted_posts))

        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ?;""", (0, 'parser_status'))
        self.connection.commit()

        if (self.connection):
            self.cursor.close()
            self.connection.close()
            print("SQLite connection closed")

        with open("static/posts.csv", "w", newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['url', 'title', 'date', 'likes', 'reposts', 'subscribers', 'text', 'images', 'index'])
            for i in self.sorted_posts:
                i[5] = i[5].replace('\n', ' ')
                filewriter.writerow([i[0], i[8]] + i[1:8])

        return (self.user_id, self.sorted_posts)


class starter():
    def __init__(self, user_id=None, limit=None, likes=None, subscribers=None, verified=None, key_word=None, stop_word=None, start_date=None, stop_date=None):
        with open('settings.txt', 'w') as settings_file:
            settings_file.write(f'{user_id}\n{likes}\n{subscribers}\n{verified}\n{key_word}\n{stop_word}\n{start_date}\n{stop_date}\n{limit}')

    def starter_function(self):
        os.system('start open_vk_parser.py')