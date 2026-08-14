from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)


# ==========================
# إعدادات النظام
# ==========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# إنشاء مجلد رفع الصور إذا لم يكن موجودًا
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


db = SQLAlchemy(app)


# ==========================
# جدول المتدربين
# ==========================

class Trainee(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    full_name = db.Column(
        db.String(100),
        nullable=False
    )


    national_id = db.Column(
        db.String(50)
    )


    phone = db.Column(
        db.String(20)
    )


    email = db.Column(
        db.String(100)
    )


    university = db.Column(
        db.String(100)
    )


    major = db.Column(
        db.String(100)
    )


    start_date = db.Column(
        db.String(20)
    )


    end_date = db.Column(
        db.String(20)
    )


    status = db.Column(
        db.String(50)
    )


    supervisor = db.Column(
        db.String(100)
    )


    # عدد ساعات التدريب
    training_hours = db.Column(
        db.String(20)
    )


    image = db.Column(
        db.String(200)
    )


# ==========================
# تحديث قاعدة البيانات
# ==========================

def update_database():

    with app.app_context():

        # إنشاء الجداول إذا لم تكن موجودة
        db.create_all()

        # فحص أعمدة جدول trainee
        result = db.session.execute(
            text("PRAGMA table_info(trainee)")
        )

        columns = [row[1] for row in result]

        # إضافة حقل ساعات التدريب إذا لم يكن موجودًا
        if "training_hours" not in columns:

            db.session.execute(
                text(
                    "ALTER TABLE trainee "
                    "ADD COLUMN training_hours VARCHAR(20)"
                )
            )

            db.session.commit()


# ==========================
# تسجيل الدخول
# ==========================

@app.route("/", methods=["GET", "POST"])
def login():


    if request.method == "POST":

        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "login.html"
    )



# ==========================
# لوحة التحكم
# ==========================

@app.route("/dashboard")
def dashboard():


    trainees = Trainee.query.all()


    total = Trainee.query.count()



    return render_template(
        "dashboard.html",
        trainees=trainees,
        total=total
    )



# ==========================
# إضافة متدرب
# ==========================

@app.route("/add", methods=["GET", "POST"])
def add_trainee():


    if request.method == "POST":


        image = request.files.get("image")


        filename = ""



        if image and image.filename:


            filename = secure_filename(
                image.filename
            )


            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )



        trainee = Trainee(

            full_name=request.form["full_name"],

            national_id=request.form["national_id"],

            phone=request.form["phone"],

            email=request.form["email"],

            university=request.form["university"],

            major=request.form["major"],

            start_date=request.form["start_date"],

            end_date=request.form["end_date"],

            status=request.form["status"],

            supervisor=request.form["supervisor"],

            # عدد ساعات التدريب
            training_hours=request.form.get(
                "training_hours",
                ""
            ),

            image=filename

        )


        db.session.add(trainee)

        db.session.commit()


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "add_trainee.html"
    )


# ==========================
# تعديل متدرب
# ==========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_trainee(id):


    trainee = Trainee.query.get_or_404(id)



    if request.method == "POST":


        trainee.full_name = request.form["full_name"]

        trainee.national_id = request.form["national_id"]

        trainee.phone = request.form["phone"]

        trainee.email = request.form["email"]

        trainee.university = request.form["university"]

        trainee.major = request.form["major"]

        trainee.start_date = request.form["start_date"]

        trainee.end_date = request.form["end_date"]

        trainee.status = request.form["status"]

        trainee.supervisor = request.form["supervisor"]

        # عدد ساعات التدريب
        trainee.training_hours = request.form.get(
            "training_hours",
            ""
        )



        image = request.files.get("image")



        if image and image.filename:


            filename = secure_filename(
                image.filename
            )


            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )


            trainee.image = filename



        db.session.commit()



        return redirect(
            url_for("dashboard")
        )



    return render_template(
        "edit_trainee.html",
        trainee=trainee
    )



# ==========================
# حذف متدرب
# ==========================

@app.route("/delete/<int:id>")
def delete_trainee(id):


    trainee = Trainee.query.get_or_404(id)



    db.session.delete(
        trainee
    )


    db.session.commit()



    return redirect(
        url_for("dashboard")
    )

# ==========================
# شهادة المتدرب
# ==========================

@app.route("/certificate/<int:id>")
def certificate(id):

    trainee = Trainee.query.get_or_404(id)

    return render_template(
        "certificate.html",
        trainee=trainee
    )

# ==========================
# تشغيل النظام
# ==========================

if __name__ == "__main__":

    update_database()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )