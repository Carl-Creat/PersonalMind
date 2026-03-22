"""
PersonalMind 文件理解模块

支持：
- 图片理解（GPT-4V）
- PDF 文档读取和总结
- 网页内容抓取
- 链接内容解析
"""
import os
import io
import re
import base64
import requests
from typing import Optional, List, Dict, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileContent:
    """文件内容"""
    filename: str
    content: str
    file_type: str
    size: int
    extracted_at: datetime = datetime.now


@dataclass
class ImageAnalysis:
    """图片分析结果"""
    description: str
    tags: List[str]
    text_found: str  # OCR 提取的文字
    analysis: str  # 详细分析


class FileProcessor:
    """
    文件处理器
    
    支持多种文件格式的理解和分析
    """
    
    def __init__(self, llm_func=None):
        self.llm = llm_func
    
    def process_file(self, filepath: str) -> FileContent:
        """
        处理文件
        
        Args:
            filepath: 文件路径
        
        Returns:
            文件内容
        """
        ext = os.path.splitext(filepath)[1].lower()
        
        processors = {
            ".txt": self._process_text,
            ".md": self._process_text,
            ".pdf": self._process_pdf,
            ".doc": self._process_doc,
            ".docx": self._process_docx,
            ".jpg": self._process_image,
            ".jpeg": self._process_image,
            ".png": self._process_image,
            ".gif": self._process_image,
            ".webp": self._process_image,
        }
        
        processor = processors.get(ext, self._process_unknown)
        return processor(filepath)
    
    def _process_text(self, filepath: str) -> FileContent:
        """处理文本文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return FileContent(
            filename=os.path.basename(filepath),
            content=content,
            file_type="text",
            size=len(content)
        )
    
    def _process_pdf(self, filepath: str) -> FileContent:
        """处理 PDF 文件"""
        try:
            import pypdf
            
            reader = pypdf.PdfReader(filepath)
            text_parts = []
            
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            content = "\n".join(text_parts)
            
            return FileContent(
                filename=os.path.basename(filepath),
                content=content,
                file_type="pdf",
                size=len(content)
            )
        except ImportError:
            return FileContent(
                filename=os.path.basename(filepath),
                content="（需要安装 pypdf 来读取 PDF）",
                file_type="pdf",
                size=0
            )
    
    def _process_doc(self, filepath: str) -> FileContent:
        """处理 Word .doc 文件"""
        try:
            import docx2txt
            content = docx2txt.process(filepath)
            
            return FileContent(
                filename=os.path.basename(filepath),
                content=content,
                file_type="doc",
                size=len(content)
            )
        except ImportError:
            return FileContent(
                filename=os.path.basename(filepath),
                content="（需要安装 python-docx 来读取 .doc 文件）",
                file_type="doc",
                size=0
            )
    
    def _process_docx(self, filepath: str) -> FileContent:
        """处理 Word .docx 文件"""
        try:
            import docx2txt
            content = docx2txt.process(filepath)
            
            return FileContent(
                filename=os.path.basename(filepath),
                content=content,
                file_type="docx",
                size=len(content)
            )
        except ImportError:
            return FileContent(
                filename=os.path.basename(filepath),
                content="（需要安装 python-docx 来读取 .docx 文件）",
                file_type="docx",
                size=0
            )
    
    def _process_image(self, filepath: str) -> FileContent:
        """处理图片文件"""
        # 读取图片并转为 base64
        with open(filepath, 'rb') as f:
            img_data = f.read()
        
        # 返回基本信息，实际分析由 analyze_image 处理
        return FileContent(
            filename=os.path.basename(filepath),
            content=f"[图片文件: {len(img_data)} bytes]",
            file_type="image",
            size=len(img_data)
        )
    
    def _process_unknown(self, filepath: str) -> FileContent:
        """处理未知格式"""
        return FileContent(
            filename=os.path.basename(filepath),
            content=f"（不支持的文件格式: {os.path.splitext(filepath)[1]}）",
            file_type="unknown",
            size=0
        )
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """
        总结文本
        
        Args:
            text: 文本内容
            max_length: 最大长度
        
        Returns:
            总结
        """
        if self.llm:
            return self.llm(f"请总结以下内容，用 {max_length} 字以内：\n\n{text[:3000]}")
        
        # 简单截断
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."


class WebContentExtractor:
    """网页内容提取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract(self, url: str) -> FileContent:
        """
        提取网页内容
        
        Args:
            url: 网页 URL
        
        Returns:
            提取的内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 简单 HTML 解析
            content = self._parse_html(response.text)
            
            return FileContent(
                filename=url,
                content=content,
                file_type="webpage",
                size=len(content)
            )
            
        except Exception as e:
            return FileContent(
                filename=url,
                content=f"（网页抓取失败：{str(e)}）",
                file_type="webpage",
                size=0
            )
    
    def _parse_html(self, html: str) -> str:
        """简单 HTML 解析，提取正文"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 提取正文
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # 清理空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines[:100])  # 限制行数


