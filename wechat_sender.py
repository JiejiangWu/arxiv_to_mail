"""
微信发送模块
使用wxauto库发送论文图片到微信
"""

import os
import logging
from typing import Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class WeChatSender:
    def __init__(self):
        self.enabled = Config.WECHAT_ENABLED
        self.recipient_username = Config.WECHAT_RECIPIENT
        self.wx = None
        
        if self.enabled:
            try:
                # 延迟导入，避免在非Windows环境下导入失败
                import wxauto
                self.wxauto = wxauto
                logger.info("wxauto library imported successfully")
            except ImportError as e:
                logger.error(f"Failed to import wxauto: {e}")
                logger.error("Please install wxauto: pip install wxauto")
                self.enabled = False
    
    def _initialize_wechat(self):
        """初始化微信实例"""
        if not self.enabled:
            return False
            
        try:
            if self.wx is None:
                logger.info("Initializing WeChat connection...")
                self.wx = self.wxauto.WeChat()
                logger.info("WeChat connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WeChat: {e}")
            return False
    
    def send_paper_image(self, paper, image_path):
        """
        发送论文图片到微信
        
        Args:
            paper: 论文信息字典
            image_path: 图片文件路径
        
        Returns:
            bool: 发送是否成功
        """
        if not self.enabled:
            logger.warning("WeChat sending is disabled")
            return False
            
        if not self.recipient_username:
            logger.error("WeChat recipient username not configured")
            return False
            
        if not image_path or not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False
        
        try:
            # 初始化微信连接
            if not self._initialize_wechat():
                return False
            
            # 发送图片
            logger.info(f"Sending image to WeChat user: {self.recipient_username}")
            logger.info(f"Image path: {image_path}")
            
            # 使用wxauto发送文件
            success = self.wx.SendFiles(image_path, who=self.recipient_username)
            
            if success:
                logger.info(f"Successfully sent paper image to WeChat: {paper.get('arxiv_id', 'unknown')}")
                return True
            else:
                logger.error("Failed to send image via wxauto.SendFiles")
                return False
                
        except Exception as e:
            logger.error(f"Error sending image to WeChat: {e}")
            return False
    
    def test_connection(self):
        """
        测试微信连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.enabled:
            logger.info("WeChat sending is disabled in config")
            return False
        
        try:
            if self._initialize_wechat():
                logger.info("WeChat connection test successful")
                return True
            else:
                logger.error("WeChat connection test failed - initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"WeChat connection test failed: {e}")
            return False