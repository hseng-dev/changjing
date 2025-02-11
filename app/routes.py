from flask import Blueprint, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import logging
from .utils.video import split_video_scenes
from .utils.api import generate_midjourney_prompt
from flask import current_app

logger = logging.getLogger(__name__)
bp = Blueprint('main', __name__, template_folder='templates')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@bp.route('/get_prompt/<scene_id>', methods=['GET'])
def get_prompt(scene_id):
    try:
        logger.info(f"接收到场景ID请求: {scene_id}")
        
        # 确保scene_id是整数
        try:
            scene_num = int(scene_id)
        except ValueError:
            logger.error(f"无效的场景ID: {scene_id}")
            return jsonify({'error': '无效的场景ID'}), 400
            
        # 构建图片路径
        image_path = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            f'scene_{scene_num:03d}.jpg'
        )
        logger.info(f"尝试访问图片路径: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"图片不存在: {image_path}")
            return jsonify({'error': '图片不存在'}), 404
            
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        logger.info(f"图片大小: {file_size} 字节")
        
        if file_size == 0:
            return jsonify({'error': '图片文件为空'}), 400
            
        # 获取提示词
        prompt_data = generate_midjourney_prompt(
            image_path,
            current_app.config['API_KEY'],
            current_app.config['API_URL']
        )
        
        if prompt_data is None:
            return jsonify({'prompts': ['API返回为空']}), 200
            
        return jsonify(prompt_data)
        
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({'prompts': [f'错误: {str(e)}']}), 200

@bp.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({'error': '没有上传视频文件'})
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': '未选择文件'})
    
    try:
        # 保存上传的视频
        video_filename = secure_filename(video.filename)
        video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_filename)
        video.save(video_path)
        
        # 处理视频并获取场景图片路径
        scene_paths = split_video_scenes(
            video_path=video_path,
            output_dir=current_app.config['OUTPUT_FOLDER'],
            min_threshold=current_app.config['MIN_THRESHOLD'],
            max_threshold=current_app.config['MAX_THRESHOLD'],
            min_scene_duration=current_app.config['MIN_SCENE_DURATION']
        )
        
        # 返回相对于static目录的路径
        relative_paths = [
            'output_scenes/' + os.path.basename(path) 
            for path in scene_paths
        ]
        
        return jsonify({
            'success': True,
            'scenes': relative_paths
        })
    except Exception as e:
        logger.error(f"处理视频时出错: {str(e)}")
        return jsonify({'error': str(e)})

@bp.route('/delete_scene/<scene_id>', methods=['POST'])
def delete_scene(scene_id):
    try:
        data = request.get_json()
        scene_path = data.get('path')
        
        if not scene_path:
            return jsonify({'error': '未提供场景路径'}), 400
            
        # 构建完整的文件路径
        full_path = os.path.join(current_app.config['STATIC_FOLDER'], scene_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return jsonify({'error': '场景文件不存在'}), 404
            
        # 删除文件
        os.remove(full_path)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"删除场景时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/save_scene/<scene_id>', methods=['POST'])
def save_scene(scene_id):
    try:
        data = request.get_json()
        scene_path = data.get('path')
        
        if not scene_path:
            return jsonify({'error': '未提供场景路径'}), 400
            
        # 确保downloads文件夹存在
        downloads_path = current_app.config['DOWNLOADS_FOLDER']
        os.makedirs(downloads_path, exist_ok=True)
        
        # 构建源文件和目标文件的完整路径
        source_path = os.path.join(current_app.config['STATIC_FOLDER'], scene_path)
        filename = os.path.basename(scene_path)
        target_path = os.path.join(downloads_path, filename)
        
        # 打印路径信息
        logger.info(f"Downloads文件夹路径: {downloads_path}")
        logger.info(f"源文件路径: {source_path}")
        logger.info(f"目标文件路径: {target_path}")
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            return jsonify({'error': '场景文件不存在'}), 404
            
        # 复制文件到downloads文件夹
        import shutil
        shutil.copy2(source_path, target_path)
        
        # 返回相对路径的消息
        relative_path = os.path.join('downloads', filename)
        return jsonify({
            'success': True,
            'message': f'场景已保存到: {relative_path}'
        })
        
    except Exception as e:
        logger.error(f"保存场景时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500 