from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.experiment import Experiment
from app.models.experiment_stage import ExperimentStage
from app import db

@bp.route('/experiments/<int:experiment_id>/stages', methods=['GET'])
@jwt_required()
def get_stages(experiment_id):
    """获取实验阶段列表"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    stages = ExperimentStage.query.filter_by(experiment_id=experiment_id)\
        .order_by(ExperimentStage.order_index.asc()).all()
    
    return jsonify([stage.to_dict() for stage in stages])

@bp.route('/experiments/<int:experiment_id>/stages', methods=['POST'])
@jwt_required()
def create_stage(experiment_id):
    """创建实验阶段"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    stage_name = data.get('stage_name')
    if not stage_name:
        return jsonify({'error': 'Stage name is required'}), 400
    
    # 获取最大排序索引
    max_order = db.session.query(db.func.max(ExperimentStage.order_index))\
        .filter_by(experiment_id=experiment_id).scalar() or 0
    
    stage = ExperimentStage(
        experiment_id=experiment_id,
        stage_name=stage_name,
        order_index=data.get('order_index', max_order + 1),
        config=data.get('config'),
        notes=data.get('notes')
    )
    
    db.session.add(stage)
    db.session.commit()
    
    return jsonify({
        'message': 'Stage created successfully',
        'stage': stage.to_dict()
    }), 201

@bp.route('/experiments/<int:experiment_id>/stages/init', methods=['POST'])
@jwt_required()
def init_stages(experiment_id):
    """初始化实验阶段（创建默认阶段）"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 检查是否已有阶段
    existing_stages = ExperimentStage.query.filter_by(experiment_id=experiment_id).count()
    if existing_stages > 0:
        return jsonify({'error': 'Stages already initialized'}), 400
    
    # 创建默认阶段
    default_stages = [
        ('data_prep', 0),
        ('model_design', 1),
        ('training', 2),
        ('evaluation', 3),
        ('analysis', 4)
    ]
    
    stages = []
    for stage_name, order_index in default_stages:
        stage = ExperimentStage(
            experiment_id=experiment_id,
            stage_name=stage_name,
            order_index=order_index
        )
        db.session.add(stage)
        stages.append(stage)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stages initialized successfully',
        'stages': [stage.to_dict() for stage in stages]
    }), 201

@bp.route('/stages/<int:stage_id>', methods=['GET'])
@jwt_required()
def get_stage(stage_id):
    """获取单个阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(stage.to_dict())

@bp.route('/stages/<int:stage_id>', methods=['PUT'])
@jwt_required()
def update_stage(stage_id):
    """更新阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'config' in data:
        stage.config = data['config']
    if 'notes' in data:
        stage.notes = data['notes']
    if 'order_index' in data:
        stage.order_index = data['order_index']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stage updated successfully',
        'stage': stage.to_dict()
    })

@bp.route('/stages/<int:stage_id>', methods=['DELETE'])
@jwt_required()
def delete_stage(stage_id):
    """删除阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(stage)
    db.session.commit()
    
    return jsonify({'message': 'Stage deleted successfully'})

@bp.route('/stages/<int:stage_id>/start', methods=['POST'])
@jwt_required()
def start_stage(stage_id):
    """开始阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    stage.start()
    
    return jsonify({
        'message': 'Stage started successfully',
        'stage': stage.to_dict()
    })

@bp.route('/stages/<int:stage_id>/complete', methods=['POST'])
@jwt_required()
def complete_stage(stage_id):
    """完成阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    stage.complete()
    
    return jsonify({
        'message': 'Stage completed successfully',
        'stage': stage.to_dict()
    })

@bp.route('/stages/<int:stage_id>/skip', methods=['POST'])
@jwt_required()
def skip_stage(stage_id):
    """跳过阶段"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    stage.skip()
    
    return jsonify({
        'message': 'Stage skipped successfully',
        'stage': stage.to_dict()
    })

@bp.route('/stages/<int:stage_id>/progress', methods=['PUT'])
@jwt_required()
def update_stage_progress(stage_id):
    """更新阶段进度"""
    user_id = int(get_jwt_identity())
    stage = ExperimentStage.query.get_or_404(stage_id)
    experiment = Experiment.query.get_or_404(stage.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'progress' not in data:
        return jsonify({'error': 'Progress is required'}), 400
    
    stage.update_progress(data['progress'])
    
    return jsonify({
        'message': 'Stage progress updated successfully',
        'stage': stage.to_dict()
    })