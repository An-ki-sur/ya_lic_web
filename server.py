import flask
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
import sqlite3
import random
from os import path

app = Flask(__name__)
alf = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'


ROOT = path.dirname(path.realpath(__file__))

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@app.route('/')
@app.route('/main')
def main():
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        name = session["name"]
        link = session["link"]
        r_post = cur.execute('''SELECT * FROM posts ORDER BY random() LIMIT 1''').fetchall()[0]
        post_author = cur.execute(f'''SELECT name, link_to_user FROM user_info WHERE id = {r_post[3]}''').fetchall()[0]
        con.close()
        print(r_post)

        post = {'name' : r_post[1], "text" : r_post[2], 'author_link' : post_author[1], 'author' : post_author[0], 'post_link': r_post[4]}

        return render_template('main.html', name=name, link=link, post=post)
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
<a href = "/reg">Зарегистрироваться</a>'''


@app.route('/exit')
def exit():
    session['acc'] = '-1'
    return redirect(url_for('main'))


@app.route('/log', methods=['POST','GET'])
def login():
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

                return redirect(url_for('main'))
            else:
                return "error"

        else:
            return render_template('login.html')


@app.route('/reg', methods=['POST','GET'])
def reg():
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
                    cur.execute(f'INSERT INTO user_info (login, pass, link_to_user, name) values ("{login}", "{pas}", "{link}", "{name}")').fetchall()
                    con.commit()
                    return '<a href = /log> Регистрация успешна! Теперь войдите в аккаунт </a>'
                else:
                    return '''<a href = /reg> В пароле должно быть не менее 8 символов </a>'''

        else:
            return render_template('reg.html')
@app.route('/user/<username>')
def profile(username):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        u_id = cur.execute(f'select id, name from user_info where link_to_user = "{username}"').fetchall()[0]
        if u_id[0]:
            posts = cur.execute(f'''select * from posts where author = {u_id[0]}''').fetchall()
            if "acc" in session and session['acc'] != "-1":
                name = session["name"]
                link = session["link"]
                ul = []
                for i in range(len(posts)):
                    ul.append({})
                    ul[i]['name'] = posts[i][1]
                    ul[i]['link'] = posts[i][4]
                return render_template('profile.html', name=name, link=link, post_list=ul, author_name=u_id[1])
            else:
                return '<a href = "/log">Войдите в аккаунт</a>'
        else:
            return "404 error"
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''


@app.route('/new_post', methods=['POST','GET'])
def new_post():
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        if flask.request.method == 'POST':
            if flask.request.form['post_name'] and flask.request.form['text']:
                while True:
                    link = ''.join(random.sample(alf, len(alf)))
                    flag = cur.execute(f'select * from posts where post_link = "{link}"').fetchall()
                    if not flag:
                        break
                cur.execute(f'''INSERT INTO posts(title, text, author, post_link) values ("{flask.request.form['post_name']}", "{flask.request.form['text']}", {session['acc']}, "{link}")''')
                con.commit()
                return '<a href=/main>Пост создан! Вернуться на главную</a>'
            else:
                return "<a href=/new_post>Не оставляйте поля пустыми</a>"
        else:
            if "acc" in session and session['acc'] != "-1":
                name = session["name"]
                link = session["link"]
                return render_template('new_post.html', name=name, link=link)
            return "error"
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''


@app.route('/add_com/<post_link>', methods=['POST','GET'])
def add_com(post_link):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))
        cur = con.cursor()
        post = cur.execute(f'select * from posts where post_link = "{post_link}"').fetchall()
        if post:
            if flask.request.method == 'POST':
                if flask.request.form['comment']:
                    cur.execute(f'''INSERT INTO comments (commetator, text, post) VALUES ({session["acc"]}, "{flask.request.form['comment']}", {post[0][0]})''').fetchall()
                    con.commit()

                    return f"""<p>Вы добавили коммент <a href=/post/{post_link}>вернуться к посту</a></p>
        """
                else:
                    return f"<a href = /add_com/{post_link}> Надо что-то написать </a>"

            else:
                name = session["name"]
                link = session["link"]
                return render_template('add_com.html', name=name, link=link, post_link=post_link)
        else:
            return f"<a href = /main> 404 </a>"
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''
@app.route('/post/<post_link>')
def post_stran(post_link):
    if "acc" in session and session['acc'] != "-1":
        con = sqlite3.connect(path.join(ROOT, "web_db.db"))

        cur = con.cursor()
        post = cur.execute(f'select * from posts where post_link = "{post_link}"').fetchall()
        if post:
            name = session["name"]
            link = session["link"]
            post = post[0]
            comments = cur.execute(f'select * from comments where post = {post[0]}').fetchall()
            ul = []
            for i in range(len(comments)):
                ul.append({})
                user = cur.execute(f'select name, link_to_user from user_info where id = {comments[i][1]}').fetchall()[0]
                ul[i]['name'] = user[0]
                ul[i]['link'] = user[1]
                ul[i]['text'] = comments[i][2]
            print(ul)
            author = cur.execute(f'select name, link_to_user from user_info where id={post[3]}').fetchall()[0]
            return render_template('post.html', name=name, link=link, post={'name': post[1], 'text': post[2], 'author': author[0], 'author_link': author[1], 'post_link': post_link}, com=ul)
        else:
            return '<a href = "/main">Такого поста не существует</a>'
    else:
        return '''<a href = "/log">Войдите в аккаунт<br></a>
    <a href = "/reg">Зарегистрироваться</a>'''