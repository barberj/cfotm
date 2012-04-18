from wtforms import Form, TextField, PasswordField, validators

class SignupForm(Form):
    email = TextField('Email',
                    [validators.Required(),
                     validators.Email()])
    password = PasswordField('Password',
                    [validators.Required(),
                     validators.EqualTo('password_confirm',
                                    message="Passwords must match.")])
    password_confirm = PasswordField('Confirm Password',
                        [validators.Required()])
