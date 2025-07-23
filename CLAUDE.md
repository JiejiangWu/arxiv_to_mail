# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing and Running
- **Test run (single execution)**: `python main.py once` or `python run.py test`
- **Start scheduled service**: `python main.py` or `python run.py start`
- **Install dependencies**: `pip install -r requirements.txt` or `python run.py install`
- **Setup project**: `python run.py setup` (installs deps, creates .env from .env.example, creates directories)
- **Check status**: `python run.py status` (validates dependencies, config, shows recent logs)

### Configuration
- Environment variables are loaded from `.env` file using python-dotenv
- Required variables: `GEMINI_API_KEY`, `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAIL`
- Optional variables: `SEND_AS_IMAGE` (true/false, default: true) - controls email format
- Configuration validation happens in `config.py:Config.validate()`
- Create `.env` from `.env.example` template

## Architecture Overview

This is an automated ArXiv paper discovery and email notification system with the following components:

### Core Workflow (main.py)
1. **ArxivSearcher** searches for papers using keywords in CS categories (AI, ML, CV, CL, etc.)
2. **PDFProcessor** downloads PDFs and generates first-page screenshots
3. **GeminiAnalyzer** uses Google Gemini API to analyze abstracts in Chinese
4. **EmailSender** sends formatted emails with paper info, screenshots, and AI analysis

### Key Modules
- **config.py**: Centralized configuration management with environment variable loading and validation
- **arxiv_search.py**: ArXiv API integration with CS category filtering and keyword-based search
- **pdf_processor.py**: PDF download and screenshot generation using PyMuPDF and Pillow
- **gemini_analyzer.py**: Google Gemini AI integration for Chinese abstract analysis
- **image_generator.py**: Generates shareable images combining paper info, PDF screenshot, and AI analysis
- **email_sender.py**: SMTP email sending with both HTML and image format options
- **run.py**: CLI wrapper providing setup, testing, and status checking commands

### Data Flow
- Papers are searched daily based on configured keywords and CS categories
- Each paper gets: PDF downloaded → screenshot created → abstract analyzed → email sent
- Two email formats: HTML (detailed layout) or Image (shareable social media format)
- Image format combines all content into a single PNG for easy sharing
- Supports both single execution (`once` mode) and scheduled daily runs
- All operations are logged to `arxiv_to_mail.log`

### Configuration Dependencies
- Gemini API key for abstract analysis
- Gmail SMTP credentials (requires app-specific password)
- Configurable search keywords, paper limits, and schedule timing
- Download directory for PDFs and screenshots

### Error Handling
- Configuration validation on startup
- Graceful paper processing failures (continues with next paper)
- Gemini API fallback mechanisms
- Comprehensive logging throughout the pipeline