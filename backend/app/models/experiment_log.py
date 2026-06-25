from datetime import datetime
from app import db

class ExperimentLog(db.Model):
    """实验日志模型"""
    __tablename__ = 'experiment_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    log_type = db.Column(db.String(20), default='info')  # info, warning, error, milestone, debug
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    
    # 关联信息
    stage_name = db.Column(db.String(50))  # 关联的阶段
    metric_name = db.Column(db.String(50))  # 关联的指标
    metric_value = db.Column(db.Float)  # 指标值
    
    # 元数据
    extra_metadata = db.Column('metadata', db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 日志类型映射
    LOG_TYPES = {
        'info': '信息',
        'warning': '警告',
        'error': '错误',
        'milestone': '里程碑',
        'debug': '调试'
    }
    
    def __init__(self, experiment_id, content, log_type='info', **kwargs):
        self.experiment_id = experiment_id
        self.content = content
        self.log_type = log_type
        for key, value in kwargs.items():
            if key == 'metadata':
                self.extra_metadata = value
            else:
                setattr(self, key, value)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'log_type': self.log_type,
            'log_type_label': self.LOG_TYPES.get(self.log_type, self.log_type),
            'title': self.title,
            'content': self.content,
            'stage_name': self.stage_name,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metadata': self.extra_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ExperimentLog {self.log_type}: {self.title}>'