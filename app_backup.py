from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.app_context().push()

#ADD MYSQL DATA BASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Maker_Space_Password687737!@localhost/our_users'
app.config['SECRET_KEY'] = "my secret key"

#Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
@app.before_first_request
def create_tables():
    db.create_all()
    
# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    favorite_color = db.Column(db.String(150))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Password Stuff
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name
    
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(),
        EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class PasswordForm(FlaskForm):
    email = StringField("Whats Your Email?", validators=[DataRequired()])
    password_hash = PasswordField("Whats Your Password?", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again")
        else:
            flash("That User Doesn't Exist - Try Again")
    return render_template("simple-sidebar/dist/login.html", form = form)

# Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out.")
    return redirect(url_for('login'))

# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("simple-sidebar/dist/dashboard.html")

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("simple-sidebar/dist/update.html",
                form = form,
                name_to_update = name_to_update)
        except:
            db.session.commit()
            flash("Error! There was a problem. Try Again!")
            return render_template("simple-sidebar/dist/update.html",
                form = form,
                name_to_update = name_to_update)
    else:
        return render_template("simple-sidebar/dist/update.html",
                form = form,
                name_to_update = name_to_update,
                id = id)
    
    
# Delete Database Record
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
        
        our_users = Users.query.order_by(Users.date_added)
        return redirect(url_for('add_user'))
        return render_template("simple-sidebar/dist/add_user.html",
            form = form,
            name=name,
            our_users=our_users)
    except:
        flash("Whoops... There was a problem deleting user. Try Again!")
        return redirect(url_for('add_user'))
        return render_template("simple-sidebar/dist/add_user.html",
            form = form,
            name=name,
            our_users=our_users)
        
# Main Page
@app.route('/')
def index():
    return render_template("simple-sidebar/dist/base.html")

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
        return render_template("simple-sidebar/dist/404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
        return render_template("simple-sidebar/dist/500.html"), 500

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email= form.email.data).first()
        #checks if email is unique, if it is keep going
        if user is None:
            # Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            
            user = Users(name=form.name.data, email=form.email.data, username = form.username.data,
                         favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("simple-sidebar/dist/add_user.html",
        form = form,
        name=name,
        our_users=our_users)

# Password Test Page (Login)
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear Form
        form.email.data = ''
        form.password_hash.data = ''
        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
    return render_template("simple-sidebar/dist/test_pw.html",
        email = email,
        password=password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form) 
    

if __name__ == "__main__":
    app.run(host="127.0.0.2", port=8080, debug=True)




