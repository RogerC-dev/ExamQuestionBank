import os
import logging
from django.conf import settings
from typing import Optional, Dict, List, Any
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

class AIService:
    """AI 服務類，處理與 OpenAI API 的互動"""

    def __init__(self):
        # 從環境變數或設定檔取得 API key
        self.api_key = os.getenv('OPENAI_API_KEY', getattr(settings, 'OPENAI_API_KEY', None))
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """取得系統提示詞"""
        return """你是一位專業的台灣法律學習助手，專門協助法律系學生準備司法官和律師考試。

你的職責包括：
1. 回答法律相關問題，並引用相關法條
2. 解釋考試題目的答案和解析
3. 分析法律案例，提取關鍵點
4. 推薦相關的練習題目

請用繁體中文回答，回答要準確、清晰，並適時引用相關法條。"""

    def is_configured(self) -> bool:
        """檢查是否已設定 API Key"""
        return self.client is not None

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        發送訊息給 AI 並取得回應

        Args:
            message: 使用者訊息
            context: 上下文資訊（如題目ID、案例內容等）

        Returns:
            AI 回應文字
        """
        if not self.is_configured():
            logger.warning("OpenAI API key not configured")
            return "AI 服務尚未設定，請聯繫管理員設定 OpenAI API Key。"

        try:
            # 建立訊息列表
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            # 如果有上下文，加入上下文資訊
            if context:
                context_message = self._build_context_message(context)
                if context_message:
                    messages.append({"role": "system", "content": context_message})

            # 加入使用者訊息
            messages.append({"role": "user", "content": message})

            # 呼叫 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "AI 服務暫時無法使用，請稍後再試。"
        except Exception as e:
            logger.error(f"Unexpected error in AI chat: {str(e)}")
            return "發生未預期的錯誤，請聯繫管理員。"

    def _build_context_message(self, context: Dict[str, Any]) -> Optional[str]:
        """
        建立上下文訊息

        Args:
            context: 上下文字典
        """
        parts = []

        if context.get('question_id'):
            parts.append(f"當前討論的題目ID：{context['question_id']}")

        if context.get('question_content'):
            parts.append(f"題目內容：{context['question_content']}")

        if context.get('case_text'):
            parts.append(f"案例內容：{context['case_text']}")

        if context.get('related_laws'):
            laws = ", ".join(context['related_laws'])
            parts.append(f"相關法條：{laws}")

        if parts:
            return "\n".join(parts)
        return None

    def analyze_case(self, case_text: str) -> Dict[str, Any]:
        """
        分析法律案例

        Args:
            case_text: 案例文字

        Returns:
            包含分析結果的字典
        """
        default_response = {
            "summary": "無法進行分析",
            "key_points": [],
            "related_laws": []
        }

        if not self.is_configured():
            return {**default_response, "summary": "AI 服務尚未設定"}

        try:
            prompt = f"""請分析以下法律案例，並提供：
1. 案例摘要（100字以內）
2. 關鍵爭點（3-5個）
3. 相關法條（列出主要適用的法條）

案例內容：
{case_text}
"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )

            analysis_text = response.choices[0].message.content.strip()

            return {
                "summary": analysis_text,
                "key_points": self._extract_key_points(analysis_text),
                "related_laws": self._extract_laws(analysis_text)
            }

        except Exception as e:
            logger.error(f"Error analyzing case: {str(e)}")
            return {**default_response, "summary": f"分析時發生錯誤：{str(e)}"}

    def _extract_key_points(self, text: str) -> List[str]:
        """從分析文字中提取關鍵點"""
        lines = text.split('\n')
        key_points = []
        for line in lines:
            line = line.strip()
            # 支援多種列表格式
            if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                # 移除標號
                content = line.lstrip('0123456789.-*• ')
                if content:
                    key_points.append(content)
        return key_points[:5]

    def _extract_laws(self, text: str) -> List[str]:
        """從分析文字中提取法條"""
        import re
        # 改進的正則表達式，匹配更多法條格式
        pattern = r'(?:第\s*\d+\s*[條項款]|[\u4e00-\u9fa5]+法\s*第\s*\d+\s*條)'
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]


# 建立單例
ai_service = AIService()

