from flask import *
import time
from vk_parser import parser, starter
import sqlite3
import sys
from rich.console import Console
import datetime

from settings import TYPE, SERVER_HOST, DEV_HOST, SERVER_AUTO_UPDATE, DEV_AUTO_UPDATE



if TYPE == "SERVER":
    HOST = SERVER_HOST
    AUTO_UPDATE = SERVER_AUTO_UPDATE
elif TYPE == "DEV":
    HOST = DEV_HOST
    AUTO_UPDATE = DEV_AUTO_UPDATE
else:
    Console().print(f'[red]Invalid value of variable TYPE (now: "{TYPE}")[/red]')
    sys.exit()



app = Flask(__name__)
posts = list()

status = 'one_console'

connection = sqlite3.connect('static/db.db', check_same_thread=False)
cursor = connection.cursor()

console = Console()

error = ['' for i in range(51)]
list_filters = list()



@app.route('/login/')
def login():
    error = request.args.get('error')
    if error == None:
        error = ''
    return render_template('login.html', error=error)



@app.route('/')
def home():
    user_id = request.args.get('user_id')
    print('USER ID:', user_id)
    if user_id not in ['', None]:
        if not (len(user_id) == 2 and 0 <= int(user_id) <= 50):
            return redirect('/login?error=Wrong+user+id+%28from+00+to+50%29') # Wrong user id (from 00 to 50)
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_status', user_id))
        if int(cursor.fetchone()[0]) == 1:
            return redirect(f'/show_status_load/{user_id}', code=302)
        return render_template('home.html', error=error, user_id=user_id)
    return redirect('/login?error=')



@app.route('/change_password/')
def change_password():
    return render_template('change_password.html', error=error)



@app.route('/set_new_password/', methods=['GET', 'POST'])
def set_new_password():
    global error
    if request.method == 'POST':
        user_id = request.form.get('id-input', '')
        old_password = request.form.get('old_password-input', '')
        new_password = request.form.get('new_password-input', '')
        repeat_new_password = request.form.get('repeat_new_password-input', '')

        user_info = cursor.execute("""SELECT * FROM "users" WHERE "user_id"='{}';""".format(user_id)).fetchone()
        if bool(user_info):
            if user_info[1] != old_password:
                error[int(user_id)] = 'Wrong password'
                return redirect('/change_password', code=302)
            else:
                if new_password != repeat_new_password:
                    error[int(user_id)] = 'Password mismatch'
                    return redirect('/change_password', code=302)
                else:
                    error[int(user_id)] = ''
                    cursor.execute("""UPDATE "users" SET "password"=? WHERE "user_id"=?;""", (new_password, user_id))
                    connection.commit()
                    return redirect('/', code=302)
        else:
            error[int(user_id)] = 'Wrong username'
            return redirect('/change_password', code=302)
    else:
        return redirect('/', code=302)



def sort_posts(posts, bool_posts=False):
    _posts = list()
    list_img = list()
    index = 1
    if bool_posts:
        for i in posts:
            list_img = i[9].split(', ')
            list_img[0] = list_img[0][1:]
            list_img[-1] = list_img[-1][:-1]
            for j in range(len(list_img )):
                list_img[j] = list_img[j][1:-1]
            if list_img == ['']:
                list_img = list()
            cursor.execute("""SELECT * FROM "favourite" WHERE "user_id"='{}' AND "url"='{}';""".format(i[0], i[2]))
            favurite_checker = cursor.fetchone()
            favurite_checker = bool(favurite_checker)

            _posts.append((i[0], index, i[2], i[3], i[4], i[5], i[6], i[7], i[8], list_img, favurite_checker))

            index += 1
    else:
        for i in posts:
            list_img = i[8].split(', ')
            list_img[0] = list_img[0][1:]
            list_img[-1] = list_img[-1][:-1]
            for j in range(len(list_img )):
                list_img[j] = list_img[j][1:-1]
            if list_img == ['']:
                list_img = list()
            cursor.execute("""SELECT * FROM "favourite" WHERE "user_id"='{}' AND "url"='{}';""".format(i[0], i[1]))
            favurite_checker = bool(cursor.fetchone())

            _posts.append((i[0], index, i[1], i[2], i[3], i[4], i[5], i[6], i[7], list_img, favurite_checker))

            index += 1
    return _posts



def get_all_posts(user_id):
    cursor.execute("""SELECT * FROM "posts" WHERE "user_id"='{}';""".format(user_id))
    posts = cursor.fetchall()

    return sort_posts(posts, bool_posts=True)



