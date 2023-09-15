from PIL import Image

def convert_jpg_to_png(jpg_image_path, png_image_path):
    """
    将 JPG 图像转换为 PNG 格式。
    
    Args:
        jpg_image_path (str): JPG 图像的文件路径。
        png_image_path (str): 要保存的 PNG 图像的文件路径。
        
    Returns:
        bool: 转换成功返回 True，否则返回 False。
    """
    try:
        # 打开 JPG 图像
        jpg_image = Image.open(jpg_image_path)

        # 将 JPG 图像保存为 PNG 格式
        jpg_image.save(png_image_path, "PNG")

        # 关闭图像
        jpg_image.close()

        print(f"JPG 图像 '{jpg_image_path}' 已成功转换为 PNG 图像 '{png_image_path}'")
        return True
    except Exception as e:
        print(f"转换失败: {e}")
        return False