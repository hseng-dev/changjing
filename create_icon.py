from PIL import Image, ImageDraw
import os

# 创建一个 256x256 的图像
size = (256, 256)
image = Image.new('RGBA', size, (255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# 绘制一个简单的相机图标
# 相机主体
draw.rectangle([50, 80, 206, 176], fill=(52, 152, 219))
# 镜头
draw.ellipse([90, 100, 166, 176], fill=(41, 128, 185))
draw.ellipse([100, 110, 156, 166], fill=(236, 240, 241))
# 闪光灯
draw.rectangle([170, 60, 190, 80], fill=(52, 152, 219))

# 保存为 .ico 文件
if not os.path.exists('app/static'):
    os.makedirs('app/static')
image.save('app/static/icon.ico', format='ICO')

print("图标已创建在 app/static/icon.ico") 