def get_favourited_posts(user_id):
    cursor.execute("""SELECT * FROM "favourite" WHERE "user_id"='{}';""".format(user_id))
    posts = cursor.fetchall()

    return sort_posts(posts)



@app.route('/show_status_load/<string:user_id>/', methods=['GET', 'POST'])
def show_status_load(user_id):
    cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_status', user_id))
    if int(cursor.fetchone()[0]) == 1:
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_time', user_id))
        _time = cursor.fetchone()[0]
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_post', user_id))
        now_post = cursor.fetchone()[0]
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_all_posts', user_id))
        all_post = cursor.fetchone()[0]
        return render_template('load.html', time=_time, now_post=now_post, all_post=all_post, user_id=user_id, auto_update=AUTO_UPDATE)
    else:
        return redirect(f'/result/1/{user_id}', code=302)



@app.route('/load/')
def load():
    global cursor, connection, error, list_filters
    print('/load')

    user_id = request.args.get('user_id')

    cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_status', user_id))
    if int(cursor.fetchone()[0]) == 1:
        return redirect(f'/show_status_load/{user_id}', code=302)

    cursor.execute("""SELECT * FROM "filters" WHERE "user_id"='{}';""".format(user_id))
    list_filters = cursor.fetchall()


    limit = request.args.get('limit-input')
    if request.args.get('likes-input__count') != '':
        likes = [True, request.args.get('likes_select'), int(request.args.get('likes-input__count'))]
    else:
        likes = [False, ' ', 0]
    if request.args.get('subscribers-input__count') != '':
        subscribers = [True, request.args.get('subscribers_select'), int(request.args.get('subscribers-input__count'))]
    else:
        subscribers = [False, ' ', 0]
    verified = True if request.args.get('verified-select') == 'Yes' else False
    key_word = request.args.get('key_word-input')
    stop_word = [i for i in request.args.get('stop_word-input').split(', ') if i != ""]
    bool_time = True if request.args.get('date-checkbox') == 'YES' else False
    if bool_time:
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
    else:
        start_time, end_time = '', ''

    print('User id:', user_id)
    print('Limit:', limit)
    print('Likes:', likes)
    print('Subscribers:', subscribers)
    print('Verified:', verified)
    print('Key word:', key_word)
    print('Stop word:', stop_word)
    print('Bool time:', bool_time)
    print('Start time:', start_time)
    print('End time:', end_time)

    microseconds = int(int(datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp()).strftime("%f")) % 10)
    date = datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp()).strftime("%d/%m/%Y %H:%M:%S.{}".format(microseconds))
    cursor.execute("""INSERT INTO "filters" ([date], user_id, [limit], likes, subscribers, verified, key_word, pass_word, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (date, user_id, limit, likes[1] + str(likes[2]), subscribers[1] + str(subscribers[2]), int(verified), key_word, ", ".join(stop_word), start_time, end_time))
    connection.commit()

    if key_word != '' and limit != 0:
        if bool_time:
            if end_time == '' or start_time == '' or end_time == start_time:
                return redirect('/', code=302)
        if status == 'new_console':
            starter(user_id=user_id, limit=limit, likes=likes, subscribers=subscribers, verified=verified, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).starter_function()
            time.sleep(2)
            return render_template('load.html', time='...', now_post='...', all_post='...')
        elif status == 'one_console':
            parser(user_id=user_id, limit=limit, likes=likes, subscribers=subscribers, verified=verified, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).parser_function()
            return redirect(f'/result/1/{user_id}', code=302)
    else:
        return redirect('/', code=302)



@app.route('/result/<int:page>/<string:user_id>/')
def int_result(page, user_id):
    cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_status', user_id))
    if int(cursor.fetchone()[0]) == 0:
        cursor.execute("""SELECT * FROM "filters" WHERE "user_id" = '{}';""".format(user_id))
        _list_filters = cursor.fetchall()[-1]
        list_filters = [
            ["Limit", _list_filters[2]],
            ["Likes", "≥" + _list_filters[3][1] if _list_filters[3][0] == " " else _list_filters[3]],
            ["Subscribers", "≥" + _list_filters[4][1] if _list_filters[4][0] == " " else _list_filters[4]],
            ["Verified", _list_filters[5]],
            ["Key_word", _list_filters[6]],
            ["Pass_word", _list_filters[7]],
            ["Start_time", _list_filters[8]],
            ["End_time", _list_filters[9]],
        ]
        _posts = get_all_posts(user_id)
        if _posts != list() and _posts != None:
            range_posts = range(1, ((len(_posts) // 1000) + (2 if len(_posts) % 1000 != 0 else 1)))
            return render_template('result.html', user_id=user_id, posts=_posts, len_posts=len(_posts), page=page, range_posts=range_posts, list_filters=list_filters, host=HOST)
        else:
            return redirect('/', code=302)
    else:
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_time', user_id))
        _time = cursor.fetchone()[0]
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_post', user_id))
        now_post = cursor.fetchone()[0]
        cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_all_posts', user_id))
        all_post = cursor.fetchone()[0]
        return render_template('load.html', time=_time, now_post=now_post, all_post=all_post, user_id=user_id)



@app.route('/favourite/<string:user_id>/<int:page>/<int:post_id>/')
def do_favourite(user_id, page, post_id):
    console.print(f'[yellow][bold][INFO]:[/bold] Now post {post_id} on page {page} has become a favorite of user {user_id}[/yellow]')

    cursor.execute("""SELECT * FROM "posts" WHERE "user_id"='{}' AND "index"='{}';""".format(user_id, post_id))
    data = list(cursor.fetchone())
    data = tuple([data[0]] + data[2:])

    cursor.execute("""INSERT INTO "favourite" (user_id, url, title, date, likes, reposts, subscribers, text, img_or_video) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""", data)
    connection.commit()

    return redirect(f'/result/{page}/{user_id}/#{post_id}', code=302)



@app.route('/unfavourite/<string:user_id>/<int:page>/<int:post_id>/')
def do_unfavourite(user_id, page, post_id):
    url = request.args.get('url')

    console.print(f'[yellow][bold][INFO]:[/bold] Now post {post_id} on page {page} has become an unfavorite of user {user_id}[/yellow]')

    if request.args.get('from') == "fp":
        # cursor.execute("""SELECT * FROM "favourite" WHERE "user_id"='{}' AND "url"='{}';""".format(user_id, url))
        # data = list(cursor.fetchone())

        cursor.execute("""DELETE FROM "favourite" WHERE "user_id"='{}' AND "url"='{}';""".format(user_id, url))
        connection.commit()

        return redirect(f'/favourited_posts/{page}/{user_id}#{post_id}', code=302)
    else:
        cursor.execute("""DELETE FROM "favourite" WHERE "user_id"='{}' AND "url"='{}';""".format(user_id, url))
        connection.commit()

        return redirect(f'/result/{page}/{user_id}#{post_id}', code=302)



@app.route('/favourited_posts/<int:page>/<string:user_id>/')
def favourited_posts(page, user_id):

    favourited_posts = get_favourited_posts(user_id)

    range_posts = range(1, ((len(favourited_posts) // 1000) + (2 if len(favourited_posts) % 1000 != 0 else 1)))

    return render_template('favourite.html', user_id=user_id, favourited_posts=favourited_posts, page=page, range_posts=range_posts, len_favourited_posts=len(favourited_posts), host=HOST)



@app.route('/search_history/<int:page>/<string:user_id>/')
def search_history(page, user_id):
    cursor.execute("""SELECT * FROM "filters";""")
    data = cursor.fetchall()[::-1]
    _data = list()
    for i in data:
        _data.append([i[0], i[1], [
                                    ["Limit", i[2]],
                                    ["Likes", i[3]],
                                    ["Subscribers", i[4]],
                                    ["Verified", bool(i[5])],
                                    ["Key word", i[6]],
                                    ["Pass word", i[7]],
                                    ["Start date", i[8]],
                                    ["End date", i[9]]
                                  ]])

    return render_template('search_history.html', page=page, history_data=_data, user_id=user_id)



@app.route('/search_history/<int:page>/')
def search_history_2(page):
    cursor.execute("""SELECT * FROM "filters";""")
    data = cursor.fetchall()[::-1]
    _data = list()
    for i in data:
        _data.append([i[0], i[1], [
                                    ["Limit", i[2]],
                                    ["Likes", i[3]],
                                    ["Subscribers", i[4]],
                                    ["Verified", bool(i[5])],
                                    ["Key word", i[6]],
                                    ["Pass word", i[7]],
                                    ["Start date", i[8]],
                                    ["End date", i[9]]
                                  ]])

    return render_template('search_history.html', page=page, history_data=_data, user_id="")



@app.route("/admin/")
def admin():
    date = datetime.datetime.utcfromtimestamp(datetime.datetime.now().timestamp()).strftime("%d.%m.%Y")
    return render_template("admin.html", date=date, host=HOST)



@app.route('/test')
def test():
    return render_template('test.html')



if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(host='0.0.0.0')