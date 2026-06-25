from datetime import datetime
from app import db

class ExperimentMilestone(db.Model):
    """实验里程碑模型"""
    __tablename__ = 'experiment_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 时间信息
    target_date = db.Column(db.Date)  # 目标完成日期
    completed_date = db.Column(db.Date)  # 实际完成日期
    
    # 状态
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, overdue
    
    # 关联阶段
    stage_name = db.Column(db.String(50))
    
    # 优先级
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # 排序
    order_index = db.Column(db.Integer, default=0)
    
    # 备注
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, experiment_id, title, **kwargs):
        self.experiment_id = experiment_id
        self.title = title
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def complete(self):
        """完成里程碑"""
        self.status = 'completed'
        self.completed_date = datetime.utcnow().date()
        db.session.commit()
    
    def is_overdue(self):
        """检查是否过期"""
        if self.target_date and self.status not in ['completed']:
            return datetime.utcnow().date() > self.target_date
        return False
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'title': self.title,
            'description': self.description,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'stage_name': self.stage_name,
            'priority': self.priority,
            'order_index': self.order_index,
            'notes': self.notes,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExperimentMilestone {self.title}>'