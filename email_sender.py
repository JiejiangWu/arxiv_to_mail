"""
邮件发送模块
发送包含论文信息和分析结果的邮件
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import logging
from config import Config
from image_generator import ImageGenerator

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.SENDER_PASSWORD
        self.recipient_email = Config.RECIPIENT_EMAIL
        self.image_generator = ImageGenerator()
    
    def create_email_content(self, paper, analysis):
        """
        创建邮件HTML内容
        
        Args:
            paper: 论文信息字典
            analysis: Gemini分析结果
        
        Returns:
            HTML格式的邮件内容
        """
        # 格式化日期
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 格式化作者列表
        authors_str = ", ".join(paper.get('authors', ['未知作者'])[:5])  # 最多显示5个作者
        if len(paper.get('authors', [])) > 5:
            authors_str += " 等"
        
        # 格式化发布日期
        pub_date = paper.get('published_date', datetime.now()).strftime("%Y年%m月%d日")
        
        # 创建HTML内容
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .paper-title {{
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            line-height: 1.3;
        }}
        .paper-info {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #4CAF50;
            margin: 20px 0;
        }}
        .info-item {{
            margin: 8px 0;
            color: #555;
        }}
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .analysis-section {{
            background-color: #e8f5e8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .analysis-title {{
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 8px;
        }}
        .screenshot-section {{
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .screenshot-title {{
            color: #2c3e50;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .screenshot-img {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
            text-align: center;
        }}
        .arxiv-link {{
            color: #4CAF50;
            text-decoration: none;
            font-weight: bold;
        }}
        .arxiv-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="paper-title">{paper['title']}</div>
        </div>
        
        <div class="paper-info">
            <div class="info-item">
                <span class="info-label">ArXiv编号：</span>{paper['arxiv_id']}
            </div>
            <div class="info-item">
                <span class="info-label">作者：</span>{authors_str}
            </div>
            <div class="info-item">
                <span class="info-label">发布日期：</span>{pub_date}
            </div>
            <div class="info-item">
                <span class="info-label">ArXiv链接：</span>
                <a href="{paper.get('arxiv_url', '#')}" class="arxiv-link">查看原文</a>
            </div>
        </div>
        
        <div class="screenshot-section">
            <div class="screenshot-title">📄 论文首页预览</div>
            <img src="cid:screenshot" alt="论文首页截图" class="screenshot-img">
        </div>
        
        <div class="analysis-section">
            <div class="analysis-title">🤖 AI智能分析</div>
            <div style="white-space: pre-line; color: #2c3e50; line-height: 1.8;">
{analysis}
            </div>
        </div>
        
        <div class="footer">
            <p>📧 这是一封自动生成的论文分享邮件</p>
            <p>🤖 由ArXiv论文转发工具自动发送 | ⏰ {today}</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def send_paper_email(self, paper, analysis, screenshot_path):
        """
        发送论文邮件
        
        Args:
            paper: 论文信息字典
            analysis: 分析结果
            screenshot_path: 截图文件路径
        
        Returns:
            发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('related')
            
            # 设置邮件主题
            today = datetime.now().strftime("%Y-%m-%d")
            subject = f"【AI论文分享】{today}-{paper['title'][:30]}..."
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # 创建HTML内容
            html_content = self.create_email_content(paper, analysis)
            
            # 添加HTML内容到邮件
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加截图附件
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    with open(screenshot_path, 'rb') as f:
                        screenshot_data = f.read()
                    
                    screenshot_part = MIMEImage(screenshot_data)
                    screenshot_part.add_header('Content-ID', '<screenshot>')
                    screenshot_part.add_header('Content-Disposition', 'inline', filename=f"{paper['arxiv_id']}.png")
                    msg.attach(screenshot_part)
                    
                except Exception as e:
                    logger.warning(f"Failed to attach screenshot: {str(e)}")
            
            # 发送邮件
            logger.info(f"Sending email for paper: {paper['arxiv_id']}")
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                # server.starttls()  # 启用TLS加密
                server.login(self.sender_email, self.sender_password)
                
                text = msg.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
            
            logger.info(f"Email sent successfully for paper: {paper['arxiv_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email for paper {paper.get('arxiv_id', 'unknown')}: {str(e)}")
            return False
    
    def send_paper_image_email(self, paper, analysis, screenshot_path):
        """
        发送论文图片邮件（将内容生成为图片发送）
        
        Args:
            paper: 论文信息字典
            analysis: 分析结果
            screenshot_path: 截图文件路径
        
        Returns:
            发送是否成功
        """
        try:
            # 生成论文摘要图片
            logger.info(f"Generating summary image for paper: {paper['arxiv_id']}")
            image_path = self.image_generator.generate_paper_image(paper, analysis, screenshot_path)
            
            if not image_path or not os.path.exists(image_path):
                logger.warning("Failed to generate image, trying simple text image")
                image_path = self.image_generator.generate_simple_text_image(paper, analysis)
            
            if not image_path or not os.path.exists(image_path):
                logger.error("Failed to generate any image, falling back to HTML email")
                return self.send_paper_email(paper, analysis, screenshot_path)
            
            # 创建邮件对象
            msg = MIMEMultipart('related')
            
            # 设置邮件主题
            today = datetime.now().strftime("%Y-%m-%d")
            subject = f"【AI论文分享】{today}-{paper['title'][:30]}..."
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # 创建简单的HTML内容作为邮件正文
            simple_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .image-container {{
            margin: 20px 0;
        }}
        .summary-image {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }}
        .arxiv-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>📚 AI论文分享</h2>
        <p>以下是今日推荐的ArXiv论文摘要，点击查看原文：</p>
        
        <div class="image-container">
            <img src="cid:summary_image" alt="论文摘要图片" class="summary-image">
        </div>
        
        <p>
            <a href="{paper.get('arxiv_url', '#')}" class="arxiv-link">📖 查看论文原文</a>
        </p>
        
        <div class="footer">
            <p>🤖 ArXiv论文转发工具自动生成 | ⏰ {today}</p>
            <p>💡 此图片可直接保存分享到社交媒体</p>
        </div>
    </div>
