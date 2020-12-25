from datetime import datetime
from flask import Flask , render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy import select

from wtform_fields import *
from models import *

app = Flask(__name__)  # Creating the server app
app.secret_key = 'replace later'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/criminal_database'   # Connecting to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)   # Creating the database object

log_in = LoginManager(app)   # Configuring flask-login
log_in.init_app(app)


@log_in.user_loader
def load_user(username):
    return Users.query.filter_by(Username=username).first()


# The url of the page. '/' means url will be 127.0.0.1:port/
# index Method is called when '127.0.0.1:port/' this url is used.
@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form= RegistrationForm()   # The form used to make the registration page.
    current_user.get_id()
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

        flash('Registered successfully. Please Login.', 'success')
        return redirect(url_for('Login'))   # Taking the user to login page when successfully registered.

    return render_template("Registration_Page.html", form=reg_form)   # The html page to load when going to '127.0.0.1:port/'


# login Method is called when '127.0.0.1:port/login' this url is used.
@app.route('/login', methods=['GET', 'POST'])
def Login():
    login_form = LoginForm()   # The form used to make the Login page

    # Checking if the user is logged in or not. If so, redirecting to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Checks if the username and the corresponding passwords exists in the database
    if login_form.validate_on_submit():

        user_obj = Users.query.filter_by(Username=login_form.username.data).first()
        login_user(user_obj)

        ''' Shows the dashboard after successful login '''
        return redirect(url_for('dashboard'))

    return render_template('login.html', form=login_form)   # The html page to load when going to '127.0.0.1:port/login'


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('Logged Out Successfully', 'success')
    return redirect(url_for('Login'))


# login Method is called when '127.0.0.1:port/dashboard' this url is used.
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if not current_user.is_authenticated:
        flash('Please Login first.','danger')
        return redirect(url_for('Login'))

    return render_template('dashboard.html')   # The html page to load when going to '127.0.0.1:port/dashboard'


# login Method is called when '127.0.0.1:port/dashboard/criminals' this url is used.
@app.route('/dashboard/criminals', methods=['GET','POST'])
def showcriminals():
    if not current_user.is_authenticated:
        flash('Please Login first.','danger')
        return redirect(url_for('Login'))

    stmt = 'Select c.Criminal_id,c.Name,c.Age,c.Nationality,c.Nid_No,c.Motive,c.Phone_No,c.Address,cr.Remark from criminal c, Criminal_Remarks cr where c.Criminal_id = cr.Criminal_id'
    crims = db.session.execute(stmt).fetchall()
    if(request.method == 'POST'):
        return redirect(url_for('insert_criminal'))
    return render_template('dashboard-criminal.html', data=crims, head=crims[0].keys(), flag=False)


@app.route('/dashboard/criminals/insert', methods=['GET','POST'])
def insert_criminal():
    insert_info = CriminalForm()
    if insert_info.validate_on_submit():
        name = insert_info.name.data
        age = insert_info.age.data
        nationality = insert_info.nationality.data
        motive = insert_info.motive.data
        phone_number = insert_info.phone_number.data
        address = insert_info.address.data
        remark = insert_info.remark.data
        nid_no = insert_info.nid_no.data

        crim = criminal(Name=name, Age=age, Nationality=nationality,
            Motive=motive, Phone_No=phone_number, Address=address,NID_No=nid_no)
        db.session.add(crim)
        db.session.commit()

        latest_crim = criminal.query.filter_by(NID_No=nid_no).first()
        crim_remark = criminal_remarks(Criminal_id=latest_crim.Criminal_id, Remark=remark)
        db.session.add(crim_remark)
        db.session.commit()

        return redirect(url_for('showcriminals'))
    return render_template('dashboard-criminal.html', flag=True, form=insert_info)



@app.route('/validate',methods=['GET','POST'])
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
            stmt='Select * from police_officers'
            crims = db.session.execute(stmt).fetchall()
            return redirect(url_for('validate'))

    stmt1 = 'SELECT * from police_officers'
    stmt2 = 'select * from crime'
    pol = db.session.execute(stmt1).fetchall()
    crim = db.session.execute(stmt2).fetchall()
    Off=clr_form.Off.data
    Cas=clr_form.Cas.data
    o1_obj = police_officers.query.filter_by(Officer_id=Off).first()
    p1_obj = crime.query.filter_by(Case_No=Cas).first()
    if o1_obj or p1_obj:
        '''stmt1 = 'Select o.Username,o.Officer_id,o.Station,o.Rank,o.Clearance from Users u, police_officers o where o.Username = u.Username and o.officer_id = "'+Off+'"'
        pol1 = db.session.execute(stmt1).fetchall()
        return render_template('present.html', data1=pol1, head1=pol1[0].keys())
    if p1_obj:
        stmt2='Select c.Case_No,i.Officer_id  AS Investigated_By , co.Criminal_id,cr.Name AS Criminal_Name,c.Crime_date,c.End_date,c.Address,c.Clearance from  investigate_by i ,crime c, criminal cr, Committed_by co where c.Case_No = co.Case_No AND cr.Criminal_id = co.Criminal_id AND i.Case_No = co.Case_No AND c.Case_No = "'+Cas+'"'
        crim2 = db.session.execute(stmt2).fetchall()'''
        if o1_obj:
            return redirect(url_for('Search',keys1=Off))
        if p1_obj:
            return  redirect(url_for('Search',keys1=Cas))


    return render_template("security_clearance.html", flag=True, form=clr_form, data1=pol, head1=pol[0].keys(), data2=crim, head2=crim[0].keys())



