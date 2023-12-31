import jwt
import datetime
import hashlib
import uuid
import os
from os.path import join, dirname
from bson import ObjectId
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
    token_receive = request.cookies.get("token")
    courses = list(db.courses.find().limit(3))
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        return render_template("index.html", user_info=user_info, courses=courses)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html", courses=courses)

@app.route('/about')
def about():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("about.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("about.html")

@app.route('/courses')
def courses():
    token_receive = request.cookies.get("token")
    courses = list(db.courses.find())
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        courses = db.courses.find()

        return render_template("courses.html", user_info=user_info, courses=courses)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("courses.html", courses=courses)

@app.route('/courses/<slug>')
def course(slug):
    token_receive = request.cookies.get("token")
    course = db.courses.find_one({"slug": slug})
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        course["id"] = str(course["_id"])

        return render_template("detail-course.html", user_info=user_info, course=course)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("detail-course.html", course=course)

@app.route('/status')
def status():
    token_receive = request.cookies.get("token")
    msg = request.args.get("msg")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        # Cari statusregistrasi ("registrations") berdasarkan id user(dapat dari user_info di atas), masukkan data ke variabel "status", dan sertakan variabel ke dalam render template (_id jadikan str)
        user_id = user_info["_id"]
        statuses = list(db.registrations.find({"userId": str(user_id)}))
        
        for status in statuses:
            status["id"] = str(status["_id"])

            course = db.courses.find_one({"_id": ObjectId(status["courseId"])})
            courseName = course["name"]
            coursePrice = course["price"]

            status["courseName"] = courseName
            status["coursePrice"] = coursePrice

        return render_template("status.html", user_info=user_info, msg=msg, statuses=statuses)
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/user_info')
def user_info():
    msg = request.args.get("msg")
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        return render_template("user-info.html", user_info=user_info, msg=msg)
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin')
def admin_dashboard():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Ambil semua data pendaftar dari database("registrations")
        registrations_data = list(db.registrations.find())
        
        # Hitung jumlah pendaftar dengan status waiting dan accepted
        registrantWaitingCount = sum(1 for reg in registrations_data if reg['status'] == 'waiting')
        registrantAcceptedCount = sum(1 for reg in registrations_data if reg['status'] == 'accepted')
        
        # Ambil semua data kursus dari database("courses")
        courses_data = list(db.courses.find())
        
        # Hitung jumlah total kursus
        coursesCount = len(courses_data)
        
        return render_template("admin/index.html", 
                               user_info=user_info,
                               registrantWaitingCount=registrantWaitingCount,
                               registrantAcceptedCount=registrantAcceptedCount,
                               coursesCount=coursesCount)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/registrant')
def registrant():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        registrations = list(db.registrations.find())
        
        for registration in registrations:
            registration["id"] = str(registration["_id"])
            
            user = db.users.find_one({"_id": ObjectId(registration["userId"])})
            course = db.courses.find_one({"_id": ObjectId(registration["courseId"])})

            registration["userName"] = user["name"]
            registration["mobileNum"] = user["mobileNum"]
            registration["courseName"] = course["name"]

        return render_template("admin/registrant.html", user_info=user_info, registrations=registrations)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/courses')
def admin_courses():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        courses = list(db.courses.find())
        for course in courses:
            course["id"] = str(course["_id"])

        return render_template("admin/courses.html", user_info=user_info, courses=courses)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/admin/courses/<id>')
def admin_course_detail(id):
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        course = db.courses.find_one({"_id": ObjectId(id)})
        course["id"] = str(course["_id"])

        return render_template("admin/detail-course.html", user_info=user_info, course=course)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def api_login():
    email = request.form.get("email")
    password = request.form.get("password")
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    result = db.users.find_one({"email": email, "password": pw_hash})

    if result is not None:
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
        msg = "Akun dengan kombinasi email atau password tersebut tidak ditemukan"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/register', methods=['POST'])
def api_register():
    # Data yang diterima dari form adalah name, email, mobileNum, dan password
    name = request.form.get("name")
    email = request.form.get("email")
    dupEmail = db.users.find_one({"email": email})
    if dupEmail is not None:
        msg="Akun dengan email tersebut sudah ada. Silahkan inputkan email lain atau login dengan email tersebut"
        response = make_response(redirect(url_for("register")))
        response.set_cookie("msg", msg)
        return response
    mobileNum = request.form.get("mobileNum")
    password = request.form.get("password")
    passwordConf = request.form.get("passwordConf")
    if password != passwordConf:
        msg="Password konfirmasi anda berbeda"
        response = make_response(redirect(url_for("register")))
        response.set_cookie("msg", msg)
        return response
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
    msg = "Akun berhasil dibuat. Silahkan login"
    response = make_response(redirect(url_for('login')))
    response.set_cookie("msg", msg)
    return response

@app.route('/api/update_user', methods=['POST'])
def update_user():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        nama = request.form.get("name")
        email = request.form.get("email")
        mobileNum = request.form.get("mobileNum")
        updated_data = {}
        if nama:
            updated_data["name"] = nama
        if nama:
            updated_data["mobileNum"] = mobileNum
        if email != user_info["email"]:
            dupEmail = db.users.find_one({"email": email})
            if dupEmail is not None:
                msg="Akun dengan email tersebut sudah ada. Silahkan inputkan email lain"
                response = make_response(redirect(url_for("user_info")))
                response.set_cookie("msg", msg)
                return response
            
            updated_data["email"] = email

        db.users.update_one({"_id": user_info["_id"]}, {"$set": updated_data})
        if "email" in updated_data:
            payload = {"id": email, "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),}
            new_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            msg="User updated successfully"
            response = make_response(redirect(url_for("user_info")))
            response.set_cookie("token", new_token)
            response.set_cookie("msg", msg)
            return response
        
        msg="User updated successfully"
        response = make_response(redirect(url_for("user_info")))
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/register_course', methods=['POST'])
def register_course():
    token_receive = request.cookies.get("token")
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

        if learningScheme == "offline" and location == "":
            response = make_response(jsonify({"result": "fail"}))
            msg = "Pendaftaran gagal dibuat. Masukkan lokasi kursus!"
            response.set_cookie("msg", msg)
            return response
        
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
        if not result:
            response = make_response(jsonify({"result": "fail"}))
            msg = "Pendaftaran gagal dibuat"
            response.set_cookie("msg", msg)
            return response
        
        message = "Pendaftaran berhasil dibuat, silahkan upload bukti pembayaran"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        response = make_response(jsonify({"result": "success"}))
        msg = "Pendaftaran berhasil dibuat"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/upload_payment', methods=['POST'])
def upload_payment():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        
        registration_id = request.form.get("registration_id")
        payment_file = request.files.get("paymentFile")

        file_extension = os.path.splitext(payment_file.filename)[1]
        if file_extension.lower() not in allowed_extensions:
            msg="File yang diinputkan tidak"
            response = redirect(url_for("status"))
            response.set_cookie("msg", msg)
            return response

        unique_filename = str(uuid.uuid4()) + os.path.splitext(payment_file.filename)[1]
        save_to = f'static/payment_files/{unique_filename}'

        # registration = db.registrations.find_one({"_id": ObjectId(registration_id)})

        # if registration['payment']:
        #     old_payment_file = f'static/payment_files/{registration["payment"]}'
        
        # if os.path.exists(old_payment_file):
        #     os.remove(old_payment_file)
        
        payment_file.save(save_to)

        result = db.registrations.update_one({"_id": ObjectId(registration_id)}, {"$set": {"payment": unique_filename}})

        if result.matched_count > 0 and result.modified_count > 0:
            msg="Berhasil mengupload bukti pembayaran"
            response = redirect(url_for("status"))
            response.set_cookie("msg", msg)
            return response
        
        msg="Gagal mengupload bukti pembayaran"
        response = redirect(url_for("status"))
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/get_notifications', methods=['GET'])
def get_notifications():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        notifications = list(db.notifications.find({"userId": str(user_info["_id"])}))
        for notification in notifications:
            notification["_id"] = str(notification["_id"])

        return jsonify({"result": "success", "notifications": notifications})
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response


@app.route('/api/update_status_notification', methods=['POST'])
def update_status_notification():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        
        notification_id = request.form.get("notification_id")
        notification = db.notifications.find_one({"_id": ObjectId(notification_id)})

        if notification is not None:
            db.notifications.update_one({"_id": ObjectId(notification_id)}, {"$set": {"isRead": True}})
            return jsonify({"status": "success"})
        return jsonify({"status": "fail"})

    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/accept_registration', methods=['POST'])
def accept_registration():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        id = request.form.get("id")
        new_status = {"$set": {"status": "accepted"}}

        result = db.registrations.update_one({"_id": ObjectId(id)}, new_status)
        if result.matched_count <= 0:
            response = make_response(jsonify({"status": "fail"}))
            msg = "Update failed"
            response.set_cookie("msg", msg)
            return response

        userId = request.form.get("userId")
        message = "Pendaftaran anda telah disetujui. Silahkan periksa WhatsApp untuk informasi lebih lanjut"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        response = make_response(jsonify({"status": "success"}))
        msg = "Data updated. Registration accepted"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/reject_registration', methods=['POST'])
def reject_registration():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        id = request.form.get("id")
        new_status = {"$set": {"status": "rejected"}}

        result = db.registrations.update_one({"_id": ObjectId(id)}, new_status)
        if result.matched_count <= 0:
            response = make_response(jsonify({"status": "fail"}))
            msg = "Update failed"
            response.set_cookie("msg", msg)
            return response

        userId = request.form.get("userId")
        message = "Pendaftaran anda ditolak"
        isRead = False
        
        notifications = {
            "userId": userId,
            "message": message,
            "isRead": isRead,
        }
        db.notifications.insert_one(notifications)

        response = make_response(jsonify({"status": "success"}))
        msg = "Data updated. Registration rejected"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/add_course', methods=['POST'])
def add_course():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))
        
        # Data yang diterima dari form adalah name, desc, duration, dan price
        
        name = request.form.get("name")
        dupName = db.courses.find_one({"name": name})
        if dupName is not None:
            msg="Course dengan nama teresbut sudah ada. Silahkan masukkan nama lain"
            response = make_response(redirect(url_for("admin_courses")))
            response.set_cookie("msg", msg)
            return response
        
        desc = request.form.get("desc")
        longDesc = request.form.get("longDesc")
        duration = request.form.get("duration")
        price = request.form.get("price")
        slug = name.replace(" ", "-")
        
        doc = {
            "name": name,
            "slug": slug,
            "desc": desc,
            "longDesc": longDesc,
            "duration": duration,
            "price": price,
        }

        result = db.courses.insert_one(doc)

        if result:
            response = make_response(redirect(url_for('admin_courses')))
            msg = "Course added successfully"
            response.set_cookie("msg", msg)
            return response
        
        response = make_response(redirect(url_for('admin_courses')))
        msg = "Update failed"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/update_course', methods=['POST'])
