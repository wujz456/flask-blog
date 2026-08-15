import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

# 1. 创建数据库引擎
engine = create_engine('sqlite:///test.db', echo=True)  # 用 SQLite 数据库，文件名叫 test.db，放在当前目录。

# 2. 定义模型基类
Base = declarative_base()#像造了一个"空白申请表模板"，之后每个模型类都从它继承

# 3. 定义文章模型
class Article(Base):
    __tablename__ = 'articles' # 数据库里实际表名是 articles
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)

# 4. 创建表
Base.metadata.create_all(engine)#检查一下 Article 这个模型，在数据库里有没有对应的表？没有就创建

# 5. 插入数据
session = Session(engine)#是一张"工作台"。 你对数据的所有操作（增、删、改），都要在工作台上进行。
a1 = Article(title='数据库入门', category='基础')
session.add(a1)#把这一行放在工作台上
session.commit()#"确认提交"，正式写入数据库文件
a2 = Article(title='SQLAlchemy 入门', category='进阶')
session.add(a2)
session.commit()
# 6. 查询
result = session.query(Article).all()#在工作台上执行查询，获取所有文章记录
for a in result:
    print(f'ID: {a.id}, 标题: {a.title}, 分类: {a.category}')

session.close()