class ImageAnalyzer:
    """图片分析器"""
    
    def __init__(self, llm_func=None):
        self.llm = llm_func
    
    def analyze(self, filepath: str) -> ImageAnalysis:
        """
        分析图片
        
        Args:
            filepath: 图片路径
        
        Returns:
            分析结果
        """
        # 读取图片并转为 base64
        with open(filepath, 'rb') as f:
            img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        if self.llm:
            return self._llm_analyze(filepath, img_base64)
        
        # 简单返回基本信息
        return ImageAnalysis(
            description=f"这是一张 {os.path.basename(filepath)} 图片",
            tags=["图片"],
            text_found="",
            analysis="（需要配置 LLM 来分析图片）"
        )
    
    def _llm_analyze(self, filepath: str, img_base64: str) -> ImageAnalysis:
        """使用 LLM 分析图片（GPT-4V）"""
        try:
            import openai
            
            # 使用 GPT-4 Vision 分析
            response = openai.chat.completions.create(
                model="gpt-4o",  # 支持视觉的模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请详细描述这张图片，包括：1) 图片内容 2) 关键细节 3) 如果有文字请 OCR 提取 4) 你的专业分析和建议"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # 简单提取标签
            tags = self._extract_tags(analysis_text)
            
            # 提取发现的文字
            text_found = self._extract_text(analysis_text)
            
            return ImageAnalysis(
                description=analysis_text[:200],
                tags=tags,
                text_found=text_found,
                analysis=analysis_text
            )
            
        except Exception as e:
            return ImageAnalysis(
                description=f"（图片分析失败：{str(e)}）",
                tags=[],
                text_found="",
                analysis=""
            )
    
    def _extract_tags(self, text: str) -> List[str]:
        """提取关键词作为标签"""
        # 简单实现
        common_tags = [
            "图表", "数据", "人物", "风景", "文字", "代码",
            "产品", "界面", "截图", "照片", "艺术", "设计"
        ]
        
        found_tags = [tag for tag in common_tags if tag in text]
        return found_tags[:5]
    
    def _extract_text(self, text: str) -> str:
        """提取 OCR 文字"""
        # 简单实现，实际应该解析更复杂
        if "文字" in text or "内容" in text:
            lines = text.split('\n')
            # 返回可能包含文字的部分
            return '\n'.join(lines[:5])
        return ""


class FileUnderstanding:
    """
    文件理解综合接口
    
    统一处理各种文件的理解和分析
    """
    
    def __init__(self, llm_func=None):
        self.llm = llm_func
        self.file_processor = FileProcessor(llm_func)
        self.web_extractor = WebContentExtractor()
        self.image_analyzer = ImageAnalyzer(llm_func)
    
    def process(self, source: str) -> str:
        """
        处理各种来源的内容
        
        Args:
            source: 文件路径或 URL
        
        Returns:
            处理/分析结果
        """
        if source.startswith('http://') or source.startswith('https://'):
            return self._process_url(source)
        elif os.path.isfile(source):
            return self._process_local_file(source)
        else:
            return f"无法处理：{source}"
    
    def _process_url(self, url: str) -> str:
        """处理 URL"""
        content = self.web_extractor.extract(url)
        
        if self.llm:
            summary = self.llm(f"请总结以下网页内容：\n\n{content.content[:3000]}")
            return f"【网页摘要】\n\n{summary}"
        
        return f"【网页内容】\n\n{content.content[:1000]}..."
    
    def _process_local_file(self, filepath: str) -> str:
        """处理本地文件"""
        content = self.file_processor.process_file(filepath)
        
        if content.file_type == "image":
            # 图片需要特殊处理
            analysis = self.image_analyzer.analyze(filepath)
            return f"""【图片分析】

描述：{analysis.description}

发现的文字：{analysis.text_found or '无'}

详细分析：
{analysis.analysis}

标签：{', '.join(analysis.tags) or '无'}"""
        
        elif content.file_type == "unknown":
            return content.content
        
        elif self.llm and len(content.content) > 100:
            summary = self.llm(f"请总结以下文档内容：\n\n{content.content[:5000]}")
            return f"""【文档摘要】

文件名：{content.filename}
文件类型：{content.file_type}
大小：{content.size} 字符

摘要：
{summary}"""
        
        return f"""【文档内容】

文件名：{content.filename}
类型：{content.file_type}

{content.content[:1000]}"""


def demo():
    """演示"""
    print("=" * 50)
    print("PersonalMind 文件理解演示")
    print("=" * 50)
    
    # 模拟 LLM
    def mock_llm(prompt: str) -> str:
        return f"【LLM 总结】：这是对内容的总结分析。\n\n原始内容前100字：{prompt[30:130]}..."
    
    # 创建文件理解器
    understanding = FileUnderstanding(mock_llm)
    
    print("\n支持的格式：")
    print("  📄 文本文件: .txt, .md")
    print("  📑 PDF文档: .pdf")
    print("  📝 Word文档: .doc, .docx")
    print("  🖼️ 图片: .jpg, .png, .gif, .webp")
    print("  🌐 网页: http://..., https://...")
    
    print("\n使用示例：")
    print("""
# 处理本地文件
result = understanding.process("path/to/file.pdf")

# 处理网页
result = understanding.process("https://example.com/article")

# 处理图片
result = understanding.process("path/to/image.png")
""")


if __name__ == "__main__":
    demo()
