"""
PDF处理模块
下载ArXiv PDF并生成首页截图
"""

import os
import io
import requests
import fitz  # PyMuPDF
from PIL import Image
import logging
from config import Config

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.download_dir = Config.PDF_DOWNLOAD_DIR
        self.screenshot_dir = os.path.join(self.download_dir, 'screenshots')
        
        # 创建目录
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def download_pdf(self, pdf_url, arxiv_id):
        """
        下载PDF文件
        
        Args:
            pdf_url: PDF下载链接
            arxiv_id: ArXiv ID
        
        Returns:
            下载的PDF文件路径
        """
        try:
            pdf_path = os.path.join(self.download_dir, f"{arxiv_id}.pdf")
            
            # 如果文件已存在，直接返回路径
            if os.path.exists(pdf_path):
                logger.info(f"PDF already exists: {pdf_path}")
                return pdf_path
            
            logger.info(f"Downloading PDF: {pdf_url}")
            
            # 下载PDF
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(pdf_url, headers=headers, timeout=60, stream=True)
            response.raise_for_status()
            
            # 保存PDF文件
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"PDF downloaded successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error downloading PDF {arxiv_id}: {str(e)}")
            return None
    
    def create_screenshot(self, pdf_path, arxiv_id):
        """
        创建PDF首页截图（高质量版本）
        
        Args:
            pdf_path: PDF文件路径
            arxiv_id: ArXiv ID
        
        Returns:
            截图文件路径
        """
        try:
            screenshot_path = os.path.join(self.screenshot_dir, f"{arxiv_id}.png")
            
            # 如果截图已存在，直接返回路径
            if os.path.exists(screenshot_path):
                logger.info(f"Screenshot already exists: {screenshot_path}")
                return screenshot_path
            
            logger.info(f"Creating high-quality screenshot from PDF: {pdf_path}")
            
            # 使用PyMuPDF打开PDF
            pdf_document = fitz.open(pdf_path)
            
            if len(pdf_document) == 0:
                raise ValueError("PDF has no pages")
            
            # 获取第一页
            first_page = pdf_document[0]
            
            # 设置高分辨率渲染参数
            # 使用4倍缩放以获得更高清晰度，特别是对文字渲染
            matrix = fitz.Matrix(4.0, 4.0)  # 4倍放大，提升文字清晰度
            
            # 启用抗锯齿和高质量渲染
            pix = first_page.get_pixmap(
                matrix=matrix,
                alpha=False,  # 不需要透明度，减少文件大小
                annots=True,  # 包含注释
                clip=None     # 不裁剪
            )
            
            # 转换为PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            # 智能调整尺寸策略
            target_width = 1600  # 提高目标宽度
            target_height = 2000  # 提高目标高度
            
            # 计算合适的尺寸，保持宽高比
            current_ratio = image.width / image.height
            target_ratio = target_width / target_height
            
            if current_ratio > target_ratio:
                # 图片偏宽，以宽度为准
                new_width = target_width
                new_height = int(target_width / current_ratio)
            else:
                # 图片偏高，以高度为准
                new_height = target_height
                new_width = int(target_height * current_ratio)
            
            # 只有在需要缩小时才调整尺寸
            if image.width > new_width or image.height > new_height:
                # 使用高质量重采样算法
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {pix.width}x{pix.height} to {new_width}x{new_height}")
            
            # 可选：锐化图像以增强文字清晰度
            from PIL import ImageFilter
            try:
                # 轻微锐化，增强文字边缘
                image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))
            except Exception as e:
                logger.warning(f"Failed to apply sharpening filter: {e}")
            
            # 保存为高质量PNG
            # 使用最高压缩级别但不优化，保证质量
            image.save(
                screenshot_path, 
                'PNG', 
                compress_level=1,  # 最小压缩，最高质量
                optimize=False,    # 不优化，避免质量损失
                dpi=(600, 600)     # 设置高DPI
            )
            
            pdf_document.close()
            
            # 检查生成的文件大小和尺寸
            file_size = os.path.getsize(screenshot_path) / (1024 * 1024)  # MB
            logger.info(f"High-quality screenshot created: {screenshot_path}")
            logger.info(f"Final image size: {image.width}x{image.height}, file size: {file_size:.2f}MB")
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error creating screenshot for {arxiv_id}: {str(e)}")
            return None
    
    def process_paper(self, paper):
        """
        处理论文：下载PDF并创建截图
        
        Args:
            paper: 论文信息字典
        
        Returns:
            截图文件路径
        """
        try:
            arxiv_id = paper['arxiv_id']
            pdf_url = paper['pdf_url']
            
            # 下载PDF
            pdf_path = self.download_pdf(pdf_url, arxiv_id)
            if not pdf_path:
                raise ValueError(f"Failed to download PDF for {arxiv_id}")
            
            # 创建截图
            screenshot_path = self.create_screenshot(pdf_path, arxiv_id)
            if not screenshot_path:
                raise ValueError(f"Failed to create screenshot for {arxiv_id}")
            
            # 清理PDF文件（节省空间，只保留截图）
            try:
                os.remove(pdf_path)
                logger.info(f"Cleaned up PDF file: {pdf_path}")
            except:
                pass  # 如果删除失败也不影响主流程
            
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error processing paper {paper.get('arxiv_id', 'unknown')}: {str(e)}")
            return None