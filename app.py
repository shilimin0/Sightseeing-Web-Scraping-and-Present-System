from flask import Flask, flash, redirect, render_template, request, session, abort,url_for,g
import os
import sqlite3


DATABASE = 'test.db'

class User:
    def __init__ (self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    def __repr__(self):
        return f'<User: {self.username}>'
users = []
users.append(User(1,'admin','password'))


app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = "super secret key"

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])



@app.before_request
def before_request():
    if 'user_id' in session:
        user = [X for X in users if X.id == session['user_id']][0]
        g.user = user
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id',None)
        username = request.form['username']
        password = request.form['password']
        try:
            user = [x for x in users if x.username == username][0]
        except:
            return redirect((url_for('login')))
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect((url_for('profile')))
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/profile")
def profile():
    if not g.user:
        return redirect(url_for('login'))
    g.db = connect_db()
    views = ['lijiang', 'chengdu', 'lasa']
    datas = []
    for i in views:
        cur = g.db.execute('select sight, overal, rating, sight_price , hotel_price ,distance_price , sight_address from '+i)
        data1 = [dict(sight = row[0], overal = row[1], rating = row[2], sight_price = row[3] , hotel_price = row[4] ,distance_price=row[5] , sight_address = row[6]) for row in cur. fetchall()]
        datas.append(data1)
    g.db.close()
    return render_template('profile.html',data = datas)

@app.route("/lijiang")
def lijiang():
    if not g.user:
        return redirect(url_for('login'))
    g.db = connect_db()
    views = ['lijiang', 'chengdu', 'lasa']
    datas = []
    for i in views:
        cur = g.db.execute('select sight, overal, rating, sight_price , hotel_price ,distance_price , sight_address from '+i)
        data1 = [dict(sight = row[0], overal = row[1], rating = row[2], sight_price = row[3] , hotel_price = row[4] ,distance_price=row[5] , sight_address = row[6]) for row in cur. fetchall()]
        datas.append(data1)
    g.db.close()
    return render_template('lijiang.html',data = datas)

@app.route("/chengdu")
def chengdu():
    if not g.user:
        return redirect(url_for('login'))
    g.db = connect_db()
    views = ['lijiang', 'chengdu', 'lasa']
    datas = []
    for i in views:
        cur = g.db.execute('select sight, overal, rating, sight_price , hotel_price ,distance_price , sight_address from '+i)
        data1 = [dict(sight = row[0], overal = row[1], rating = row[2], sight_price = row[3] , hotel_price = row[4] ,distance_price=row[5] , sight_address = row[6]) for row in cur. fetchall()]
        datas.append(data1)
    g.db.close()
    return render_template('chengdu.html',data = datas)

@app.route("/lasa")
def lasa():
    if not g.user:
        return redirect(url_for('login'))
    g.db = connect_db()
    views = ['lijiang', 'chengdu', 'lasa']
    datas = []
    for i in views:
        cur = g.db.execute('select sight, overal, rating, sight_price , hotel_price ,distance_price , sight_address from '+i)
        data1 = [dict(sight = row[0], overal = row[1], rating = row[2], sight_price = row[3] , hotel_price = row[4] ,distance_price=row[5] , sight_address = row[6]) for row in cur. fetchall()]
        datas.append(data1)
    g.db.close()
    return render_template('lasa.html',data = datas)

if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1', port=5000)
