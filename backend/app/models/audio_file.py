from datetime import datetime
import os
from app import db

class AudioFile(db.Model):
    """音频文件模型"""
    __tablename__ = 'audio_files'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    file_format = db.Column(db.String(20))  # 文件格式
    
    # 音频属性
    duration = db.Column(db.Float)  # 时长（秒）
    sample_rate = db.Column(db.Integer)  # 采样率
    channels = db.Column(db.Integer)  # 声道数
    bit_depth = db.Column(db.Integer)  # 位深度
    
    # 标注信息
    speaker_info = db.Column(db.JSON)  # 说话人信息
    transcription = db.Column(db.Text)  # 转录文本
    labels = db.Column(db.JSON)  # 标签
    annotation = db.Column(db.JSON)  # 标注信息
    
    # 元数据
    extra_metadata = db.Column('metadata', db.JSON)  # 其他元数据
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, experiment_id, file_name, file_path, **kwargs):
        self.experiment_id = experiment_id
        self.file_name = file_name
        self.file_path = file_path
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get_file_size_mb(self):
        """获取文件大小（MB）"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    def get_duration_formatted(self):
        """获取格式化的时长"""
        if self.duration:
            minutes = int(self.duration // 60)
            seconds = int(self.duration % 60)
            return f"{minutes:02d}:{seconds:02d}"
        return "00:00"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_mb': self.get_file_size_mb(),
            'file_format': self.file_format,
            'duration': self.duration,
            'duration_formatted': self.get_duration_formatted(),
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bit_depth': self.bit_depth,
            'speaker_info': self.speaker_info,
            'transcription': self.transcription,
            'labels': self.labels,
            'annotation': self.annotation,
            'metadata': self.extra_metadata,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self):
        return f'<AudioFile {self.file_name}>'