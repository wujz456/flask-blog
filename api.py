from flask import Blueprint
from app import Article, db,Tag
from flask import jsonify,request

api = Blueprint('api', __name__)
@api.route('/articles')
def get_articles():
    # 查询所有文章
    articles = Article.query.all()
    # 将文章对象转换为字典列表
    articles_list = []
    for article in articles:
        articles_list.append({
            'id': article.id,
            'title': article.title,
            'category': article.category,
            'body': article.body,
            'author': article.author.name if article.author else '未知作者',         # 一对多的反向访问
            'tags': [t.name for t in article.tags]  # 多对多的反向访问
})
    return {'articles': articles_list}

@api.route('/articles/<int:article_id>')
def get_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': '文章不存在'}), 404
    return jsonify({...})   # 和列表一样的字典

@api.route('/articles', methods=['POST'])
def create_article():
    
    data = request.json
    title = data.get('title')
    category = data.get('category')
    body = data.get('body')
    author_id = data.get('author_id')
    tag_ids = data.get('tag_ids', [])
    
    new_article = Article(title=title, category=category, body=body, author_id=author_id)
    new_article.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    db.session.add(new_article)
    db.session.commit()
    
    return jsonify({'message': '文章创建成功', 'article_id': new_article.id}), 201

@api.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': '文章不存在'}), 404
    
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({'message': '文章删除成功'}),200

@api.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    article = db.session.get(Article, article_id)
    if not article:
        return jsonify({'error': '文章不存在'}), 404
    
    data = request.json
    article.title = data.get('title', article.title)
    article.category = data.get('category', article.category)
    article.body = data.get('body', article.body)
    author_id = data.get('author_id')
    if author_id:
        article.author_id = author_id
    tag_ids = data.get('tag_ids')
    if tag_ids is not None:
        article.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    
    db.session.commit()
    
    return jsonify({'message': '文章更新成功'})

