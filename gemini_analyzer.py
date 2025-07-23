"""
Gemini API分析模块
使用Google Gemini API分析论文摘要并生成概括
"""

import google.generativeai as genai
import logging
from config import Config

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        # 配置Gemini API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # 选择模型
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # 分析提示词模板
        self.analysis_prompt_template = """
请分析以下ArXiv论文的摘要，并提供一个简洁明了的中文概括。请按照以下格式输出：

**研究领域**：[论文所属的具体研究领域]

**核心贡献**：[论文的主要贡献和创新点，1-2句话]

**技术方法**：[使用的主要技术方法或算法，1-2句话]

**实验结果**：[关键实验结果或性能表现，如果摘要中有提到的话，1句话]

**意义价值**：[该研究的实际应用价值或学术意义，1句话]

论文标题：{title}

论文摘要：{abstract}

请用通俗易懂的中文进行概括，每部分控制在50字以内，总长度不超过300字。
"""
    
    def analyze_abstract(self, abstract, title="", max_retries=3):
        """
        使用Gemini API分析论文摘要
        
        Args:
            abstract: 论文摘要
            title: 论文标题（可选）
            max_retries: 最大重试次数
        
        Returns:
            分析结果字符串
        """
        try:
            # 构建提示词
            prompt = self.analysis_prompt_template.format(
                title=title,
                abstract=abstract
            )
            
            logger.info("Analyzing abstract with Gemini API...")
            
            # 调用Gemini API
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    
                    if response.text:
                        analysis = response.text.strip()
                        logger.info("Abstract analysis completed successfully")
                        return analysis
                    else:
                        logger.warning(f"Empty response from Gemini API, attempt {attempt + 1}")
                        
                except Exception as e:
                    logger.warning(f"Gemini API call failed on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    
            # 如果所有重试都失败，返回默认分析
            return self._get_fallback_analysis(abstract, title)
            
        except Exception as e:
            logger.error(f"Error analyzing abstract with Gemini: {str(e)}")
            return self._get_fallback_analysis(abstract, title)
    
    def _get_fallback_analysis(self, abstract, title=""):
        """
        当Gemini API不可用时的备用分析
        
        Args:
            abstract: 论文摘要
            title: 论文标题
        
        Returns:
            简单的备用分析
        """
        logger.info("Using fallback analysis due to Gemini API unavailable")
        
        # 简单的关键词匹配来判断研究领域
        field = "人工智能"
        if any(word in abstract.lower() for word in ["machine learning", "deep learning", "neural"]):
            field = "机器学习"
        elif any(word in abstract.lower() for word in ["computer vision", "image", "visual"]):
            field = "计算机视觉"
        elif any(word in abstract.lower() for word in ["natural language", "nlp", "text"]):
            field = "自然语言处理"
        elif any(word in abstract.lower() for word in ["robot", "control", "planning"]):
            field = "机器人学"
        
        fallback_analysis = f"""
**研究领域**：{field}

**核心贡献**：该论文在{field}领域提出了新的方法和见解。

**技术方法**：采用了先进的算法和技术框架来解决相关问题。

**实验结果**：实验验证了所提方法的有效性。

**意义价值**：为{field}领域的发展提供了有价值的贡献。

注：此为自动生成的简化分析，详细内容请查看原论文摘要。
"""
        return fallback_analysis.strip()
    
    def analyze_multiple_papers(self, papers):
        """
        批量分析多篇论文
        
        Args:
            papers: 论文列表
        
        Returns:
            包含分析结果的论文列表
        """
        analyzed_papers = []
        
        for i, paper in enumerate(papers, 1):
            try:
                logger.info(f"Analyzing paper {i}/{len(papers)}: {paper['title'][:50]}...")
                
                analysis = self.analyze_abstract(
                    paper['abstract'], 
                    paper['title']
                )
                
                # 将分析结果添加到论文信息中
                paper_with_analysis = paper.copy()
                paper_with_analysis['analysis'] = analysis
                analyzed_papers.append(paper_with_analysis)
                
                logger.info(f"Paper {i} analysis completed")
                
            except Exception as e:
                logger.error(f"Error analyzing paper {i}: {str(e)}")
                # 即使分析失败，也保留论文信息（不包含分析）
                paper_with_analysis = paper.copy()
                paper_with_analysis['analysis'] = self._get_fallback_analysis(
                    paper['abstract'], 
                    paper['title']
                )
                analyzed_papers.append(paper_with_analysis)
        
        return analyzed_papers