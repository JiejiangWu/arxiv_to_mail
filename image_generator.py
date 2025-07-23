"""
图片生成模块
将论文信息和分析结果生成为一张可分享的图片
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import textwrap
import logging
from config import Config

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.output_dir = os.path.join(Config.PDF_DOWNLOAD_DIR, 'generated_images')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 图片尺寸和颜色配置
        self.width = 1080  # 增加宽度以支持左右分栏
        self.height = 1820  # 增加高度以容纳更大的预览区域
        self.background_color = '#f8fafc'
        self.card_color = '#ffffff'
        self.header_color = '#1e293b'
        self.text_color = '#475569'
        self.accent_color = '#0ea5e9'
        self.ai_section_color = '#f0fdf4'
        self.border_color = '#e2e8f0'
        
        # 间距和边距
        self.margin = 20  # 减少左右边距
        self.padding = 20
        self.line_spacing = 12
        self.section_spacing = 15
        
        # 分栏布局配置
        self.left_column_width = 160  # 缩小左侧信息栏宽度
        self.right_column_width = 920  # 增大右侧PDF预览宽度
        self.column_gap = 20  # 左右栏之间的间距
        
        # 尝试加载中文字体
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """加载字体"""
        fonts = {}
        
        # 常见的中文字体路径
        font_paths = [
            # Windows字体
            'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
            'C:/Windows/Fonts/simsun.ttc',  # 宋体
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
            # macOS字体
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            # Linux中文字体
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',    # 文泉驿正黑
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Noto CJK
            '/usr/share/fonts/truetype/arphic/uming.ttc',      # AR PL UMing
            # 项目内字体文件
            './fonts/NotoSansCJK-Regular.ttc',
            './fonts/wqy-microhei.ttc',
            # 通用fallback
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        
        # 尝试加载字体
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    fonts['title'] = ImageFont.truetype(font_path, 26)
                    fonts['subtitle'] = ImageFont.truetype(font_path, 18)
                    fonts['body'] = ImageFont.truetype(font_path, 15)
                    fonts['small'] = ImageFont.truetype(font_path, 14)
                    logger.info(f"Successfully loaded font: {font_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")
                    continue
        
        # 如果没有找到字体，使用默认字体
        if not fonts:
            try:
                fonts['title'] = ImageFont.load_default()
                fonts['subtitle'] = ImageFont.load_default()
                fonts['body'] = ImageFont.load_default()
                fonts['small'] = ImageFont.load_default()
                logger.warning("Using default font, Chinese characters may not display correctly")
            except:
                fonts = {}
                logger.error("Failed to load any font")
        
        return fonts
    
    def _draw_rounded_rectangle(self, draw, xy, radius, fill=None, outline=None, width=1):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = xy
        
        # 验证坐标
        if x2 <= x1 or y2 <= y1:
            logger.warning(f"Invalid rectangle coordinates: ({x1}, {y1}, {x2}, {y2})")
            return
            
        # 确保半径不会太大
        max_radius = min((x2 - x1) // 2, (y2 - y1) // 2)
        radius = min(radius, max_radius)
        
        if radius <= 0:
            # 如果半径无效，绘制普通矩形
            draw.rectangle(xy, fill=fill, outline=outline, width=width)
            return
        
        # 绘制圆角
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=outline, width=width)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=outline, width=width)
        
        # 绘制四个角的圆
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill, outline=outline, width=width)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill, outline=outline, width=width)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill, outline=outline, width=width)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill, outline=outline, width=width)
    
    def _add_shadow(self, img, draw, xy, radius, shadow_offset=3, shadow_color='#00000020'):
        """为圆角矩形添加阴影效果"""
        x1, y1, x2, y2 = xy
        # 确保坐标有效
        if x2 <= x1 or y2 <= y1:
            return
        shadow_xy = (x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset)
        self._draw_rounded_rectangle(draw, shadow_xy, radius, fill=shadow_color)
    
    def _wrap_text(self, text, font, max_width):
        """改进的文字换行处理，支持现有\n和自动换行缩进"""
        if not self.fonts:
            return [text]
        
        lines = []
        # 先按现有的\n分割文本
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                # 空行保持为空行
                lines.append("")
                continue
                
            # 处理每个段落的自动换行
            current_line = ""
            is_first_line = True
            
            for char in paragraph:
                test_line = current_line + char
                bbox = font.getbbox(test_line)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line = test_line
                else:
                    # 如果是空格或标点，尝试在前一个位置换行
                    if current_line and (char == ' ' or char in '，。！？、；：'):
                        lines.append(current_line)
                        # 自动换行的后续行添加缩进
                        current_line = ("    " if not is_first_line else "") + (char if char != ' ' else '')
                        is_first_line = False
                    elif current_line:
                        lines.append(current_line)
                        # 自动换行的后续行添加缩进
                        current_line = ("    " if not is_first_line else "") + char
                        is_first_line = False
                    else:
                        # 单个字符就超宽，强制添加
                        lines.append(char)
                        current_line = ""
            
            if current_line:
                lines.append(current_line)
        
        return lines
    
    def _draw_text_block(self, draw, text, x, y, font, color, max_width, line_height_factor=1.4):
        """绘制文本块，修复行间距问题"""
        if not self.fonts:
            draw.text((x, y), text[:100] + "...", fill=color)
            return y + 20
        
        lines = self._wrap_text(text, font, max_width)
        current_y = y
        
        # 获取字体的基础行高
        bbox = font.getbbox("测试Ag")  # 使用包含高低字符的测试字符串
        base_line_height = bbox[3] - bbox[1]
        actual_line_height = int(base_line_height * line_height_factor)
        
        for line in lines:
            if line.strip():  # 只绘制非空行
                draw.text((x, current_y), line, font=font, fill=color)
            current_y += actual_line_height
        
        return current_y
    
    def generate_paper_image(self, paper, analysis, screenshot_path):
        """
        生成左右分栏布局的论文信息图片
        
        Args:
            paper: 论文信息字典
            analysis: AI分析结果
            screenshot_path: PDF截图路径
        
        Returns:
            生成的图片文件路径
        """
        try:
            # 创建画布
            img = Image.new('RGB', (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            current_y = self.margin
            
            # 1. 绘制标题区域 - 全宽
            title_height = 120
            title_rect = (self.margin, current_y, self.width - self.margin, current_y + title_height)
            
            # 添加阴影
            self._add_shadow(img, draw, title_rect, 15)
            
            # 绘制背景矩形
            self._draw_rounded_rectangle(
                draw, title_rect, radius=15,
                fill=self.card_color, outline=None, width=0
            )
            
            # 绘制标题文字
            title_y = current_y + self.padding
            if self.fonts:
                title_y = self._draw_text_block(
                    draw, paper['title'], 
                    self.margin + self.padding, title_y,
                    self.fonts['title'], self.header_color,
                    self.width - 2 * self.margin - 2 * self.padding, 1.3
                )
            
            current_y += title_height + self.section_spacing
            
            # 2. 左右分栏区域 - 左侧信息栏，右侧PDF预览
            middle_section_height = 1200  # 增大中间分栏区域的高度
            
            # 左侧信息栏
            info_rect = (self.margin, current_y, 
                        self.margin + self.left_column_width, 
                        current_y + middle_section_height)
            
            self._add_shadow(img, draw, info_rect, 12)
            self._draw_rounded_rectangle(
                draw, info_rect, radius=12,
                fill=self.card_color, outline=None, width=0
            )
            
            # 绘制信息内容
            info_y = current_y + self.padding
            
            # ArXiv ID
            if self.fonts:
                draw.text((self.margin + self.padding, info_y), "---", 
                         font=self.fonts['body'], fill=self.accent_color)
                draw.text((self.margin + self.padding, info_y + 25), "ArXiv ID:", 
                         font=self.fonts['body'], fill=self.header_color)
                draw.text((self.margin + self.padding, info_y + 45), paper['arxiv_id'], 
                         font=self.fonts['body'], fill=self.text_color)
                info_y += 80
                
                # 作者 - 逐行显示
                draw.text((self.margin + self.padding, info_y), "---", 
                         font=self.fonts['body'], fill=self.accent_color)
                draw.text((self.margin + self.padding, info_y + 25), "作者:", 
                         font=self.fonts['body'], fill=self.header_color)
                
                author_y = info_y + 45
                authors = paper.get('authors', ['未知作者'])
                for i, author in enumerate(authors[:4]):  # 最多显示4个作者
                    draw.text((self.margin + self.padding, author_y), author, 
                             font=self.fonts['body'], fill=self.text_color)
                    author_y += 20
                
                if len(authors) > 4:
                    draw.text((self.margin + self.padding, author_y), "等...", 
                             font=self.fonts['body'], fill=self.text_color)
                    author_y += 20
                
                info_y = author_y + 20
                
                # 发布日期
                pub_date = paper.get('published_date', datetime.now()).strftime("%Y年%m月%d日")
                draw.text((self.margin + self.padding, info_y), "---", 
                         font=self.fonts['body'], fill=self.accent_color)
                draw.text((self.margin + self.padding, info_y + 25), "发布:", 
                         font=self.fonts['body'], fill=self.header_color)
                draw.text((self.margin + self.padding, info_y + 45), pub_date, 
                         font=self.fonts['body'], fill=self.text_color)
                info_y += 80
                
                # 关键词（如果有）
                if paper.get('keywords'):
                    draw.text((self.margin + self.padding, info_y), "---", 
                             font=self.fonts['body'], fill=self.accent_color)
                    draw.text((self.margin + self.padding, info_y + 25), "关键词:", 
                             font=self.fonts['body'], fill=self.header_color)
                    
                    keyword_y = info_y + 45
                    for keyword in paper['keywords'][:3]:  # 最多显示3个关键词
                        draw.text((self.margin + self.padding, keyword_y), keyword, 
                                 font=self.fonts['body'], fill=self.text_color)
                        keyword_y += 18
            
            # 右侧PDF截图区域
            pdf_rect = (self.margin + self.left_column_width + self.column_gap, current_y,
                       self.width - self.margin, current_y + middle_section_height)
            
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    # 添加阴影
                    self._add_shadow(img, draw, pdf_rect, 15)
                    
                    # 绘制截图背景
                    self._draw_rounded_rectangle(
                        draw, pdf_rect, radius=15,
                        fill=self.card_color, outline=None, width=0
                    )
                    
                    # 绘制标题栏
                    title_bar_rect = (pdf_rect[0], pdf_rect[1], pdf_rect[2], pdf_rect[1] + 40)
                    self._draw_rounded_rectangle(draw, title_bar_rect, radius=15, fill='#f1f5f9')
                    
                    if self.fonts:
                        draw.text((pdf_rect[0] + self.padding, pdf_rect[1] + 10), "📄 论文预览", 
                                 font=self.fonts['subtitle'], fill=self.header_color)
                    
                    # 加载并处理截图 - 提高清晰度
                    screenshot = Image.open(screenshot_path)
                    
                    # 计算截图尺寸 - 更大的显示区域
                    available_width = self.right_column_width - 2 * self.padding
                    available_height = middle_section_height - 60  # 减去标题栏
                    
                    # 智能缩放策略 - 最大化显示尺寸
                    screenshot_ratio = screenshot.width / screenshot.height
                    
                    # 计算两种缩放方案
                    # 方案1：按宽度缩放
                    width_based_width = available_width
                    width_based_height = int(width_based_width / screenshot_ratio)
                    
                    # 方案2：按高度缩放
                    height_based_height = available_height
                    height_based_width = int(height_based_height * screenshot_ratio)
                    
                    # 选择能完全放入容器的最大方案
                    if width_based_height <= available_height:
                        new_width = width_based_width
                        new_height = width_based_height
                    else:
                        new_width = height_based_width
                        new_height = height_based_height
                    
                    # 确保不会过小
                    if new_width < 500 or new_height < 600:
                        # 如果太小，优先保证可读性
                        new_width = max(500, new_width)
                        new_height = max(600, new_height)
                    
                    # 使用最高质量缩放
                    if new_width != screenshot.width or new_height != screenshot.height:
                        # 先放大后缩小可能会更清晰
                        if new_width > screenshot.width:
                            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.BICUBIC)
                        else:
                            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 居中粘贴截图
                    screenshot_x = pdf_rect[0] + (self.right_column_width - screenshot.width) // 2
                    screenshot_y = pdf_rect[1] + 50
                    
                    img.paste(screenshot, (screenshot_x, screenshot_y))
                    
                    # 在PDF预览区域底部添加标识
                    footer_y_in_pdf = pdf_rect[3] -40 # PDF区域底部向上40像素
                    today = datetime.now().strftime("%Y-%m-%d")
                    footer_text = f"ArXiv论文转发工具 by 贾维 | {today}"
                    if self.fonts:
                        bbox = self.fonts['small'].getbbox(footer_text)
                        footer_x_in_pdf = pdf_rect[0] + (self.right_column_width - (bbox[2] - bbox[0])) // 2
                        
                        # 添加半透明背景条
                        footer_bg_rect = (pdf_rect[0], footer_y_in_pdf - 10, pdf_rect[2], pdf_rect[3])
                        self._draw_rounded_rectangle(
                            draw, footer_bg_rect, radius=12,
                            fill='#ffffff80', outline=None, width=0  # 半透明白色背景
                        )
                        
                        draw.text((footer_x_in_pdf, footer_y_in_pdf), footer_text,
                                 font=self.fonts['small'], fill='#D3D3D3')
                    
                except Exception as e:
                    logger.warning(f"Failed to add screenshot to image: {e}")
                    # 占位符
                    self._draw_rounded_rectangle(
                        draw, pdf_rect, radius=15,
                        fill='#f8fafc', outline=None, width=0
                    )
                    if self.fonts:
                        draw.text((pdf_rect[0] + self.padding, pdf_rect[1] + middle_section_height // 2), 
                                 "PDF截图加载失败", font=self.fonts['body'], fill=self.text_color)
            
            current_y += middle_section_height + self.section_spacing
            
            # 3. AI分析区域 - 全宽，高度减小
            analysis_height = 360
            analysis_rect = (self.margin, current_y, self.width - self.margin, current_y + analysis_height)
            
            # 添加阴影
            self._add_shadow(img, draw, analysis_rect, 15)
            
            # 绘制背景
            self._draw_rounded_rectangle(
                draw, analysis_rect, radius=15,
                fill=self.ai_section_color, outline=None, width=0
            )
            
            # AI分析标题
            analysis_y = current_y + self.padding
            if self.fonts:
                draw.text((self.margin + self.padding, analysis_y), "AI智能概括", 
                         font=self.fonts['subtitle'], fill=self.header_color)
            
            # 绘制分析内容 - 修复换行问题
            analysis_content_y = current_y + 50
            if analysis and self.fonts:
                # 精确计算可用宽度
                max_width = self.width - 2 * self.margin - 2 * self.padding
                self._draw_text_block(
                    draw, analysis,
                    self.margin + self.padding, analysis_content_y,
                    self.fonts['body'], self.text_color,
                    max_width, 1.3
                )
            elif analysis:
                # fallback处理
                lines = textwrap.wrap(analysis, width=80)
                for i, line in enumerate(lines[:6]):  # 最多显示6行
                    draw.text((self.margin + self.padding, analysis_content_y + i * 20), 
                             line, fill=self.text_color)
            
            
            # 保存图片 - 高质量设置
            output_path = os.path.join(self.output_dir, f"{paper['arxiv_id']}_summary.png")
            img.save(output_path, 'PNG', quality=98, optimize=True, dpi=(150, 150))
            
            logger.info(f"Generated two-column layout paper summary image: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating paper image: {str(e)}")
            return None
    
    def generate_simple_text_image(self, paper, analysis):
        """
        生成简单的文本图片（当PDF截图不可用时）
        """
        try:
            img = Image.new('RGB', (self.width, 800), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # 简化版布局，只包含文本信息
            current_y = self.margin
            
            # 绘制主要内容区域
            self._draw_rounded_rectangle(
                draw,
                (self.margin, current_y, self.width - self.margin, 800 - self.margin),
                radius=15,
                fill=self.card_color,
                outline='#e1e8ed',
                width=2
            )
            
            content_y = current_y + self.padding * 2
            
            # 标题
            if self.fonts:
                content_y = self._draw_text_block(
                    draw, paper['title'],
                    self.margin + self.padding, content_y,
                    self.fonts['title'], self.header_color,
                    self.width - 2 * self.margin - 2 * self.padding
                ) + 20
                
                # 基本信息
                info_text = f"ArXiv ID: {paper['arxiv_id']}\n作者: {', '.join(paper.get('authors', [])[:2])}\n发布: {paper.get('published_date', datetime.now()).strftime('%Y-%m-%d')}"
                content_y = self._draw_text_block(
                    draw, info_text,
                    self.margin + self.padding, content_y,
                    self.fonts['body'], self.text_color,
                    self.width - 2 * self.margin - 2 * self.padding
                ) + 30
                
                # AI分析
                if analysis:
                    draw.text((self.margin + self.padding, content_y), "🤖 AI分析:", 
                             font=self.fonts['subtitle'], fill=self.header_color)
                    content_y += 30
                    
                    self._draw_text_block(
                        draw, analysis,
                        self.margin + self.padding, content_y,
                        self.fonts['body'], self.text_color,
                        self.width - 2 * self.margin - 2 * self.padding
                    )
            
            # 保存图片
            output_path = os.path.join(self.output_dir, f"{paper['arxiv_id']}_simple.png")
            img.save(output_path, 'PNG', quality=95)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating simple text image: {str(e)}")
            return None