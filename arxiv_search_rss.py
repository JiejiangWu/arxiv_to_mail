"""
ArXiv论文RSS搜索模块
从 rss.arxiv.org/rss/cs 拉取RSS，按日期与关键词过滤
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set

import feedparser
import requests
import re
import html as html_lib

logger = logging.getLogger(__name__)


class ArxivRSSSearcher:
    """基于 arXiv CS RSS 源的搜索器。

    - 数据源: http://rss.arxiv.org/rss/cs
    - 过滤: 依据发布时间窗口(days_back)与关键词(标题/摘要匹配)
    - 返回数据结构与 `arxiv_search.ArxivSearcher.extract_paper_info` 一致
    """

    RSS_URL = "http://rss.arxiv.org/rss/cs"

    def __init__(self) -> None:
        pass

    def search_papers(self, keywords: List[str], max_results: int = 10, days_back: int = 1) -> List[Dict[str, Any]]:
        """从 CS RSS 源抓取论文，并按日期窗口与关键词过滤。

        Args:
            keywords: 关键词列表（大小写不敏感），在标题与摘要中进行匹配
            max_results: 每个关键词的最大抓取数量上限（用于限制最终数量）
            days_back: 近几天的论文（默认1天，即“每日”）

        Returns:
            符合条件的论文列表（去重，按发布时间倒序）。字段：
            - arxiv_id, title, abstract, authors, published_date, categories, arxiv_url, pdf_url
        """
        cutoff_dt = datetime.now() - timedelta(days=days_back)
        keywords_norm = [kw.strip().lower() for kw in keywords if kw and kw.strip()]

        logger.info(
            f"Fetching arXiv CS RSS feed, filtering by last {days_back} day(s) and keywords: {keywords_norm}"
        )

        try:
            resp = requests.get(self.RSS_URL, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed: {e}")
            return []

        feed = feedparser.parse(resp.content)
        if getattr(feed, "bozo", 0):
            logger.warning("RSS feed parsing encountered issues, attempting to continue with recovered entries")

        results: List[Dict[str, Any]] = []
        seen_ids: Set[str] = set()

        for entry in getattr(feed, "entries", []):
            try:
                paper_info = self._extract_paper_info(entry)
            except Exception as e:
                logger.warning(f"Error extracting paper info: {e}")
                continue

            # 日期过滤
            if paper_info["published_date"] < cutoff_dt:
                continue

            # 关键词过滤（标题/摘要）
            text_blob = f"{paper_info['title']}\n{paper_info['abstract']}".lower()
            if keywords_norm and not any(kw in text_blob for kw in keywords_norm):
                continue

            # 去重
            if paper_info["arxiv_id"] in seen_ids:
                continue

            seen_ids.add(paper_info["arxiv_id"])
            results.append(paper_info)

        # 排序与截断
        results.sort(key=lambda x: x["published_date"], reverse=True)

        # 近似与现有逻辑对齐：给出不低于 max_results*len(keywords) 的上限，避免漏掉同一天多关键词命中
        final_cap = max(len(results), max_results * max(1, len(keywords)))
        return results[:final_cap]

    def _extract_paper_info(self, entry: Any) -> Dict[str, Any]:
        """从 RSS entry 提取论文信息，字段对齐 `arxiv_search.extract_paper_info`。
        - arxiv_id: 从 link/links 提取，不含版本号
        - authors: 使用 entry.authors 或 entry.author，并拆分逗号/and
        - published_date: 优先使用 published_parsed
        - categories: 来自 entry.tags（如可用）
        - arxiv_url: 条目的原文链接（abs页）
        - pdf_url: https://arxiv.org/pdf/{id}.pdf
        """
        # 链接与ID
        entry_link = getattr(entry, "link", None) or ""
        if not entry_link and hasattr(entry, "links") and entry.links:
            try:
                alt = next((l for l in entry.links if getattr(l, "rel", "") == "alternate" and "arxiv.org/abs/" in getattr(l, "href", "")), None)
                entry_link = getattr(alt, "href", "") if alt else ""
            except Exception:
                entry_link = ""
        entry_id_raw = getattr(entry, "id", None) or ""
        link_for_id = entry_link or entry_id_raw
        arxiv_id = self._extract_arxiv_id_from_link(link_for_id)

        # 作者
        authors: List[str] = []
        if hasattr(entry, "authors") and entry.authors:
            names = []
            for a in entry.authors:
                name_val = getattr(a, "name", "").strip()
                if not name_val:
                    continue
                # 如果单个 name 包含多个作者，用逗号/and 拆分
                parts = [p.strip() for p in re.split(r",| and ", name_val) if p.strip()]
                names.extend(parts if len(parts) > 1 else [name_val])
            authors = [n for n in (n.strip() for n in names) if n]
        elif hasattr(entry, "author") and entry.author:
            raw_author = entry.author.strip()
            parts = [p.strip() for p in re.split(r",| and ", raw_author) if p.strip()]
            authors = parts if len(parts) > 1 else [raw_author]

        # 发布时间
        published_dt: datetime
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_dt = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published_dt = datetime(*entry.updated_parsed[:6])
        else:
            published_str = getattr(entry, "published", None) or getattr(entry, "updated", None) or ""
            published_dt = self._safe_parse_datetime(published_str)

        # 分类
        categories: List[str] = []
        if hasattr(entry, "tags") and entry.tags:
            categories = [t.term for t in entry.tags if hasattr(t, "term")]

        title = (getattr(entry, "title", "") or "").replace("\n", " ").replace("  ", " ").strip()
        # 摘要：从 summary 中截取 Abstract: 之后的内容，并反转义 HTML 实体
        raw_summary = getattr(entry, "summary", "") or ""
        cleaned_summary = raw_summary
        if "Abstract:" in raw_summary:
            try:
                cleaned_summary = raw_summary.split("Abstract:", 1)[1]
            except Exception:
                cleaned_summary = raw_summary
        cleaned_summary = html_lib.unescape(cleaned_summary)
        cleaned_summary = cleaned_summary.replace("\n", " ").replace("  ", " ").strip()

        arxiv_url = entry_link or entry_id_raw
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else ""

        return {
            "arxiv_id": arxiv_id or "",
            "title": title,
            "abstract": cleaned_summary,
            "authors": authors,
            "published_date": published_dt,
            "categories": categories,
            "arxiv_url": arxiv_url,
            "pdf_url": pdf_url,
        }

    @staticmethod
    def _extract_arxiv_id_from_link(link: str) -> str:
        """从 RSS 的 entry 链接或 OAI ID 提取 arXiv ID，移除结尾版本号。
        支持如下形式：
        - https://arxiv.org/abs/XXXX.YYYYv3
        - https://arxiv.org/pdf/XXXX.YYYYv1.pdf
        - oai:arXiv.org:XXXX.YYYYv2
        - oai:arXiv.org:cs/0501001v2
        """
        if not link:
            return ""
        try:
            candidate = link
            # 优先从 /abs/ 或 /pdf/ 提取
            for token in ["/abs/", "/pdf/"]:
                if token in candidate:
                    candidate = candidate.split(token, 1)[1]
                    break

            # 如果仍然不是常规形式，处理 OAI: 取最后一个冒号后的部分
            if ":" in candidate and (candidate.startswith("oai:") or "arXiv.org:" in candidate):
                candidate = candidate.split(":")[-1]

            # 去掉 .pdf 与 URL 参数
            candidate = candidate.split(".pdf", 1)[0]
            candidate = candidate.split("?", 1)[0]

            # 仅移除结尾版本号 v\d+
            candidate = re.sub(r"v\d+$", "", candidate)
            return candidate.strip()
        except Exception:
            return ""

    @staticmethod
    def _safe_parse_datetime(dt_str: str) -> datetime:
        """尽力解析时间字符串；失败时返回当前时间，避免中断流程。"""
        if not dt_str:
            return datetime.now()
        for fmt in [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]:
            try:
                return datetime.strptime(dt_str, fmt)
            except Exception:
                continue
        return datetime.now() 