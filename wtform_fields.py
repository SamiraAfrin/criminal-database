from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from models import Users


def validate_credentials(form, field):
    '''
    This is checking the login info given by using, and checking
    if the database contains the user and if the password provided
    is the correct password.
    '''
    username_e = form.username.data
    pswd = field.data
    user_obj = Users.query.filter_by(Username=username_e).first()
    if user_obj is None:
        raise ValidationError("Username or Password do not match.")
    elif not pbkdf2_sha256.verify(pswd, user_obj.Pass):
        raise ValidationError("Username or Password do not match.")



class RegistrationForm(FlaskForm):
    '''
    This the where all the info from the Registration_Page gets store in.
    All the different attributes are each a input field in Registration_Page
    See the Registration_Page.html file to see how they are connected
    '''
    choice = ['Male', 'Female']

    fullname = StringField('fullname_label' , validators=[InputRequired(message="Input required")])
    password = PasswordField('password_label',validators=[InputRequired(message="Input required")])
    confirm_pswd = PasswordField('confirm_pswd_label',validators=[InputRequired(message="Input required"), EqualTo('password', message='Password doesn\'t match.')])
    personal_email = StringField('personal_email_label',validators=[InputRequired(message="Input required")])
    department_email = StringField('department_email_label',validators=[InputRequired(message="Input required")])
    sex = SelectField(u'Choose',choices=choice)
    phone_number = StringField('phone_number_label',validators=[InputRequired(message="Input required")])
    national_id_card_number = IntegerField('national_id_card_number_label',validators=[InputRequired(message="Input required")])
    username = StringField('username_label',validators=[InputRequired(message="Input required")])
    rank = StringField('rank_label',validators=[InputRequired(message="Input required")])
    station = StringField('station_label',validators=[InputRequired(message="Input required")])
    officer_id = StringField('officer_id_label',validators=[InputRequired(message="Input required")])
    submit_button = SubmitField('Register')

    def validate_username(self, username):
        '''
        This is validating if the username already exists in the database. If so, raises an ValidationError
        and form is not submitted.
        '''
        user_obj = Users.query.filter_by(Username=username.data).first()
        if user_obj:
            raise ValidationError("Username Already Exists. Choose Another.")


class LoginForm(FlaskForm):
    '''
    This the where all the info from the login page gets store in.
    All the different attributes are each a input field in login page.
    See the login.html file to see how they are connected
    '''
    username = StringField('username_label',validators=[InputRequired(message="Input required")])
    password = PasswordField('password_label',validators=[InputRequired(message="Input required"),validate_credentials])
    submit_button = SubmitField('Login')


class CriminalForm(FlaskForm):
    name = StringField('name_label', validators=[InputRequired()])
    age = IntegerField('age_label', validators=[InputRequired()])
    nationality = StringField('nationality_label')
    nid_no = IntegerField('nid_label')
    motive = StringField('motive_label')
    phone_number = StringField('phone_number_label')
    address = StringField('address_label')
    remark = StringField('remark_label')
    submit_button = SubmitField('Submit')






class SecurityForm(FlaskForm):
    choice = [1,2,3,4,5,6,7,8,9,10]
    Off = StringField('Offier_id_label' )
    Cas = StringField('Case_No_label' )

    Officer_id = StringField('Offier_id_label')
    Clearance = SelectField(u'Choose',choices=choice)


    submit_button = SubmitField()

class DataForm (FlaskForm):
    Officer_id = StringField('Offier_id_label')
    submit_button = SubmitField('Click Here')

class TableForm(FlaskForm):
    choice=['Report On Officer','Crime Report','Criminal Report','Medical Team']

    T_name = SelectField(u'Choose',choices=choice)
    submit_button = SubmitField('Click Here')

class AttributeForm(FlaskForm):
    Atr= IntegerField('Attrubute_label', validators=[InputRequired(message="InputRequired")])
    submit_button = SubmitField('Click Here')



class TestForm(FlaskForm):
    name = StringField()
    length = IntegerField()
