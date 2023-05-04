from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, UserForm, PasswordForm, PostForm, addMachineForm, editMachineForm
import sys
import pytz
sys.path.append('MakerSpace/Google_API')
from Google_API import quickstart
from Google_API import create
import json
from time import *
import calendar
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import re
from flask_ckeditor import CKEditor
from twilio.rest import Client

###########################################################################   
###########################| INITIALIZE APP|###############################
###########################################################################

#######| Create App |########
app = Flask(__name__)
app.app_context().push()
ckeditor = CKEditor(app)


####| Add MySQL Database |###
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Maker_Space_Password687737!@localhost/our_users'
app.config['SECRET_KEY'] = "my secret key"


######| Set Constants |######
UPLOAD_FOLDER = 'static/user_add_csvs'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv'])
MACHINE_TYPES = ["3D-Printer", "Circuit Board Creator", "Injection Mold", "Vinyl Cutter", "Heat Press", "Laser Machine", "Oscilloscope"]
MACHINES_LISTED = {
    1: "3D-Printer",
    2: "Circuit Board Creator",
    3: "Injection Mold",
    4: "Vinyl Cutter",
    5: "Heat Press",
    6: "Laser Machine",
    7: "Oscilloscope"
}


#| Initialize the Database |#
db = SQLAlchemy(app)
migrate = Migrate(app, db)
@app.before_first_request
def create_tables():
    db.create_all()
    
    
####| Flask Login Stuff |####
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



###########################################################################   
######################| ADMIN FUNCTIONS AND PAGES|#########################
###########################################################################



########################| Allowed File Check|##############################
# This function is called when a file is uploaded by an admin, it         #
# checks the file type to make sure it is a CSV                           #
###########################################################################
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###########################| Upload Users |################################
# This function proccesses the CSV into a readable file, saves it to      #
# the server csv folder, and sends it to csv_to_db()                      #
###########################################################################
@app.route("/upload_users", methods=['POST'])
@login_required
def upload_users():
    if (current_user.role == "Admin"):
        uploaded_file = request.files['file']
        if uploaded_file and allowed_file(uploaded_file.filename):
            timenow = re.sub(r'[:.]', '_', str(datetime.now()))
            new_filename = f'{uploaded_file.filename.split(".")[0]}_{timenow}.csv'
            # set the file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            # save the file
            uploaded_file.save(file_path)
            csv_to_db(file_path)
            message = "User(s) Added Successfully!"
            return jsonify(message=message)
    return jsonify(error="Upload Failed")

#############################| csv to db |#################################
# This function parses each row of the CSV file to extract the values     #
# of 'name', 'email', 'password_hash', 'username', and 'role', in the     #
# respective order they appear in the file. Then, it creates a user       #
# with these values for each row found in the CSV.                        #
###########################################################################
def csv_to_db(filePath):
      # CVS Column Names
      col_names = ['email', 'role']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None, dtype=str)
      # Loop through the Rows
      for i,row in csvData.iterrows():
          print(str(row['email']) + "<-----------------------------------")
          hashed_email = generate_password_hash(row['email'], "sha256")
          user = Users(email_hash=hashed_email, role=row['role'])
          db.session.add(user)
          db.session.commit()
      flash("User(s) Added Successfully!")
      
#########################| upload time slots |#############################
# This function proccesses the CSV into a readable file, saves it to      #
# the server csv folder, and sends it to csv_to_api()                     #
###########################################################################
@app.route("/upload_time_slots", methods=['POST'])
@login_required
def upload_time_slots():
    if (current_user.role == "Admin" or current_user.role == "Worker"):
        uploaded_file = request.files['dataFile']
        if uploaded_file and allowed_file(uploaded_file.filename):
            timenow = re.sub(r'[:.]', '_', str(datetime.now()))
            new_filename = f'{uploaded_file.filename.split(".")[0]}_{timenow}.csv'
            # set the file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            # save the file
            uploaded_file.save(file_path)
            csv_to_api(file_path)
            message = "User(s) Added Successfully!"
            return jsonify(message=message)
    return jsonify(error="Upload Failed")

