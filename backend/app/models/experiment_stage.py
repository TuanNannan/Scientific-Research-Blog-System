from datetime import datetime
from app import db

class ExperimentStage(db.Model):
    """实验阶段模型"""
    __tablename__ = 'experiment_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    stage_name = db.Column(db.String(50), nullable=False)  # data_prep, model_design, training, evaluation, analysis
    stage_label = db.Column(db.String(100))  # 阶段显示名称
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, skipped
    progress = db.Column(db.Float, default=0.0)  # 0-100
    
    # 阶段配置
    config = db.Column(db.JSON)  # 阶段相关配置
    
    # 时间信息
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 持续时间（秒）
    
    # 备注
    notes = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)  # 排序索引
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 阶段名称映射
    STAGE_NAMES = {
        'data_prep': '数据准备',
        'model_design': '模型设计',
        'training': '模型训练',
        'evaluation': '评估测试',
        'analysis': '结果分析'
    }
    
    def __init__(self, experiment_id, stage_name, order_index=0, **kwargs):
        self.experiment_id = experiment_id
        self.stage_name = stage_name
        self.stage_label = self.STAGE_NAMES.get(stage_name, stage_name)
        self.order_index = order_index
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def start(self):
        """开始阶段"""
        self.status = 'in_progress'
        self.start_time = datetime.utcnow()
        db.session.commit()
    
    def complete(self):
        """完成阶段"""
        self.status = 'completed'
        self.progress = 100.0
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
        db.session.commit()
    
    def skip(self):
        """跳过阶段"""
        self.status = 'skipped'
        db.session.commit()
    
    def update_progress(self, progress):
        """更新进度"""
        self.progress = min(100.0, max(0.0, progress))
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'stage_name': self.stage_name,
            'stage_label': self.stage_label,
            'status': self.status,
            'progress': self.progress,
            'config': self.config,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'notes': self.notes,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExperimentStage {self.stage_name}: {self.status}>'