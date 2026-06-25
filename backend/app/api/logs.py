from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.experiment import Experiment
from app.models.experiment_log import ExperimentLog
from app import db

@bp.route('/experiments/<int:experiment_id>/logs', methods=['GET'])
@jwt_required()
def get_logs(experiment_id):
    """获取实验日志列表"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    log_type = request.args.get('log_type')
    stage_name = request.args.get('stage_name')
    
    query = ExperimentLog.query.filter_by(experiment_id=experiment_id)
    
    # 过滤条件
    if log_type:
        query = query.filter_by(log_type=log_type)
    if stage_name:
        query = query.filter_by(stage_name=stage_name)
    
    # 分页
    logs = query.order_by(ExperimentLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })

@bp.route('/experiments/<int:experiment_id>/logs', methods=['POST'])
@jwt_required()
def create_log(experiment_id):
    """创建实验日志"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    log = ExperimentLog(
        experiment_id=experiment_id,
        content=content,
        log_type=data.get('log_type', 'info'),
        title=data.get('title'),
        stage_name=data.get('stage_name'),
        metric_name=data.get('metric_name'),
        metric_value=data.get('metric_value'),
        metadata=data.get('metadata')
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Log created successfully',
        'log': log.to_dict()
    }), 201

@bp.route('/experiments/<int:experiment_id>/logs/batch', methods=['POST'])
@jwt_required()
def create_logs_batch(experiment_id):
    """批量创建实验日志"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'logs' not in data:
        return jsonify({'error': 'Logs array is required'}), 400
    
    logs_data = data['logs']
    created_logs = []
    
    for log_data in logs_data:
        content = log_data.get('content')
        if not content:
            continue
        
        log = ExperimentLog(
            experiment_id=experiment_id,
            content=content,
            log_type=log_data.get('log_type', 'info'),
            title=log_data.get('title'),
            stage_name=log_data.get('stage_name'),
            metric_name=log_data.get('metric_name'),
            metric_value=log_data.get('metric_value'),
            metadata=log_data.get('metadata')
        )
        
        db.session.add(log)
        created_logs.append(log)
    
    db.session.commit()
    
    return jsonify({
        'message': f'{len(created_logs)} logs created successfully',
        'logs': [log.to_dict() for log in created_logs]
    }), 201

@bp.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """获取单个日志"""
    user_id = int(get_jwt_identity())
    log = ExperimentLog.query.get_or_404(log_id)
    experiment = Experiment.query.get_or_404(log.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(log.to_dict())

@bp.route('/logs/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_log(log_id):
    """更新日志"""
    user_id = int(get_jwt_identity())
    log = ExperimentLog.query.get_or_404(log_id)
    experiment = Experiment.query.get_or_404(log.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'content' in data:
        log.content = data['content']
    if 'title' in data:
        log.title = data['title']
    if 'log_type' in data:
        log.log_type = data['log_type']
    if 'stage_name' in data:
        log.stage_name = data['stage_name']
    if 'metadata' in data:
        log.extra_metadata = data['metadata']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Log updated successfully',
        'log': log.to_dict()
    })

@bp.route('/logs/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_log(log_id):
    """删除日志"""
    user_id = int(get_jwt_identity())
    log = ExperimentLog.query.get_or_404(log_id)
    experiment = Experiment.query.get_or_404(log.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(log)
    db.session.commit()
    
    return jsonify({'message': 'Log deleted successfully'})

@bp.route('/experiments/<int:experiment_id>/logs/timeline', methods=['GET'])
@jwt_required()
def get_logs_timeline(experiment_id):
    """获取实验日志时间线"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 按日期分组获取日志
    logs = ExperimentLog.query.filter_by(experiment_id=experiment_id)\
        .order_by(ExperimentLog.created_at.asc()).all()
    
    # 按日期分组
    timeline = {}
    for log in logs:
        date_key = log.created_at.strftime('%Y-%m-%d')
        if date_key not in timeline:
            timeline[date_key] = []
        timeline[date_key].append(log.to_dict())
    
    return jsonify(timeline)