############################| csv to api |#################################
# This function parses each row of the CSV file to extract the values     #
# of 'year', 'month' , 'day', 'start_hour', 'end_hour', in the            #
# respective order they appear in the file. Then, it creates a google     #
# calendar event with these values for each row found in the CSV.         #
###########################################################################
def csv_to_api(filePath):
      # CVS Column Names
      col_names = ['year', 'month' , 'day', 'start_hour', 'end_hour']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None)
      # Loop through the Rows
      machines = Machines.query.all()
      for machine in machines:
          for each in range(machine.amount_of_machines):
              for i,row in csvData.iterrows():
                  machine_name = machine.machine_name
                  start_date = f"{row['year']}-{row['month']}-{row['day']}T{row['start_hour']}:00-04:00"
                  end_date = f"{row['year']}-{row['month']}-{row['day']}T{row['end_hour']}:00-04:00"
                  create.getDates(machine_name, start_date, end_date)
      flash("Time Slot(s) Created Successfully!")

#########################| delete time slots |#############################
# This function proccesses the CSV into a readable file, saves it to      #
# the server csv folder, and sends it to csv_to_delete()                  #
###########################################################################
@app.route("/delete_time_slots", methods=['POST'])
@login_required
def delete_time_slots():
    if (current_user.role == "Admin" or current_user.role == "Worker"):
        uploaded_file = request.files['data2File']
        if uploaded_file and allowed_file(uploaded_file.filename):
            timenow = re.sub(r'[:.]', '_', str(datetime.now()))
            new_filename = f'{uploaded_file.filename.split(".")[0]}_{timenow}.csv'
            # set the file path
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            # save the file
            uploaded_file.save(file_path)
            csv_to_delete(file_path)
            message = "Time Slots Removed Successfully!"
            return jsonify(message=message)
    return jsonify(error="Upload Failed")

########################| csv to delete timeslots |########################
# This function parses each row of the CSV file to extract the values     #
# of 'year', 'month' , 'day', 'start_hour', 'end_hour', in the            #
# respective order they appear in the file. Then, it deletes all google   #
# calendar events with these values for each row found in the CSV.        #
###########################################################################
def csv_to_delete(filePath):
      # CVS Column Names
      col_names = ['year', 'month' , 'day', 'start_hour', 'end_hour']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None)
      # Loop through the Rows
      for i,row in csvData.iterrows():
          start_time = f"{row['year']}-{row['month']}-{row['day']}T{row['start_hour']}:00-04:00"
          end_time = f"{row['year']}-{row['month']}-{row['day']}T{row['end_hour']}:00-04:00"
          quickstart.deleteDateInTimeframe(start_time, end_time)
          
###########################| Admin Search User |###########################
# This code defines a function called search_user() that searches for a   #
# user in a database based on their email address. It checks if the       #
# current user has the "Admin" role and then retrieves the email from a   #
# form request. It then iterates over all the users in the database and   #
# uses the check_password_hash() function to validate if the email        #
# address matches any of the hashed email addresses stored in the         #
# database. If a matching email address is found, the function            #
# redirects the user to a page for updating the selected users            #
# information.                                                            #
###########################################################################
@app.route('/search_user', methods=['POST'])
def search_user():
    if (current_user.role == "Admin"):
        email = request.form['email']
        selected_user = None
        for user in Users.query.all():
                valid_email = check_password_hash(user.email_hash, email)
                if valid_email:
                    selected_user = user
        
        if selected_user is not None:
            return redirect(url_for('admin_update', id = selected_user.id))
        else:
            flash('Could not find user with email: {}'.format(email))
            return redirect(url_for('admin_dashboard'))
    
###########################| Admin Dashboard |#############################
# This page is designed to provide administrative tools for viewing all   #
# reservations made by users, uploading new users via a CSV file, and     #
# uploading Google API events via a CSV file. Access to this page is      #
# restricted to administrators only.                                      #
###########################################################################
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    flash_message = session.pop('flash_message', None)
    if(current_user.role == "Admin" or current_user.role == "Worker"):
        return render_template("simple-sidebar/dist/admin_dashboard.html",
                            get_user_reservations = get_user_reservations,
                            datetime = datetime,
                            get_machines = get_machines)
    else:
        return redirect(url_for('dashboard'))

#############################| Get Status |################################
# gets status of the makerspace to return to the admin toggle status      #
# button in admin_dashboard.html.                                         #
###########################################################################
@app.route('/get_status')
def get_status():
    status = Status.query.first()
    return {'status': status.active}

