from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.post import Post, Comment
from app.models.user import User
from app import db

@bp.route('/posts', methods=['GET'])
def get_posts():
    """获取文章列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    tag = request.args.get('tag')
    status = request.args.get('status', 'published')
    
    query = Post.query
    
    # 过滤条件
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if tag:
        query = query.filter(Post.tags.contains([tag]))
    
    # 排序和分页
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': posts.page
    })

@bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """创建文章"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    content = data.get('content')
    
    if not all([title, content]):
        return jsonify({'error': 'Title and content are required'}), 400
    
    post = Post(
        title=title,
        content=content,
        author_id=user_id,
        category=data.get('category'),
        tags=data.get('tags', [])
    )
    
    # 设置可选字段
    if 'summary' in data:
        post.summary = data['summary']
    if 'status' in data:
        post.status = data['status']
    if 'featured_image' in data:
        post.featured_image = data['featured_image']
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'message': 'Post created successfully',
        'post': post.to_dict()
    }), 201

@bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单个文章"""
    post = Post.query.get_or_404(post_id)
    
    # 增加浏览次数
    post.increment_views()
    
    return jsonify(post.to_dict())

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """更新文章"""
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.author_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    if 'summary' in data:
        post.summary = data['summary']
    if 'category' in data:
        post.category = data['category']
    if 'tags' in data:
        post.tags = data['tags']
    if 'status' in data:
        post.status = data['status']
    if 'featured_image' in data:
        post.featured_image = data['featured_image']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Post updated successfully',
        'post': post.to_dict()
    })

@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """删除文章"""
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.author_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'})

@bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """点赞文章"""
    post = Post.query.get_or_404(post_id)
    post.increment_likes()
    
    return jsonify({
        'message': 'Post liked successfully',
        'likes_count': post.likes_count
    })

# 评论相关API
@bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """获取文章评论"""
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
        .order_by(Comment.created_at.desc()).all()
    
    return jsonify([comment.to_dict() for comment in comments])

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """创建评论"""
    user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    comment = Comment(
        content=data['content'],
        post_id=post_id,
        author_id=user_id,
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment created successfully',
        'comment': comment.to_dict()
    }), 201

@bp.route('/posts/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    categories = db.session.query(Post.category).distinct().all()
    return jsonify([category[0] for category in categories if category[0]])

@bp.route('/posts/tags', methods=['GET'])
def get_tags():
    """获取所有标签"""
    posts = Post.query.filter(Post.tags.isnot(None)).all()
    tags = set()
    for post in posts:
        if post.tags:
            tags.update(post.tags)
    return jsonify(list(tags))