def update_course():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        id = request.form.get("id")
        name = request.form.get("name")
        dupName = db.courses.find_one({"name": name})
        if dupName is not None:
            if dupName["_id"] != ObjectId(id):
                msg="Course dengan nama teresbut sudah ada. Silahkan masukkan nama lain"
                response = make_response(jsonify({"status": "fail"}))
                response.set_cookie("msg", msg)
                return response
        
        desc = request.form.get("desc")
        longDesc = request.form.get("longDesc")
        duration = request.form.get("duration")
        price = request.form.get("price")
        slug = name.replace(" ", "-")
        
        new_status = {"$set": {
            "name": name,
            "slug": slug,
            "desc": desc,
            "longDesc": longDesc,
            "duration": duration,
            "price": price,
        }}

        result = db.courses.update_one({"_id": ObjectId(id)}, new_status)
        if result:
            response = make_response(jsonify({"status": "success"}))
            msg = "Course updated"
            response.set_cookie("msg", msg)
            return response
        
        response = make_response(jsonify({"status": "fail"}))
        msg = "Update failed"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

@app.route('/api/delete_course', methods=['POST'])
def delete_course():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})

        if not user_info["isAdmin"]:
            return redirect(url_for("home"))

        id = request.form.get("id")

        result = db.courses.delete_one({"_id": ObjectId(id)})
        if result:
            response = make_response(redirect(url_for('admin_courses')))
            msg = "Course deleted"
            response.set_cookie("msg", msg)
            return response
        
        response = make_response(jsonify({"status": "fail"}))
        msg = "Delete failed"
        response.set_cookie("msg", msg)
        return response
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    
@app.route('/api/delete_notifications', methods=['POST'])
def delete_notifications():
    token_receive = request.cookies.get("token")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        user_info = db.users.find_one({"email": payload["id"]})
        
        db.notifications.delete_many({"userId": str(user_info["_id"])})

        return jsonify({"status": "success", "msg": "Notifications deleted successfully"})
    except jwt.ExpiredSignatureError:
        msg="Your login token has expired"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response
    except jwt.exceptions.DecodeError:
        msg="There was an issue logging you in"
        response = make_response(redirect(url_for('login')))
        response.set_cookie("msg", msg)
        return response

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)