###########################| Toggle Status |###############################
# toggles status of the makerspace, called by toggle status button in     #
# admin_dashboard.html.                                                   #
###########################################################################
@app.route('/toggle_status')
def toggle_status():
    if (current_user.role == "Admin" or current_user.role == "Worker"):
        status = Status.query.first()
        status.active = not status.active
        db.session.commit()
        return {'status': status.active}
    else:
        return redirect(url_for('dashboard'))

###################| Admin Function to Delete API Event |##################
# This route function deletes a reservation made via the Google           #
# Calendar API. It first checks if the current user is an admin and       #
# then extracts the 'event_id' from the JSON data sent in the POST        #
# request. It then uses this event_id to delete the corresponding event   #
# from Google Calendar using the 'deleteDate' function defined in the     #
# 'quickstart' module. Finally, it finds the corresponding reservation    #
# object in the database using the event_id, deletes it from the          #
# database and saves the changes. If the current user is not an admin,    #
# it redirects them to the dashboard page.                                #
###########################################################################
@app.route('/delete_API_reservation', methods=['POST'])
@login_required
def delete_API_reservation():
    if (current_user.role == "Admin"):
        data = json.loads(request.data)
        event_id = data['event_id']
        quickstart.deleteDate(event_id)
        reservation = Reservations.query.filter_by(eventid=event_id).first()
        reservation_id = reservation.id
        reservation_to_delete = Reservations.query.get_or_404(reservation_id)
        db.session.delete(reservation_to_delete)
        db.session.commit()
    else:
        flash("You are not authorized to delete reservations. Nice try!")

##############| Admin Function to Delete API Event via loop |##############
# This function bassically does the same as the other delete function,    #
# except it is called by deleteDateInTimeframe() function in              #
# quickstart.py that deletes events found in a given timeframe and        #
# deletes the via loop                                                    #
########################################################################### 
def delete_API_reservation_loop(event_id):
    if (current_user.role == "Admin"):
        quickstart.deleteDate(event_id)
        reservation = Reservations.query.filter_by(eventid=event_id).first()
        if reservation is not None:
            reservation_id = reservation.id
            reservation_to_delete = Reservations.query.get_or_404(reservation_id)
            db.session.delete(reservation_to_delete)
            db.session.commit()
    else:
        flash("You are not authorized to delete reservations. Nice try!")

