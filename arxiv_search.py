"""
ArXiv论文搜索模块
使用ArXiv API搜索计算机科学领域的论文
"""

import requests
import feedparser
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)

def get_date_range_for_arxiv(days_back=7):
    """获取用于 arXiv API 查询的日期范围"""

    today = date.today()
    week_ago = today - timedelta(days=days_back)
    
    today_str = today.strftime("%Y%m%d")
    week_ago_str = week_ago.strftime("%Y%m%d")
    
    return week_ago_str, today_str

class ArxivSearcher:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.cs_categories = [
            "cs.AI",  # Artificial Intelligence
            "cs.CL",  # Computation and Language
            "cs.CV",  # Computer Vision and Pattern Recognition
            "cs.LG",  # Machine Learning
            "cs.NE",  # Neural and Evolutionary Computing
            "cs.RO",  # Robotics
            "stat.ML"  # Statistics - Machine Learning
        ]
    
    def build_query(self, keywords, max_results=50, days_back=10):
        """
        构建ArXiv搜索查询
        
        Args:
            keywords: 关键词列表
            days_back: 搜索最近几天的论文
        
        Returns:
            构建的查询字符串
        """
        # 构建关键词查询 (在标题、摘要中搜索)
        keyword_queries = []
        for keyword in keywords:
            keyword = keyword.strip()
            # keyword_queries.append(f"(ti:{keyword} OR abs:{keyword})")
            keyword_queries.append(f"all:{keyword}")

        keywords_part = " OR ".join(keyword_queries)
        
        # 构建分类查询 (计算机科学相关分类)
        category_queries = [f"cat:{cat}" for cat in self.cs_categories]
        categories_part = " OR ".join(category_queries)
        # query = f"({keywords_part}) AND ({categories_part})"

        
        # 时间限制
        start_date, end_date = get_date_range_for_arxiv(days_back)
        time_query = f"submittedDate:[{start_date}* TO {end_date}*]"

        # 组合查询
        # query = f"({keywords_part}) AND ({categories_part}) AND {time_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
        query = f"({keywords_part}) AND ({categories_part}) AND {time_query}&sortBy=lastUpdatedDate&sortOrder=descending&max_results={max_results}"
        
        return query
    
    def search_papers(self, keywords, max_results=10, days_back=1):
        """
        搜索ArXiv论文
        
        Args:
            keywords: 关键词列表
            max_results: 最大结果数量
            days_back: 搜索最近几天的论文
          
        Returns:
            论文列表
        """
        try:
            query = self.build_query(keywords, max_results, days_back)
            
            # 按照提交日期排序，获取最新的论文
            params = {
                'search_query': query,
            }
            
            logger.info(f"Searching ArXiv with query: {query}")

            response = requests.get(self.base_url, params=params, timeout=30)
            # response = requests.get(self.base_url+'/'+query,timeout=30)
            response.raise_for_status()
            
            # 解析RSS feed
            feed = feedparser.parse(response.content)
            
            papers = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                try:
                    # 提取论文信息
                    paper_info = self.extract_paper_info(entry)
                    
                    # 检查日期过滤
                    if paper_info['published_date'] >= cutoff_date:
                        papers.append(paper_info)
                        
                        # 达到所需数量就停止
                        if len(papers) >= max_results:
                            break
                    
                except Exception as e:
                    logger.warning(f"Error extracting paper info: {str(e)}")
                    continue
            
            logger.info(f"Found {len(papers)} papers matching criteria")
            return papers[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching ArXiv: {str(e)}")
            return []
    
    def extract_paper_info(self, entry):
        """
        从ArXiv API响应中提取论文信息
        
        Args:
            entry: feedparser entry对象
        
        Returns:
            论文信息字典
        """
        # 提取ArXiv ID
        arxiv_id = entry.id.split('/')[-1].split('v')[0]  # 移除版本号
        
        # 提取作者信息
        authors = []
        if hasattr(entry, 'authors'):
            authors = [author.name for author in entry.authors]
        elif hasattr(entry, 'author'):
            authors = [entry.author]
        
        # 解析发布日期
        published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
        
        # 提取分类
        categories = []
        if hasattr(entry, 'tags'):
            categories = [tag.term for tag in entry.tags]
        
        # 构建PDF链接
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        return {
            'arxiv_id': arxiv_id,
            'title': entry.title.replace('\n', ' ').replace('  ', ' ').strip(),
            'abstract': entry.summary.replace('\n', ' ').replace('  ', ' ').strip(),
            'authors': authors,
            'published_date': published_date,
            'categories': categories,
            'arxiv_url': entry.id,
            'pdf_url': pdf_url
        }