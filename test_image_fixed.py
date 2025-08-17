#!/usr/bin/env python3
"""
测试修复后的图片生成功能
"""

import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_image_generation():
    """测试图片生成功能"""
    
    try:
        from image_generator import ImageGenerator
        
        # 创建测试用的论文数据
        test_paper = {
            'arxiv_id': '2507.12345',
            'title': 'A Novel Deep Learning Approach for Automated Text Summarization Using Transformer-Based Neural Networks',
            'abstract': 'This paper presents a comprehensive study on the application of transformer architecture in natural language processing tasks. We propose a novel attention mechanism that significantly improves performance on various NLP benchmarks. Our experiments demonstrate state-of-the-art results on sentiment analysis, machine translation, and text summarization tasks with improved efficiency and accuracy.',
            'authors': ['张伟', 'John Smith', 'Alice Wang', 'Bob Chen'],
            'published_date': datetime(2025, 1, 15),
            'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
            'arxiv_url': 'https://arxiv.org/abs/2507.12345',
            'pdf_url': 'https://arxiv.org/pdf/2507.12345.pdf'
        }
        
        test_analysis = """**研究领域**：自然语言处理与深度学习

**核心贡献**：提出了一种基于Transformer的新型注意力机制，显著提升了文本摘要任务的性能表现，在多个基准数据集上达到了最优结果。

**技术方法**：采用改进的多头自注意力机制，结合位置编码优化和层归一化技术，构建了高效的神经网络架构。

**实验结果**：在ROUGE-1、ROUGE-2和ROUGE-L指标上分别提升了3.2%、2.8%和3.5%，同时推理速度提升了15%。

**意义价值**：为自动文本摘要领域提供了新的技术方案，具有广泛的实际应用价值和学术研究意义。"""
        
        # 创建图片生成器
        print("初始化图片生成器...")
        image_generator = ImageGenerator()
        
        print("开始测试图片生成...")
        
        # 查找现有的截图文件用于测试
        screenshot_path = None
        screenshot_dir = os.path.join(image_generator.output_dir, '../screenshots')
        if os.path.exists(screenshot_dir):
            for file in os.listdir(screenshot_dir):
                if file.endswith('.png'):
                    screenshot_path = os.path.join(screenshot_dir, file)
                    print(f"找到测试截图: {screenshot_path}")
                    break
        
        if not screenshot_path:
            print("未找到截图文件，将生成无截图版本")
        
        # 生成图片
        image_path = image_generator.generate_paper_image(test_paper, test_analysis, screenshot_path)
        
        if image_path and os.path.exists(image_path):
            print(f"✅ 成功生成图片: {image_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(image_path)
            print(f"📁 文件大小: {file_size / 1024:.1f} KB")
            
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
    print("=== 测试修复后的图片生成功能 ===")
    success = test_image_generation()
    if success:
        print("\n🎉 测试成功完成！")
    else:
        print("\n💥 测试失败，请检查错误信息")