#########################| Admin User Update |#############################
# The code defines a Flask route for updating user information for an     #
# administrator. It checks if the user has the admin role, creates a      #
# UserForm object, retrieves user data from the database, and updates     #
# it if the form is submitted with valid data. The function flashes a     #
# success or error message and redirects the user to the admin            #
# dashboard or renders the update form, respectively.                     #
###########################################################################
@app.route('/admin_update/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_update(id):
    if (current_user.role == "Admin"):
        form = UserForm()
        name_to_update = Users.query.get_or_404(id)
        if form.validate_on_submit():
            password_field = request.form['password_hash']
            if (password_field != "None"):
                hashed_pw = generate_password_hash(password_field, "sha256")
                name_to_update.password_hash = hashed_pw
            name_to_update.username = request.form['username']
            name_to_update.role = request.form['role']
            
            try:
                db.session.commit()
                flash("User Updated Successfully")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
            except:
                db.session.commit()
                flash("Error! There was a problem. Try Again!")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
        else:
            return render_template("simple-sidebar/dist/admin_update.html",
                    form = form,
                    name_to_update = name_to_update,
                    id = id)
        
#######################| Admin Machine Creation |##########################
# In the view function add_machine(), an instance of addMachineForm       #
# form is created to allow for adding a new machine. If the form is       #
# submitted and validated successfully, a new instance of Machines is     #
# created with the data provided by the form, added to the session, and   #
# committed to the database. Used in admin_dashboard.html                 #
###########################################################################
@app.route('/add_machine', methods=['GET', 'POST'])
@login_required
def add_machine():
    if (current_user.role == "Admin"):
        form = addMachineForm()
        if form.validate_on_submit():
            machine_to_add =  Machines(machine_name=form.name.data, amount_of_machines=form.amount_of_machines.data)
            db.session.add(machine_to_add)
            try:
                db.session.commit()
                flash("Machine Added Successfully")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
            except:
                db.session.commit()
                flash("Error! There was a problem. Try Again!")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
        else:
            return render_template("simple-sidebar/dist/add_machines.html",
                    form = form,
                    id = id)
        
#######################| Admin Machine Edit |############################
# The first line of the function retrieves the "machine_id" from the      #
# requests form data. Then, an instance of the "editMachineForm" class    #
# is created to validate the form data. Next, the machine to be updated   #
# is retrieved from the database using the "machine_id" value. If the     #
# machine does not exist, a 404 error is returned. If the form data is    #
# validated, the machines "machine_name" and "amount_of_machines"         #
# attributes are updated with the new data, and the changes are           #
# committed to the database. Used in admin_dashboard.html and             #
# update_machines.html                                                    #
###########################################################################
@app.route('/edit_machine', methods=['POST'])
@login_required
def edit_machine():
    if (current_user.role == "Admin"):
        machine_id = request.form['machine_id']
        form = editMachineForm()
        machine_to_update = Machines.query.get_or_404(machine_id)
        if form.validate_on_submit():
            machine_to_update.machine_name = request.form['name']
            machine_to_update.amount_of_machines = request.form['amount_of_machines']
            try:
                db.session.commit()
                flash("Machine Updated Successfully")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
            except:
                db.session.commit()
                flash("Error! There was a problem. Try Again!")
                return render_template("simple-sidebar/dist/admin_dashboard.html",
                    get_user_reservations = get_user_reservations,
                    datetime = datetime,
                    get_machines = get_machines)
        else:
            return render_template("simple-sidebar/dist/update_machines.html",
                    form = form,
                    machine_to_update = machine_to_update,
                    machine_id = machine_id)

########################| Get all Machines (SQL) |#########################
@app.route('/get_machines', methods=['GET'])
@login_required
def get_machines():
        if ("Admin" == current_user.role):
            machines = Machines.query.all()
        return machines

########################| Get All Users (SQL) |############################
@app.route('/get_all_users', methods=['GET'])
@login_required
def get_all_users(id):
    if (id == current_user.id):
        try:
            if ("Admin" == current_user.role):
                users = Users.query.all()

                return users
        except:
            flash("Whoops... There was a problem getting your reservations. Try Again!")
            return
      
###########################################################################   
#######################| WEBPAGES AND FUNCTIONS|###########################
###########################################################################


##########################| Convert to JSON |##############################
@app.template_filter('tojson')
def tojson(value):
    return json.dumps(value)

############################| Format Time |################################
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
    selected_user = None
    valid = False
    admin_check = Users.query.filter_by(username= form.username.data).first()
    if ((form.username.data == "admin") and (admin_check is None)):
        hashed_email = generate_password_hash(form.email.data, "sha256")
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        admin_creation =  Users(username=form.username.data, role="Admin", password_hash=hashed_pw, email_hash=hashed_email,)
        db.session.add(admin_creation)
        db.session.commit()
        flash("Admin Added Successfully!")
        return redirect(url_for('login'))
    
    if form.validate_on_submit():
        authenticated = False
        for user in Users.query.all():
            valid_email = check_password_hash(user.email_hash, form.email.data)
            if valid_email:
                if user.username is None:
                    selected_user = user
                    valid = True
                    break
                else:
                    authenticated = True

        user = Users.query.filter_by(username= form.username.data).first()
        #checks if email is unique, if it is keep going
        if user is None and valid is True:
            # Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            
            selected_user.username = form.username.data
            selected_user.password_hash = hashed_pw

            db.session.commit()
            flash("User Added Successfully!")
            return redirect(url_for('login'))
        else:
            if user is not None:
                flash("This username is already in use!")
                return redirect(url_for('add_user'))
            else:
                if authenticated:
                    flash("This email has already been used to authenticate an account.")
                else:
                    flash("This email is not authenticated to create an account.")
                return redirect(url_for('add_user'))
                
        form.username.data = ''
        form.email.data = ''
        form.password_hash = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("simple-sidebar/dist/add_user.html",
        form = form,
        name=name,
        our_users=our_users)
    
##################| User Function for Adding Reservation |#################
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
    event_id = data['event_id']
    print(event_id)
    reservations = Reservations.query.filter_by(eventid=event_id).with_entities(Reservations.eventid).all()
    machineid_list = [tup[0] for tup in reservations]
    
    
    if (event_id in machineid_list):
        flash("This time slot is taken!")
    else:
        reservation = Reservations(userid=current_user, machineid=machine_id, selected_date_start=event_date_start, selected_date_end=event_date_end, eventid=event_id)
        db.session.add(reservation)
        db.session.commit()
        return redirect(url_for('scheduled_reservations'))
        
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
            current_url = request.url.split('/')[-1]
            if (current_url == "dashboard"):
                if (current_user.role == "Admin" or current_user.role == "Worker"):
                    reservations = Reservations.query.all()
                else:
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
            else:
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
                'selected_date': formatted_date,
                'eventid' : reservation.eventid
            }
            reservations_list.append(reservation_dict)
        return jsonify(reservations_list)
    except:
        flash("Whoops... There was a problem getting the reservations. Try Again!")
        return ""

