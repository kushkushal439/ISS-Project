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
from moviepy.editor import ImageSequenceClip, concatenate_videoclips
import psycopg2




app = Flask(__name__)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)


app.config['SECRET_KEY'] = 'secret'
app.config['JWT_SECRET_KEY'] = 'key'
app.config['JWT_TOKEN_LOCATION']=['headers','json','cookies','query_string']
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db = psycopg2.connect("postgresql://kushal:PpjAtagZofTf_1r7_5Yi7A@weisnoob-8900.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/users?sslmode=verify-full")
cursor = db.cursor()

# try:
#     db = mysql.connector.connect(
#         host='localhost',
#         database='Users',
#         user='kushal',
#         password='password'
#     )
#     if db.is_connected():
#         cursor = db.cursor()
#         print('Connected to MySQL database')

# except Error as e:
#     print("Error while connecting to MySQL", e)


output_dir = "static/images"

if not os.path.exists(output_dir):
    print("HEy there")
    os.makedirs(output_dir)

cursor.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq")
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT DEFAULT nextval('users_id_seq') PRIMARY KEY, username VARCHAR(255), email VARCHAR(255) NOT NULL, password VARCHAR(255), CONSTRAINT unique_email UNIQUE (email))")
db.commit()


jwt = JWTManager(app)

sql = """
    CREATE TABLE IF NOT EXISTS images (
        img_id INT DEFAULT nextval('img_id_seq') PRIMARY KEY,
        user_id INT,
        chosen INT,
        image_data BYTES
    )
    """


cursor.execute("CREATE SEQUENCE IF NOT EXISTS img_id_seq")
cursor.execute(sql)
db.commit()



@app.route('/', methods=['GET'])
@jwt_required(optional=True)
def first():
    try:
        current_user = get_jwt_identity()
        if current_user:
            if current_user == -1:
                return redirect(url_for('admin'))
            else:
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
        # userid = current_user
        # sql = "SELECT user_id, img_id, image_data FROM images WHERE images.user_id = %s"
        # cursor.execute(sql,(userid,))
        # data = cursor.fetchall()
        # iter = 0
        # for i in data:
        #     iter = i[1]
        #     name = "img" + str(iter) + ".jpg"
        #     output_path = os.path.join(output_dir,name)
        #     img1 = Image.open(io.BytesIO(i[2]))

        #     if img1.mode == 'RGBA':
        #         img1 = img1.convert('RGB')
        #     img1.save(output_path)

        # finaloutdir = "static/selected"
        # if os.path.exists('static/selected'): shutil.rmtree('static/selected')
        # if not os.path.exists(finaloutdir):
        #     print("Entered entered entered")
        #     os.makedirs(finaloutdir)
        # images = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        # image_paths = [os.path.join('images', img) for img in images]
        # tokeep = 1
        # sql = "SELECT user_id, img_id, chosen FROM images WHERE images.user_id = %s and chosen = %s"
        # cursor.execute(sql,(userid,tokeep))
        # data = cursor.fetchall()
        # numbers1= []
        # for i in data:
        #     numbers1.append(int(i[1]))
        # finaloutdir = "static/selected"
        # images1 = []
        # if not os.path.exists(finaloutdir):
        #     os.makedirs(finaloutdir)
        # for num in numbers1:
        #     name = 'img'
        #     name += str(num)
        #     name += '.jpg'
        #     input_path = os.path.join(output_dir,name)
        #     output_path = os.path.join(finaloutdir,name)
        #     shutil.copy(input_path,output_path)
        # return render_template('intro.html')
   except ExpiredSignatureError:
        # If token is expired, redirect to login page
        return redirect('/login')



@app.route('/main',methods=['POST','GET','DELETE'])
@jwt_required()
def main():
    finaloutdir = "static/selected"
    images = [f for f in os.listdir(finaloutdir) if os.path.isfile(os.path.join(finaloutdir, f))]
    image_paths = [os.path.join('selected', img) for img in images]
    return render_template("main.html", images = image_paths)




