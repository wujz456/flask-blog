
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,SelectMultipleField,PasswordField,TextAreaField
from wtforms.validators import DataRequired,Length, ValidationError

class ArticleForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    category = StringField('分类', validators=[DataRequired()])
    author_id = SelectField('作者', coerce=int)#coerce=int 表示"收到后自动转成整数 1"，正好匹配外键的整数类型
    tag_ids = SelectMultipleField('标签', coerce=int)
    body = TextAreaField('正文', validators=[DataRequired()])
    submit = SubmitField('提交')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128)])
    submit = SubmitField('注册')
    def validate_username(self, field):
        from app import User 
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('用户名已被注册')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')