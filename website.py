from flask import *
import time
from vk_parser import parser, starter
import sqlite3

app = Flask(__name__)
posts = list()

connection = sqlite3.connect('db.db', check_same_thread=False)
cursor = connection.cursor()

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/load', methods=['GET', "POST"])
def load():
    global _posts, cursor, connection, list_img
    print('/load')
    # if 
    if request.method == 'POST':
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
            else:
                if limit > 1000:
                    return redirect('/', code=302)
            starter(limit=limit, likes=likes, subscribers=subscribers, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).starter_function()

            time.sleep(2)

            _time = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_time',)).fetchone()[0]
            now_post = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_post',)).fetchone()[0]
            all_post = cursor.execute("""SELECT status FROM params WHERE info = ?""", ('parser_all_posts',)).fetchone()[0]
            return render_template('load.html', time=_time, now_post=now_post, all_post=all_post)
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
            cursor.execute("""SELECT * FROM posts""")
            posts = cursor.fetchall()
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
                # print(list_img, type(list_img))
                _posts.append((i[0], i[1], i[2], i[3], i[4], i[5], list_img, i[7]))
            return redirect('/result/1', code=302)

@app.route('/result/<int:page>')
def int_result(page):
    if _posts != list() and _posts != None:
        return render_template('result.html', posts=_posts, page=page, range_posts=range(1, ((len(_posts) // 1000) + (2 if len(_posts) % 1000 != 0 else 1))))
    else:
        return redirect('/', code=302)

@app.route('/result/<int:page>')
def result():
    return redirect('/', code=302)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    print('run')
    app.run()
    # app.run(host='10.10.10.58', debug=False, port=5500)
    # app.run(host='localhost', debug=False, port=5500)
