import os
import sys
import webbrowser
from threading import Timer
import traceback
import logging
import ctypes

# 创建控制台窗口
kernel32 = ctypes.WinDLL('kernel32')
kernel32.AllocConsole()
sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
sys.stderr = open('CONOUT$', 'w', encoding='utf-8')

# 配置日志 - 同时输出到文件和控制台
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def open_browser():
    try:
        webbrowser.open('http://127.0.0.1:8082/')
    except Exception as e:
        print(f"Failed to open browser: {e}")

if __name__ == '__main__':
    try:
        print("="*50)
        print("Starting application...")
        print("="*50)
        
        # 确保在打包后也能找到正确的路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            application_path = os.path.dirname(sys.executable)
            print(f"Running as exe, path: {application_path}")
        else:
            # 如果是直接运行的python脚本
            application_path = os.path.dirname(os.path.abspath(__file__))
            print(f"Running as script, path: {application_path}")
        
        # 设置工作目录
        os.chdir(application_path)
        print(f"Changed working directory to: {application_path}")
        print(f"Current directory contents: {os.listdir('.')}")
        
        print("\nTrying to import create_app...")
        from app import create_app
        
        print("Creating Flask app...")
        app = create_app()
        
        # 在应用启动后延迟1秒打开浏览器
        Timer(1, open_browser).start()
        print("Browser timer started...")
        
        # 启动Flask应用
        print("Starting Flask server...")
        app.run(host='127.0.0.1', port=8082, debug=False)
        
    except Exception as e:
        error_msg = f"""
{'='*50}
ERROR OCCURRED:
{str(e)}

TRACEBACK:
{traceback.format_exc()}
{'='*50}
"""
        print(error_msg)
        
        # 将错误信息写入文件
        with open('error.log', 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        print("\nPress Enter to exit...")
        input()
    finally:
        # 保持控制台窗口打开
        print("\nApplication ended. Press Enter to close...")
        input() 