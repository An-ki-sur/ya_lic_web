import base64
import io
import os
from PIL import Image

import flask
import socketio
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, send_from_directory
import sqlite3
import random
from os import path
from datetime import date, datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
alf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

ROOT = path.dirname(path.realpath(__file__))

UPLOAD_FOLDER = 'static/images/avs'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
c = 0

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}



def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/updateLikes/<link>')
def suggestions(link, requests=None):
    con = sqlite3.connect(path.join(ROOT, "web_db.db"))
    cur = con.cursor()
    ppost = cur.execute(f'''SELECT * FROM posts where id = {link}''').fetchall()[0]

    return {f"like{link}": str(ppost[5]),
            f"com{link}": str(ppost[6]),
            f"date{link}": str(f'Дата публикации:{ppost[8]}'),
            f"rep{link}": str(ppost[7]),
            f"looks{link}": str(ppost[9])}




@app.route('/addLike/<post>')
def addLike(post):
    con = sqlite3.connect(path.join(ROOT, "web_db.db"))
    cur = con.cursor()
    ppost = cur.execute(f'''SELECT * FROM posts where id = {post}''').fetchall()[0]
    if ppost[10] and f"_{session['acc']}_" in ppost[10]:
        cur.execute(f'''update posts 
set like_users = "{''.join(ppost[10].split(f"_{session['acc']}_"))}", like = like - 1 where id = {post}''').fetchall()
        im = 'heart1.png'
        con.commit()
    else:
        if ppost[10]:
            cur.execute(f'''update posts 
            set like_users = "{ppost[10] + f"_{session['acc']}_"}", like = like + 1 where id = {post}''').fetchall()
        else:
            cur.execute(f'''update posts 
            set like_users = "{f"_{session['acc']}_"}", like = 1 where id = {post}''').fetchall()
        im = 'heart.png'
        con.commit()
    return {'img': im}

