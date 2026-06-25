from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.experiment import Experiment
from app.models.experiment_milestone import ExperimentMilestone
from app import db
from datetime import datetime

@bp.route('/experiments/<int:experiment_id>/milestones', methods=['GET'])
@jwt_required()
def get_milestones(experiment_id):
    """获取实验里程碑列表"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    status = request.args.get('status')
    
    query = ExperimentMilestone.query.filter_by(experiment_id=experiment_id)
    
    # 过滤条件
    if status:
        query = query.filter_by(status=status)
    
    milestones = query.order_by(ExperimentMilestone.order_index.asc()).all()
    
    return jsonify([milestone.to_dict() for milestone in milestones])

@bp.route('/experiments/<int:experiment_id>/milestones', methods=['POST'])
@jwt_required()
def create_milestone(experiment_id):
    """创建实验里程碑"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # 获取最大排序索引
    max_order = db.session.query(db.func.max(ExperimentMilestone.order_index))\
        .filter_by(experiment_id=experiment_id).scalar() or 0
    
    milestone = ExperimentMilestone(
        experiment_id=experiment_id,
        title=title,
        description=data.get('description'),
        target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None,
        stage_name=data.get('stage_name'),
        priority=data.get('priority', 'medium'),
        order_index=data.get('order_index', max_order + 1),
        notes=data.get('notes')
    )
    
    db.session.add(milestone)
    db.session.commit()
    
    return jsonify({
        'message': 'Milestone created successfully',
        'milestone': milestone.to_dict()
    }), 201

@bp.route('/milestones/<int:milestone_id>', methods=['GET'])
@jwt_required()
def get_milestone(milestone_id):
    """获取单个里程碑"""
    user_id = int(get_jwt_identity())
    milestone = ExperimentMilestone.query.get_or_404(milestone_id)
    experiment = Experiment.query.get_or_404(milestone.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(milestone.to_dict())

@bp.route('/milestones/<int:milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(milestone_id):
    """更新里程碑"""
    user_id = int(get_jwt_identity())
    milestone = ExperimentMilestone.query.get_or_404(milestone_id)
    experiment = Experiment.query.get_or_404(milestone.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'title' in data:
        milestone.title = data['title']
    if 'description' in data:
        milestone.description = data['description']
    if 'target_date' in data:
        milestone.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data['target_date'] else None
    if 'stage_name' in data:
        milestone.stage_name = data['stage_name']
    if 'priority' in data:
        milestone.priority = data['priority']
    if 'notes' in data:
        milestone.notes = data['notes']
    if 'order_index' in data:
        milestone.order_index = data['order_index']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Milestone updated successfully',
        'milestone': milestone.to_dict()
    })

@bp.route('/milestones/<int:milestone_id>', methods=['DELETE'])
@jwt_required()
def delete_milestone(milestone_id):
    """删除里程碑"""
    user_id = int(get_jwt_identity())
    milestone = ExperimentMilestone.query.get_or_404(milestone_id)
    experiment = Experiment.query.get_or_404(milestone.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(milestone)
    db.session.commit()
    
    return jsonify({'message': 'Milestone deleted successfully'})

@bp.route('/milestones/<int:milestone_id>/complete', methods=['POST'])
@jwt_required()
def complete_milestone(milestone_id):
    """完成里程碑"""
    user_id = int(get_jwt_identity())
    milestone = ExperimentMilestone.query.get_or_404(milestone_id)
    experiment = Experiment.query.get_or_404(milestone.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    milestone.complete()
    
    return jsonify({
        'message': 'Milestone completed successfully',
        'milestone': milestone.to_dict()
    })

@bp.route('/experiments/<int:experiment_id>/milestones/overdue', methods=['GET'])
@jwt_required()
def get_overdue_milestones(experiment_id):
    """获取过期的里程碑"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    milestones = ExperimentMilestone.query.filter(
        ExperimentMilestone.experiment_id == experiment_id,
        ExperimentMilestone.target_date < datetime.utcnow().date(),
        ExperimentMilestone.status != 'completed'
    ).order_by(ExperimentMilestone.target_date.asc()).all()
    
    return jsonify([milestone.to_dict() for milestone in milestones])

@bp.route('/experiments/<int:experiment_id>/milestones/stats', methods=['GET'])
@jwt_required()
def get_milestone_stats(experiment_id):
    """获取里程碑统计"""
    user_id = int(get_jwt_identity())
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    total = ExperimentMilestone.query.filter_by(experiment_id=experiment_id).count()
    completed = ExperimentMilestone.query.filter_by(experiment_id=experiment_id, status='completed').count()
    pending = ExperimentMilestone.query.filter_by(experiment_id=experiment_id, status='pending').count()
    in_progress = ExperimentMilestone.query.filter_by(experiment_id=experiment_id, status='in_progress').count()
    
    overdue = ExperimentMilestone.query.filter(
        ExperimentMilestone.experiment_id == experiment_id,
        ExperimentMilestone.target_date < datetime.utcnow().date(),
        ExperimentMilestone.status != 'completed'
    ).count()
    
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'overdue': overdue
    })