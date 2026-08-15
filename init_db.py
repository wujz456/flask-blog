from app import app, db, Author,Tag, User
with app.app_context():
    db.drop_all()      # 删掉所有旧表
    db.create_all()    # 按新模型重建（包含 authors 表 + articles 表的外键列）
    db.session.add(Author(name='小明'))
    db.session.add(Author(name='小红'))
    db.session.add(Tag(name='Flask'))
    db.session.add(Tag(name='数据库'))
    admin = User(username='admin')
    admin.set_password('password')   # set_password 内部会哈希
    db.session.add(admin)
    db.session.commit()
    print('数据库重建完成')