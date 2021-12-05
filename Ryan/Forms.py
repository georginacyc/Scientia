from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators

class CreateUserForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    lastName = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1, max=150), validators.DataRequired()])
    password = StringField('Password', [validators.Length(min=1, max=150), validators.DataRequired()])
    bio = StringField('About Me', [validators.Length(min=1, max=300), validators.DataRequired()])
    learn = StringField('Wants to Learn', [validators.Length(min=1, max=150), validators.DataRequired()])
    teach = StringField('Wants to Teach', [validators.Length(min=1, max=150), validators.DataRequired()])
