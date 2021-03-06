from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

mysql = MySQL()
app = Flask(__name__)
app.debug = True

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'marie'
app.config['MYSQL_DATABASE_PASSWORD'] = 'marikiki9283'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def signUp():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            _hashed_password = generate_password_hash(_password, method='pbkdf2:sha256', salt_length=16)

            cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message': 'User created successfully !'})
            else:
                return json.dumps({'error': str(data[0])})
        else:
            return json.dumps({'html': '<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():

    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
 
        # connect to mysql
 
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
 
        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                return json.dumps({'error1': str(data[0])})
                # return redirect('/userHome')
            else:
                return json.dumps({'error2': str(data[0])})
                # return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return json.dumps({'error3': str(data[0])})
            # return render_template('error.html',error = 'Wrong Email address or Password.')
 
 
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()








if __name__ == "__main__":
    app.run()