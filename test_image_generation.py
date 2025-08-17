#!/usr/bin/env python3
"""
测试图片生成功能
"""

import os
from datetime import datetime
from image_generator import ImageGenerator

def test_image_generation():
    """测试图片生成功能"""
    
    # 创建测试用的论文数据
    test_paper = {
        'arxiv_id': '2507.12345',
        'title': 'A Novel Approach to Machine Learning with Transformer Architecture for Natural Language Processing',
        'abstract': 'This paper presents a comprehensive study on the application of transformer architecture in natural language processing tasks. We propose a novel attention mechanism that significantly improves performance on various NLP benchmarks. Our experiments demonstrate state-of-the-art results on sentiment analysis, machine translation, and text summarization tasks.',
        'authors': ['张三', 'John Smith', 'Alice Wang', 'Bob Chen', 'Carol Liu'],
        'published_date': datetime(2025, 1, 15),
        'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
        'arxiv_url': 'https://arxiv.org/abs/2507.12345',
        'pdf_url': 'https://arxiv.org/pdf/2507.12345.pdf'
    }
    
    test_analysis = """**研究领域**：自然语言处理与机器学习

**核心贡献**：提出了一种新型注意力机制，显著提升了多个NLP任务的性能表现。

**技术方法**：基于Transformer架构设计了改进的注意力模块，优化了计算效率和准确性。

**实验结果**：在情感分析、机器翻译和文本摘要三个任务上达到了最优性能。

**意义价值**：为自然语言处理领域提供了新的技术方案，具有广泛的应用前景。"""
    
    # 创建图片生成器
    image_generator = ImageGenerator()
    
    print("开始测试图片生成...")
    
    # 测试1：生成带截图的图片
    print("1. 测试生成带截图的图片...")
    screenshot_path = None
    
    # 查找现有的截图文件用于测试
    screenshot_dir = os.path.join(image_generator.output_dir, '../screenshots')
    if os.path.exists(screenshot_dir):
        for file in os.listdir(screenshot_dir):
            if file.endswith('.png'):
                screenshot_path = os.path.join(screenshot_dir, file)
                print(f"找到测试截图: {screenshot_path}")
                break
    
    image_path = image_generator.generate_paper_image(test_paper, test_analysis, screenshot_path)
    
    if image_path and os.path.exists(image_path):
        print(f"✅ 成功生成图片: {image_path}")
    else:
        print("❌ 图片生成失败")
    
    # 测试2：生成简单文本图片
    print("\n2. 测试生成简单文本图片...")
    simple_image_path = image_generator.generate_simple_text_image(test_paper, test_analysis)
    
    if simple_image_path and os.path.exists(simple_image_path):
        print(f"✅ 成功生成简单图片: {simple_image_path}")
    else:
        print("❌ 简单图片生成失败")
    
    # 显示输出目录信息
    print(f"\n📁 图片输出目录: {image_generator.output_dir}")
    if os.path.exists(image_generator.output_dir):
        files = os.listdir(image_generator.output_dir)
        print(f"📄 生成的文件: {files}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_image_generation()