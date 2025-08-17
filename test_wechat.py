#!/usr/bin/env python3
"""
测试微信发送功能
"""

import os
import sys
import logging
from datetime import datetime
from config import Config
from wechat_sender import WeChatSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_wechat_connection():
    """测试微信连接"""
    print("=" * 50)
    print("微信发送功能测试")
    print("=" * 50)
    
    try:
        # 验证配置
        Config.validate()
        print("✓ 配置验证通过")
        
        if not Config.WECHAT_ENABLED:
            print("❌ 微信发送功能未启用")
            print("请在.env文件中设置 WECHAT_ENABLED=true")
            return False
        
        print(f"📱 微信收件人: {Config.WECHAT_RECIPIENT}")
        
        # 初始化微信发送器
        wechat_sender = WeChatSender()
        
        # 测试连接
        print("🔌 测试微信连接...")
        if wechat_sender.test_connection():
            print("✓ 微信连接测试成功")
            return True
        else:
            print("❌ 微信连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_image_sending():
    """测试图片发送功能"""
    print("\n" + "=" * 50)
    print("测试图片发送功能")
    print("=" * 50)
    
    try:
        wechat_sender = WeChatSender()
        
        # 创建测试图片
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建一个简单的测试图片
        test_image = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(test_image)
        
        # 添加测试文本
        test_text = f"微信发送测试\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        draw.text((50, 100), test_text, fill='black')
        
        # 保存测试图片
        test_image_path = os.path.join(Config.PDF_DOWNLOAD_DIR, 'wechat_test.png')
        os.makedirs(Config.PDF_DOWNLOAD_DIR, exist_ok=True)
        test_image.save(test_image_path)
        
        print(f"📷 生成测试图片: {test_image_path}")
        
        # 模拟论文数据
        test_paper = {
            'arxiv_id': 'test-2024.001',
            'title': '微信发送功能测试',
            'arxiv_url': 'https://arxiv.org/abs/test-2024.001'
        }
        
        # 发送测试图片
        print("📤 发送测试图片到微信...")
        success = wechat_sender.send_paper_image(test_paper, test_image_path)
        
        if success:
            print("✓ 图片发送成功")
            return True
        else:
            print("❌ 图片发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 图片发送测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试微信发送功能...\n")
    
    # 测试连接
    connection_ok = test_wechat_connection()
    
    if connection_ok:
        # 测试图片发送
        image_ok = test_image_sending()
        
        if image_ok:
            print("\n🎉 所有测试通过！微信发送功能正常工作")
        else:
            print("\n⚠️  连接正常但图片发送失败")
    else:
        print("\n❌ 微信连接失败，请检查配置和微信客户端状态")
    
    print("\n测试完成")

if __name__ == "__main__":
    main()