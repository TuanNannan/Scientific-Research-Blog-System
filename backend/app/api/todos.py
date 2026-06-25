from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models.todo import Todo, TodoTag
from app.models.user import User
from app import db
from datetime import datetime

@bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    """获取待办事项列表"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category = request.args.get('category')
    priority = request.args.get('priority')
    
    query = Todo.query.filter_by(user_id=user_id)
    
    # 过滤条件
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    
    # 排序和分页
    todos = query.order_by(Todo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'todos': [todo.to_dict() for todo in todos.items],
        'total': todos.total,
        'pages': todos.pages,
        'current_page': todos.page
    })

@bp.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    """创建待办事项"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    todo = Todo(
        title=title,
        user_id=user_id,
        description=data.get('description'),
        category=data.get('category'),
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
        estimated_hours=data.get('estimated_hours'),
        notes=data.get('notes')
    )
    
    db.session.add(todo)
    db.session.flush()  # 获取todo.id
    
    # 添加标签
    if 'tags' in data and data['tags']:
        for tag_name in data['tags']:
            tag = TodoTag(todo_id=todo.id, tag=tag_name)
            db.session.add(tag)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Todo created successfully',
        'todo': todo.to_dict()
    }), 201

@bp.route('/todos/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    """获取单个待办事项"""
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    
    # 检查权限
    if todo.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(todo.to_dict())

@bp.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    """更新待办事项"""
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    
    # 检查权限
    if todo.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # 更新字段
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'category' in data:
        todo.category = data['category']
    if 'priority' in data:
        todo.priority = data['priority']
    if 'status' in data:
        todo.status = data['status']
    if 'due_date' in data:
        todo.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'estimated_hours' in data:
        todo.estimated_hours = data['estimated_hours']
    if 'actual_hours' in data:
        todo.actual_hours = data['actual_hours']
    if 'notes' in data:
        todo.notes = data['notes']
    
    # 更新标签
    if 'tags' in data:
        # 删除现有标签
        TodoTag.query.filter_by(todo_id=todo.id).delete()
        # 添加新标签
        if data['tags']:
            for tag_name in data['tags']:
                tag = TodoTag(todo_id=todo.id, tag=tag_name)
                db.session.add(tag)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Todo updated successfully',
        'todo': todo.to_dict()
    })

@bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    """删除待办事项"""
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    
    # 检查权限
    if todo.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': 'Todo deleted successfully'})

@bp.route('/todos/<int:todo_id>/complete', methods=['POST'])
@jwt_required()
def complete_todo(todo_id):
    """完成待办事项"""
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    
    # 检查权限
    if todo.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    todo.complete()
    
    return jsonify({
        'message': 'Todo completed successfully',
        'todo': todo.to_dict()
    })

@bp.route('/todos/<int:todo_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_todo(todo_id):
    """取消待办事项"""
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    
    # 检查权限
    if todo.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    todo.cancel()
    
    return jsonify({
        'message': 'Todo cancelled successfully',
        'todo': todo.to_dict()
    })

@bp.route('/todos/stats', methods=['GET'])
@jwt_required()
def get_todo_stats():
    """获取待办事项统计信息"""
    user_id = int(get_jwt_identity())
    
    # 获取各种状态的待办事项数量
    total = Todo.query.filter_by(user_id=user_id).count()
    pending = Todo.query.filter_by(user_id=user_id, status='pending').count()
    in_progress = Todo.query.filter_by(user_id=user_id, status='in_progress').count()
    completed = Todo.query.filter_by(user_id=user_id, status='completed').count()
    cancelled = Todo.query.filter_by(user_id=user_id, status='cancelled').count()
    
    # 获取过期的待办事项
    overdue = Todo.query.filter(
        Todo.user_id == user_id,
        Todo.due_date < datetime.utcnow(),
        Todo.status.notin_(['completed', 'cancelled'])
    ).count()
    
    return jsonify({
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'cancelled': cancelled,
        'overdue': overdue
    })

@bp.route('/todos/categories', methods=['GET'])
@jwt_required()
def get_todo_categories():
    """获取所有待办事项分类"""
    user_id = int(get_jwt_identity())
    categories = db.session.query(Todo.category).filter_by(user_id=user_id).distinct().all()
    return jsonify([category[0] for category in categories if category[0]])

@bp.route('/todos/overdue', methods=['GET'])
@jwt_required()
def get_overdue_todos():
    """获取过期的待办事项"""
    user_id = int(get_jwt_identity())
    
    overdue_todos = Todo.query.filter(
        Todo.user_id == user_id,
        Todo.due_date < datetime.utcnow(),
        Todo.status.notin_(['completed', 'cancelled'])
    ).order_by(Todo.due_date.asc()).all()
    
    return jsonify([todo.to_dict() for todo in overdue_todos])