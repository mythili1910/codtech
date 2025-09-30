from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Role", choices=[("employer", "Employer"), ("candidate", "Candidate")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class JobForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    salary = StringField("Salary")
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Post Job")

class ApplicationForm(FlaskForm):
    resume = FileField("Upload Resume", validators=[DataRequired()])
    submit = SubmitField("Apply")