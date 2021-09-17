import requests
import datetime
import math
import sys
import re
from rich.console import Console
from timeit import default_timer as timer
import time
from datetime import date

class parser():
    def __init__(self, limit=None, likes=None, subscribers=None, key_word=None, stop_word=None, start_date=None, stop_date=None):
        self.access_tokens = [
                                '02d50ad6edce3f9e67574e3e18f47af62c4b210874046fe12c072614dcdf225ed073cf7da24a5d0b2dc1a',
                                'e9387c4a47fc49f73344aedf116359d6910861ee0426b36de2741a0e35dc93fbd5dc033cfc43aeec431db',
                                '5724e7ceb79635b90d7968b1aed098b552c205cf34daab7f7b7b055de59ba7dc5bfa49f2d5a6c6c9d22cf',
                                '608a295216df63589fd7a2a91dd2563b0207ef7ecfbab9609b0298677605cb4eeb4b562a93af9a634d77b',
                                '7a175f3ed49de566131cc8c9ce759c3fe9ce3a8d2a6e83d6efaa141e7388a9b51c1fdd1d7854ce4c83f0d',
                                '0902ee67d0a673e1c33a265eeb97daf8ba36b206cf2d6b6d6c518ab9628f41a8088bf29e77e9a392b5d3b',
                                'a123325be251d031e5906030e02e2bc762f803f85e62fb7506a8ab9004e6210707b2adf08e4e784f475a8',
                                '45f0e89c394b9685a87ba533ee08ee0d0f1dd054307b6fe5aca373e96e19d7bede5f0d517e859759e6e88',
                            ]
        
        self.access_token_index = 0
        self.console = Console()
        self.start_from = 0
        self.filters = 'post'
        self.v = '5.61'
        try:
            start_date = start_date.split('-')
            stop_date = stop_date.split('-')
            try:
                start_date = round(int(time.mktime(date(int(start_date[0]), int(start_date[1]), int(start_date[2])).timetuple())))
                stop_date = round(int(time.mktime(date(int(stop_date[0]), int(stop_date[1]), int(stop_date[2])).timetuple())))
            except:
                start_date, stop_date = 1136073600, round(time.time())
        except AttributeError:
            start_date, stop_date = '', ''
        self.FILTERS = {'likes': likes, 'subscribers': subscribers, 'key_word': key_word, 'stop_word': stop_word, 'start_date': start_date, 'stop_date': stop_date}
        self.LIMIT = limit
        self.posts = list()
        self.sorted_posts = list()
        self.all_timers = list()

    def parser_function(self):
        self.start = timer()
        _continue = True

        print(self.LIMIT)

        with self.console.status("[bold green]Parsind data...") as self.status:
            self.counter = 0
            self.end_date = self.FILTERS['stop_date']
            while True:
                self.counter += 1

                self.console.print(f'[yellow]Index: [bold]{self.counter}[/bold][yellow]')
                while True:
                    try:
                        response = requests.get(f"https://api.vk.com/method/newsfeed.search?access_token={self.access_tokens[self.access_token_index]}&q={self.FILTERS['key_word']}&end_time={self.end_date}&start_time={self.FILTERS['start_date']}&extended=1&count=200&v=5.131")
                    except IndexError:
                        self.access_token_index = 0
                        print('Next')
                        continue

                    try:
                        if response.json()['response']['items'] == list():
                            self.access_token_index += 1
                            continue
                    except KeyError:
                        if response.json()['error']['error_msg'] == 'Too many requests per second':
                            continue
                        elif response.json()['error']['error_msg'] == 'User authorization failed: user is blocked.':
                            print(f'{self.access_tokens[self.access_token_index]} - This access token has is already blocked.')
                            self.access_token_index += 1
                            continue
                        elif response.json()['error']['error_msg'] == 'User authorization failed: invalid access_token (4).':
                            print(f'{self.access_tokens[self.access_token_index]} - invalid access_token.')
                        else:
                            print(response.json())

                    if len(self.posts) >= self.LIMIT:
                        _continue = False
                        break

                    print(response.url)
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

        self.end = timer()
        self.console.print('[cyan]Parsing from VK completed successfully (', round(self.end - self.start, 2), '[bold cyan]sec[/bold cyan] [cyan])!')
        print()

        print(datetime.datetime.utcfromtimestamp(self.posts[-1]['date']))
        self.posts = self.posts[:self.LIMIT]
        self.start = timer()
        self.index = 0

        # sys.exit()
        self.access_token_index = 0

        with self.console.status("[bold green]Scaning data...") as self.status:
            for j in self.posts:
                self.start_time = timer()
                self.console.log(f"[yellow]Scaning post [bold]{self.index + 1}/{len(self.posts)}[/bold] complete[/yellow]")

                self.text = j['text']

                self.date = j['date']

                self.likes = j['likes']['count']

                self.reposts = j['reposts']['count']

                self._id = int(j['owner_id'])
                if self._id < 0:
                    try:
                        self.subscribers = requests.get(f'http://api.vk.com/method/groups.getById?group_id={abs(self._id)}&fields=members_count&access_token={self.access_tokens[self.access_token_index]}&v={self.v}').json()['response'][0]['members_count']
                    except KeyError:
                        self.subscribers = ''
                    except requests.exceptions.ConnectionError:
                        continue
                else:
                    try:
                        self.subscribers = requests.get(f'http://api.vk.com/method/users.getFollowers?access_token={self.access_tokens[self.access_token_index]}&v={self.v}&user_id={self._id}').json()['response']['count']
                    except KeyError:
                        self.subscribers = ''
                    except requests.exceptions.ConnectionError:
                        continue

                self.check = [None, None, None, None, None]

                if self.FILTERS['likes'][0]:
                    if self.FILTERS['likes'][1] == '>' and self.likes > self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '>=' and self.likes >= self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '=' and self.likes == self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '<=' and self.likes <= self.FILTERS['likes'][2] or self.FILTERS['likes'][1] == '<' and self.likes < self.FILTERS['likes'][2]:
                        pass
                    else:
                        continue

                if self.FILTERS['subscribers'][0]:
                    if self.FILTERS['subscribers'][1] == '>' and self.subscribers > self.FILTERS['subscribers'][2] or FILTERS['subscribers'][1] == '>=' and self.subscribers >= self.FILTERS['subscribers'][2] or FILTERS['subscribers'][1] == '=' and self.subscribers == self.FILTERS['subscribers'][2] or FILTERS['subscribers'][1] == '<=' and self.subscribers <= self.FILTERS['subscribers'][2] or FILTERS['subscribers'][1] == '<' and self.ubscribers < self.FILTERS['subscribers'][2]:
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

                self.sorted_posts.append(['https://vk.com/wall' + str(j['owner_id']) + '_' + str(j['id']), datetime.datetime.utcfromtimestamp(int(j['date'])).strftime('%Y-%m-%d %H:%M:%S'), j['likes']['count'], j['reposts']['count'], j['text'].encode('ascii', 'ignore').decode('ascii'), img_or_video, self.index + 1])

                # console.print(f'\n[bold white]Text:[/bold white] [white]{text}[/white]')
                # console.print(f'[bold blue]Date:[/bold blue] [blue]{date}[/blue]')
                # console.print(f'[bold red]Likes:[/bold red] [red]{likes}[/red]', end=', ')
                # console.print(f'[bold green]Reposts:[/bold green] [green]{reposts}[/green]', end=', ')
                # console.print(f'[bold yellow]Subscribers:[/bold yellow] [yellow]{subscribers}[/yellow]')
                # print()
                # print()

                self.index += 1

                self.end = timer()

                self.all_timers.append(self.end - self.start_time)

                self.primernoe_time = (sum(self.all_timers) / len(self.all_timers)) * self.LIMIT
                self.timer = self.primernoe_time - (self.end - self.start)

                print('≈' + str(round(self.timer, 2)))

        print()
        self.console.print('[cyan]Parsing from VK completed successfully (', round(self.end - self.start, 2), '[bold cyan]sec[/bold cyan] [cyan])!')
        print()

        self.console.print('[bold green]All posts:', len(self.sorted_posts))

        with open('posts.txt', 'w') as file:
            file.write('\n——————————————————————————————————————————————————\n'.join([str(i) for i in self.sorted_posts]))

        return self.sorted_posts