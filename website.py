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

error = ['' for i in range(51)]
list_filters = list()

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/', methods=['GET'])
def home():
    user_id = request.args.get('user_id')
    if user_id != None and user_id != '':
        return render_template('home.html', error=error, user_id=user_id)
    return redirect('/login')

@app.route('/change_password', methods=['GET'])
def change_password():
    return render_template('change_password.html', error=error)

@app.route('/set_new_password', methods=['GET', 'POST'])
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

def get_all_posts(user_id):
    global cursor
    cursor.execute("""SELECT * FROM "{}";""".format(user_id))
    posts = cursor.fetchall()
    _posts = list()
    list_img = list()
    for i in posts:
        list_img = i[7].split(', ')
        list_img[0] = list_img[0][1:]
        list_img[-1] = list_img[-1][:-1]
        for j in range(len(list_img )):
            list_img[j] = list_img[j][1:-1]
        if list_img == ['']:
            list_img = list()
        _posts.append((i[0], i[1], i[2], i[3], i[4], i[5], i[6], list_img, i[8]))
    return _posts

@app.route('/show_status_load/<string:user_id>', methods=['GET', 'POST'])
def show_status_load(user_id):
    cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_status', user_id))
    if int(cursor.fetchone()[0]) == 1:
        _time = cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_time', user_id)).fetchone()[0]
        now_post = cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_post', user_id)).fetchone()[0]
        all_post = cursor.execute("""SELECT status FROM params WHERE info = ? AND user_id = ?;""", ('parser_all_posts', user_id)).fetchone()[0]
        return render_template('load.html', time=_time, now_post=now_post, all_post=all_post, user_id=user_id)
    else:
        return redirect(f'/result/1/{user_id}', code=302)

@app.route('/load', methods=['GET'])
def load():
    global cursor, connection, error, list_filters
    print('/load')
    # time.sleep(1000)

    list_filters = list()
    user_id = request.args.get('user_id')
    # user_info = cursor.execute("""SELECT * FROM "users" WHERE "user_id"='{}';""".format(user_id)).fetchone()
    # if bool(user_info):
    #     if user_info[1] != password:
    #         error[int(user_id)] = 'Wrong password'
    #         return redirect('/', code=302)
    #     else:
    #         error[int(user_id)] = ''
    # else:
    #     error[int(user_id)] = 'Wrong username'
    #     return redirect('/', code=302)


    limit = request.args.get('limit-input')
    if request.args.get('likes-input__count') != '':
        likes = [(True if request.args.get('likes-input__count') != '' else False), request.args.get('likes_select'), int(request.args.get('likes-input__count'))]
    else:
        likes = [False, '', 0]
    if request.args.get('subscribers-input__count') != '':
        subscribers = [(True if request.args.get('subscribers-input__count') != '' else False), request.args.get('subscribers_select'), int(request.args.get('subscribers-input__count'))]
    else:
        subscribers = [False, '', 0]
    verified = True if request.args.get('verified-select') != 'Yes' else False
    key_word = request.args.get('key_word-input')
    stop_word = request.args.get('stop_word-input')
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

    list_filters.append(['Limit', limit])
    if likes[0]:
        list_filters.append(['Likes', (likes[1] + ' ' + str(likes[2]))])
    if subscribers[0]:
        list_filters.append(['Subscribers', (subscribers[1] + ' ' + str(subscribers[2]))])
    list_filters.append(['Verified', verified])
    list_filters.append(['Key word', key_word])
    list_filters.append(['Pass word', stop_word])
    if bool_time:
        list_filters.append(['Start time', start_time])
        list_filters.append(['End time', end_time])

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
    global list_filters
    _posts = get_all_posts(user_id)
    print('Len posts:', len(_posts))
    if _posts != list() and _posts != None:
        return render_template('result.html', user_id=user_id, posts=_posts, len_posts=len(_posts), page=page, range_posts=range(1, ((len(_posts) // 1000) + (2 if len(_posts) % 1000 != 0 else 1))), list_filters=list_filters)
    else:
        return redirect('/', code=302)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    print('run')
    app.run(host='0.0.0.0')
    # app.run(host='10.10.10.58', debug=False, port=5500)
    # app.run(host='localhost', debug=False, port=5500)