@app.route ('/search/<keys1>', methods=['GET','POST'])
def Search(keys1):
    clr_form = SecurityForm()
    o1_obj = police_officers.query.filter_by(Officer_id=keys1).first()
    p1_obj = crime.query.filter_by(Case_No=keys1).first()
    if o1_obj:
        stmt1 = 'Select o.Username,o.Officer_id,o.Station,o.Rank,o.Clearance from Users u, police_officers o where o.Username = u.Username and o.officer_id = "'+keys1+'"'
        pol1 = db.session.execute(stmt1).fetchall()
        return render_template('security_clearance.html',form=clr_form, data=pol1, head=pol1[0].keys(), flag=False)
    elif p1_obj:
        stmt2='Select c.Case_No,i.Officer_id  AS Investigated_By , co.Criminal_id,cr.Name AS Criminal_Name,c.Crime_date,c.End_date,c.Address,c.Clearance from  investigate_by i ,crime c, criminal cr, Committed_by co where c.Case_No = co.Case_No AND cr.Criminal_id = co.Criminal_id AND i.Case_No = co.Case_No AND c.Case_No = "'+keys1+'"'
        crim2 = db.session.execute(stmt2).fetchall()
        return render_template('security_clearance.html',form=clr_form, data=crim2, head=crim2[0].keys(), flag=False)
    return render_template("security_clearance.html", form=clr_form)








@app.route ('/show1', methods=['GET','POST'])
def Table():
    tb_form = TableForm()
    if tb_form.validate_on_submit():
        s=tb_form.T_name.data
        if s=='Report On Officer':
        #return render_template("present.html", query=Users.query.all(),form=tb_form,c=1)
            stmt = 'Select o.Username,u.Name,o.Officer_id,u.NID_No,u.Gender,u.Phone_No,u.Personal_email,u.Department_email,o.Station,o.Rank,o.Clearance from Users u, police_officers o where u.username = o.username'
            crims = db.session.execute(stmt).fetchall()
            return render_template('present.html', data=crims, head=crims[0].keys())
        elif s=='Crime Report':
            stmt='Select c.Case_No,i.Officer_id  AS Investigated_By , co.Criminal_id,cr.Name AS Criminal_Name,c.Crime_date,c.End_date,c.Address,c.Clearance from  investigate_by i ,crime c, criminal cr, Committed_by co where c.Case_No = co.Case_No AND cr.Criminal_id = co.Criminal_id AND i.Case_No = co.Case_No'
            crims = db.session.execute(stmt).fetchall()
            return render_template('present.html', data=crims, head=crims[0].keys())
        elif s=="Criminal Report":
            stmt = 'Select c.Criminal_id,c.Name,c.Age,c.Nationality,c.Nid_No,c.Motive,c.Phone_No,c.Address,cr.Remark from criminal c, Criminal_Remarks cr where c.Criminal_id = cr.Criminal_id'
            crims = db.session.execute(stmt).fetchall()
            return render_template('present.html', data=crims, head=crims[0].keys())
        elif s=='Medical Team':
            stmt = 'Select * from medical_history'
            crims = db.session.execute(stmt).fetchall()
            return render_template('present.html', data=crims, head=crims[0].keys())
    return render_template('any_table.html', form=tb_form)


@app.route ('/create_table', methods=['GET','POST'])
def Attr():
    at_form = AttributeForm()

    return render_template('Create_Table.html', c=1,form=at_form)


@app.route ('/complete', methods=['GET','POST'])
def TableCall():
    at_form = AttributeForm()
    if at_form.validate_on_submit():
        num = at_form.Atr.data
        return render_template('Create_Table.html',num=2,c=2)


    return redirect(url_for('Attr'))





'''@app.route('/test', methods=['GET'])
def test():
    testing = TestForm()
    return render_template('ff.html',attrs=1, form=testing)



@app.route('/test1', methods=['GET','POST'])
def test1():
    testing = TestForm()
    print(testing.name.data)
    print(testing.length.data)
    return 'hoise toh'''




if __name__ == "__main__":
    app.run(debug=True)   # Running the server with Debug mode on
