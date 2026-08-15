# -*- coding: utf-8 -*-
import os
import sys
import click
from flask import Flask, render_template, request, redirect, flash, url_for, session,abort
from flask_sqlalchemy import SQLAlchemy
from forms import ArticleForm, RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'wjz5566')

# 数据库配置
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/wujz456/articles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义文章模型
article_tags = db.Table(
    'article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False,unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
from functools import wraps

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))  # 外键
    body = db.Column(db.Text, nullable=False)   # 正文
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    articles = db.relationship('Article', backref='author', cascade='all, delete-orphan')  # 一对多：一个作者多篇文章

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    articles = db.relationship('Article', secondary=article_tags, backref='tags')
   
# 创建表（首次运行自动建表）
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ArticleForm()
    form.author_id.choices = [(a.id, a.name) for a in Author.query.all()]
    form.tag_ids.choices = [(t.id, t.name) for t in Tag.query.all()]
    #从数据库查出所有作者，变成 [(1, '小明'), (2, '小红')] 这种格式——第一个是提交的值，第二个是下拉框显示的文字。
    if request.method == 'POST' and 'user_id' not in session:
        flash('请先登录！')
        return redirect(url_for('login'))
    if form.validate_on_submit():
        title = form.title.data
        category = form.category.data
        body = form.body.data
        new_article = Article(title=title, category=category, body=body, author_id=form.author_id.data)
        new_article.tags = Tag.query.filter(Tag.id.in_(form.tag_ids.data)).all()
        db.session.add(new_article)
        db.session.commit()
        
        flash('文章《%s》已添加！' % title)
        return redirect(url_for('index'))
    
    category_filter = request.args.get('category', '')
    if category_filter:
        articles = db.session.query(Article).filter(Article.category == category_filter).all()
    else:
        articles = db.session.query(Article).all()
        
    categories = db.session.query(Article.category).distinct().all()
    categories = [item[0] for item in categories]
    return render_template('home.html', form=form, articles=articles, categories=categories, category_filter=category_filter)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 1. 先查用户名有没有被占用
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('用户名已被注册！')
        else:
            # 2. 创建用户，密码用 set_password 哈希后存
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录！')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 1. 按用户名查用户
        user = User.query.filter_by(username=form.username.data).first()
        # 2. 用户存在 且 密码正确
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id      # 戴上"手环"
            flash('登录成功，欢迎 %s！' % user.username)
            return redirect(url_for('index'))
        flash('用户名或密码错误！')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)   # 摘下手环
    flash('已退出登录！')
    return redirect(url_for('index'))

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        abort(404)   # 查不到文章返回 404 页面
    return render_template('article_detail.html', article=article)

@app.route('/authors', methods=['GET', 'POST'])
@login_required
def authors():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            db.session.add(Author(name=name))
            db.session.commit()
            flash('作者《%s》已添加！' % name)
            return redirect(url_for('authors'))
        else:
            flash('作者名字不能为空！')
    author_list = Author.query.all()
    return render_template('authors.html', authors=author_list)

@app.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            db.session.add(Tag(name=name))
            db.session.commit()
            flash('标签《%s》已添加！' % name)
            return redirect(url_for('tags'))
        else:
            flash('标签名字不能为空！')
    tag_list = Tag.query.all()
    return render_template('tags.html', tags=tag_list)

@app.route('/tag/<int:tag_id>')
def tag_detail(tag_id):
    tag = db.session.get(Tag, tag_id)
    if not tag:
        flash('找不到这个标签！')
        return redirect(url_for('tags'))
    articles = tag.articles          # 多对多的反向查询：这个标签下所有文章
    return render_template('tag_detail.html', tag=tag, articles=articles)

@app.route('/delete_tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_id):
    if request.method == 'POST':
        tag = db.session.get(Tag, tag_id)
        if tag:
            db.session.delete(tag)
            db.session.commit()
            flash('标签%s已删除！' % tag.name)
        else:
            flash('找不到标签！')
    return redirect(url_for('index'))


@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    if 'q' in request.args and not keyword:
        flash('请输入搜索关键词！')
        return redirect(url_for('index'))
    flash('提示：试试搜索"Flask"')
    if keyword:
        result = db.session.query(Article).filter(Article.title.contains(keyword)).all()
    
    else:
        result = []
    return render_template('search.html', keyword=keyword, result=result)

@app.route('/delete/<title>', methods=['GET', 'POST'])
@login_required
def delete_article(title):
    if request.method == 'POST':
        article = db.session.query(Article).filter(Article.title == title).first()
        if article:
            db.session.delete(article)
            db.session.commit()
            flash('文章《%s》已删除！' % title)
        else:
            flash('找不到文章《%s》！' % title)
    return redirect(url_for('index'))

@app.route('/delete_author/<int:author_id>', methods=['GET', 'POST'])
@login_required
def delete_author(author_id):
    if request.method == 'POST':
        author = db.session.get(Author, author_id)
        if author:
            db.session.delete(author)
            db.session.commit()
            flash('作者%s已删除！' % author.name)
        else:
            flash('找不到作者！')
    return redirect(url_for('index'))

# ---- 新增：编辑文章（Update） ----
@app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        flash('找不到这篇文章！')
        return redirect(url_for('index'))

    form = ArticleForm()
    form.tag_ids.choices = [(t.id, t.name) for t in Tag.query.all()]
    form.author_id.choices = [(a.id, a.name) for a in Author.query.all()]
    if form.validate_on_submit():
        article.title = form.title.data
        article.category = form.category.data
        article.tags = Tag.query.filter(Tag.id.in_(form.tag_ids.data)).all()
        article.author_id = form.author_id.data
        article.body = form.body.data
        db.session.commit()
        flash('文章《%s》已更新！' % article.title)
        return redirect(url_for('index'))

    form.title.data = article.title
    form.category.data = article.category
    form.body.data = article.body
    form.tag_ids.data = [t.id for t in article.tags]
    return render_template('edit.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500