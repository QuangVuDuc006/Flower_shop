from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[DataRequired()])
    price = FloatField('Giá', validators=[DataRequired()])
    category = SelectField('Danh mục', coerce=int, validators=[DataRequired()])
    stock = IntegerField('Số lượng kho', validators=[DataRequired()])
    description = TextAreaField('Mô tả')
    image = FileField('Ảnh sản phẩm')
    submit = SubmitField('Lưu sản phẩm')

class CheckoutForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired()])
    phone = StringField('Số điện thoại', validators=[DataRequired()])
    address = TextAreaField('Địa chỉ giao hàng', validators=[DataRequired()])
    submit = SubmitField('Đặt hàng ngay')