from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.app_context().push()

#ADD DATA BASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


#Initialize the Database
db = SQLAlchemy(app)
#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Main Page
@app.route('/')
def index():
    return render_template("simple-sidebar/dist/index.html")

# localhost:5000/user/John
@app.route('/user/<name>')
def user(name):
    return render_template("simple-sidebar/dist/add_user.html", user_name=name)

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
        return render_template("simple-sidebar/dist/404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
        return render_template("simple-sidebar/dist/500.html"), 500
    
if __name__ == "__main__":
    app.run(host="127.0.0.2", port=8080, debug=True)



