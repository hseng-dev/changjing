import os

class Config:
    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    STATIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static')
    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
    OUTPUT_FOLDER = os.path.join(STATIC_FOLDER, 'output_scenes')
    DOWNLOADS_FOLDER = os.path.join(BASE_DIR, 'downloads')
    
    # API配置
    API_KEY = 'sk-2DzRFHGNR4GXk6QQPTlzCuQgRH37GjKn7XKu9MR71NoVurwG'
    API_URL = 'https://api.deerapi.com/mj/submit/describe'
    
    # 应用配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 视频处理配置
    MIN_THRESHOLD = 0.15
    MAX_THRESHOLD = 0.60
    MIN_SCENE_DURATION = 15 