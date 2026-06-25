from datetime import datetime
from app import db

class ExperimentMetric(db.Model):
    """实验结果指标模型"""
    __tablename__ = 'experiment_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    metric_name = db.Column(db.String(50), nullable=False)  # 如: accuracy, loss, f1_score
    metric_value = db.Column(db.Float, nullable=False)
    epoch = db.Column(db.Integer)
    step = db.Column(db.Integer)
    phase = db.Column(db.String(20))  # train, validation, test
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 元数据
    extra_metadata = db.Column('metadata', db.JSON)  # 额外的元数据
    
    def __init__(self, experiment_id, metric_name, metric_value, **kwargs):
        self.experiment_id = experiment_id
        self.metric_name = metric_name
        self.metric_value = metric_value
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
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'epoch': self.epoch,
            'step': self.step,
            'phase': self.phase,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'metadata': self.extra_metadata
        }
    
    def __repr__(self):
        return f'<ExperimentMetric {self.metric_name}: {self.metric_value}>'