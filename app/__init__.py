from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Config
import os

def create_app():
    # 获取当前文件所在目录的绝对路径
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # 创建Flask应用实例
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=os.path.join(base_dir, 'static'),
                template_folder=os.path.join(base_dir, 'templates'))
    
    app.config.from_object(Config)
    
    # 添加代理支持
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOADS_FOLDER'], exist_ok=True)
    
    # 注册路由
    from .routes import bp
    app.register_blueprint(bp)
    
    return app 