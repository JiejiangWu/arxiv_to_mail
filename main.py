#!/usr/bin/env python3
"""
ArXiv Paper to Email Tool
自动搜索ArXiv论文，使用Gemini API分析摘要，并发送到邮箱
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime
from config import Config
from pdf_processor import PDFProcessor
from gemini_analyzer import GeminiAnalyzer
from email_sender import EmailSender
from wechat_sender import WeChatSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arxiv_to_mail.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main_task():
    """Main task to search papers and send emails"""
    try:
        logger.info("Starting ArXiv paper search and email task...")
        
        # Initialize components
        if Config.ARXIV_SOURCE == 'rss':
            from arxiv_search_rss import ArxivRSSSearcher
            arxiv_searcher = ArxivRSSSearcher()
        else:
            from arxiv_search import ArxivSearcher
            arxiv_searcher = ArxivSearcher()
        logger.info(f"Using arXiv search source: {Config.ARXIV_SOURCE}")
        pdf_processor = PDFProcessor()
        gemini_analyzer = GeminiAnalyzer()
        email_sender = EmailSender()
        wechat_sender = WeChatSender()
        
        # Search for papers
        papers = arxiv_searcher.search_papers(Config.KEYWORDS, Config.MAX_PAPERS, Config.MAX_BACK_DAY)
        logger.info(f"Found {len(papers)} papers")
        
        if not papers:
            logger.info("No papers found for today")
            return
        
        # Process each paper
        for i, paper in enumerate(papers, 1):
            logger.info(f"Processing paper {i}/{len(papers)}: {paper['title'][:50]}...")
            
            try:
                # Download PDF and create screenshot
                screenshot_path = pdf_processor.process_paper(paper)
                
                # Analyze abstract with Gemini
                analysis = gemini_analyzer.analyze_abstract(paper['abstract'])
                
                # Send email (choose format based on config)
                email_success = False
                if Config.SEND_AS_IMAGE:
                    email_success = email_sender.send_paper_image_email(paper, analysis, screenshot_path)
                else:
                    email_success = email_sender.send_paper_email(paper, analysis, screenshot_path)
                
                # Send to WeChat if enabled
                wechat_success = False
                if Config.WECHAT_ENABLED:
                    # For WeChat, we always use the image format
                    # Generate image if not already generated for email
                    if not Config.SEND_AS_IMAGE:
                        from image_generator import ImageGenerator
                        image_gen = ImageGenerator()
                        image_path = image_gen.generate_paper_image(paper, analysis, screenshot_path)
                        if not image_path:
                            image_path = image_gen.generate_simple_text_image(paper, analysis)
                    else:
                        # Use the same image generated for email
                        from image_generator import ImageGenerator
                        image_gen = ImageGenerator()
                        image_path = image_gen.generate_paper_image(paper, analysis, screenshot_path)
                    
                    if image_path:
                        wechat_success = wechat_sender.send_paper_image(paper, image_path)
                    else:
                        logger.warning("Failed to generate image for WeChat sending")
                
                # Log results
                if email_success and (not Config.WECHAT_ENABLED or wechat_success):
                    logger.info(f"Successfully processed and sent paper {i}")
                elif email_success:
                    logger.warning(f"Paper {i} sent via email but failed via WeChat")
                elif wechat_success:
                    logger.warning(f"Paper {i} sent via WeChat but failed via email")
                else:
                    logger.error(f"Paper {i} failed to send via both email and WeChat")
                
            except Exception as e:
                logger.error(f"Error processing paper {i}: {str(e)}")
                continue
        
        logger.info("Task completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main task: {str(e)}")

def run_once():
    """Run the task once"""
    main_task()

def run_scheduled():
    """Run the task on schedule"""
    schedule.every().day.at(Config.SCHEDULE_TIME).do(main_task)
    
    logger.info(f"Scheduled daily task at {Config.SCHEDULE_TIME}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        # Validate configuration
        Config.validate()
        
        # Create download directory
        os.makedirs(Config.PDF_DOWNLOAD_DIR, exist_ok=True)
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "once":
            run_once()
        else:
            run_scheduled()
            
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)