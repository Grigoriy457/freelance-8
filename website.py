from flask import *
import time
from vk_parser import parser

app = Flask(__name__)
posts = list()

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/load', methods=['GET', "POST"])
def load():
    global posts
    print('/load')
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
                if start_time == '' or end_time == '':
                    return redirect('/', code=302)
            else:
                if limit > 1000:
                    return redirect('/', code=302)
            posts = parser(limit=limit, likes=likes, subscribers=subscribers, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).parser_function()
            return redirect('/result/1', code=302)
        else:
            return redirect('/', code=302)
    else:
        return redirect('/', code=302)

@app.route('/result/<int:page>')
def int_result(page):
    if posts != list():
        return render_template('result.html', posts=posts, page=page, range_posts=range(1, ((len(posts) // 1000) + (2 if len(posts) % 1000 != 0 else 1))))
    else:
        return redirect('/', code=302)

@app.route('/result/<int:page>')
def result():
    return redirect('/', code=302)

if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    print('run')
    # app.run(host='10.10.10.58', debug=False, port=5500)
    app.run(host='created-by-vlasov-grigoriy.tk', debug=False)
