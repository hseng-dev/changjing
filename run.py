import os
import logging
from app import create_app

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = create_app()

if __name__ == '__main__':
    # 确保所需目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOADS_FOLDER'], exist_ok=True)
    
    app.run(host='127.0.0.1', port=8082, debug=True) 