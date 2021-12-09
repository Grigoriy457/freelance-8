import requests
import datetime
from datetime import date
from timeit import default_timer as timer
import time
import sys
import os
import re
from rich.console import Console
import sqlite3
import csv


class parser():
    def __init__(self, user_id=None, limit=None, likes=None, subscribers=None, verified=None, key_word=None, stop_word=None, start_date=None, stop_date=None):
        create_table_1 = """CREATE TABLE IF NOT EXISTS posts (
                            user_id      VARCHAR (255)  NOT NULL,
                            [index]      INTEGER        NOT NULL,
                            url          VARCHAR (255)  NOT NULL,
                            title        VARCHAR (255)  NOT NULL,
                            date         VARCHAR (255)  NOT NULL,
                            likes        INTEGER        NOT NULL,
                            reposts      INTEGER        NOT NULL,
                            subscribers  INTEGER        NOT NULL,
                            text         VARCHAR (4000),
                            img_or_video VARCHAR (1000),
                        );"""
        create_table_2 = """CREATE TABLE IF NOT EXISTS params (
                            info VARCHAR (255),
                            status VARCHAR (255),
                            user_id VARCHAR (2)
                        );"""
        delete_table_1 = """DROP TABLE IF EXISTS posts;"""
        delete_table_2 = """DROP TABLE IF EXISTS params;"""

        self.connection = sqlite3.connect('db.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

        print("SQLite connected")

        self.cursor.execute("""DELETE FROM "posts" WHERE "user_id"='{}';""".format(user_id))
        self.connection.commit()

        self.cursor.execute("""UPDATE "params" SET "status"='{}' WHERE "user_id"='{}' AND "info"='{}';""".format(1, user_id, "parser_status"))
        self.connection.commit()
        self.cursor.execute("""UPDATE "params" SET "status"='{}' WHERE "user_id"='{}' AND "info"='{}';""".format("...", user_id, "parser_post"))
        self.connection.commit()
        self.cursor.execute("""UPDATE "params" SET "status"='{}' WHERE "user_id"='{}' AND "info"='{}';""".format("...", user_id, "parser_all_posts"))
        self.connection.commit()
        self.cursor.execute("""UPDATE "params" SET "status"='{}' WHERE "user_id"='{}' AND "info"='{}';""".format("...", user_id, "parser_time"))
        self.connection.commit()


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
        self.end_date = self.FILTERS['stop_date']
        self.start_date = self.FILTERS['start_date']
        while True:
            response = requests.get(f"https://api.vk.com/method/newsfeed.search?lang=ru&access_token={self.access_tokens[0]}&q={self.FILTERS['key_word']}&end_time={self.end_date}&start_time={self.start_date}&count=200&v=5.131").json()
            try:
                response = int(response['response']['count'])
                break
            except KeyError:
                if response['error']['error_msg'] == 'User authorization failed: user is blocked.':
                    self.access_tokens.pop(self.access_token_index)
        with open('access_tokens.txt', 'w') as access_tokens_file:
            access_tokens_file.write('\n'.join(self.access_tokens))
        if self.LIMIT > response and response != 1000:
            self.LIMIT = response - 3
        print('LIMIT:', self.LIMIT)
        self.posts = list()
        self.sorted_posts = list()
        self.all_timers = list()
        self.invalid_access_tokens = list()
        self.user_id = user_id

    def parser_function(self):
        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ? AND user_id = ?;""", (1, 'parser_status', self.user_id))
        self.connection.commit()

        self.start = timer()
        _continue = True

        with self.console.status("[bold green]Parsind data...") as self.status:
            self.counter = 0
            while True:
                self.counter += 1

                self.console.print(f'[yellow]Index: [bold]{self.counter}[/bold][yellow]')
                while True:
                    if self.FILTERS['start_date'] != '':
                        if self.end_date <= self.FILTERS['start_date']:
                            _continue = False
                            break


                    if len(self.posts) >= self.LIMIT:
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
                            self.console.print('[red][bold]Access token index[/bold] - ' + str(self.access_token_index - 1) + '[/red]')
                            continue
                    except KeyError:
                        try:
                            if response.json()['error']['error_msg'] == 'Too many requests per second':
                                continue
                            elif response.json()['error']['error_msg'] == 'User authorization failed: user is blocked.':
                                self.console.print(f'[red]{self.access_tokens[self.access_token_index]} - [bold]user is blocked.[/bold][/red]')
                                self.access_tokens.pop(self.access_token_index)
                                continue
                            elif response.json()['error']['error_msg'] in ['User authorization failed: invalid access_token (4).', 'User authorization failed: invalid access_token (8).', 'User authorization failed: invalid session.']:
                                self.console.print(f'[red]{self.access_tokens[self.access_token_index]} - [bold]invalid access_token.[/bold][/red]')
                                self.invalid_access_tokens.append(self.access_tokens[self.access_token_index])
                                self.access_tokens.pop(self.access_token_index)
                                continue
                            else:
                                self.console.print('[red bold]<ERROR:>[/red bold] [yellow]', response.json())
                        except KeyError:
                            self.console.print('[red bold]<ERROR:>[/red bold] [yellow]', response.json())

                    print(response.url)

                    try:
                        response = response.json()['response']['items']
                    except KeyError:
                        pass
                    break

                if not _continue:
                    break

                print()
                for j in response:
                    self.posts.append(j)

                index = -1
                while True:
                    try:
                        self.end_date = self.posts[index]['date'] - 1
                        break
                    except TypeError:
                        index -= 1
                if index < -1:
                    index += 1
                    self.posts = self.posts[:index]

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

        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ? AND user_id = ?;""", (str(len(self.posts)), 'parser_all_posts', self.user_id))
        self.connection.commit()

        # sys.exit()
        self.access_token_index = 0

        with self.console.status("[bold green]Scaning data...") as self.status:
            for j in self.posts:
                self.start_time = timer()

                self.console.log(f"[yellow]Scaning post [bold]{self.index + 1}/{len(self.posts)}[/bold] complete[/yellow]")
                self.cursor.execute("""UPDATE params SET status = ? WHERE info = ? AND user_id = ?;""", (str(self.index + 1), 'parser_post', self.user_id))
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
                            try:
                                if response['error']['error_msg'] == 'Too many requests per second':
                                    continue
                                else:
                                    print(response)
                                    break
                            except KeyError:
                                self.console.print('[red bold]<ERROR:>[/red bold] [yellow]', response)


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

                post = ['https://vk.com/wall' + str(j['owner_id']) + '_' + str(j['id']), str(datetime.datetime.utcfromtimestamp(int(j['date'])).strftime('%Y-%m-%d %H:%M:%S')), int(j['likes']['count']), int(j['reposts']['count']), int(self.subscribers), self.text, img_or_video, int(self._index + 1), self.title]
                # print(post)
                text = ''
                for j in post[5]:
                    if j == 'Ь':
                        text += j.lower()
                    else:
                        text += j
                post[5] = text
                self.cursor.execute("""INSERT INTO "posts" (user_id, [index], url, title, date, likes, reposts, subscribers, text, img_or_video) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (self.user_id, post[7], post[0], post[8], post[1], post[2], post[3], post[4], post[5], str(post[6])))
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

                self.cursor.execute("""UPDATE params SET status = ? WHERE info = ? AND user_id = ?;""", (str(round(self.timer, 2)), 'parser_time', self.user_id))
                self.connection.commit()

        print()
        self.console.print('[cyan]Parsing from VK completed successfully (', round(self.end - self.start, 2), '[bold cyan]sec[/bold cyan] [cyan])!')
        print()

        self.console.print('[bold green]All posts:', len(self.sorted_posts))

        self.cursor.execute("""UPDATE params SET status = ? WHERE info = ? AND user_id = ?;""", (0, 'parser_status', self.user_id))
        self.connection.commit()

        if (self.connection):
            self.cursor.close()
            self.connection.close()
            print("SQLite connection closed")

        path = f"static/users/{self.user_id}/posts.csv"
        path_2 = f"static/users/{self.user_id}"

        if not os.path.exists(path):
            os.mkdir(os.path.abspath(path_2))

        with open(path, "w", newline='', encoding='utf-16') as csvfile:
            filewriter = csv.writer(csvfile, dialect='excel', delimiter=',', quoting=csv.QUOTE_ALL)
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