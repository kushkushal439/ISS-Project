from flask import Flask, render_template, request, redirect, url_for,session, jsonify,make_response
import json
import shutil

import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime,timedelta
import jwt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_access_cookies, set_access_cookies, unset_jwt_cookies

from werkzeug.security import generate_password_hash, check_password_hash
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from functools import wraps
import requests
from PIL import Image
import binascii
import io




app = Flask(__name__)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)


app.config['SECRET_KEY'] = 'secret'
app.config['JWT_SECRET_KEY'] = 'key'
app.config['JWT_TOKEN_LOCATION']=['headers','json','cookies','query_string']
app.config["JWT_COOKIE_CSRF_PROTECT"] = False


try:
    db = mysql.connector.connect(
        host='localhost',
        database='Users',
        user='sriyansh',
        password='Sriyansh@28'
    )
    if db.is_connected():
        cursor = db.cursor()
        print('Connected to MySQL database')

except Error as e:
    print("Error while connecting to MySQL", e)


output_dir = "static/images"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255))")


jwt = JWTManager(app)

sql = """
    CREATE TABLE IF NOT EXISTS images (
        img_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        image_data LONGBLOB
    )
    """
cursor.execute(sql)






@app.route('/', methods=['GET'])
@jwt_required(optional=True)
def first():
    try:
        current_user = get_jwt_identity()
        if current_user:
            return render_template('intro.html')
        else:
            return redirect(url_for('login'))
    except ExpiredSignatureError:
        # Handle token expiration gracefully
        return redirect(url_for('login'), message="Your session has expired. Please log in again.")

    except Exception as e:
        # Log the error for debugging purposes

        return redirect(url_for('login'), message="An unexpected error occurred. Please try again later.")



# @jwt.expired_token_loader
# def my_expired_token_callback(expired_token):
#     return 1
    

@app.route('/intro' , methods=['GET'])
@jwt_required()
def intro():
   try:
        current_user = get_jwt_identity()
        return render_template('intro.html')
   except ExpiredSignatureError:
        # If token is expired, redirect to login page
        return redirect('/login')


@app.route('/main' , methods=['POST','GET','DELETE'])
@jwt_required()
def main():
    return render_template('main.html') 
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
            username = request.form['username']
            password = request.form['password']

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
           
            

            if user_data:
                user_id=user_data[0]
                stored_password=user_data[3]
                if check_password_hash(stored_password , password):
                                                         
                        access_token = create_access_token(identity=user_id)
                      

                        resp = make_response(redirect(url_for('intro')))
                        set_access_cookies(resp, access_token)
                        return resp
                     

                else:
                    return "Incorrect Password"
            else:
                return "User does not exist"
    else:
        return render_template('login.html')




@app.route('/signup', methods=['POST','GET'])
def signup():

    if request.method=='POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

      

        try:
            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Insert user into the database
            sql = "INSERT INTO users (username,email,password) VALUES (%s, %s,%s)"
            val = (username , email, hashed_password)
            cursor.execute(sql, val)
            db.commit()
            
            return jsonify({"msg": "User registered successfully"}), 200

        except Exception as e:
               # Rollback changes if an error occurs
                db.rollback()
                print("Error:", e)
                return "Error"
    else:
        return render_template('signup.html')
    


@app.route('/main',methods=['POST','GET','DELETE'])
@jwt_required
def main():
    return render_template('main.html')



@app.route('/addimages', methods = ['POST','GET'])
@jwt_required()
def addimage():
    if request.method == 'POST':
            if 'file' not in request.files:
                return "file not in files"
            image1 = request.files.getlist('file')
            for image in image1:
                image_bytes = image.read()
                id = get_jwt_identity()
                id = int(id)
                sql = "INSERT INTO images (user_id,image_data) VALUES (%s, %s)"
                cursor.execute(sql,(id,image_bytes))
                db.commit()
                return render_template('addimage.html')
    else:
        return  render_template('addimage.html')
    

# @app.route('/gallery', methods = ["GET"])
# @jwt_required()
# def usrimagelist():

#     if not os.path.exists(output_dir):
#            os.makedirs(output_dir)
#     id = get_jwt_identity()
#     id = int(id)
#     print(f"Users is {id}")
#     # print("Hellog6fh4ferfr5")

#     sql = "SELECT user_id, img_id, image_data FROM images WHERE images.user_id = %s"
#     cursor.execute(sql,(id,))
#     data = cursor.fetchall()
#     iter = 0
#     for i in data:
#         iter = iter + 1
#         name = "img" + str(iter) + ".jpg"
#         output_path = os.path.join(output_dir,name)
#         img1 = Image.open(io.BytesIO(i[2]))

#         if img1.mode == 'RGBA':
#             img1 = img1.convert('RGB')
#         img1.save(output_path)

#     images = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
#     image_paths = [os.path.join('images', img) for img in images]

#     return render_template('gallery.html', images = image_paths)
    

@app.route('/gallery', methods = ["GET","POST"])
@jwt_required()
def usrimagelist():
    if request.method == "POST":
            sring = request.form['selectedImagesInput']
            selected_images = json.loads(sring)
            finaloutdir = "static/selected"
            if not os.path.exists(finaloutdir):
                os.makedirs(finaloutdir)
            for name in selected_images:
                name1 = name[7:]
                input_path = os.path.join(output_dir,name1)
                output_path = os.path.join(finaloutdir,name1)
                shutil.copy(input_path,output_path)
            return render_template("main.html")
    userid = int(get_jwt_identity())
    sql = "SELECT user_id, img_id, image_data FROM images WHERE images.user_id = %s"
    cursor.execute(sql,(userid,))
    data = cursor.fetchall()
    iter = 0
    for i in data:
        iter = iter + 1
        name = "img" + str(iter) + ".jpg"
        output_path = os.path.join(output_dir,name)
        img1 = Image.open(io.BytesIO(i[2]))

        if img1.mode == 'RGBA':
            img1 = img1.convert('RGB')
        img1.save(output_path)

    images = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    image_paths = [os.path.join('images', img) for img in images]
    return render_template('gallery.html', images = image_paths)


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    shutil.rmtree('/home/hibiki/Desktop/project/ISS-Project/static/images')
    shutil.rmtree('/home/hibiki/Desktop/project/ISS-Project/static/selected')

    return response



if __name__== '__main__':
    app.run(debug=True)