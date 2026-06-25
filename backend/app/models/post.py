from datetime import datetime
from app import db

class Post(db.Model):
    """博客文章模型"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.JSON)  # 存储标签数组
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    featured_image = db.Column(db.String(255))
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    
    def __init__(self, title, content, author_id, category=None, tags=None):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.category = category
        self.tags = tags or []
    
    def increment_views(self):
        """增加浏览次数"""
        self.views_count += 1
        db.session.commit()
    
    def increment_likes(self):
        """增加点赞次数"""
        self.likes_count += 1
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'category': self.category,
            'tags': self.tags,
            'status': self.status,
            'featured_image': self.featured_image,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comments_count': self.comments.count()
        }
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 回复评论
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    author = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'author_name': self.author.username if self.author else None,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'replies_count': self.replies.count()
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'