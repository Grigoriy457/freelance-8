from flask import *
import time
from vk_parser import parser, starter
import sqlite3
import sys

app = Flask(__name__)
posts = list()

status = 'one_console'

connection = sqlite3.connect('db.db', check_same_thread=False)
cursor = connection.cursor()

error = ''

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', error=error)

@app.route('/change_password', methods=['GET'])
def change_password():
    return render_template('change_password.html', error=error)

@app.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    global error
    error = ''
    if request.method == 'POST':
        user_id = request.form.get('id-input', '')
        old_password = request.form.get('old_password-input', '')
        new_password = request.form.get('new_password-input', '')
        repeat_new_password = request.form.get('repeat_new_password-input', '')

        user_info = cursor.execute("""SELECT * FROM "users" WHERE "user_id"='{}';""".format(user_id)).fetchone()
        if bool(user_info):
            if user_info[1] != old_password:
                error = 'Wrong password'
                return redirect('/change_password', code=302)
            else:
                if new_password != repeat_new_password:
                    error = 'Password mismatch'
                    return redirect('/change_password', code=302)
                else:
                    error = ''
                    cursor.execute("""UPDATE "users" SET "password"=? WHERE "user_id"=?;""", (new_password, user_id))
                    connection.commit()
                    return redirect('/', code=302)
        else:
            error = 'Wrong username'
            return redirect('/change_password', code=302)
    else:
        return redirect('/', code=302)

def get_all_posts():
    global cursor, posts, user_id
    posts = cursor.execute("""SELECT * FROM "{}";""".format(user_id)).fetchall()
    _posts = list()
    list_img = list()
    for i in posts:
        list_img = i[6].split(', ')
        list_img[0] = list_img[0][1:]
        list_img[-1] = list_img[-1][:-1]
        for j in range(len(list_img )):
            list_img[j] = list_img[j][1:-1]
        if list_img == ['']:
            list_img = list()
        _posts.append((i[0], i[1], i[2], i[3], i[4], i[5], list_img, i[7]))
    return _posts

@app.route('/load', methods=['GET', "POST"])
def load():
    global _posts, cursor, connection, list_img, error, user_id
    print('/load')
    # if 
    if request.method == 'POST':
        user_id = request.form.get('id-input', '')
        password = request.form.get('password-input', '')
        user_info = cursor.execute("""SELECT * FROM "users" WHERE "user_id"='{}';""".format(user_id)).fetchone()
        if bool(user_info):
            if user_info[1] != password:
                error = 'Wrong password'
                return redirect('/', code=302)
            else:
                error = ''
        else:
            error = 'Wrong username'
            return redirect('/', code=302)

        limit = int(0 if request.form.get('limit-input', '') == '' else request.form.get('limit-input', ''))
        try:
            likes = [(True if request.form.get('likes-input', 'off') == 'on' else False), request.form.get('likes_select', ''), int(request.form.get('likes-input__count', ''))]
        except ValueError:
            likes = [False, '=', 0]
        try:
            subscribers = [(True if request.form.get('subscribers-input', 'off') == 'on' else False), request.form.get('subscribers_select', ''), int(request.form.get('subscribers-input__count', ''))]
        except ValueError:
            subscribers = [False, '=', 0]
        key_word = request.form.get('key_word-input', '')
        stop_word = request.form.get('stop_word-input', '')
        bool_time = True if request.form.get('date-input', 'off') == 'on' else False
        start_time = request.form.get('start_time', '')
        end_time = request.form.get('end_time', '')
        if key_word != '' and limit != 0:
            if bool_time:
                if end_time == '' or start_time == '' or end_time == start_time:
                    return redirect('/', code=302)
            if status == 'new_console':
                starter(user_id=user_id, limit=limit, likes=likes, subscribers=subscribers, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).starter_function()
                time.sleep(2)
                return render_template('load.html', time='...', now_post='...', all_post='...')
            elif status == 'one_console':
                parser(user_id=user_id, limit=limit, likes=likes, subscribers=subscribers, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).parser_function()
                _posts = get_all_posts()
                return redirect('/result/1', code=302)
        else:
            return redirect('/', code=302)
    else:
        cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_status',))
        if int(cursor.fetchone()[0]) == 1:
            _time = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_time',)).fetchone()[0]
            now_post = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_post',)).fetchone()[0]
            all_post = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_all_posts',)).fetchone()[0]
            return render_template('load.html', time=_time, now_post=now_post, all_post=all_post)
        else:
            _posts = get_all_posts()
            return redirect('/result/1', code=302)

@app.route('/result/<int:page>')
def int_result(page):
    global _posts
    if _posts != list() and _posts != None:
        return render_template('result.html', posts=_posts, len_posts=len(_posts), page=page, range_posts=range(1, ((len(_posts) // 1000) + (2 if len(_posts) % 1000 != 0 else 1))))
    else:
        return redirect('/', code=302)

@app.route('/result')
def result():
    return redirect('/', code=302)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    print('run')
    app.run(host='0.0.0.0')
    # app.run(host='10.10.10.58', debug=False, port=5500)
    # app.run(host='localhost', debug=False, port=5500)