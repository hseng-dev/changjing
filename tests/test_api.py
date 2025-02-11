import unittest
import os
import sys
from pathlib import Path
import base64
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # 创建测试用的临时目录
        self.test_output_folder = os.path.join(os.path.dirname(__file__), 'test_output')
        os.makedirs(self.test_output_folder, exist_ok=True)
        self.app.config['OUTPUT_FOLDER'] = self.test_output_folder
        
        # 创建测试用的场景图片
        self.test_image_path = os.path.join(self.test_output_folder, 'scene_000.jpg')
        with open(self.test_image_path, 'wb') as f:
            f.write(b'fake image data')

    def tearDown(self):
        """测试后的清理"""
        # 清理测试文件
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.test_output_folder):
            os.rmdir(self.test_output_folder)

    def test_index_route(self):
        """测试首页路由"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('app.requests.post')
    @patch('app.requests.get')
    def test_get_prompt_success(self, mock_get, mock_post):
        """测试成功获取提示词的情况"""
        # 模拟 POST 请求响应
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'code': 200,
                'data': {'task_id': 'test_task_id'}
            }
        )
        
        # 模拟 GET 请求响应
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'code': 200,
                'data': {
                    'status': 'SUCCESS',
                    'result': {
                        'prompt': '测试提示词',
                        'negative_prompt': '测试负向提示词'
                    }
                }
            }
        )

        response = self.client.get('/get_prompt/0')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('prompts', data)
        self.assertEqual(data['prompts'][0]['prompt'], '测试提示词')

    def test_get_prompt_invalid_id(self):
        """测试无效的场景ID"""
        response = self.client.get('/get_prompt/invalid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_get_prompt_missing_image(self):
        """测试图片不存在的情况"""
        # 删除测试图片
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
            
        response = self.client.get('/get_prompt/0')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)

    @patch('app.requests.post')
    def test_api_timeout(self, mock_post):
        """测试API超时情况"""
        # 模拟请求超时
        mock_post.side_effect = requests.exceptions.Timeout()
        
        response = self.client.get('/get_prompt/0')
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('超时', data['error'])

if __name__ == '__main__':
    unittest.main() 