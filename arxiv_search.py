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
    
    def build_query(self, keyword, max_results=50, days_back=10):
        """
        构建ArXiv搜索查询 (单个关键词)
        
        Args:
            keyword: 单个关键词
            days_back: 搜索最近几天的论文
        
        Returns:
            构建的查询字符串
        """
        # 构建关键词查询 (在标题、摘要中搜索)
        keyword = keyword.strip()
        keyword_query = f"all:{keyword}"
        
        # 构建分类查询 (计算机科学相关分类)
        category_queries = [f"cat:{cat}" for cat in self.cs_categories]
        categories_part = " OR ".join(category_queries)
        
        # 时间限制
        start_date, end_date = get_date_range_for_arxiv(days_back)
        time_query = f"submittedDate:[{start_date}* TO {end_date}*]"

        # 组合查询 (不包含max_results，这个会单独作为参数)
        query = f"({keyword_query}) AND {time_query} AND {categories_part}"

        return query
    
    def search_papers(self, keywords, max_results=10, days_back=1):
        """
        搜索ArXiv论文 - 逐个关键词查询并合并结果
        
        Args:
            keywords: 关键词列表
            max_results: 最大结果数量
            days_back: 搜索最近几天的论文
          
        Returns:
            论文列表（已去重）
        """
        all_papers = []
        seen_arxiv_ids = set()
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # 逐个关键词查询
        for keyword in keywords:
            try:
                query = self.build_query(keyword, max_results, days_back)
                
                # 按照提交日期排序，获取最新的论文
                params = {
                    'search_query': query,
                    'sortBy': 'lastUpdatedDate',
                    'sortOrder': 'descending',
                    'max_results': max_results
                }
                
                logger.info(f"Searching ArXiv with keyword '{keyword}', query: {query}")

                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                # 解析RSS feed
                feed = feedparser.parse(response.content)
                
                keyword_papers = []
                for entry in feed.entries:
                    try:
                        # 提取论文信息
                        paper_info = self.extract_paper_info(entry)
                        
                        # 检查是否已经存在（去重）
                        if paper_info['arxiv_id'] in seen_arxiv_ids:
                            continue
                        # 检查日期过滤
                        if paper_info['published_date'] >= cutoff_date:
                            keyword_papers.append(paper_info)
                            seen_arxiv_ids.add(paper_info['arxiv_id'])
                        
                    except Exception as e:
                        logger.warning(f"Error extracting paper info: {str(e)}")
                        continue
                
                logger.info(f"Found {len(keyword_papers)} papers for keyword '{keyword}'")
                all_papers.extend(keyword_papers)
                
            except Exception as e:
                logger.error(f"Error searching ArXiv with keyword '{keyword}': {str(e)}")
                continue
        
        # 按发布时间降序排序
        all_papers.sort(key=lambda x: x['published_date'], reverse=True)
        
        logger.info(f"Total found {len(all_papers)} unique papers after merging all keywords")
        final_res_num = max(len(all_papers),max_results*len(keywords))
        
        return all_papers[:final_res_num]
    
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