################| User Function for Deleteing Reservation |################
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
    if (user_id == current_user.id or current_user.role == "Admin" or current_user.role == "Worker"):
        reservation_to_delete = Reservations.query.get_or_404(reservation_id)
        try:
            db.session.delete(reservation_to_delete)
            db.session.commit()
            flash("Reservation Deleted Successfully")
            return redirect(request.referrer or url_for('index'))
        except:
            flash("Whoops... There was a problem deleting your reservation. Try Again!")
            return redirect(request.referrer or url_for('index'))
    return ''
    
#########################| Calendar Page |#################################
# This function is responsible for rendering the HTML template for the    #
# calendar page, which displays a monthly calendar with available         #
# time slots for each day. It takes the current user's scheduled events   #
# and available time slots as inputs and passes them to the HTML          #
# template for rendering.                                                 #
#                                                                         #
# It is also a route function that can handle both GET and POST           #
# requests, and requires the user to be logged in to access the page.     #
###########################################################################
@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    return render_template("simple-sidebar/dist/schedule.html",
    event = quickstart,
    datetime = datetime)

###########################| Load Modal |##################################
# This function is triggered when the user clicks the "reserve"           #
# button on the HTML page to reserve a machine. It takes the ID           #
# of the selected machine as an argument and retrieves its name           #
# from a dictionary. The retrieved machine name is then passed to         #
# a modal that displays a list of available dates for the user to         #
# choose from. The code also includes other elements such as              #
# rendering templates, generating event content, and adding               #
# reservations.                                                           #
###########################################################################
@app.route('/load_modal')
def load_modal():
    machine_id = request.args.get('event_id')
    if int(machine_id) in MACHINES_LISTED:
        machine_name = MACHINES_LISTED.get(int(machine_id))
    else:
        return
    # Code to generate the event content goes here
    return render_template('simple-sidebar/dist/schedulemodal.html',
    event = quickstart,
    datetime = datetime,
    machine_name = machine_name)

##############################| Status Page |##############################
# This code defines a route for a page that displays the current status   #
# of all machines. It checks each machine type in MACHINE_TYPES and       #
# queries the database to get all reservations made for that machine.     #
# It then checks the start and end times of each reservation and          #
# compares it to the current time. If the reservation is currently        #
# active, the machine is marked as 'Closed'. If there are no              #
# reservations for the machine, it is marked as 'Open'. The status of     #
# each machine is added to a list status, which is then passed to the     #
# status.html template along with MACHINE_TYPES. The template then        #
# displays the status of each machine in a table. It first checks to see  #
# if the makerspace is even open.                                         #
###########################################################################
@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
    Status.get_instance()
    makerspace_status = Status.query.first().active
    status = []
    if makerspace_status == False:
        for machine in MACHINE_TYPES:
            status.append("Closed")
    else:
        for machine in MACHINE_TYPES:
            reservations = Reservations.query.filter_by(machineid=machine).all()
            reservations_list = []
            if not reservations:
                status.append("Open")
            for reservation in reservations:
                current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                start_time = reservation.selected_date_start
                end_time = reservation.selected_date_end
                if start_time <= current_time <= end_time:
                    print(start_time + " " + current_time + " " + end_time)
                    status.append("Closed")
                else:
                    status.append("Open")

    return render_template("simple-sidebar/dist/status.html", status = status, machine_types = MACHINE_TYPES)

