from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField


# Create Signup Form
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    role = StringField("Role")
    password_hash = PasswordField("Password", validators=[DataRequired(),
        EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
# Create Password Form
class PasswordForm(FlaskForm):
    email = StringField("Whats Your Email?", validators=[DataRequired()])
    password_hash = PasswordField("Whats Your Password?", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
# Create a Posts Form
class PostForm(FlaskForm):
        title = StringField("Title", validators=[DataRequired()])
        #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
        content = CKEditorField('Content', validators=[DataRequired()])
        submit = SubmitField("Submit")
        location = StringField("Location", validators=[DataRequired()], default="blog")

class addMachineForm(FlaskForm):
    name = StringField("Name of Machine", validators=[DataRequired()])
    amount_of_machines = IntegerField("# of Machines", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class editMachineForm(FlaskForm):
    name = StringField("Name of Machine", validators=[DataRequired()])
    amount_of_machines = IntegerField("# of Machines", validators=[DataRequired()])
    machine_id = IntegerField("Machine ID", validators=[DataRequired()])
    submit = SubmitField("Submit")
    