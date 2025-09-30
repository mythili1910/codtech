import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Job, Application
from forms import RegisterForm, LoginForm, JobForm, ApplicationForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "supersecret"
app.config["UPLOAD_FOLDER"] = "static/resumes"

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    jobs = Job.query.all()
    return render_template("home.html", jobs=jobs)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data, email=form.email.data, password=hashed_pw, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = JobForm()
    if current_user.role == "employer" and form.validate_on_submit():
        job = Job(title=form.title.data, company=form.company.data, location=form.location.data,
                  salary=form.salary.data, description=form.description.data, employer_id=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for("dashboard"))

    if current_user.role == "employer":
        jobs = Job.query.filter_by(employer_id=current_user.id).all()
    else:
        jobs = Application.query.filter_by(candidate_id=current_user.id).all()
    return render_template("dashboard.html", form=form, jobs=jobs)

@app.route("/job/<int:job_id>", methods=["GET", "POST"])
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    form = ApplicationForm()
    if form.validate_on_submit() and current_user.is_authenticated and current_user.role == "candidate":
        file = form.resume.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        application = Application(resume=filename, candidate_id=current_user.id, job_id=job.id)
        db.session.add(application)
        db.session.commit()
        flash("Application submitted!", "success")
        return redirect(url_for("dashboard"))
    return render_template("job_detail.html", job=job, form=form)

@app.route("/applications/<int:job_id>")
@login_required
def applications(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.role != "employer" or job.employer_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("dashboard"))
    apps = Application.query.filter_by(job_id=job.id).all()
    return render_template("applications.html", job=job, apps=apps)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)