@app.template_filter(name='linebreaksbr')
def linebreaksbr_filter(text):
    return text.replace('\n', '<br>')


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if flask.request.method == 'POST':
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        session['name'] = request.form['name']

        if request.form['pas1']:
            if request.files['ava'].filename:
                file = request.files['ava']

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    f = sqlite3.Binary(open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb').read())



                    cur.execute(f"""
                    UPDATE user_info
                    SET ava = ?, name="{request.form['name']}",pass="{request.form['pas1']}" where id = {session['acc']}
                    """, (f,))
                    con.commit()
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    session['ava'] = True
                    return redirect('main')
            else:
                cur.execute(f"""
                UPDATE user_info
                SET name="{request.form['name']}" ,pass="{request.form['pas1']}" where id = {session['acc']}
                """)

                con.commit()
        else:
            if request.files['ava'].filename:
                file = request.files['ava']

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    f = sqlite3.Binary(open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb').read())

                    cur.execute(f"""
                    UPDATE user_info
                    SET ava = ?, name="{request.form['name']}" where id = {session['acc']}
                    """, (f,))
                    con.commit()
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    session['ava'] = True
                    return redirect('main')
            else:
                cur.execute(f"""
                UPDATE user_info
                SET name="{request.form['name']}"  where id = {session['acc']}
                """)
                con.commit()
        return redirect('main')
    else:
        if "acc" in session and session['acc'] != "-1":
            con = sqlite3.connect(path.join(ROOT, "web_db.db"))
            cur = con.cursor()
            me = io.BytesIO(
            cur.execute(f'''SELECT ava FROM user_info where id = {session["acc"]}''').fetchall()[0][0])
            im = Image.open(me)
            data = io.BytesIO()
            im.save(data, "JPEG")
            encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')
            return render_template('Settings.html', link = session['link'], name=session['name'], im = encoded_img_data)


@app.route('/')
@app.route('/main')
def main():
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        name = session["name"]
        link = session["link"]

        me = io.BytesIO(cur.execute(f'''SELECT ava FROM user_info where id = {session["acc"]}''').fetchall()[0][0])
        im = Image.open(me)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')



        ppost = cur.execute('''SELECT * FROM posts ORDER BY random() LIMIT 10''').fetchall()
        post_list = []
        s = '\n'
        posts_segment = ''
        c = 0
        for r_post in ppost:
            post_list.append(r_post[0])
            post_author = \
                cur.execute(f'''SELECT name, link_to_user, ava FROM user_info WHERE id = {r_post[3]}''').fetchall()[0]


            if r_post[10] and f'_{session["acc"]}_' in r_post[10]:
                like_pic = "heart.png"
            else:
                like_pic = "heart1.png"

            cur.execute(f'''
            update posts
            set looks = looks + 1, look_users = look_users || "_{session['acc']}_"
            where not( look_users like "%_{session['acc']}_%") and id={r_post[0]}''')
            con.commit()


            # if post_author[2]:
            #     file_object = io.BytesIO()
            #     img = Image.fromarray(post_author[2].astype('uint8'))
            #     img.save(file_object, 'PNG')
            #     base64img = "data:image/png;base64," + base64.b64encode(file_object.getvalue()).decode('ascii')
            # else:
            #     file_object = io.BytesIO()
            #     f = open('static/images/headshot.jpg', 'rb').read()
            #     img = Image.fromarray(f.astype('uint8'))
            #     img.save(file_object, 'PNG')
            #     base64img = "data:image/png;base64," + base64.b64encode(file_object.getvalue()).decode('ascii')


            me = io.BytesIO(post_author[2])
            im = Image.open(me)
            data = io.BytesIO()
            im.save(data, "JPEG")
            encoded_img_data_author = base64.b64encode(data.getvalue()).decode('utf-8')



            posts_segment += f'''
            <div class="u-container-style u-gradient u-group u-radius-36 u-shape-round u-group-1">
          <div class="u-container-layout u-container-layout-1">
              
            <img class="u-image u-image-circle u-preserve-proportions u-image-1" src="data:image/jpeg;base64,{encoded_img_data_author}" alt="" data-image-width="5000" data-image-height="5000">
            <h5 class="u-custom-font u-font-lobster u-text u-text-default u-text-2"><a href = /user/{post_author[1]}>{post_author[0]}</a></h5>
            <div class="u-border-3 u-border-grey-dark-1 u-expanded-width u-line u-line-horizontal u-line-1"></div>
            <h4 class="u-align-center u-custom-font u-font-lobster u-text u-text-3"><a href = /post/{r_post[4]}>{r_post[1]}</a></h4>
            <p class="u-text u-text-4"> 
            {'<br>'.join(r_post[2].split(s))}
            </p>
            <div class="u-border-3 u-border-grey-dark-1 u-expanded-width u-line u-line-horizontal u-line-2"></div>
            <a onclick="liked({r_post[0]});" class="u-border-none u-btn u-button-style u-none u-btn-1"><span class="u-file-icon u-icon u-icon-1"><img id="likepic{r_post[0]}" src="/static/images/{like_pic}" alt=""></span>
            </a>
            <a href = /post/{r_post[4]} class="u-border-none u-btn u-button-style u-none u-btn-2"><span class="u-file-icon u-icon u-icon-2"><img src="/static/images/7783038.png" alt=""></span>&nbsp;
            </a>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-3"><span class="u-file-icon u-icon u-text-palette-4-dark-1 u-icon-3"><img src="/static/images/2340321-9133d62e.png" alt=""></span>&nbsp;
            </a>
            <p id="com{r_post[0]}" class="u-custom-font u-font-lobster u-text u-text-5">{r_post[6]}</p>
            <p id="date{r_post[0]}" class="u-custom-font u-font-lobster u-text u-text-6">Дата публикации:{r_post[8]}</p>
            <p id="like{r_post[0]}" class="u-custom-font u-font-lobster u-text u-text-7">{r_post[5]}</p>
            <p id="rep{r_post[0]}" class="u-custom-font u-font-lobster u-text u-text-8">{r_post[7]}</p><span class="u-file-icon u-icon u-icon-4"><img src="/static/images/829117.png" alt=""></span>
            <p id="looks{r_post[0]}" class="u-custom-font u-font-lobster u-text u-text-9">{r_post[9]}</p>
            <br>
          </div>
        </div>
            '''

        con.close()
        return render_template('MainWithReg.html', name=name, link=link, post=posts_segment, post_list=post_list, im=encoded_img_data, encoded_img_data_author = encoded_img_data_author)
    else:
        return render_template('MainWithoutReg.html')


@app.route('/exit')
def exit():
    session['acc'] = '-1'
    return redirect(url_for('main'))


@app.route('/log', methods=['POST', 'GET'])
def login():
    print(flask.request.method)
    con = sqlite3.connect(path.join(ROOT, "web_db.db"))
    if flask.request.method == 'POST':
        cur = con.cursor()
        login = flask.request.form['log']
        pas = flask.request.form['pass']

        acc = cur.execute(f'''SELECT * FROM user_info WHERE login = "{login}" AND pass = "{pas}"''').fetchall()
        if acc:
            session['acc'] = str(acc[0][0])
            session['name'] = str(acc[0][4])
            session['link'] = str(acc[0][3])
            if acc[0][5] != None:
                session['ava'] = True
            else:
                session['ava'] = False

            return redirect(url_for('main'))
        else:
            return "error"

    else:
        return render_template('login.html')


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    print(flask.request.form)
    con = sqlite3.connect(path.join(ROOT, "web_db.db"))
    if flask.request.method == 'POST':
        cur = con.cursor()
        name = flask.request.form['name']
        login = flask.request.form['log']
        pas = flask.request.form['pass']

        acc = cur.execute(f'''SELECT * FROM user_info WHERE login = "{login}" or name = "{name}"''').fetchall()

        if acc and acc[0][1] == login:
            return '''<a href = /reg> Логин занят </a>'''
        elif acc and acc[0][4] == name:
            return '''<a href = /reg> Имя занято </a>'''
        else:
            if len(pas) >= 8:
                while True:
                    link = ''.join(random.sample(alf, len(alf)))
                    flag = cur.execute(f'select * from user_info where link_to_user = "{link}"').fetchall()
                    if not flag:
                        break

                f = sqlite3.Binary(open(os.path.join(app.config['UPLOAD_FOLDER'], 'headshot.jpg'), 'rb').read())
                cur.execute(
                    f"INSERT INTO user_info (login, pass, link_to_user, name, ava) values ('{login}', '{pas}', '{link}', '{name}', ?)", (f, )).fetchall()
                con.commit()
                return '<a href = /log> Регистрация успешна! Теперь войдите в аккаунт </a>'
            else:
                return '''<a href = /reg> В пароле должно быть не менее 8 символов </a>'''

    else:
        return render_template('reg.html')


@app.route('/del/<postname>')
def delete_post(postname):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        post = cur.execute(f'select author from posts where post_link = "{postname}"').fetchall()[0]
        print(session['acc'], str(post[0]))
        if session['acc'] == str(post[0]):
            cur.execute(f'''DELETE FROM posts where post_link = "{postname}"''').fetchall()
            con.commit()
            print(session['link'])
            return redirect(url_for(f"profile", username=session['link']))
    return '<a href = /main>Вы не имеете права доступа к этому действию<a>'


@app.route('/user/<username>')
def profile(username):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        u_id = cur.execute(f'select id, name, ava from user_info where link_to_user = "{username}"').fetchall()[0]

        me = io.BytesIO(
            u_id[2])
        im = Image.open(me)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')

        me = io.BytesIO(
            cur.execute(f'''SELECT ava FROM user_info where id = {session["acc"]}''').fetchall()[0][0])
        im = Image.open(me)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data1 = base64.b64encode(data.getvalue()).decode('utf-8')

        if u_id[0]:
            posts = cur.execute(f'''select * from posts where author = {u_id[0]}''').fetchall()
            if "acc" in session and session['acc'] != "-1":
                name = session["name"]
                link = session["link"]
                ul = ''
                pp = []
                for i in range(len(posts)):
                    pp.append(posts[i][0])
                    if (session['acc'] == str(u_id[0])):

                        if posts[i][10] and f'_{session["acc"]}_' in posts[i][10]:
                            like_pic = "heart.png"
                        else:
                            like_pic = "heart1.png"
                        ul += f'''
                        <div class="u-container-style u-expanded-width-lg u-expanded-width-md u-expanded-width-sm u-expanded-width-xs u-gradient u-group u-radius-36 u-shape-round u-group-1">
                      <div class="u-container-layout u-container-layout-1">
                        <h4 class="u-custom-font u-font-lobster u-text u-text-2"><a href = /post/{posts[i][4]}>{posts[i][1]}</a></h4>
                        <a href=/new_post/{posts[i][4]} class="u-border-none u-btn u-button-style u-none u-btn-1"><span class="u-file-icon u-icon u-text-palette-1-dark-1 u-icon-1"><img src="/static/images/66761-5ae31591.png" alt=""></span>&nbsp;
                        </a>
                        <a href="/del/{posts[i][4]}" class="u-border-none u-btn u-button-style u-none u-btn-2"><span class="u-file-icon u-icon u-text-palette-2-base u-icon-2"><img src="/static/images/3156999-3d0dddf3.png" alt=""></span>&nbsp;
                        </a>
                        <p id="rep{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-3">{posts[i][7]}</p><span class="u-file-icon u-icon u-icon-3"><img src="/static/images/829117.png" alt=""></span>
                        
<a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-3"> &nbsp;</a>
                        <p id="like{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-4">{posts[i][5]}</p>
                        <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-4"> &nbsp;</a>
                        <p id="com{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-5">{posts[i][6]}</p>
                        <p id="looks{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-6">{posts[i][9]}</p>
                        <p  id="date{posts[i][0]}" class="u-custom-font u-font-lobster u-text u-text-7">Дата публикации:{posts[i][8]}</p>
                        <br>
                        <a href="https://nicepage.com/c/sale-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-5"></a>
                        <a onclick="liked({posts[i][0]});" class="u-border-none u-btn u-button-style u-none u-btn-6"><span  class="u-file-icon u-icon u-icon-4"><img id="likepic{posts[i][0]}" src="/static/images/{like_pic}" alt=""></span>
                        </a>
                        <a href = /post/{posts[i][4]} class="u-border-none u-btn u-button-style u-none u-btn-7"><span class="u-file-icon u-icon u-icon-5"><img src="/static/images/7783038.png" alt=""></span>&nbsp;
                        </a>
                        <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-8"><span class="u-file-icon u-icon u-text-palette-4-dark-1 u-icon-6"><img src="/static/images/2340321-9133d62e.png" alt=""></span>&nbsp;
                        </a>
                      </div>
                    </div>'''


                    else:
                        if posts[i][10] and f'_{session["acc"]}_' in posts[i][10]:
                            like_pic = "heart.png"
                        else:
                            like_pic = "heart1.png"

                        ul += f'''<div class="u-container-style u-expanded-width-lg u-expanded-width-md u-expanded-width-sm u-expanded-width-xs u-gradient u-group u-radius-36 u-shape-round u-group-1">
          <div class="u-container-layout u-container-layout-1">
            <h4 class="u-custom-font u-font-lobster u-text u-text-2"><a href = /post/{posts[i][4]}>{posts[i][1]}</a></h4>
            <a class="u-border-none u-btn u-button-style u-none u-btn-3"><span class="u-file-icon u-icon u-opacity u-opacity-0 u-text-palette-1-dark-1 u-icon-1"><img  alt=""></span>&nbsp;
            </a>
            <a class="u-border-none u-btn u-button-style u-none u-btn-4"><span class="u-file-icon u-icon u-opacity u-opacity-0 u-text-palette-2-base u-icon-2"><img  alt=""></span>&nbsp;
            </a>                        
            
          <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-5"> &nbsp;</a>
          <p id="rep{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-3">{posts[i][7]}</p><span class="u-file-icon u-icon u-icon-3"><img src="/static/images/829117.png" alt=""></span>
<a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-5"> &nbsp;</a>
            <p id="like{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-4">{posts[i][5]}</p>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-6"> &nbsp;</a>
            <p id="com{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-5">{posts[i][6]}</p>
            <p id="looks{posts[i][0]}" class="u-align-center-sm u-align-center-xs u-custom-font u-font-lobster u-text u-text-6">{posts[i][9]}</p>
           <p  id="date{posts[i][0]}" class="u-custom-font u-font-lobster u-text u-text-7">Дата публикации:{posts[i][8]}</p>
           <br>
            <a href="https://nicepage.com/c/sale-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-7"></a>
            <a onclick="liked({posts[i][0]});" class="u-border-none u-btn u-button-style u-none u-btn-8"><span class="u-file-icon u-icon u-icon-4"><img id="likepic{posts[i][0]}" src="/static/images/{like_pic}" alt=""></span>
            </a>
            <a href = /post/{posts[i][4]} class="u-border-none u-btn u-button-style u-none u-btn-9"><span class="u-file-icon u-icon u-icon-5"><img src="/static/images/7783038.png" alt=""></span>&nbsp;
            </a>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-10"><span class="u-file-icon u-icon u-text-palette-4-dark-1 u-icon-6"><img src="/static/images/2340321-9133d62e.png" alt=""></span>&nbsp;
            </a>
          </div>
        </div>'''




                if (session['acc'] == str(u_id[0])):
                    return render_template('MyProfile.html', name=name, link=link, post_list=ul, author_name=u_id[1],
                                           pp=pp, im=encoded_img_data)
                else:
                    return render_template('OtherProfile.html', name=name, link=link, post_list=ul, author_name=u_id[1],
                                           pp=pp, im1=encoded_img_data, im2=encoded_img_data1)
            else:
                return '<a href = "/log">Войдите в аккаунт</a>'
        else:
            return "404 error"
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''


@app.route('/new_post/<link_st>', methods=['POST', 'GET'])
def new_post(link_st):
        if "acc" in session and session['acc'] != "-1":
            current_date = datetime.now()
            date1 = current_date.strftime('%d.%m.%Y')

            con = sqlite3.connect(path.join(ROOT, "web_db.db"))
            cur = con.cursor()
            if flask.request.method == 'POST':
                if link_st == 'new':

                    if flask.request.form['post_name'] and flask.request.form['text']:
                        while True:
                            link = ''.join(random.sample(alf, len(alf)))
                            flag = cur.execute(f'select * from posts where post_link = "{link}"').fetchall()
                            if not flag:
                                break
                        cur.execute(
                            f'''INSERT INTO posts(title, text, author, post_link, like, coments, rep, data, looks) values ('{flask.request.form['post_name']}', '{flask.request.form['text']}', {session['acc']}, '{link}', 0, 0, 0, "{date1}", 0)''')
                        con.commit()
                        return redirect(url_for(f"profile", username=session['link']))
                    else:
                        return "<a href=/new_post>Не оставляйте поля пустыми</a>"
                else:
                    if flask.request.form['post_name'] and flask.request.form['text']:
                        cur.execute(f'''
                        update posts 
                        set title = '{flask.request.form['post_name']}', text='{flask.request.form['text']}' where post_link = "{link_st}"''')
                        con.commit()
                        return redirect(url_for('profile', username=session['link']))
            else:
                if link_st == 'new':
                    if "acc" in session and session['acc'] != "-1":
                        name = session["name"]
                        link = session["link"]

                        u_id = cur.execute(
                            f'select id, name, ava from user_info where link_to_user = "{session["link"]}"').fetchall()[
                            0]
                        me = io.BytesIO(u_id[2])
                        im = Image.open(me)
                        data = io.BytesIO()
                        im.save(data, "JPEG")
                        encoded_img_data1 = base64.b64encode(data.getvalue()).decode('utf-8')
                        text = ''
                        post_name = ''


                        return render_template('EditPost.html', link_st=link_st, name=name, link=link,
                                               image=encoded_img_data1, text=text, post_name=post_name, title='Новый пост')
                    return "error"
                else:
                    if "acc" in session and session['acc'] != "-1":
                        name = session["name"]
                        link = session["link"]

                        u_id = cur.execute(
                            f'select id, name, ava from user_info where link_to_user = "{session["link"]}"').fetchall()[
                            0]

                        me = io.BytesIO(u_id[2])
                        im = Image.open(me)
                        data = io.BytesIO()
                        im.save(data, "JPEG")
                        encoded_img_data1 = base64.b64encode(data.getvalue()).decode('utf-8')

                        post = cur.execute(f'''
                        SELECT * FROM posts where post_link="{link_st}"''').fetchall()[0]




                        text = post[2]
                        post_name = post[1]

                        return render_template('EditPost.html', link_st=link_st, name=name, link=link,
                                               image=encoded_img_data1, text=text, post_name=post_name, title='Изменить')
        else:
            return '''<a href = "/log">Войдите в аккаунт<br></a>
        <a href = "/reg">Зарегистрироваться</a>'''


@app.route('/add_com/<post_link>/<comment>', methods=['POST', 'GET'])
def add_com(post_link, comment):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        post = cur.execute(f'select * from posts where post_link = "{post_link}"').fetchall()
        if post:
            if flask.request.method == 'POST':
                if comment == 'new':
                    if flask.request.form['comment']:
                        cur.execute(
                            f'''INSERT INTO comments (commetator, text, post) VALUES ({session["acc"]}, '{flask.request.form['comment']}', {post[0][0]})''').fetchall()
                        cur.execute(f'''update posts set coments = coments + 1 where post_link = "{post_link}"''')
                        con.commit()

                        return redirect(url_for('post_stran', post_link=post_link))


                    else:
                        return f"<a href = /add_com/{post_link}> Надо что-то написать </a>"
                else:

                    cur.execute(f'''
                    update comments 
                    set text = "{flask.request.form['comment']}" where id = {comment}''')
                    con.commit()
                    return redirect(url_for('post_stran', post_link=post_link))

            else:

                u_id = cur.execute(f'select id, name, ava from user_info where link_to_user = "{session["link"]}"').fetchall()[0]
                me = io.BytesIO(u_id[2])
                im = Image.open(me)
                data = io.BytesIO()
                im.save(data, "JPEG")
                encoded_img_data1 = base64.b64encode(data.getvalue()).decode('utf-8')

                name = session["name"]
                link = session["link"]
                if comment == 'new':
                    return render_template('EditComm.html', name=name, link=link, post_link=post_link, image=encoded_img_data1, state=comment, title='Новый коментарий')

                com = cur.execute(f'''
                Select * from comments where id = {comment}''').fetchall()[0]
                return render_template('EditComm.html', name=name, link=link, post_link=post_link,
                                       image=encoded_img_data1, state=comment, com=com[2], title='Изменить коментарий')
        else:
            return f"<a href = /main> 404 </a>"
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''


@app.route('/del_comment/<comment>/<post>')
def del_comment(comment, post):
    con = sqlite3.connect(path.join(ROOT, "web_db.db"))
    cur = con.cursor()
    com = cur.execute(f'''
    select * from comments where id = {comment}''').fetchall()[0]
    if str(com[1]) == session['acc']:
        cur.execute(f'''DELETE FROM comments where id = {comment}''')
        cur.execute(f'''update posts set coments = coments - 1 where post_link = "{post}"''')
        con.commit()
    return redirect(url_for('post_stran', post_link = post))



@app.route('/post/<post_link>')
def post_stran(post_link):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))




        cur = con.cursor()

        cur.execute(f'''
        update posts
        set looks = looks + 1, look_users = look_users || "_{session['acc']}_"
        where not( look_users like "%_{session['acc']}_%") and post_link="{post_link}"''')

        con.commit()





        post = cur.execute(f'select * from posts where post_link = "{post_link}"').fetchall()


        u_id = cur.execute(f'select id, name, ava from user_info where link_to_user = "{session["link"]}"').fetchall()[0]
        me = io.BytesIO(
            u_id[2])
        im = Image.open(me)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')


        



        if post:
            if post[0][10] and f'_{session["acc"]}_' in post[0][10]:
                like_pic = "heart.png"
            else:
                like_pic = "heart1.png"

            name = session["name"]
            link = session["link"]
            post = post[0]
            comments = cur.execute(f'select * from comments where post = {post[0]}').fetchall()
            ul = []
            comT = ''
            for i in range(len(comments)):
                ul.append({})
                user = cur.execute(f'select name, link_to_user, ava, id from user_info where id = {comments[i][1]}').fetchall()[
                    0]
                ul[i]['name'] = user[0]
                ul[i]['link'] = user[1]
                ul[i]['text'] = comments[i][2]

                me = io.BytesIO(user[2])
                im = Image.open(me)
                data = io.BytesIO()
                im.save(data, "JPEG")
                encoded_img_data1 = base64.b64encode(data.getvalue()).decode('utf-8')

                dl = "\n"
                if str(user[3]) != str(session['acc']):
                    comT += f'''
<div class="u-container-style u-gradient u-group u-radius-36 u-shape-round u-group-3">
          <div class="u-container-layout u-container-layout-3">
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-9"> &nbsp;</a>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-10"> &nbsp;</a>
            <h5 class="u-custom-font u-font-lobster u-text u-text-default-lg u-text-default-md u-text-default-sm u-text-default-xl u-text-11"><a href=/user/{user[1]}>{user[0]}</a></h5>
            <img class="u-image u-image-circle u-preserve-proportions u-image-3" src="data:image/jpeg;base64,{encoded_img_data1}" alt="" data-image-width="5000" data-image-height="5000">
            <div class="u-border-2 u-border-grey-dark-1 u-gradient u-opacity u-opacity-0 u-shape u-shape-rectangle u-shape-2"></div>
            <a href="https://nicepage.com/html-templates" class="u-border-none u-btn u-button-style u-none u-btn-11"> &nbsp;</a>
            <div class="u-border-3 u-border-grey-dark-1 u-expanded-width u-line u-line-horizontal u-line-4"></div>
            <a href="https://nicepage.com/c/sale-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-12"></a>
            <a href="https://nicepage.com/html-templates" class="u-border-none u-btn u-button-style u-none u-btn-13"> &nbsp;</a>
            <p class="u-text u-text-12">{'<br>'.join(comments[i][2].split(dl))}<br>
            </p>
          </div>
        </div> '''
                else:
                    comT += f'''


        <div class="u-container-style u-gradient u-group u-radius-36 u-shape-round u-group-2">
          <div class="u-container-layout u-container-layout-2">
            <img class="u-image u-image-circle u-preserve-proportions u-image-2" src="data:image/jpeg;base64,{encoded_img_data1}" alt="" data-image-width="5000" data-image-height="5000">
            <h5 class="u-custom-font u-font-lobster u-text u-text-default-lg u-text-default-md u-text-default-sm u-text-default-xl u-text-9"><a href=/user/{user[1]}>{user[0]}</a></h5>
            <div class="u-border-3 u-border-grey-dark-1 u-expanded-width u-line u-line-horizontal u-line-3"></div>
            <a href="https://nicepage.com/c/sale-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-4"></a>
            <a href=/add_com/{post_link}/{comments[i][0]} class="u-border-none u-btn u-button-style u-none u-btn-5"><span class="u-file-icon u-icon u-text-palette-1-dark-1 u-icon-4"><img src="/static/images/66761-5ae31591.png" alt=""></span>&nbsp;
            </a>
            <a href=/del_comment/{comments[i][0]}/{post_link} class="u-border-none u-btn u-button-style u-none u-btn-6"><span class="u-file-icon u-icon u-text-palette-2-base u-icon-5"><img src="/static/images/3156999-3d0dddf3.png" alt=""></span>&nbsp;
            </a>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-7"> &nbsp;</a>
            <a href="https://nicepage.com/k/awards-website-templates" class="u-border-none u-btn u-button-style u-none u-btn-8"> &nbsp;</a>
            <p class="u-text u-text-10">{'<br>'.join(comments[i][2].split(dl))}<br>
            </p>
            <div class="u-border-2 u-border-grey-dark-1 u-gradient u-opacity u-opacity-0 u-shape u-shape-rectangle u-shape-1"></div>
          </div>
        </div>
'''







            print(ul)
            author = cur.execute(f'select name, link_to_user from user_info where id={post[3]}').fetchall()[0]
            return render_template('post.html', name=name, link=link, im=encoded_img_data,
                                   like_pic=like_pic, post={'name': post[1], 'text': post[2], 'author': author[0],
                                         'author_link': author[1], 'post_link': post_link, 'id': post[0]}, com=ul, comT=comT)
        else:
            return '<a href = "/main">Такого поста не существует</a>'
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''

