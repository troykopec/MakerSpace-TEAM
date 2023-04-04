from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, UserForm, PasswordForm
import sys
import pytz
sys.path.append('MakerSpace/Google_API')
from Google_API import quickstart
import json



from time import *
import calendar


import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



#############################
#######| Create App |########
#############################
app = Flask(__name__)
app.app_context().push()

#############################
####| Add MySQL Database |###
#############################
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Maker_Space_Password687737!@localhost/our_users'
app.config['SECRET_KEY'] = "my secret key"

#############################
#| Initialize the Database |#
#############################
db = SQLAlchemy(app)
migrate = Migrate(app, db)
@app.before_first_request
def create_tables():
    db.create_all()
    
#############################
####| Flask Login Stuff |####
#############################
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

########################################################################    
#############################| WEBPAGES |###############################
########################################################################

@app.template_filter('tojson')
def tojson(value):
    return json.dumps(value)

@app.template_filter()
def format_time(value, format='%Y-%m-%d %H:%M:%S'):
    date_str = value['dateTime']
    return datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S').strftime(format)

#############################| Signup Page |###############################
# If a GET request is made, the function renders an HTML template that    #
# includes a form for adding a new user. If a POST request is made, the   #
# function validates the data submitted in the form, checks if the        #
# email and username are unique, hashes the password, creates a new       #
# user with the provided information, adds the new user to the database   #
# using SQLAlchemy, and flashes a success message. If the email or        #
# username is already in use, it flashes an error message. Used in        #
# add_user.html                                                           #
###########################################################################
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username= form.username.data).first()
        email = Users.query.filter_by(email= form.email.data).first()
        #checks if email is unique, if it is keep going
        if email is None and user is None:
            # Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            
            user = Users(name=form.name.data, email=form.email.data, username = form.username.data,
                         favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully!")
        else:
            if user is not None:
                flash("This username is already in use!")
            else:
                flash("This email is already in use!")
                
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("simple-sidebar/dist/add_user.html",
        form = form,
        name=name,
        our_users=our_users)


##################| User Function for adding reservation |#################
# The function retrieves the necessary data from the request, checks if   #
# the selected time slot is already reserved, creates a new reservation   #
# in the database using SQLAlchemy, and returns a JSON response           #
# indicating the status of the operation. Finally, a flash message is     #
# displayed to the user indicating whether the operation was successful   #
# or not. Called in modal.js via the app route when reserve button is     #
# clicked (AJAX).                                                         #
###########################################################################
@app.route('/reserve/add', methods=['GET', 'POST'])
@login_required
def add_reservation():
    data = json.loads(request.data)
    event_date_start = data['event_date_start']
    event_date_end = data['event_date_end']
    machine_id = data['machine_id']
    current_user = data['current_user']
    reservations = Reservations.query.filter_by(selected_date_start=event_date_start).with_entities(Reservations.machineid).all()
    machineid_list = [tup[0] for tup in reservations]
    
    if machine_id in machineid_list:
        flash("This time slot is taken!")
    else:
        reservation = Reservations(userid=current_user, machineid=machine_id, selected_date_start=event_date_start, selected_date_end=event_date_end)
        db.session.add(reservation)
        db.session.commit()
        
    flash("Reservation Created Successfully!")
    response_data = {'status': 'success'}
    return json.dumps(response_data)


#######################| Get User's Reservations |#########################
# The function retrieves reservations from the database for the user      #
# with the specified ID and formats the reservation dates to be           #
# displayed in US/Eastern time. The formatted reservations are then       #
# returned as a list. If an error occurs while retrieving the             #
# reservations, an error message is flashed and an empty response is      #
# returned. Used in sheduled_reservations.html to return all of a users   #
# reservations.                                                           #
###########################################################################
@app.route('/get_user_reservations', methods=['GET'])
@login_required
def get_user_reservations(id):
    if (id == current_user.id):
        try:
            reservations = Reservations.query.filter_by(userid=id).all()
            for reservation in reservations:
                dt_start = datetime.strptime(reservation.selected_date_start[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                utc_start = pytz.timezone('UTC').localize(dt_start)
                eastern_start = utc_start.astimezone(pytz.timezone('US/Eastern'))
                formatted_date_start = eastern_start.strftime('%Y-%m-%d %I:%M %p')
                reservation.selected_date_start = formatted_date_start
                
                dt_end = datetime.strptime(reservation.selected_date_end[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                utc_end = pytz.timezone('UTC').localize(dt_end)
                eastern_end = utc_end.astimezone(pytz.timezone('US/Eastern'))
                formatted_date_end = eastern_end.strftime('%Y-%m-%d %I:%M %p')
                reservation.selected_date_end = formatted_date_end
                
                
            return reservations
        except:
            flash("Whoops... There was a problem getting your reservations. Try Again!")
            return


#####################| Get All Reservations (SQL) |########################
# The function retrieves all reservations from Reservations the           #
# database using SQLAlchemy and formats the selected date to display in   #
# Eastern Time. The reservations are then returned as a JSON object. If   #
# there is an error, an error message is flashed and an empty string is   #
# returned. Used in modal.js to check if reservations overlap with        #
# another.                                                                #
###########################################################################
@app.route('/get_all_reservations', methods=['GET'])
@login_required
def get_all_reservations():
    try:
        reservations = Reservations.query.all()
        reservations_list = []
        for reservation in reservations:
            dt = datetime.strptime(reservation.selected_date_start[:-1], '%Y-%m-%dT%H:%M:%S.%f')
            utc = pytz.timezone('UTC').localize(dt)
            eastern = utc.astimezone(pytz.timezone('US/Eastern'))
            formatted_date = eastern.strftime('%Y-%m-%d %I:%M %p')
            
            reservation_dict = {
                'id': reservation.id,
                'userid': reservation.userid,
                'machineid': reservation.machineid,
                'selected_date': formatted_date
            }
            reservations_list.append(reservation_dict)
        return jsonify(reservations_list)
    except:
        flash("Whoops... There was a problem getting the reservations. Try Again!")
        return ""


#############| User Function for deleting reservations |###################
# This function allows users to delete their reservation from the         #
# database. It retrieves the reservation ID and user ID from the POST     #
# request, and if the user ID matches the ID of the currently logged in   #
# user, the corresponding reservation is deleted from the database        #
# using SQLAlchemy. If the deletion is successful, a success message is   #
# flashed and they are redirected to the 'scheduled_reservations' page.   #
# Otherwise, an error message is flashed and they are redirected to the   #
# same page.                                                              #
###########################################################################
@app.route('/cancel_reservation', methods=['POST'])
@login_required
def cancelReservation():
    reservation_id = request.form['reservation_id']
    user_id = int(request.form['user_id']) 
    print(reservation_id)
    print(user_id)
    print(current_user.id)
    if (user_id == current_user.id):
        reservation_to_delete = Reservations.query.get_or_404(reservation_id)
        try:
            db.session.delete(reservation_to_delete)
            db.session.commit()
            flash("Reservation Deleted Successfully")
            return redirect(url_for('scheduled_reservations'))
        except:
            flash("Whoops... There was a problem deleting your reservation. Try Again!")
            return redirect(url_for('scheduled_reservations'))
    return ''
    

######################## | Calender Page | #############################
# This function is responsible for rendering the HTML template for the #
# calendar page, which displays a monthly calendar with available      #
# time slots for each day. It takes the current user's scheduled events#
# and available time slots as inputs and passes them to the HTML       #
# template for rendering.                                              #
#                                                                      #
# It is also a route function that can handle both GET and POST        #
# requests, and requires the user to be logged in to access the page.  #
########################################################################
@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    return render_template("simple-sidebar/dist/schedule.html",
    event = quickstart,
    datetime = datetime)



###########################| Load Modal |###########################
# This function is triggered when the user clicks the "reserve"    #
# button on the HTML page to reserve a machine. It takes the ID    #
# of the selected machine as an argument and retrieves its name    #
# from a dictionary. The retrieved machine name is then passed to  #
# a modal that displays a list of available dates for the user to  #
# choose from. The code also includes other elements such as       #
# rendering templates, generating event content, and adding        #
# reservations.                                                    #
####################################################################
@app.route('/load_modal')
def load_modal():
    machine_id = request.args.get('event_id')
    
    machines = {
    1: "3D-Printer",
    2: "Circuit Board Creator",
    3: "Injection Mold",
    4: "Vinyl Cutter",
    5: "Heat Press",
    6: "Laser Machine",
    7: "Oscilloscope"
    }
    if int(machine_id) in machines:
        machine_name = machines.get(int(machine_id))
    else:
        return
    # Code to generate the event content goes here
    return render_template('simple-sidebar/dist/schedulemodal.html',
    event = quickstart,
    datetime = datetime,
    machine_name = machine_name)

#############################| Status Page |############################
@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    status = []
    machine_types = ["3D-Printer", "Circuit Board Creator", "Injection Mold", "Vinyl Cutter", "Heat Press", "Laser Machine", "Oscilloscope"]
    for machine in machine_types:
        reservations = Reservations.query.filter_by(machineid=machine).all()
        reservations_list = []
        if not reservations:
            print("Open")
            status.append("Open")
        for reservation in reservations:
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            start_time = reservation.selected_date_start
            end_time = reservation.selected_date_end
            if start_time <= current_time <= end_time:
                print(start_time + " " + current_time + " " + end_time)
                print("Closed")
                status.append("Closed")
            else:
                print("Open")
                status.append("Open")

    return render_template("simple-sidebar/dist/status.html", status = status, machine_types = machine_types)

#############################| Training Page |############################
@app.route('/scheduled_reservations', methods=['GET', 'POST'])
@login_required
def scheduled_reservations():
    return render_template("simple-sidebar/dist/scheduled_reservations.html",
                            get_user_reservations = get_user_reservations,
                            datetime = datetime)

#############################| Training Page |############################
@app.route('/training', methods=['GET', 'POST'])
@login_required
def training():
    return render_template("simple-sidebar/dist/training.html")


########################| Create Dashboard Page |#######################
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("simple-sidebar/dist/dashboard.html")


########################| Delete Database Record |######################
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if (id == current_user.id):
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
    
##############################| Main Page |#############################
@app.route('/')
def index():
    return render_template("simple-sidebar/dist/base.html")


##########################| Create Login Page |#########################
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


#########################| Create Logout Page |#########################
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out.")
    return redirect(url_for('login'))


########################| Invalid URL Error Page |######################
@app.errorhandler(404)
def page_not_found(e):
        return render_template("simple-sidebar/dist/404.html"), 404


######################| Internal Server Error Page |####################
@app.errorhandler(500)
def page_not_found(e):
        return render_template("simple-sidebar/dist/500.html"), 500
    
    
######################| Password Test Page (Login) |####################
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


########################| Update Database Record |######################
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
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
            return render_template("simple-sidebar/dist/dashboard.html",
                form = form,
                name_to_update = name_to_update)
        except:
            db.session.commit()
            flash("Error! There was a problem. Try Again!")
            return render_template("simple-sidebar/dist/dashboard.html",
                form = form,
                name_to_update = name_to_update)
    else:
        return render_template("simple-sidebar/dist/update.html",
                form = form,
                name_to_update = name_to_update,
                id = id)


    
    
    
########################################################################    
##########################| DATABASE MODELS |###########################
########################################################################
    
########################| Create User DB Model |########################
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

####################| Create Reservation DB Model |#####################

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    machineid = db.Column(db.String(255))
    selected_date_start = db.Column(db.String(255))
    selected_date_end = db.Column(db.String(255))

########################################################################    
################################| RUN |#################################
########################################################################
if __name__ == "__main__":
    app.run(host="127.0.0.2", port=8080, debug=True)



