#!/usr/bin/env python3
"""
测试新的左右分栏布局图片生成
"""

import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_new_layout():
    """测试新布局的图片生成"""
    
    try:
        from image_generator import ImageGenerator
        
        # 创建测试用的论文数据
        test_paper = {
            'arxiv_id': '2507.12345',
            'title': 'Attention Is All You Need: A Comprehensive Study of Transformer Architecture for Large-Scale Natural Language Processing Tasks',
            'abstract': 'This paper presents a revolutionary approach to sequence-to-sequence learning through the introduction of the Transformer architecture. Our model relies entirely on attention mechanisms, dispensing with recurrence and convolutions. Experiments on two machine translation tasks show that the Transformer achieves superior quality while being more parallelizable and requiring significantly less time to train. Our approach establishes new state-of-the-art results on the WMT 2014 English-to-German translation task and demonstrates strong performance across various sequence modeling tasks.',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit', 'Llion Jones'],
            'published_date': datetime(2025, 1, 22),
            'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
            'keywords': ['transformer', 'attention mechanism', 'machine translation', 'neural networks'],
            'arxiv_url': 'https://arxiv.org/abs/2507.12345',
            'pdf_url': 'https://arxiv.org/pdf/2507.12345.pdf'
        }
        
        test_analysis = """**研究领域**：深度学习与自然语言处理，专注于序列到序列学习任务的架构创新。

**核心贡献**：提出了完全基于注意力机制的Transformer架构，摒弃了传统的循环和卷积结构，在机器翻译等任务上取得了突破性性能。

**技术方法**：采用多头自注意力机制和位置编码，通过编码器-解码器结构实现端到端的序列建模，具有高度可并行化的特点。

**实验结果**：在WMT 2014英德翻译任务上达到了新的最优性能，BLEU分数显著提升，同时训练时间大幅减少。

**意义价值**：为自然语言处理领域带来了范式转变，成为现代大语言模型的基础架构，具有深远的学术和实际应用价值。"""
        
        # 创建图片生成器
        print("=== 测试新的左右分栏布局 ===")
        image_generator = ImageGenerator()
        
        print("新布局配置:")
        print(f"- 画布尺寸: {image_generator.width} x {image_generator.height}")
        print(f"- 左栏宽度: {image_generator.left_column_width}px")
        print(f"- 右栏宽度: {image_generator.right_column_width}px")
        print(f"- 边距: {image_generator.margin}px")
        
        # 查找截图文件
        screenshot_path = None
        screenshot_dir = os.path.join(image_generator.output_dir, '../screenshots')
        if os.path.exists(screenshot_dir):
            for file in os.listdir(screenshot_dir):
                if file.endswith('.png'):
                    screenshot_path = os.path.join(screenshot_dir, file)
                    print(f"找到测试截图: {screenshot_path}")
                    break
        
        if not screenshot_path:
            print("未找到截图文件，将测试无截图版本")
        
        print("\n开始生成图片...")
        
        # 生成新布局图片
        image_path = image_generator.generate_paper_image(test_paper, test_analysis, screenshot_path)
        
        if image_path and os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"✅ 成功生成新布局图片!")
            print(f"📁 文件路径: {image_path}")
            print(f"📏 文件大小: {file_size / 1024:.1f} KB")
            
            # 显示生成信息
            from PIL import Image
            with Image.open(image_path) as img:
                print(f"🖼️  图片尺寸: {img.width} x {img.height}")
                print(f"🎨 色彩模式: {img.mode}")
            
            return True
        else:
            print("❌ 图片生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_layout()
    if success:
        print("\n🎉 新布局测试完成！请查看生成的图片效果。")
    else:
        print("\n💥 测试失败，请检查错误信息。")