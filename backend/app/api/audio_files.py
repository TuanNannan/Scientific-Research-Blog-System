import os
from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.api import bp
from app.models.audio_file import AudioFile
from app.models.experiment import Experiment
from app import db
from config import Config

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_AUDIO_EXTENSIONS

@bp.route('/experiments/<int:experiment_id>/audio', methods=['GET'])
@jwt_required()
def get_audio_files(experiment_id):
    """获取实验的音频文件列表"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    audio_files = AudioFile.query.filter_by(experiment_id=experiment_id)\
        .order_by(AudioFile.uploaded_at.desc()).all()
    
    return jsonify([audio_file.to_dict() for audio_file in audio_files])

@bp.route('/experiments/<int:experiment_id>/audio', methods=['POST'])
@jwt_required()
def upload_audio_file(experiment_id):
    """上传音频文件"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    # 创建实验目录
    experiment_dir = os.path.join(Config.AUDIO_UPLOAD_FOLDER, str(experiment_id))
    os.makedirs(experiment_dir, exist_ok=True)
    
    file_path = os.path.join(experiment_dir, filename)
    file.save(file_path)
    
    # 获取文件信息
    file_size = os.path.getsize(file_path)
    
    # 这里可以添加音频文件信息提取（使用librosa）
    # 暂时使用默认值
    audio_file = AudioFile(
        experiment_id=experiment_id,
        file_name=filename,
        file_path=file_path,
        file_size=file_size,
        file_format=filename.rsplit('.', 1)[1].lower(),
        speaker_info=request.form.get('speaker_info'),
        transcription=request.form.get('transcription'),
        labels=request.form.get('labels')
    )
    
    db.session.add(audio_file)
    db.session.commit()
    
    return jsonify({
        'message': 'Audio file uploaded successfully',
        'audio_file': audio_file.to_dict()
    }), 201

@bp.route('/audio/<int:audio_id>', methods=['GET'])
@jwt_required()
def get_audio_file(audio_id):
    """获取音频文件信息"""
    user_id = int(get_jwt_identity())
    audio_file = AudioFile.query.get_or_404(audio_id)
    experiment = Experiment.query.get_or_404(audio_file.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(audio_file.to_dict())

@bp.route('/audio/<int:audio_id>/download', methods=['GET'])
@jwt_required()
def download_audio_file(audio_id):
    """下载音频文件"""
    user_id = int(get_jwt_identity())
    audio_file = AudioFile.query.get_or_404(audio_id)
    experiment = Experiment.query.get_or_404(audio_file.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    if not os.path.exists(audio_file.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        audio_file.file_path,
        as_attachment=True,
        download_name=audio_file.file_name
    )

@bp.route('/audio/<int:audio_id>', methods=['PUT'])
@jwt_required()
def update_audio_file(audio_id):
    """更新音频文件信息"""
    user_id = int(get_jwt_identity())
    audio_file = AudioFile.query.get_or_404(audio_id)
    experiment = Experiment.query.get_or_404(audio_file.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'speaker_info' in data:
        audio_file.speaker_info = data['speaker_info']
    if 'transcription' in data:
        audio_file.transcription = data['transcription']
    if 'labels' in data:
        audio_file.labels = data['labels']
    if 'annotation' in data:
        audio_file.annotation = data['annotation']
    if 'metadata' in data:
        audio_file.metadata = data['metadata']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Audio file updated successfully',
        'audio_file': audio_file.to_dict()
    })

@bp.route('/audio/<int:audio_id>', methods=['DELETE'])
@jwt_required()
def delete_audio_file(audio_id):
    """删除音频文件"""
    user_id = int(get_jwt_identity())
    audio_file = AudioFile.query.get_or_404(audio_id)
    experiment = Experiment.query.get_or_404(audio_file.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 删除文件
    if os.path.exists(audio_file.file_path):
        os.remove(audio_file.file_path)
    
    db.session.delete(audio_file)
    db.session.commit()
    
    return jsonify({'message': 'Audio file deleted successfully'})

@bp.route('/audio/stats', methods=['GET'])
@jwt_required()
def get_audio_stats():
    """获取音频文件统计信息"""
    user_id = int(get_jwt_identity())
    
    # 获取用户的实验ID
    experiment_ids = [exp.id for exp in Experiment.query.filter_by(researcher_id=user_id).all()]
    
    if not experiment_ids:
        return jsonify({
            'total_files': 0,
            'total_size_mb': 0,
            'total_duration': 0
        })
    
    # 统计信息
    total_files = AudioFile.query.filter(AudioFile.experiment_id.in_(experiment_ids)).count()
    total_size = db.session.query(db.func.sum(AudioFile.file_size))\
        .filter(AudioFile.experiment_id.in_(experiment_ids)).scalar() or 0
    total_duration = db.session.query(db.func.sum(AudioFile.duration))\
        .filter(AudioFile.experiment_id.in_(experiment_ids)).scalar() or 0
    
    return jsonify({
        'total_files': total_files,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'total_duration': round(total_duration, 2)
    })