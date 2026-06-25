from datetime import datetime
from app import db

class Experiment(db.Model):
    """实验记录模型"""
    __tablename__ = 'experiments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    researcher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 模型相关
    model_architecture = db.Column(db.String(100))  # 如: CNN, RNN, Transformer
    model_version = db.Column(db.String(50))
    framework = db.Column(db.String(50))  # 如: PyTorch, TensorFlow
    
    # 实验配置
    hyperparameters = db.Column(db.JSON)  # 存储超参数
    dataset_info = db.Column(db.JSON)  # 数据集信息
    training_config = db.Column(db.JSON)  # 训练配置
    
    # 实验状态
    status = db.Column(db.String(20), default='planning')  # planning, running, completed, failed
    progress = db.Column(db.Float, default=0.0)  # 进度百分比
    
    # 时间信息
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 训练时长（秒）
    
    # 结果
    results = db.Column(db.JSON)  # 存储实验结果
    best_metric = db.Column(db.Float)  # 最佳指标值
    notes = db.Column(db.Text)  # 实验备注
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    audio_files = db.relationship('AudioFile', backref='experiment', lazy='dynamic')
    metrics = db.relationship('ExperimentMetric', backref='experiment', lazy='dynamic')
    
    def __init__(self, title, researcher_id, description=None):
        self.title = title
        self.researcher_id = researcher_id
        self.description = description
    
    def start_experiment(self):
        """开始实验"""
        self.status = 'running'
        self.start_date = datetime.utcnow()
        db.session.commit()
    
    def complete_experiment(self, results=None):
        """完成实验"""
        self.status = 'completed'
        self.end_date = datetime.utcnow()
        if self.start_date:
            self.duration = int((self.end_date - self.start_date).total_seconds())
        if results:
            self.results = results
        db.session.commit()
    
    def fail_experiment(self, error_message=None):
        """实验失败"""
        self.status = 'failed'
        self.end_date = datetime.utcnow()
        if self.start_date:
            self.duration = int((self.end_date - self.start_date).total_seconds())
        if error_message:
            self.notes = f"实验失败: {error_message}"
        db.session.commit()
    
    def update_progress(self, progress):
        """更新进度"""
        self.progress = min(100.0, max(0.0, progress))
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'researcher_id': self.researcher_id,
            'researcher_name': self.researcher.username if self.researcher else None,
            'model_architecture': self.model_architecture,
            'model_version': self.model_version,
            'framework': self.framework,
            'hyperparameters': self.hyperparameters,
            'dataset_info': self.dataset_info,
            'training_config': self.training_config,
            'status': self.status,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration': self.duration,
            'results': self.results,
            'best_metric': self.best_metric,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'audio_files_count': self.audio_files.count(),
            'metrics_count': self.metrics.count()
        }
    
    def __repr__(self):
        return f'<Experiment {self.title}>'