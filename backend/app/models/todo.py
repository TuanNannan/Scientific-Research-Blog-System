from datetime import datetime
from app import db

class Todo(db.Model):
    """待办事项模型"""
    __tablename__ = 'todos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # 如: 实验、论文、会议、日常
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)  # 预计工时
    actual_hours = db.Column(db.Float)  # 实际工时
    notes = db.Column(db.Text)  # 备注
    
    # 关系
    tags = db.relationship('TodoTag', backref='todo', lazy='dynamic', cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, user_id, **kwargs):
        self.title = title
        self.user_id = user_id
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def complete(self):
        """完成待办事项"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """取消待办事项"""
        self.status = 'cancelled'
        db.session.commit()
    
    def is_overdue(self):
        """检查是否过期"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    def get_priority_weight(self):
        """获取优先级权重"""
        weights = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'urgent': 4
        }
        return weights.get(self.priority, 2)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'notes': self.notes,
            'tags': [tag.to_dict() for tag in self.tags],
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Todo {self.title}>'


class TodoTag(db.Model):
    """待办事项标签模型"""
    __tablename__ = 'todo_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    
    def __init__(self, todo_id, tag):
        self.todo_id = todo_id
        self.tag = tag
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'todo_id': self.todo_id,
            'tag': self.tag
        }
    
    def __repr__(self):
        return f'<TodoTag {self.tag}>'