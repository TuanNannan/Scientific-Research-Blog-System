import os
from flask import Flask, jsonify
from extensions import db, migrate, jwt, cors, api

def create_app(config_name=None):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    api.init_app(app)
    
    # 导入模型（在应用上下文中）
    with app.app_context():
        from app.models import user, post, experiment, audio_file, experiment_metric, todo
        from app.models import experiment_stage, experiment_log, experiment_milestone
    
    # 注册蓝图
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Blog API is running'})
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# 为Flask CLI创建应用
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)