import jwt
import datetime
import hashlib
import os
from os.path import join, dirname
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")
SECRET_KEY =  os.environ.get("SECRET_KEY")

app=Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

@app.route('/')
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("index.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/about')
def about():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("about.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("about.html")

@app.route('/courses')
def courses():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Ambil semua data courses("courses") dari database, masukkan data ke variabel "courses", dan sertakan variabel ke dalam render template (_id jadikan str)
        courses = db.courses.find()

        return render_template("courses.html", user_info=user_info, courses=courses)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("courses.html")

@app.route('/courses/<slug>')
def course(slug):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Cari course("courses") berdasarkan slug yang didapat, masukkan data ke variabel "course", dan sertakan variabel ke dalam render template (_id jadikan str)

        return render_template("detail-course.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("detail-course.html")

@app.route('/status')
def status():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Cari statusregistrasi ("registrations") berdasarkan id user(dapat dari user_info di atas), masukkan data ke variabel "status", dan sertakan variabel ke dalam render template (_id jadikan str)

        return render_template("status.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/user_info')
def user_info():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("user-info.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin')
def admin_dashboard():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))

        return render_template("admin/index.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/registrant')
def registrant():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))

        # Ambil semua data registrasi("registrations") dari database, masukkan data ke variabel "registrations", dan sertakan variabel ke dalam render template (_id jadikan str)
        # Tambahkan atribut "name" dan course name di setiap data dalam variabel registrations serta hapus atribut courseId
        # Cari nama("users") berdasarkan userId pada setiap data pada variable registrations dan masukkan nama tersebut ke dalam atribut name yang sebelumnya dibuat
        # Lakukan yang sama untuk courseId

        return render_template("admin/registrant.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/courses')
def admin_courses():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))

        # Ambil semua data course("courses") dari database, masukkan data ke variabel "courses", dan sertakan variabel ke dalam render template (_id jadikan str)

        return render_template("admin/courses.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/courses/<id>')
def admin_course_detail(id):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))

        # Cari course("courses") berdasarkan id yang didapat, masukkan data ke variabel "course", dan sertakan variabel ke dalam render template (_id jadikan str)

        return render_template("admin/detail-course.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/api/login')
def api_login():
    email = request.form["email"]
    password = request.form["password"]
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    result = db.users.find_one({"email": email, "password": pw_hash})

    if result:
        payload = {"id": email, "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"result": "success", "token": token})
    else:
        return jsonify({"result": "fail", "msg": "We could not find a user with that id/password combination"})

@app.route('/api/register')
def api_register():
    # Copy aja register/sign up dari project lama, tapi data yang dimasukkan name, email, mobileNum, password, isAdmin. isAdmin nilai nya false, sisanya dari form
    return

@app.route('/api/update_user')
def update_user():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Ambil data dari form dan _id atau email user lalu update data user dengan data yang didapat dari form berdasarkan _id user
        # Karena id pada payload session berisi email dan ada kemungkinan user mengubah email pada proses ini, buat ulang token jwt untuk login session dengan email yang baru
        # Return pesan success

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/register_course')
def register_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Dapatkan data userId, courseId, learningScheme, location, date, status dari form dan jadikan satu variabel dengan nama "registration" serta tambahkan satu atribut dengan nama payment dengan value kosong
        # userId didapat dari user_info sedangkan courseId dan data lainnya didapatkan dari input form
        # Masukkan variabel registration ke database("registrations")

        # Buat variabel notification dengan atribut userId, message, dan isRead. userId didapat dari user_info, message berisi "Anda berhasil mendaftarkan course" dan isRead bernilai false
        # Masukkan variabel notification ke database("notifications")
        
        # Return pesan success

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/upload_payment')
def upload_payment():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Dapatkan registrationId dan bukti pembayaran dari form
        # Rename file bukti pembayaran dengan unique name
        # Pindahkan file bukti pembayaran ke dalam folder static
        # Tambahkan nama file bukti pembayaran ke dalam atribut payment pada data yang memiliki _id yang sama dengan registrationId
        # Return pesan success

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/get_notifications')
def get_notifications():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Ambil semua notifications dari database("notifications") dengan atribut userId yang sama dengan id user(didapatkan dari user_info)
        # Return pesan success dan notification yang didapat

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/update_status_notification')
def update_status_notification():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Dapatkan data id notification dari form
        # Update atribut isRead menjadi true

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/accept_registration')
def accept_registration():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Dapatkan data id registration dari form
        # Update atribut status menjadi accepted

        # Buat variabel notification dengan atribut userId, message, dan isRead. userId didapat dari form, message berisi "Pendaftaran anda telah disetujui" dan isRead bernilai false
        # Masukkan variabel notification ke database("notifications")
        
        # Return pesan success

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/reject_registration')
def reject_registration():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Dapatkan data id registration dari form
        # Update atribut status menjadi rejected

        # Buat variabel notification dengan atribut userId, message, dan isRead. userId didapat dari form, message berisi "Pendaftaran anda ditolak" dan isRead bernilai false
        # Masukkan variabel notification ke database("notifications")
        
        # Return pesan success

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/add_course')
def add_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Dapatkan data name, desc, duration, dan price dari form
        # Buat variabel slug yang berisi value name dengan karakter spasi yang sudah diubah menjadi "-" (contoh "kursus persiapan toefl" jadi "kursus-persiapan-toefl")
        # Masukkan semua data ke dalam variabel course dan insert ke dalam database("courses")

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/update_course')
def update_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Dapatkan data id course, name, desc, duration, price dari form
        # Buat variabel slug yang berisi value name dengan karakter spasi yang sudah diubah menjadi "-"
        # Update course dengan data yang telah didapat pada data yang memiliki id yang sama dengan id course yang didapat

        return 
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)