#####################| Scheduled Reservations Page |#######################
# This page displays all of a users scheduled reservations                #
###########################################################################
@app.route('/scheduled_reservations', methods=['GET', 'POST'])
@login_required
def scheduled_reservations():
    return render_template("simple-sidebar/dist/scheduled_reservations.html",
                            get_user_reservations = get_user_reservations,
                            datetime = datetime)

#############################| Training Page |#############################
# This page displays a training page with info about each machine and     #
# links to a training video                                               #
###########################################################################
@app.route('/training', methods=['GET', 'POST'])
@login_required
def training():
    posts = Posts.query.filter_by(location="training").order_by(Posts.date_posted)
    return render_template("simple-sidebar/dist/training.html", posts=posts)

########################| Extra Machine Info Page |########################
# This page displays a training page with info about each machine         #
###########################################################################
@app.route('/machineinfo', methods=['GET', 'POST'])
@login_required
def machine_info():
    return render_template("simple-sidebar/dist/machineinfo.html")

#########################| Create Dashboard Page |#########################
# This page displays all of a users database information and allows for   #
# the user to update information                                          #
###########################################################################
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("simple-sidebar/dist/dashboard.html")

#########################| Delete Database Record |########################
# This code defines a route for deleting a user with a given ID from      #
# the database. The route is only accessible to logged-in users. If the   #
# user to be deleted has the same ID as the currently logged-in user,     #
# the function proceeds to delete the user from the database and          #
# redirects to the add_user page with a flash message indicating          #
# success. If the user to be deleted has a different ID than the          #
# currently logged-in user, the function redirects to the add_user page   #
# with a flash message indicating that there was a problem deleting the   #
# user. The add_user page displays a form for adding new users and a      #
# table of all existing users in the database.                            #
###########################################################################
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

##############################| Main Page |################################
@app.route('/')
def index():
    return render_template("simple-sidebar/dist/base.html")


##############################| Login Page |###############################
# This code defines a Flask route for the login page and allows users     #
# to login by submitting a form with their username and password. It      #
# uses a LoginForm instance to validate the user's input and checks if    #
# the user exists in the database. If the user exists and the password    #
# is correct, the user is logged in and redirected to the dashboard       #
# page. If the username or password is incorrect, an appropriate flash    #
# message is displayed and the user is redirected back to the login       #
# page.                                                                   #
###########################################################################
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

###############################| Logout Page |#############################
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out.")
    return redirect(url_for('login'))

########################| Invalid URL Error Page |#########################
@app.errorhandler(404)
def page_not_found(e):
        return render_template("simple-sidebar/dist/404.html"), 404


######################| Internal Server Error Page |#######################
@app.errorhandler(500)
def page_not_found(e):
        return render_template("simple-sidebar/dist/500.html"), 500

####################| Update User Database Record |########################
# This code defines a route for updating a user's information. The        #
# route takes an id parameter that specifies the user to update. The      #
# function first retrieves the user from the database using the id. If    #
# the request method is POST, it updates the user's information with      #
# the data from the form and commits the changes to the database. If      #
# the update is successful, it redirects to the dashboard page and        #
# flashes a success message. If there's an error, it flashes an error     #
# message and returns the update page. If the request method is GET, it   #
# renders the update page with the current user's information populated   #
# in the form.                                                            #
###########################################################################
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
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

#############################| Delete Post |###############################
# This code defines a Flask route for deleting a specific blog post       #
# with the given id. It requires the user to be logged in and checks      #
# whether the user is either the author of the post or an admin. If the   #
# user is authorized to delete the post, it deletes the post from the     #
# database and redirects the user to the page displaying all blog posts   #
# with a success message. If there is an error while deleting the post,   #
# it redirects the user to the page displaying all blog posts with an     #
# error message. If the user is not authorized to delete the post, it     #
# redirects the user to the page displaying all blog posts with an        #
# error message.                                                          #
###########################################################################
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    
    if ( current_user.id == post_to_delete.post_userid or current_user.role == "Admin"):
        try:
                db.session.delete(post_to_delete)
                db.session.commit()

                # Return a message
                flash("Blog Post Was Deleted!")
                # Grab all the posts from the databas
                posts = Posts.query.filter_by(location="blog").order_by(Posts.date_posted)
                return redirect(url_for('posts', posts=posts))

        except:
                flash("Whoops! There was a problem deleting post, try again!")
                # Grab all the posts from the databas
                posts = Posts.query.order_by(Posts.date_posted)
                return redirect(url_for('posts', posts=posts))
    else:
        flash("You cannot delete others posts!")
        return redirect(url_for('posts'))

