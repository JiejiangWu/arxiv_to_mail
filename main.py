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
from arxiv_search import ArxivSearcher
from pdf_processor import PDFProcessor
from gemini_analyzer import GeminiAnalyzer
from email_sender import EmailSender

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
        arxiv_searcher = ArxivSearcher()
        pdf_processor = PDFProcessor()
        gemini_analyzer = GeminiAnalyzer()
        email_sender = EmailSender()
        
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
                if Config.SEND_AS_IMAGE:
                    email_sender.send_paper_image_email(paper, analysis, screenshot_path)
                else:
                    email_sender.send_paper_email(paper, analysis, screenshot_path)
                
                logger.info(f"Successfully processed and sent paper {i}")
                
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