</body>
</html>
"""
            
            # 添加HTML内容到邮件
            html_part = MIMEText(simple_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加图片附件（内嵌显示）
            try:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                image_part = MIMEImage(image_data)
                image_part.add_header('Content-ID', '<summary_image>')
                image_part.add_header('Content-Disposition', 'inline', 
                                    filename=f"{paper['arxiv_id']}_summary.png")
                msg.attach(image_part)
                
            except Exception as e:
                logger.warning(f"Failed to attach summary image: {str(e)}")
                return False
            
            # 发送邮件
            logger.info(f"Sending image email for paper: {paper['arxiv_id']}")
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                
                text = msg.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
            
            logger.info(f"Image email sent successfully for paper: {paper['arxiv_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending image email for paper {paper.get('arxiv_id', 'unknown')}: {str(e)}")
            return False
    
    def send_daily_summary_email(self, papers_count, success_count, failed_count):
        """
        发送每日汇总邮件
        
        Args:
            papers_count: 发现的论文总数
            success_count: 成功处理的论文数
            failed_count: 失败的论文数
        
        Returns:
            发送是否成功
        """
        try:
            msg = MIMEMultipart()
            
            today = datetime.now().strftime("%Y-%m-%d")
            msg['Subject'] = f"【AI论文分享】{today} 每日汇总报告"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # 创建汇总内容
            summary_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .summary-box {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .stat {{
            margin: 10px 0;
            font-size: 16px;
        }}
        .number {{
            font-weight: bold;
            color: #4CAF50;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <h2>📊 {today} 论文处理汇总</h2>
    <div class="summary-box">
        <div class="stat">🔍 发现论文总数: <span class="number">{papers_count}</span> 篇</div>
        <div class="stat">✅ 成功处理: <span class="number">{success_count}</span> 篇</div>
        <div class="stat">❌ 处理失败: <span class="number">{failed_count}</span> 篇</div>
        <div class="stat">📧 成功率: <span class="number">{(success_count/max(papers_count,1)*100):.1f}%</span></div>
    </div>
    
    <p style="margin-top: 30px; color: #666; text-align: center;">
        🤖 ArXiv论文转发工具自动发送
    </p>
</body>
</html>
"""
            
            html_part = MIMEText(summary_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送汇总邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                text = msg.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
            
            logger.info("Daily summary email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily summary email: {str(e)}")
            return False