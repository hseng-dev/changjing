import requests
import logging
import base64
from PIL import Image
import os
import json
import time

logger = logging.getLogger(__name__)

def process_prompts(result):
    """处理API返回的提示词结果"""
    prompt_en = result.get('promptEn', '')
    prompts = []
    
    if not prompt_en:
        return {'prompts': ['未获取到提示词']}
    
    # 分割多个提示词
    parts = prompt_en.split('\n\n')
    for part in parts:
        if part.strip():
            # 移除表情符号和参数
            clean_prompt = part.split('--ar')[0].strip()
            if clean_prompt.startswith('️⃣'):
                clean_prompt = clean_prompt[1:].strip()
            prompts.append(clean_prompt)
    
    return {'prompts': prompts if prompts else ['未获取到有效提示词']}

def poll_task_result(task_id, api_key, max_attempts=60, delay=3):
    """轮询任务结果"""
    check_url = f"https://api.deerapi.com/mj/task/{task_id}/fetch"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    logger.info("开始轮询任务结果，最大尝试次数: %d, 间隔: %d秒", max_attempts, delay)
    total_wait_time = 0
    
    for attempt in range(max_attempts):
        try:
            total_wait_time = attempt * delay
            progress_bar = f"[{'=' * (attempt % 10)}{'>' if attempt < max_attempts-1 else '='}{' ' * (9-attempt%10)}]"
            logger.info("轮询任务状态... %s (已等待: %d秒)", progress_bar, total_wait_time)
            
            response = requests.get(check_url, headers=headers, timeout=10)
            data = response.json()
            
            status = data.get('status', '')
            progress = data.get('progress', '0%')
            description = data.get('description', '')
            
            status_info = f"状态: {status}, 进度: {progress}, 描述: {description}"
            logger.info(status_info)
            
            if status == 'SUCCESS':
                return data
            elif status == 'FAILED':
                raise Exception(f"任务失败: {data.get('failReason', '未知错误')}")
            elif status in ['SUBMITTED', 'PROCESSING', 'PENDING', '']:
                time.sleep(delay)
                continue
                
        except Exception as e:
            logger.error(f"轮询出错: {str(e)}")
            time.sleep(delay)
    
    raise Exception(f"等待任务完成超时 (已等待 {total_wait_time} 秒)")

def generate_midjourney_prompt(image_path, api_key, api_url):
    """生成Midjourney提示词"""
    try:
        logger.info("开始处理图片: %s", image_path)
        
        # 处理图片
        with Image.open(image_path) as img:
            logger.info(f"图片格式: {img.format}, 尺寸: {img.size}")
            
            # 转换为JPEG格式
            temp_path = image_path + '.temp.jpg'
            img = img.convert('RGB')
            img.save(temp_path, 'JPEG', quality=95)
            
            # 读取并转换为base64
            with open(temp_path, 'rb') as img_file:
                image_bytes = img_file.read()
                image_data = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            
            # 准备请求数据
            data = {
                "model": "midjourney",
                "prompt": "",
                "base64": image_data,
                "mode": "describe",
                "language": "zh"
            }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 发送请求
            response = requests.post(api_url, json=data, headers=headers, timeout=30)
            submit_result = response.json()
            
            if submit_result.get('code') == 1:
                task_id = submit_result.get('result')
                if not task_id:
                    raise Exception("未获取到任务ID")
                
                logger.info(f"提交成功，任务ID: {task_id}")
                result = poll_task_result(task_id, api_key)
                return process_prompts(result)
            else:
                error_msg = submit_result.get('description', '未知错误')
                raise Exception(f"API错误: {error_msg}")
                
    except Exception as e:
        logger.error(f"生成提示词失败: {str(e)}")
        return {'prompts': [str(e)]}
    finally:
        # 清理临时文件
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}") 