@app.route('/create_video',methods=['POST','GET','DELETE'])
# @jwt_required()
def create_video():
   data = request.get_json()  # Get the JSON data sent from the client
   # data = request.args.get('images-container')
   str = 'None'
   print('Hello')
   # print(data)
   print("HEllo")
   clips = []
   for item in data:
       if item is not None:
           print(item)
           image_path = os.path.join(app.root_path, item['image_path'])
           duration = float(item['duration'])
           transition = item['transition']

           clip = ImageSequenceClip([image_path], durations=[duration])

           if transition == 'fade':
               clip = clip.crossfadein(1)
               print("Cross")
           elif transition == 'slide':
               # Implement slide transition here
               pass

           clips.append(clip)
   final_clip = concatenate_videoclips(clips, method="compose")


   output_file_path = "static/video/output.mp4"
   video_dir = "static/video"

   # Check if the file exists and delete it
   if os.path.isfile(output_file_path):
       os.remove(output_file_path)

   # Check if the directory exists
   if not os.path.exists(video_dir):
       # If the directory doesn't exist, create it
       os.makedirs(video_dir)

   final_clip.write_videofile(output_file_path, fps=24)
   video_url = "/static/video/output.mp4"
   return jsonify({'message': 'Video created successfully', 'newVideoUrl': video_url}), 200


@app.route('/admin',methods = ['GET'])
def admin():
    ret = []
    qry = "select id, username, email from users"
    cursor.execute(qry)
    data = cursor.fetchall()
    for i in data:
        userid = i[0]
        sql = "select count(%s) from images where user_id = %s"
        cursor.execute(sql,(userid,userid))
        num = cursor.fetchall()
        new = []
        new.append(i[0])
        new.append(i[1])
        new.append(i[2])
        new.append(num[0][0])
        ret.append(new)
    return render_template('admin.html', list = ret)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
            username = request.form['username']
            password = request.form['password']
            if(username == "admin" and password == 'admin'):
                access_token = create_access_token(identity=-1)
                resp = make_response(redirect(url_for('admin')))
                set_access_cookies(resp, access_token)
                return resp

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()


            if user_data:
                user_id=user_data[0]
                stored_password=user_data[3]
                if check_password_hash(stored_password , password):
                                                         
                        access_token = create_access_token(identity=user_id)
                        resp = make_response(redirect(url_for('intro')))
                        set_access_cookies(resp, access_token)
                        userid = user_id
                        sql = "SELECT user_id, img_id, image_data FROM images WHERE images.user_id = %s"
                        cursor.execute(sql,(userid,))
                        data = cursor.fetchall()
                        iter = 0
                        for i in data:
                            iter = i[1]
                            name = "img" + str(iter) + ".jpg"
                            output_path = os.path.join(output_dir,name)
                            img1 = Image.open(io.BytesIO(i[2]))

                            if img1.mode == 'RGBA':
                                img1 = img1.convert('RGB')
                            img1.save(output_path)

                        finaloutdir = "static/selected"
                        if os.path.exists('static/selected'): shutil.rmtree('static/selected')
                        if not os.path.exists(finaloutdir):
                            print("Entered entered entered")
                            os.makedirs(finaloutdir)
                        images = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
                        image_paths = [os.path.join('images', img) for img in images]
                        tokeep = 1
                        sql = "SELECT user_id, img_id, chosen FROM images WHERE images.user_id = %s and chosen = %s"
                        userid = user_id
                        cursor.execute(sql,(userid,tokeep))
                        data = cursor.fetchall()
                        numbers1= []
                        for i in data:
                            numbers1.append(int(i[1]))
                        images1 = []
                        if not os.path.exists(finaloutdir):
                            os.makedirs(finaloutdir)
                        for num in numbers1:
                            name = 'img'
                            name += str(num)
                            name += '.jpg'
                            input_path = os.path.join(output_dir,name)
                            output_path = os.path.join(finaloutdir,name)
                            shutil.copy(input_path,output_path)
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



@app.route('/addimages', methods = ['POST','GET'])
@jwt_required()
def addimage():
    if request.method == 'POST':
            if 'data[]' not in request.files:
                return jsonify({'error': 'data[] not in files'}), 400
            image1 = request.files.getlist('data[]')
            for image in image1:
                image_bytes = image.read()
                id = get_jwt_identity()
                id = int(id)
                tokeep = 0
                sql = "INSERT INTO images (user_id,chosen,image_data) VALUES (%s, %s, %s)"
                cursor.execute(sql,(id,tokeep,image_bytes))
                db.commit()
            return render_template('addimage.html')
    else:
        return  render_template('addimage.html')



