from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.experiment_metric import ExperimentMetric
from app.models.experiment import Experiment
from app import db

@bp.route('/experiments/<int:experiment_id>/metrics', methods=['GET'])
@jwt_required()
def get_metrics(experiment_id):
    """获取实验指标列表"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    metric_name = request.args.get('metric_name')
    phase = request.args.get('phase')
    
    query = ExperimentMetric.query.filter_by(experiment_id=experiment_id)
    
    # 过滤条件
    if metric_name:
        query = query.filter_by(metric_name=metric_name)
    if phase:
        query = query.filter_by(phase=phase)
    
    metrics = query.order_by(ExperimentMetric.recorded_at.desc()).all()
    
    return jsonify([metric.to_dict() for metric in metrics])

@bp.route('/experiments/<int:experiment_id>/metrics', methods=['POST'])
@jwt_required()
def create_metric(experiment_id):
    """创建实验指标"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    metric_name = data.get('metric_name')
    metric_value = data.get('metric_value')
    
    if not all([metric_name, metric_value is not None]):
        return jsonify({'error': 'Metric name and value are required'}), 400
    
    metric = ExperimentMetric(
        experiment_id=experiment_id,
        metric_name=metric_name,
        metric_value=metric_value,
        epoch=data.get('epoch'),
        step=data.get('step'),
        phase=data.get('phase'),
        metadata=data.get('metadata')
    )
    
    db.session.add(metric)
    db.session.commit()
    
    return jsonify({
        'message': 'Metric created successfully',
        'metric': metric.to_dict()
    }), 201

@bp.route('/experiments/<int:experiment_id>/metrics/batch', methods=['POST'])
@jwt_required()
def create_metrics_batch(experiment_id):
    """批量创建实验指标"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'metrics' not in data:
        return jsonify({'error': 'Metrics array is required'}), 400
    
    metrics_data = data['metrics']
    created_metrics = []
    
    for metric_data in metrics_data:
        metric_name = metric_data.get('metric_name')
        metric_value = metric_data.get('metric_value')
        
        if not all([metric_name, metric_value is not None]):
            continue
        
        metric = ExperimentMetric(
            experiment_id=experiment_id,
            metric_name=metric_name,
            metric_value=metric_value,
            epoch=metric_data.get('epoch'),
            step=metric_data.get('step'),
            phase=metric_data.get('phase'),
            metadata=metric_data.get('metadata')
        )
        
        db.session.add(metric)
        created_metrics.append(metric)
    
    db.session.commit()
    
    return jsonify({
        'message': f'{len(created_metrics)} metrics created successfully',
        'metrics': [metric.to_dict() for metric in created_metrics]
    }), 201

@bp.route('/metrics/<int:metric_id>', methods=['GET'])
@jwt_required()
def get_metric(metric_id):
    """获取单个指标"""
    user_id = get_jwt_identity()
    metric = ExperimentMetric.query.get_or_404(metric_id)
    experiment = Experiment.query.get_or_404(metric.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(metric.to_dict())

@bp.route('/metrics/<int:metric_id>', methods=['PUT'])
@jwt_required()
def update_metric(metric_id):
    """更新指标"""
    user_id = get_jwt_identity()
    metric = ExperimentMetric.query.get_or_404(metric_id)
    experiment = Experiment.query.get_or_404(metric.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'metric_name' in data:
        metric.metric_name = data['metric_name']
    if 'metric_value' in data:
        metric.metric_value = data['metric_value']
    if 'epoch' in data:
        metric.epoch = data['epoch']
    if 'step' in data:
        metric.step = data['step']
    if 'phase' in data:
        metric.phase = data['phase']
    if 'metadata' in data:
        metric.metadata = data['metadata']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Metric updated successfully',
        'metric': metric.to_dict()
    })

@bp.route('/metrics/<int:metric_id>', methods=['DELETE'])
@jwt_required()
def delete_metric(metric_id):
    """删除指标"""
    user_id = get_jwt_identity()
    metric = ExperimentMetric.query.get_or_404(metric_id)
    experiment = Experiment.query.get_or_404(metric.experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(metric)
    db.session.commit()
    
    return jsonify({'message': 'Metric deleted successfully'})

@bp.route('/experiments/<int:experiment_id>/metrics/summary', methods=['GET'])
@jwt_required()
def get_metrics_summary(experiment_id):
    """获取实验指标摘要"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 获取所有指标名称
    metric_names = db.session.query(ExperimentMetric.metric_name)\
        .filter_by(experiment_id=experiment_id).distinct().all()
    metric_names = [name[0] for name in metric_names]
    
    summary = {}
    for metric_name in metric_names:
        # 获取该指标的最新值
        latest_metric = ExperimentMetric.query.filter_by(
            experiment_id=experiment_id,
            metric_name=metric_name
        ).order_by(ExperimentMetric.recorded_at.desc()).first()
        
        # 获取该指标的最佳值（假设越小越好，对于loss等）
        best_metric = ExperimentMetric.query.filter_by(
            experiment_id=experiment_id,
            metric_name=metric_name
        ).order_by(ExperimentMetric.metric_value.asc()).first()
        
        # 获取该指标的平均值
        avg_value = db.session.query(db.func.avg(ExperimentMetric.metric_value))\
            .filter_by(experiment_id=experiment_id, metric_name=metric_name).scalar()
        
        summary[metric_name] = {
            'latest': latest_metric.to_dict() if latest_metric else None,
            'best': best_metric.to_dict() if best_metric else None,
            'average': round(avg_value, 4) if avg_value else None,
            'count': ExperimentMetric.query.filter_by(
                experiment_id=experiment_id,
                metric_name=metric_name
            ).count()
        }
    
    return jsonify(summary)

@bp.route('/experiments/<int:experiment_id>/metrics/timeline', methods=['GET'])
@jwt_required()
def get_metrics_timeline(experiment_id):
    """获取指标时间线数据"""
    user_id = get_jwt_identity()
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # 检查权限
    if experiment.researcher_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    metric_name = request.args.get('metric_name')
    if not metric_name:
        return jsonify({'error': 'Metric name is required'}), 400
    
    metrics = ExperimentMetric.query.filter_by(
        experiment_id=experiment_id,
        metric_name=metric_name
    ).order_by(ExperimentMetric.recorded_at.asc()).all()
    
    timeline = {
        'metric_name': metric_name,
        'timestamps': [m.recorded_at.isoformat() for m in metrics],
        'values': [m.metric_value for m in metrics],
        'epochs': [m.epoch for m in metrics],
        'steps': [m.step for m in metrics]
    }
    
    return jsonify(timeline)