#############################| Show Posts |################################
# Displays all posts onto the blog page, aslong as they have a location   #
# of 'blog'.                                                              #
###########################################################################
@app.route('/posts')
@login_required
def posts():
    # Grab all the posts from the database that are of location blog
    posts = Posts.query.filter_by(location="blog").order_by(Posts.date_posted)
    return render_template("simple-sidebar/dist/posts.html", posts=posts)

##############################| View Post |################################
# Creates individual posts shown on the blog page                         #
###########################################################################
@app.route('/posts/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("simple-sidebar/dist/post.html", post=post)

##############################| Edit Post |################################
# The function first checks whether the current user is the author of     #
# the post or an admin, and if not, it redirects to the posts page. If    #
# the user is authorized to edit the post, the function retrieves the     #
# post from the database using its id and generates a form with the       #
# current post data using the PostForm. The form is then displayed to     #
# the user, and upon submission, the function validates the form data     #
# and updates the post with the new data, commits the changes to the      #
# database, and redirects to the post page with a success message. If     #
# the form is not valid, the form is re-rendered with the invalid input   #
# fields highlighted for correction.                                      #
###########################################################################
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    if ( current_user.id == Posts.query.get_or_404(id).post_userid or current_user.role == "Admin"):
        post = Posts.query.get_or_404(id)
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            # Update Database
            db.session.add(post)
            db.session.commit()
            flash("Post Has Been Updated!")
            return redirect(url_for('post', id=post.id))
        
        form.title.data = post.title
        #form.author.data = post.author
        #form.slug.data = post.slug
        form.content.data = post.content
        return render_template('simple-sidebar/dist/edit_post.html', form=form)
    else:
        flash("You cannot edit others posts!")
        return redirect(url_for('posts'))
    
###############################| Add Post |################################
# This code defines a route for adding a new blog post to the             #
# application. The route is accessed via a GET or POST request. If the    #
# form submitted via a POST request is validated, the data is added to    #
# the database as a new blog post using the Posts class. After            #
# successful submission, a message is displayed and the user is           #
# redirected to the add_post page.                                        #
###########################################################################
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=(form.content.data).replace("</p>", "").replace("<p>", ""), location=form.location.data, post_userid=current_user.id)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.location.data = ''
        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("simple-sidebar/dist/add_post.html", form=form)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    # Your Account SID from twilio.com/console
    account_sid = "ACbc855018324a2b88daa90916999cef56"
    # Your Auth Token from twilio.com/console
    auth_token  = "cfb1f8e899bf804a87fa98c22451b0e0"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    #12032400741 Dr.Lori Number
    to="+18134408766", 
    from_="+18884955046",
    body="There is a serious problem in the Makerspace!")
    print(message.sid)
    return render_template("simple-sidebar/dist/base.html")



########################################################################    
##########################| DATABASE MODELS |###########################
########################################################################
    
    
########################| Create User DB Model |########################
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    role = db.Column(db.String(150), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Password Stuff
    password_hash = db.Column(db.String(128))
    email_hash = db.Column(db.String(150))
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
class Machines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_name = db.Column(db.String(255))
    amount_of_machines = db.Column(db.Integer)

######################| Create Machines DB Model |#######################
class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    machineid = db.Column(db.String(255))
    selected_date_start = db.Column(db.String(255))
    selected_date_end = db.Column(db.String(255))
    eventid = db.Column(db.String(255))
    
##############################| Blog Post Model|#############################
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(255))
    post_userid = db.Column(db.Integer)
    
################################| Status Model|##############################
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=False)

    _instance = None  # class-level attribute to hold the singleton instance

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls.query.first() or cls()
            db.session.add(cls._instance)
            db.session.commit()
        return cls._instance

########################################################################    
################################| RUN |#################################
########################################################################
if __name__ == "__main__":
    app.run(host="127.0.0.2", port=8080, debug=True)



