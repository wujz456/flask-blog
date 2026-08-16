# Flask 文章博客系统

一个基于 Flask 的文章博客系统，支持用户注册登录、文章 CRUD、标签、作者管理等。

## 在线体验

http://wujz456.pythonanywhere.com

## 功能

- 用户注册、登录、登出，登录保护
- 文章增删改查 + 正文 + 详情页
- 作者管理（一对多，级联删除）
- 标签管理（多对多）
- 分类筛选、标题搜索
- 密码哈希存储、CSRF 防护

## 技术栈

- Flask 3
- Flask-SQLAlchemy
- Flask-WTF
- SQLite

## 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/wujz456/flask-blog.git
cd flask-blog

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python init_db.py

# 4. 运行
flask run
```

## 项目结构

```
flask-blog/
├── app.py              # 主程序
├── forms.py            # 表单类
├── init_db.py          # 数据库初始化
├── requirements.txt    # 依赖
├── templates/          # 模板
└── static/             # 静态文件
```