@app.route('/updatedb', methods = ['POST'])
@jwt_required()
def updatedb():
    data = request.json
    str = data.get('myString')
    print(str)
    parts = str.split('/')
    last_part = parts[-1]    
    number_str = last_part.replace('.jpg', '')   
    number_str1 = number_str.replace('img', ''); 
    num = number_str1
    sql = "delete from images where img_id = %s"
    print(num)
    cursor.execute(sql,(num,))
    db.commit()
    rmdir = "static/"
    rmdir += str
    if os.path.exists(rmdir):
        os.remove(rmdir)
    rmdir1 = rmdir + 'selected/'  + last_part
    if os.path.exists(rmdir1):
        os.remove(rmdir1)
    return jsonify({'message': 'String received successfully'})



@app.route('/gallery', methods = ["GET","POST"])
@jwt_required()
def usrimagelist():
    if request.method == "POST":
        sring = request.form['selectedImagesInput']
        print(sring)
        selected_images = json.loads(sring)
        numbers = []
        for string in selected_images:
            parts = string.split('/')
            last_part = parts[-1]    
            number_str = last_part.replace('.jpg', '')   
            number_str1 = number_str.replace('img', ''); 
            numbers.append(int(number_str1))
        userid = int(get_jwt_identity())
        sqldel = "update images set chosen = %s where user_id = %s"
        cursor.execute(sqldel,(0,userid))
        for num in numbers:
            tokeep = 1
            qnow = "update images set chosen = %s where img_id = %s"
            cursor.execute(qnow,(tokeep,num))
            db.commit()
        tokeep = 1
        sql = "SELECT user_id, img_id, chosen FROM images WHERE images.user_id = %s and chosen = %s"
        cursor.execute(sql,(userid,tokeep))
        data = cursor.fetchall()
        print(data)
        numbers1= []
        for i in data:
            numbers1.append(int(i[1]))
        print(numbers1)
        finaloutdir = "static/selected"
        if os.path.exists('static/selected'): shutil.rmtree('static/selected')
        if not os.path.exists(finaloutdir):
            print("Entered entered entered")
            os.makedirs(finaloutdir)
        for num in numbers1:
            name = 'img'
            name += str(num)
            name += '.jpg'
            input_path = os.path.join(output_dir,name)
            output_path = os.path.join(finaloutdir,name)
            shutil.copy(input_path,output_path)
        images = [f for f in os.listdir(finaloutdir) if os.path.isfile(os.path.join(finaloutdir, f))]
        image_paths = [os.path.join('selected', img) for img in images]
        # return render_template("main.html", images = image_paths)
        return redirect(url_for('main'))
        # return render_template("gallery.html")
    userid = int(get_jwt_identity())
    sql = "SELECT user_id, img_id, image_data FROM images WHERE images.user_id = %s"
    cursor.execute(sql,(userid,))
    data = cursor.fetchall()
    iter = 0
    for i in data:
        iter = i[1]
        name = "img" + str(iter) + ".jpg"
        output_path = os.path.join(output_dir,name)
        img1 = Image.open(io.BytesIO(i[2]))

        if img1.mode == 'RGBA':
            img1 = img1.convert('RGB')
        img1.save(output_path)

    finaloutdir = "static/selected"

    images = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    image_paths = [os.path.join('images', img) for img in images]
    tokeep = 1
    sql = "SELECT user_id, img_id, chosen FROM images WHERE images.user_id = %s and chosen = %s"
    userid = int(get_jwt_identity())
    cursor.execute(sql,(userid,tokeep))
    data = cursor.fetchall()
    if data:
        numbers1= []
        for i in data:
            numbers1.append(int(i[1]))
        finaloutdir = "static/selected"
        images1 = []
        if not os.path.exists(finaloutdir):
            os.makedirs(finaloutdir)
        for num in numbers1:
            name = 'img'
            name += str(num)
            name += '.jpg'
            input_path = os.path.join(output_dir,name)
            output_path = os.path.join(finaloutdir,name)
            shutil.copy(input_path,output_path)
    images = [f for f in os.listdir(finaloutdir) if os.path.isfile(os.path.join(finaloutdir, f))]
    selected_images = [os.path.join('images', img) for img in images]
    print(image_paths)
    return render_template('gallery.html', images = image_paths, selected_images = selected_images)


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response(render_template('login.html'))
    unset_jwt_cookies(response)
    shutil.rmtree('static/images')
    if os.path.exists('static/selected'): shutil.rmtree('static/selected')
    output_dir = "static/images"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return response



if __name__== '__main__':
    app.run(debug=True)