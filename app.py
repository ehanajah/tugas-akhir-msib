import jwt
import datetime
import hashlib
import os
import uuid
from bson import ObjectId
from os.path import join, dirname
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
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
    msg = request.args.get("msg")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Cari statusregistrasi ("registrations") berdasarkan id user(dapat dari user_info di atas), masukkan data ke variabel "status", dan sertakan variabel ke dalam render template (_id jadikan str)
        user_id = user_info["_id"]
        status = db.registrations.find({"userId": ObjectId(user_id)})

        return render_template("status.html", user_info=user_info, msg=msg, status=status)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/user_info')
def user_info():
    msg = request.args.get("msg")
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("user-info.html", user_info=user_info, msg=msg)
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

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Ambil semua data pendaftar dari database("registrations") dan kursus dari database("courses")
        # Buat variabel registrantWaitingCount dan coursesCount
        # Isi variabel registrantWaitingCount dengan jumlah pendaftar dengan status waiting
        # Isi variabel registrantAcceptedCount dengan jumlah pendaftar dengan status accepted
        # Isi variabel coursesCount dengan jumlah course yang ada
        # sertakan tiga variabel sebelumnya ke dalam render template

        return render_template("admin/index.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/registrant')
def registrant():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        registrations = list(db.registrations.find())
        
        for registration in registrations:
            registration["_id"] = str(registration["_id"])
            
            user = db.users.find_one({"_id": ObjectId(registration["userId"])})
            course = db.courses.find_one({"_id": ObjectId(registration["courseId"])})
            name = user["name"]
            courseName = course["name"]

            registration["userName"] = name
            registration["courseName"] = courseName

        return render_template("admin/registrant.html", user_info=user_info, registrations=registrations)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/courses')
def admin_courses():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        courses = list(db.courses.find())

        return render_template("admin/courses.html", user_info=user_info, courses=courses)
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

        course = db.courses.find_one({"_id": ObjectId(id)})

        return render_template("admin/detail-course.html", user_info=user_info, course=course)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form.get("email")
    password = request.form.get("password")
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    result = db.users.find_one({"email": email, "password": pw_hash})

    if result:
        isAdmin = result["isAdmin"]
        payload = {"id": email, "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        if isAdmin:
            response = make_response(redirect(url_for('admin_dashboard')))
            response.set_cookie("token", token)
            return response

        response = make_response(redirect(url_for('home')))
        response.set_cookie("token", token)
        return response
    else:
        return jsonify({"result": "fail", "msg": "We could not find a user with that id/password combination"})

@app.route('/api/register', methods=['POST'])
def api_register():
    # Data yang diterima dari form adalah name, email, mobileNum, dan password
    name = request.form.get("name")
    email = request.form.get("email")
    mobileNum = request.form.get("mobileNum")
    password = request.form.get("password")
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    isAdmin = False

    # we should save the user to the database
    doc = {
        "name": name,
        "email": email,
        "mobileNum": mobileNum,
        "password": password_hash,
        "isAdmin": isAdmin,
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/api/update_user', methods=['POST'])
def update_user():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Ambil data dari form dan _id atau email user lalu update data user dengan data yang didapat dari form berdasarkan _id user
        nama = request.form.get("name")
        email = request.form.get("email")
        updated_data = {}
        if nama:
            updated_data["name"] = nama
        if email != user_info["email"]:
            updated_data["email"] = email
        db.users.update_one({"_id": user_info["_id"]}, {"$set": updated_data})
        if "email" in updated_data:
            new_token = jwt.encode({"id": updated_data["email"]}, SECRET_KEY, algorithm="HS256")
            response = make_response(redirect(url_for("user_info", msg="User updated successfully")))
            response.set_cookie("token", new_token)
            return response
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/register_course', methods=['POST'])
def register_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        # Data yang diterima dari form adalah courseId, learningScheme, location, dan insertedAt
        
        userId =  str(user_info["_id"])
        courseId = request.form.get("courseId")
        learningScheme = request.form.get("learningScheme")
        location = request.form.get("location")
        insertedAt = request.form.get("insertedAt")
        payment = ""
        status = "waiting"
        
        registration = {
            "userId": userId,
            "courseId": courseId,
            "learningScheme": learningScheme,
            "location": location,
            "insertedAt": insertedAt,
            "payment": payment,
            "status": status,
        }

        result = db.registrations.insert_one(registration)
        if result.matched_count <= 0:
            return jsonify({"result": "fail", "msg": "Update failed",})
        
        message = "Pendaftaran berhasil dibuat, silahkan upload bukti pembayaran"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        return jsonify({"result": "success", "msg": "Pendaftaran berhasil dibuat",})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/upload_payment', methods=['POST'])
def upload_payment():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        registration_id = "657159186292a65d163c2a18"
        payment_file = request.files.get("paymentFile")
        unique_filename = str(uuid.uuid4()) + os.path.splitext(payment_file.filename)[1]
        save_to = f'static/{unique_filename}'
        payment_file.save(save_to)

        result = db.registrations.update_one({"_id": ObjectId(registration_id)}, {"$set": {"payment": unique_filename}})

        if result.matched_count > 0 and result.modified_count > 0:
            return redirect(url_for("status", msg="Berhasil mengupload bukti pembayaran"))
        return redirect(url_for("status", msg="Gagal mengupload bukti pembayaran"))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/get_notifications', methods=['GET'])
def get_notifications():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Ambil semua notifications dari database("notifications") dengan atribut userId yang sama dengan id user(didapatkan dari user_info)
        notifications = db.notifications.find({"userId": str(user_info["_id"])})
        notifications_list = list(notifications)
        # Return pesan success dan notification yang didapat

        return jsonify({"message": "Notifications retrieved successfully", "notifications": notifications_list})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/update_status_notification', methods=['POST'])
def update_status_notification():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        notification_id = request.form.get("notification_id")
        notification = db.notifications.find_one({"_id": ObjectId(notification_id)})

        if notification:
            db.notifications.update_one({"_id": ObjectId(notification_id)}, {"$set": {"isRead": True}})
            return jsonify({"status": "success"})
        return jsonify({"status": "fail"})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/accept_registration', methods=['POST'])
def accept_registration():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Data yang diterima dari form adalah registrationId dan userId
        
        id = request.form.get("id")
        new_status = {"$set": {"status": "accepted"}}

        result = db.registrations.update_one({"_id": ObjectId(id)}, new_status)
        if result.matched_count <= 0:
            return jsonify({"result": "fail", "msg": "Update failed",})

        userId = request.form.get("userId")
        message = "Pendaftaran anda telah disetujui"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        return jsonify({"result": "success", "msg": "Data updated, registration accepted",})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/reject_registration', methods=['POST'])
def reject_registration():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Data yang diterima dari form adalah id registration dan userId
        
        id = request.form.get("id")
        new_status = {"$set": {"status": "rejected"}}

        result = db.registrations.update_one({"_id": ObjectId(id)}, new_status)
        if result.matched_count <= 0:
            return jsonify({"result": "fail", "msg": "Update failed",})

        userId = request.form.get("userId")
        message = "Pendaftaran anda ditolak"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        return jsonify({"result": "success", "msg": "Data updated, registration rejected",})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/add_course', methods=['POST'])
def add_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Data yang diterima dari form adalah name, desc, duration, dan price
        
        name = request.form.get("name")
        desc = request.form.get("desc")
        duration = request.form.get("duration")
        price = request.form.get("price")
        slug = name.replace(" ", "-")
        
        doc = {
            "name": name,
            "slug": slug,
            "desc": desc,
            "duration": duration,
            "price": price,
        }

        result = db.courses.insert_one(doc)

        if result:
            return jsonify({"result": "success", "msg": "Course added successfully",})
        
        return jsonify({"result": "fail", "msg": "Update failed",})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

@app.route('/api/update_course', methods=['POST'])
def update_course():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Data yang diterima darir form adalah id course, name, desc, duration, price dari form

        id = request.form.get("id")
        name = request.form.get("name")
        desc = request.form.get("desc")
        duration = request.form.get("duration")
        price = request.form.get("price")
        slug = name.replace(" ", "-")
        
        new_status = {"$set": {
            "name": name,
            "slug": slug,
            "desc": desc,
            "duration": duration,
            "price": price,
        }}

        result = db.courses.update_one({"_id": ObjectId(id)}, new_status)
        if result:
            return jsonify({"result": "success", "msg": "Course updated",})
        
        return jsonify({"result": "fail", "msg": "Update failed",})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)