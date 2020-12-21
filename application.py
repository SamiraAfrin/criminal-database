from flask import Flask , render_template, redirect, url_for
from datetime import datetime
import pandas as pd

from wtform_fields import *
from models import *

app = Flask(__name__)  # Creating the server app
app.secret_key = 'replace later'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/criminal_database'   # Connecting to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)   # Creating the database object


# The url of the page. '/' means url will be 127.0.0.1:port/
# index Method is called when '127.0.0.1:port/' this url is used.
@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form= RegistrationForm()   # The form used to make the registration page.

    # Checks if the form was submitted with no ValidationError
    if reg_form.validate_on_submit():

        # Storing the info taken from Registration_Page
        fullname = reg_form.fullname.data
        sex = reg_form.sex.data
        phone_number = reg_form.phone_number.data
        personal_email = reg_form.personal_email.data
        dept_email = reg_form.department_email.data
        nid_no = reg_form.national_id_card_number.data
        rank = reg_form.rank.data
        station = reg_form.station.data
        officer_id = reg_form.officer_id.data
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_pswd = pbkdf2_sha256.hash(password)   # Hashed Password

        # Making Users and police_officers table object to insert into the database
        user = Users(Username=username, Name=fullname, NID_No=nid_no,
            Gender=sex[0], Pass=hashed_pswd, Phone_No=phone_number,
            Personal_email=personal_email, Department_email=dept_email,
            privilege = 0)

        officer = police_officers(Username=username, Officer_id=officer_id,
            Station=station, Rank=rank)

        # Inserting into the database
        db.session.add(user)
        db.session.add(officer)
        db.session.commit()

        return redirect(url_for('login'))   # Taking the user to login page when successfully registered.

    return render_template("Registration_Page.html", form=reg_form)   # The html page to load when going to '127.0.0.1:port/'


# login Method is called when '127.0.0.1:port/login' this url is used.
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()   # The form used to make the Login page

    # Checks if the username and the corresponding passwords exists in the database
    if login_form.validate_on_submit():
        ''' Shows the dashboard after successful login '''
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=login_form)   # The html page to load when going to '127.0.0.1:port/login'


# login Method is called when '127.0.0.1:port/dashboard' this url is used.
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template('dashboard.html')   # The html page to load when going to '127.0.0.1:port/dashboard'



@app.route ('/validate', methods=['GET','POST'])
def validate():
    clr_form = SecurityForm()
    if clr_form.validate_on_submit():
        Officer_id=clr_form.Officer_id.data
        Clearance=clr_form.Clearance.data
        security_obj = police_officers.query.filter_by(Officer_id=Officer_id).first()
        if security_obj:
            security_obj.Clearance = Clearance
            db.session.merge(security_obj)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template("security_clearance.html", form=clr_form)

@app.route ('/show', methods=['GET','POST'])
def show():
    shw_form = DataForm()
    if shw_form.validate_on_submit():
        Officer_id=shw_form.Officer_id.data
        data = police_officers.query.filter_by(Officer_id=Officer_id).first()
        st = ''
        if data:
            st  = "Username: " + data.Username +'\n' + "Officer ID:" + data.Officer_id +'\n' + "Station:" + data.Station +'\n' +"Rank:" + data.Rank +'\n'
            return st
        if (Officer_id=="All") or (Officer_id=="ALL") or (Officer_id=="all"):
            data=police_officers.query.all()
            df = pd.DataFrame(data)
            print(df)
            for emp in data:
                st = st+'\n'+ " Username: " + emp.Username +'\n' + " Officer ID: " + emp.Officer_id +'\n' + " Station: " + emp.Station +'\n' +" Rank: " + emp.Rank +'\n'
            return st
    return render_template("show.html", form=shw_form)


if __name__ == "__main__":
    app.run(debug=True)   # Running the server with Debug mode on
