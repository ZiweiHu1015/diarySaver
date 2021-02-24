

from flask import Flask, render_template, flash, redirect, url_for, session,request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField,validators
from passlib.hash import sha256_crypt

# Mysql db file location
# /usr/local/mysql/data
# To see the db,
#   1) cd /usr/local/mysql
#   2) sudo ls -la data
'''
CREATE TABLE users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100), register_data TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
'''

app = Flask(__name__)

#config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


#init mysql
mysql = MySQL(app)

Articles = Articles()

app.debug = True

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id = id)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min = 1,max = 50)])
    username = StringField('Username', [validators.Length(min = 4, max = 25)])
    email = StringField('Email', [validators.Length(min = 6, max = 50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register',methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #Execute query
        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name,  email, username, password))

        #commit to DB
        mysql.connection.commit()

        #cloase connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form = form)

    # User login

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
    #Get Form Fields
        username = request.form('username')
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #get stored hash

            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
        else:
            error = 'Invalid login'
            return render_template('login.html', error = error)
        #Close connection
        cur.close()
    else:
        error = 'Username not found'
        return render_template('login.html', error = error)
            
    
    return render_template('login.html')


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()
