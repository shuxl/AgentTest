"""
Wikipedia 数据下载工具
支持从 Wikipedia 下载文本数据并处理，用于生成文本向量
"""

import sys
import argparse
import json
import re
import time
from pathlib import Path
from typing import List, Iterator, Optional
import urllib.request
import urllib.parse
import urllib.error
from tqdm import tqdm


class WikipediaDownloader:
    """
    Wikipedia 数据下载工具类
    支持通过 API 下载 Wikipedia 文本数据
    """
    
    # Wikipedia API 端点
    API_BASE_URL = "https://{lang}.wikipedia.org/w/api.php"
    
    def __init__(self, language: str = "zh", timeout: int = 30, retry_times: int = 3):
        """
        初始化 Wikipedia 下载器
        
        Args:
            language: Wikipedia 语言代码（默认：zh 中文）
            timeout: 请求超时时间（秒，默认：30）
            retry_times: 失败重试次数（默认：3）
        """
        self.language = language
        self.api_url = self.API_BASE_URL.format(lang=language)
        self.timeout = timeout
        self.retry_times = retry_times
        
        # 设置请求头（避免某些网络环境的问题）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _make_request(self, url: str) -> Optional[dict]:
        """
        发起 HTTP 请求（带超时和重试）
        
        Args:
            url: 请求 URL
        
        Returns:
            Optional[dict]: 解析后的 JSON 数据，失败返回 None
        """
        request = urllib.request.Request(url, headers=self.headers)
        
        for attempt in range(self.retry_times):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
            except urllib.error.URLError as e:
                if attempt < self.retry_times - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    print(f"⚠️  请求失败，{wait_time}秒后重试... ({str(e)})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ 请求失败（已重试{self.retry_times}次）: {str(e)}")
                    return None
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
                return None
        
        return None
    
    def search_pages(self, search_term: str, limit: int = 10) -> List[dict]:
        """
        搜索 Wikipedia 页面
        
        Args:
            search_term: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            List[dict]: 页面信息列表
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_term,
            'srlimit': limit,
            'format': 'json'
        }
        
        url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        if not data:
            return []
        
        pages = []
        if 'query' in data and 'search' in data['query']:
            for item in data['query']['search']:
                pages.append({
                    'title': item['title'],
                    'snippet': item['snippet']
                })
        
        return pages
    
    def get_random_pages(self, count: int = 10) -> List[dict]:
        """
        获取随机 Wikipedia 页面
        
        Args:
            count: 获取页面数量
        
        Returns:
            List[dict]: 页面标题列表
        """
        params = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': 0,  # 只获取主命名空间的页面
            'rnlimit': min(count, 500),  # API 限制最多 500
            'format': 'json'
        }
        
        url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        if not data:
            return []
        
        pages = []
        if 'query' in data and 'random' in data['query']:
            for item in data['query']['random']:
                pages.append({
                    'title': item['title'],
                    'id': item['id']
                })
        
        return pages
    
    def get_page_content(self, page_title: str) -> Optional[str]:
        """
        获取页面内容
        
        Args:
            page_title: 页面标题
        
        Returns:
            Optional[str]: 页面文本内容，失败返回 None
        """
        params = {
            'action': 'query',
            'prop': 'extracts',
            'exintro': False,  # 获取完整内容，不只是介绍
            'explaintext': True,  # 纯文本格式
            'titles': page_title,
            'format': 'json'
        }
        
        url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        if not data:
            return None
        
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            for page_id, page_data in pages.items():
                if 'extract' in page_data and page_data['extract']:
                    return page_data['extract']
        
        return None
    
    def download_pages(self, page_titles: List[str], output_file: str, 
                       chunk_size: int = 512, chunk_overlap: int = 0,
                       verbose: bool = True) -> int:
        """
        下载多个页面的内容并保存
        
        Args:
            page_titles: 页面标题列表
            output_file: 输出文件路径
            chunk_size: 文本分块大小（0 表示不分块）
            chunk_overlap: 分块重叠大小
            verbose: 是否显示进度
        
        Returns:
            int: 成功下载的页面数量
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        texts = []
        success_count = 0
        
        if verbose:
            pbar = tqdm(total=len(page_titles), desc="下载页面")
        
        for title in page_titles:
            content = self.get_page_content(title)
            if content:
                if chunk_size > 0:
                    # 分块处理
                    chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                    texts.extend(chunks)
                else:
                    # 直接使用完整内容
                    texts.append(content)
                success_count += 1
            
            if verbose:
                pbar.update(1)
        
        if verbose:
            pbar.close()
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in texts:
                # 清理文本（移除多余的空白）
                cleaned_text = re.sub(r'\s+', ' ', text.strip())
                if cleaned_text:
                    f.write(cleaned_text + '\n')
        
        print(f"✅ 成功下载 {success_count}/{len(page_titles)} 个页面")
        print(f"✅ 已保存到: {output_file}")
        print(f"   文本块数量: {len(texts)}")
        
        return success_count
    
    def download_random(self, count: int, output_file: str,
                       chunk_size: int = 512, chunk_overlap: int = 0,
                       batch_size: int = 50) -> int:
        """
        下载随机页面
        
        Args:
            count: 下载页面数量
            output_file: 输出文件路径
            chunk_size: 文本分块大小（0 表示不分块）
            chunk_overlap: 分块重叠大小
            batch_size: 批量处理大小（每次 API 请求获取的页面数）
        
        Returns:
            int: 成功下载的页面数量
        """
        all_titles = []
        
        print(f"正在获取 {count} 个随机页面标题...")
        total_batches = (count + batch_size - 1) // batch_size
        
        with tqdm(total=count, desc="获取页面标题") as pbar:
            for i in range(0, count, batch_size):
                batch_count = min(batch_size, count - i)
                print(f"\n📥 批量获取 {batch_count} 个页面标题 ({i//batch_size + 1}/{total_batches})...")
                pages = self.get_random_pages(batch_count)
                
                if pages:
                    all_titles.extend([p['title'] for p in pages])
                    pbar.update(len(pages))
                else:
                    print(f"⚠️  批量 {i//batch_size + 1} 获取失败，跳过")
                    pbar.update(batch_count)  # 仍然更新进度，避免卡住
        
        if not all_titles:
            print("❌ 未能获取到任何页面标题，请检查网络连接")
            return 0
        
        print(f"\n✅ 获取了 {len(all_titles)} 个页面标题")
        
        # 下载内容
        return self.download_pages(all_titles, output_file, chunk_size, chunk_overlap)
    
    def list_category_members(self, category: str, limit: int = 500, 
                             subcategories_only: bool = False) -> dict:
        """
        列出分类下的成员（包括子分类和页面）
        
        Args:
            category: 分类名称（如 "Category:医疗"）
            limit: 返回结果数量限制
            subcategories_only: 是否只返回子分类
        
        Returns:
            dict: 包含 'subcategories' 和 'pages' 的字典
        """
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'cmlimit': limit,
            'format': 'json'
        }
        
        url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        if not data:
            return {'subcategories': [], 'pages': []}
        
        subcategories = []
        pages = []
        
        if 'query' in data and 'categorymembers' in data['query']:
            for item in data['query']['categorymembers']:
                if item['title'].startswith('Category:'):
                    subcategories.append(item['title'])
                else:
                    pages.append(item['title'])
        
        if subcategories_only:
            return {'subcategories': subcategories, 'pages': []}
        
        return {'subcategories': subcategories, 'pages': pages}
    
    def search_categories(self, keyword: str, limit: int = 50) -> List[str]:
        """
        搜索包含关键词的分类
        
        Args:
            keyword: 搜索关键词（如 "医疗"、"医学"）
            limit: 返回结果数量限制
        
        Returns:
            List[str]: 匹配的分类名称列表
        """
        categories = []
        
        # 方法1：尝试在Category命名空间搜索
        params1 = {
            'action': 'query',
            'list': 'search',
            'srsearch': keyword,
            'srnamespace': 14,  # 命名空间14是Category命名空间
            'srlimit': limit,
            'format': 'json'
        }
        
        url1 = f"{self.api_url}?{urllib.parse.urlencode(params1)}"
        data1 = self._make_request(url1)
        
        if data1 and 'query' in data1 and 'search' in data1['query']:
            for item in data1['query']['search']:
                if item['title'].startswith('Category:'):
                    categories.append(item['title'])
        
        # 方法2：如果方法1没结果，尝试搜索"Category:关键词"
        if not categories:
            params2 = {
                'action': 'query',
                'list': 'search',
                'srsearch': f"Category:{keyword}",
                'srlimit': limit,
                'format': 'json'
            }
            
            url2 = f"{self.api_url}?{urllib.parse.urlencode(params2)}"
            data2 = self._make_request(url2)
            
            if data2 and 'query' in data2 and 'search' in data2['query']:
                for item in data2['query']['search']:
                    if item['title'].startswith('Category:'):
                        if item['title'] not in categories:
                            categories.append(item['title'])
        
        return categories
    
    def get_subcategories(self, category: str, limit: int = 500) -> List[str]:
        """
        获取某个分类的子分类
        
        Args:
            category: 分类名称（如 "Category:医疗"）
            limit: 返回结果数量限制
        
        Returns:
            List[str]: 子分类名称列表
        """
        result = self.list_category_members(category, limit, subcategories_only=True)
        return result['subcategories']
    
    def download_by_category(self, category: str, output_file: str,
                            limit: int = 100, chunk_size: int = 512,
                            chunk_overlap: int = 0) -> int:
        """
        按分类下载页面
        
        Args:
            category: 分类名称（如 "Category:计算机科学"）
            output_file: 输出文件路径
            limit: 限制下载数量
            chunk_size: 文本分块大小
            chunk_overlap: 分块重叠大小
        
        Returns:
            int: 成功下载的页面数量
        """
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'cmnamespace': 0,  # 只获取主命名空间的页面，不包括子分类
            'cmlimit': limit,
            'format': 'json'
        }
        
        url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
        data = self._make_request(url)
        
        if not data:
            return 0
        
        titles = []
        if 'query' in data and 'categorymembers' in data['query']:
            for item in data['query']['categorymembers']:
                # 只下载页面，跳过子分类
                if not item['title'].startswith('Category:'):
                    titles.append(item['title'])
        
        print(f"✅ 找到 {len(titles)} 个页面")
        
        return self.download_pages(titles, output_file, chunk_size, chunk_overlap)
    
    def download_by_search(self, search_term: str, output_file: str,
                          limit: int = 50, chunk_size: int = 512,
                          chunk_overlap: int = 0) -> int:
        """
        按搜索关键词下载页面
        
        Args:
            search_term: 搜索关键词
            output_file: 输出文件路径
            limit: 限制下载数量
            chunk_size: 文本分块大小
            chunk_overlap: 分块重叠大小
        
        Returns:
            int: 成功下载的页面数量
        """
        print(f"搜索关键词: {search_term}")
        pages = self.search_pages(search_term, limit)
        
        if not pages:
            print("❌ 未找到相关页面")
            return 0
        
        titles = [p['title'] for p in pages]
        print(f"✅ 找到 {len(titles)} 个页面")
        
        return self.download_pages(titles, output_file, chunk_size, chunk_overlap)
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """
        将文本分块
        
        Args:
            text: 原始文本
            chunk_size: 每块字符数
            overlap: 重叠字符数
        
        Returns:
            List[str]: 文本块列表
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks


def main():
    # 默认输出目录
    default_output_dir = Path(__file__).parent / 'download_wikipedia'
    default_output_dir.mkdir(parents=True, exist_ok=True)
    
    parser = argparse.ArgumentParser(description='从 Wikipedia 下载文本数据或查找分类')
    parser.add_argument('--language', type=str, default='zh',
                       help='Wikipedia 语言代码（默认：zh 中文）')
    parser.add_argument('--output', type=str, default=None,
                       help=f'输出文件路径（.txt 格式，默认：保存在 {default_output_dir} 目录）')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间（秒，默认：30）')
    parser.add_argument('--retry', type=int, default=3,
                       help='失败重试次数（默认：3）')
    
    # 查找分类选项（与下载选项互斥）
    find_group = parser.add_argument_group('查找分类选项')
    find_group.add_argument('--find-categories', type=str, metavar='KEYWORD',
                           help='搜索包含关键词的分类（如："医疗"、"医学"）')
    find_group.add_argument('--list-category', type=str, metavar='CATEGORY',
                           help='列出分类下的成员和子分类（如："Category:医疗"）')
    find_group.add_argument('--list-subcategories', type=str, metavar='CATEGORY',
                           help='列出分类的子分类（如："Category:医疗"）')
    find_group.add_argument('--find-limit', type=int, default=50,
                           help='查找结果显示数量限制（默认：50）')
    
    # 数据源选项（互斥）
    data_source_group = parser.add_mutually_exclusive_group(required=False)
    data_source_group.add_argument('--random', type=int,
                                   help='下载随机页面（指定数量）')
    data_source_group.add_argument('--search', type=str,
                                   help='按关键词搜索并下载')
    data_source_group.add_argument('--category', type=str,
                                   help='按分类下载（如 "Category:计算机科学"）')
    data_source_group.add_argument('--titles', type=str,
                                   help='指定页面标题列表文件（每行一个标题）')
    
    parser.add_argument('--limit', type=int, default=100,
                       help='限制下载数量（默认：100，仅用于 --search 和 --category）')
    parser.add_argument('--chunk-size', type=int, default=512,
                       help='文本分块大小（0 表示不分块，默认：512）')
    parser.add_argument('--chunk-overlap', type=int, default=0,
                       help='文本分块重叠大小（默认：0）')
    
    args = parser.parse_args()
    
    # 检查是否只是查找操作
    is_find_mode = args.find_categories or args.list_category or args.list_subcategories
    
    # 如果是查找模式，不需要下载参数
    if is_find_mode:
        # 创建下载器
        downloader = WikipediaDownloader(
            language=args.language,
            timeout=args.timeout,
            retry_times=args.retry
        )
        
        print("="*60)
        print("Wikipedia 分类查找工具")
        print("="*60)
        print(f"语言: {args.language}\n")
        
        try:
            # 搜索分类
            if args.find_categories:
                print(f"🔍 搜索包含关键词 '{args.find_categories}' 的分类...\n")
                categories = downloader.search_categories(args.find_categories, args.find_limit)
                
                if categories:
                    print(f"✅ 找到 {len(categories)} 个相关分类：\n")
                    for i, cat in enumerate(categories, 1):
                        cat_name = cat.replace('Category:', '')
                        print(f"  {i}. {cat}")
                        print(f"     使用命令下载: --category \"{cat}\" --limit 100\n")
                else:
                    print("❌ 未找到相关分类")
                    print("\n💡 提示：")
                    print("  - 尝试其他关键词（如：'医学'、'健康'、'疾病'）")
                    print("  - 或直接在Wikipedia网站浏览分类页面")
                    print("  - Wikipedia分类页面: https://zh.wikipedia.org/wiki/Category:首页")
            
            # 列出分类成员
            elif args.list_category:
                print(f"📋 列出分类 '{args.list_category}' 的成员...\n")
                result = downloader.list_category_members(args.list_category, args.find_limit)
                
                subcategories = result['subcategories']
                pages = result['pages']
                
                print(f"📂 子分类（{len(subcategories)} 个）：")
                if subcategories:
                    for i, subcat in enumerate(subcategories[:20], 1):  # 最多显示20个
                        subcat_name = subcat.replace('Category:', '')
                        print(f"  {i}. {subcat}")
                        print(f"     使用命令下载: --category \"{subcat}\" --limit 100")
                    if len(subcategories) > 20:
                        print(f"  ... 还有 {len(subcategories) - 20} 个子分类")
                else:
                    print("  （无子分类）")
                
                print(f"\n📄 页面（{len(pages)} 个，显示前20个）：")
                if pages:
                    for i, page in enumerate(pages[:20], 1):
                        print(f"  {i}. {page}")
                    if len(pages) > 20:
                        print(f"  ... 还有 {len(pages) - 20} 个页面")
                    print(f"\n💡 下载该分类的所有页面：")
                    print(f"   python data_generation/download_wikipedia.py --category \"{args.list_category}\" --limit {min(len(pages), 500)}")
                else:
                    print("  （无页面）")
            
            # 列出子分类
            elif args.list_subcategories:
                print(f"📂 列出分类 '{args.list_subcategories}' 的子分类...\n")
                subcategories = downloader.get_subcategories(args.list_subcategories, args.find_limit)
                
                if subcategories:
                    print(f"✅ 找到 {len(subcategories)} 个子分类：\n")
                    for i, subcat in enumerate(subcategories, 1):
                        subcat_name = subcat.replace('Category:', '')
                        print(f"  {i}. {subcat}")
                        print(f"     使用命令下载: --category \"{subcat}\" --limit 100\n")
                else:
                    print("❌ 该分类没有子分类")
                    print(f"\n💡 查看该分类下的页面：")
                    print(f"   python data_generation/download_wikipedia.py --list-category \"{args.list_subcategories}\"")
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n⚠️  用户中断操作")
        except Exception as e:
            print(f"\n❌ 操作失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return
    
    # 如果不是查找模式，需要下载参数
    if not (args.random or args.search or args.category or args.titles):
        parser.error("必须指定以下选项之一：--random, --search, --category, --titles, "
                    "或查找选项：--find-categories, --list-category, --list-subcategories")
    
    # 如果未指定输出文件，自动生成文件名
    if args.output is None:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.random:
            filename = f"wikipedia_random_{args.random}_{timestamp}.txt"
        elif args.search:
            # 清理搜索关键词，用于文件名
            safe_search = re.sub(r'[^\w\s-]', '', args.search).strip()[:20]
            filename = f"wikipedia_search_{safe_search}_{timestamp}.txt"
        elif args.category:
            # 清理分类名，用于文件名
            safe_category = re.sub(r'[^\w\s-]', '', args.category.replace('Category:', '')).strip()[:20]
            filename = f"wikipedia_category_{safe_category}_{timestamp}.txt"
        elif args.titles:
            filename = f"wikipedia_titles_{timestamp}.txt"
        else:
            filename = f"wikipedia_{timestamp}.txt"
        
        args.output = str(default_output_dir / filename)
    
    # 确保输出目录存在
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("Wikipedia 数据下载工具")
    print("="*60)
    print(f"语言: {args.language}")
    print(f"输出文件: {args.output}")
    
    if args.random:
        print(f"模式: 随机下载")
        print(f"数量: {args.random}")
    elif args.search:
        print(f"模式: 关键词搜索")
        print(f"关键词: {args.search}")
        print(f"限制: {args.limit}")
    elif args.category:
        print(f"模式: 分类下载")
        print(f"分类: {args.category}")
        print(f"限制: {args.limit}")
    elif args.titles:
        print(f"模式: 指定标题列表")
        print(f"文件: {args.titles}")
    
    print(f"文本分块: {'是' if args.chunk_size > 0 else '否'}")
    if args.chunk_size > 0:
        print(f"  分块大小: {args.chunk_size}")
        print(f"  重叠大小: {args.chunk_overlap}")
    print("="*60)
    
    # 创建下载器
    downloader = WikipediaDownloader(
        language=args.language,
        timeout=args.timeout,
        retry_times=args.retry
    )
    
    # 执行下载
    success_count = 0
    
    try:
        if args.random:
            success_count = downloader.download_random(
                args.random, args.output,
                args.chunk_size, args.chunk_overlap
            )
        elif args.search:
            success_count = downloader.download_by_search(
                args.search, args.output, args.limit,
                args.chunk_size, args.chunk_overlap
            )
        elif args.category:
            success_count = downloader.download_by_category(
                args.category, args.output, args.limit,
                args.chunk_size, args.chunk_overlap
            )
        elif args.titles:
            # 从文件读取标题列表
            with open(args.titles, 'r', encoding='utf-8') as f:
                titles = [line.strip() for line in f if line.strip()]
            
            print(f"✅ 读取了 {len(titles)} 个页面标题")
            success_count = downloader.download_pages(
                titles, args.output,
                args.chunk_size, args.chunk_overlap
            )
        
        print("\n" + "="*60)
        print("✅ 下载完成！")
        print("="*60)
        print(f"成功下载: {success_count} 个页面")
        print(f"输出文件: {args.output}")
        print("\n💡 下一步：使用以下命令生成向量")
        print(f"   python data_generation/generate_text_vectors.py --file {args.output}")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断下载")
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

