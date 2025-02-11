import cv2
import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

def split_video_scenes(video_path, output_dir, min_threshold=0.15, max_threshold=0.60, min_scene_duration=15):
    """分割视频场景"""
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开视频文件")
            
        # 获取视频信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        min_frames = fps * min_scene_duration
        
        # 初始化变量
        prev_frame = None
        scene_start = 0
        scene_count = 0
        frames = []
        scene_paths = []
        
        logger.info(f"开始处理视频: {video_path}")
        logger.info(f"FPS: {fps}, 总帧数: {frame_count}")
        
        # 逐帧处理视频
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # 计算帧差
                diff = cv2.absdiff(gray, prev_frame)
                score = np.mean(diff) / 255.0
                
                # 检测场景变化
                if score > max_threshold or score < min_threshold:
                    current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    scene_length = current_frame - scene_start
                    
                    if scene_length >= min_frames:
                        # 保存场景
                        scene_frame = frames[len(frames)//2]  # 使用中间帧作为场景代表
                        output_path = os.path.join(output_dir, f'scene_{scene_count:03d}.jpg')
                        cv2.imwrite(output_path, scene_frame)
                        scene_paths.append(output_path)
                        scene_count += 1
                        
                        # 重置场景
                        scene_start = current_frame
                        frames = []
                
            prev_frame = gray
            frames.append(frame)
            
        # 处理最后一个场景
        if frames:
            scene_frame = frames[len(frames)//2]
            output_path = os.path.join(output_dir, f'scene_{scene_count:03d}.jpg')
            cv2.imwrite(output_path, scene_frame)
            scene_paths.append(output_path)
        
        cap.release()
        logger.info(f"视频处理完成，共生成 {len(scene_paths)} 个场景")
        return scene_paths
        
    except Exception as e:
        logger.error(f"视频处理失败: {str(e)}")
        raise 