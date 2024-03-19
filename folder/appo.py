from flask import Flask, render_template, request, redirect, url_for,session
import json

import mysql.connector
import os
from datetime import datetime,timedelta
import jwt
from flask_jwt_extended import  JWTManager, jwt_required , create_access_token
app = Flask(__name__)


app.config['SECRET_KEY'] = 'secret'

db = mysql.connector.connect(
    host="localhost",
    user="sriyansh",
    password="Sriyansh@28",
    database="Users"
)
cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255))")

jwt = JWTManager(app)

def generate_jwt_token(user_id):
    # token = jwt.encode({'user_id': user_id}, app.config['JWT_SECRET_KEY'])
    token = create_access_token(identity=user_id)
    return token


@app.route('/home.html')
@jwt_required()
def home():
    # JWT token is verified, user is authenticated
    return render_template('home.html')


def find_user_details(user_id):
    cursor.execute("SELECT * FROM users WHERE username = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return {'username': user_data[1], 'email': user_data[2], 'password': user_data[3]}
    return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

@app.route('/user/<user_id>')
def user_details(user_id):
    user_data = find_user_details(user_id)
    if user_data:
        return render_template('b.html', user=user_data)
    else:
        return f"User with ID {user_id} not found."

# @app.route('/success')
# def success():
#     return 'posted successfully'

# @app.route('/')
# def welcome():
#     # return render_template('Login.html')
#     return render_template('Login.html')


# @app.route('/signup', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#         hashed_password = hash_password(password)
        
#         try:
#             cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
#                            (username, email, hashed_password))
#             db.commit()
#             return redirect(url_for('success'))
#         except mysql.connector.IntegrityError as e:
#             return "User with this email already exists. Please use a different email."
#     return render_template('SignUp.html')


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         cursor.execute("SELECT * FROM users WHERE usenrame = %s", username)
#         user_data = cursor.fetchone()

#         if user_data:
#             stored_password = user_data[3]
#             if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
#                 session['user_id'] = user_data[0] 
#                 # Generate JWT token and store it in session
#                 jwt_token = generate_jwt_token(user_data[0])
#                 session['jwt_token'] = jwt_token
#                 return render_template('intro.html')
#             else:
#                 return "Invalid email or password. Please try again."
#         else:
#             return "Invalid email or password. Please try again."

#     return render_template('Login.html')



@app.route('/' , methods=['GET','POST'])
def are_you_logged_in():
    if not session.get('logged_in'):
        return render_template('Login.html')
    else:
        return redirect(url_for('homee'))
    
@app.route('/home')
def homee():
    return render_template('intro.html')





@app.route('/login' ,  methods=['POST','GET'])
def login():
    if request.method == 'POST':
            
            # stay_logged_in = data.get('stay_logged_in')
            # permanent_session = stay_logged_in == 'true'

            username = request.form.get('username')
            password = request.form.get('password')
            if password=='123':                                  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ATTENTION:CHANGE THIS!!!!!!!!!!!!!!!!!!!!!!!!!
                session['logged_in'] = True

                token = jwt.encode(
                    {
                        'user': username,
                        'expiration': str(datetime.utcnow()+timedelta(seconds=20))
                    },
                    app.config['SECRET_KEY']
                )

            return render_template()    

            #     if permanent_session: 
            #         app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30) 
            #     else:
            #          app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
            #     session['permanent_session'] = permanent_session
            #     app.config['SESSION_MAX_AGE'] = timedelta(days=30)
            #     return redirect(url_for('home'))
            # else:
            #     return make_response('Unable to verify',403,{'WWW-Authenticate':'Basic realm:"Authentication Failed!'})
    else:
        return render_template('Login.html')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('are_you_logged_in'))







if __name__== '__main__':
    app.run(debug=True)