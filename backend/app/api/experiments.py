from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.experiment import Experiment
from app.models.user import User
from app import db
from datetime import datetime

@bp.route('/experiments', methods=['GET'])
@jwt_required()
def get_experiments():
    """获取实验列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Experiment.query.filter_by(researcher_id=user_id)
    
    # 过滤条件
    if status:
        query = query.filter_by(status=status)
    
    # 排序和分页
    experiments = query.order_by(Experiment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'experiments': [exp.to_dict() for exp in experiments.items],
        'total': experiments.total,
        'pages': experiments.pages,
        'current_page': experiments.page
    })

@bp.route('/experiments', methods=['POST'])
@jwt_required()
def create_experiment():
    """创建实验"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    experiment = Experiment(
        title=title,
        researcher_id=user_id,
        description=data.get('description')
    )
    
    # 设置可选字段
    if 'model_architecture' in data:
        experiment.model_architecture = data['model_architecture']
    if 'model_version' in data:
        experiment.model_version = data['model_version']
    if 'framework' in data:
        experiment.framework = data['framework']
    if 'hyperparameters' in data:
        experiment.hyperparameters = data['hyperparameters']
    if 'dataset_info' in data:
        experiment.dataset_info = data['dataset_info']
    if 'training_config' in data:
        experiment.training_config = data['training_config']
    if 'notes' in data:
        experiment.notes = data['notes']
    
    db.session.add(experiment)
    db.session.commit()
    
    return jsonify({
        'message': 'Experiment created successfully',
        'experiment': experiment.to_dict()
    }), 201

@bp.route('/experiments/<int:experiment_id>', methods=['GET'])
@jwt_required()
def get_experiment(experiment_id):
    """获取单个实验"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(experiment.to_dict())

@bp.route('/experiments/<int:experiment_id>', methods=['PUT'])
@jwt_required()
def update_experiment(experiment_id):
    """更新实验"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'title' in data:
        experiment.title = data['title']
    if 'description' in data:
        experiment.description = data['description']
    if 'model_architecture' in data:
        experiment.model_architecture = data['model_architecture']
    if 'model_version' in data:
        experiment.model_version = data['model_version']
    if 'framework' in data:
        experiment.framework = data['framework']
    if 'hyperparameters' in data:
        experiment.hyperparameters = data['hyperparameters']
    if 'dataset_info' in data:
        experiment.dataset_info = data['dataset_info']
    if 'training_config' in data:
        experiment.training_config = data['training_config']
    if 'status' in data:
        experiment.status = data['status']
    if 'progress' in data:
        experiment.progress = data['progress']
    if 'notes' in data:
        experiment.notes = data['notes']
    if 'results' in data:
        experiment.results = data['results']
    if 'best_metric' in data:
        experiment.best_metric = data['best_metric']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Experiment updated successfully',
        'experiment': experiment.to_dict()
    })

@bp.route('/experiments/<int:experiment_id>', methods=['DELETE'])
@jwt_required()
def delete_experiment(experiment_id):
    """删除实验"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(experiment)
    db.session.commit()
    
    return jsonify({'message': 'Experiment deleted successfully'})

@bp.route('/experiments/<int:experiment_id>/start', methods=['POST'])
@jwt_required()
def start_experiment(experiment_id):
    """开始实验"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    experiment.start_experiment()
    
    return jsonify({
        'message': 'Experiment started successfully',
        'experiment': experiment.to_dict()
    })

@bp.route('/experiments/<int:experiment_id>/complete', methods=['POST'])
@jwt_required()
def complete_experiment(experiment_id):
    """完成实验"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    results = data.get('results') if data else None
    
    experiment.complete_experiment(results)
    
    return jsonify({
        'message': 'Experiment completed successfully',
        'experiment': experiment.to_dict()
    })

@bp.route('/experiments/<int:experiment_id>/fail', methods=['POST'])
@jwt_required()
def fail_experiment(experiment_id):
    """实验失败"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    error_message = data.get('error_message') if data else None
    
    experiment.fail_experiment(error_message)
    
    return jsonify({
        'message': 'Experiment marked as failed',
        'experiment': experiment.to_dict()
    })

@bp.route('/experiments/<int:experiment_id>/progress', methods=['PUT'])
@jwt_required()
def update_progress(experiment_id):
    """更新实验进度"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'progress' not in data:
        return jsonify({'error': 'Progress is required'}), 400
    
    experiment.update_progress(data['progress'])
    
    return jsonify({
        'message': 'Progress updated successfully',
        'experiment': experiment.to_dict()
    })

@bp.route('/experiments/stats', methods=['GET'])
@jwt_required()
def get_experiment_stats():
    """获取实验统计信息"""
    user_id = get_jwt_identity()
    
    # 获取各种状态的实验数量
    total = Experiment.query.filter_by(researcher_id=user_id).count()
    planning = Experiment.query.filter_by(researcher_id=user_id, status='planning').count()
    running = Experiment.query.filter_by(researcher_id=user_id, status='running').count()
    completed = Experiment.query.filter_by(researcher_id=user_id, status='completed').count()
    failed = Experiment.query.filter_by(researcher_id=user_id, status='failed').count()
    
    return jsonify({
        'total': total,
        'planning': planning,
        'running': running,
        'completed': completed,
        'failed': failed
    })