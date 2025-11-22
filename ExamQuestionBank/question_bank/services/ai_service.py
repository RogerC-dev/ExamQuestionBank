import os
import logging
import json
from django.conf import settings
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# Lazy import OpenAI to avoid breaking schema generation if package is not installed
_openai_available = None
_OpenAI = None
_OpenAIError = None

def _get_openai_client():
    """Lazy import OpenAI client"""
    global _openai_available, _OpenAI, _OpenAIError
    if _openai_available is None:
        try:
            from openai import OpenAI as _OpenAI, OpenAIError as _OpenAIError
            _openai_available = True
        except ImportError:
            logger.warning("OpenAI package not installed. AI features will be disabled.")
            _openai_available = False
            # Create dummy classes to avoid errors
            class DummyOpenAI:
                def __init__(self, *args, **kwargs):
                    pass
            class DummyError(Exception):
                pass
            _OpenAI = DummyOpenAI
            _OpenAIError = DummyError
    return _openai_available, _OpenAI, _OpenAIError

class AIService:
    """AI 服務類，處理與 OpenAI API 的互動"""

    def __init__(self):
        # 從環境變數或設定檔取得 API key
        self.api_key = os.getenv('OPENAI_API_KEY', getattr(settings, 'OPENAI_API_KEY', None))
        self.client = None
        openai_available, OpenAIClass, _ = _get_openai_client()
        if self.api_key and openai_available:
            try:
                self.client = OpenAIClass(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
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
            _, _, OpenAIError = _get_openai_client()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            _, _, OpenAIError = _get_openai_client()
            if OpenAIError and isinstance(e, OpenAIError):
                logger.error(f"OpenAI API error: {str(e)}")
                return "AI 服務暫時無法使用，請稍後再試。"
            else:
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

    def grade_essay(self, subject: str, question_text: str, answer_text: str, rag_context: Optional[str] = None) -> Dict[str, Any]:
        """
        批改申論題答案

        Args:
            subject: 科目名稱
            question_text: 題目內容
            answer_text: 學生答案
            rag_context: RAG 檢索的相關法條/判例上下文（可選）

        Returns:
            包含評分、評語、優缺點、建議的字典
        """
        default_response = {
            "score": 0.0,
            "max_score": 100.0,
            "feedback": "無法進行批改",
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }

        if not self.is_configured():
            return {**default_response, "feedback": "AI 服務尚未設定"}

        try:
            # 建立批改提示詞
            context_part = ""
            if rag_context:
                context_part = f"\n\n相關法條與判例參考：\n{rag_context}\n"

            prompt = f"""你是一位專業的台灣司法官/律師考試申論題批改老師。請批改以下申論題答案。

科目：{subject}
題目：{question_text}
{context_part}
學生答案：
{answer_text}

請提供以下格式的批改結果（JSON格式）：
{{
    "score": 分數（0-100的數字）,
    "max_score": 100,
    "feedback": "總體評語（200字以內）",
    "strengths": ["優點1", "優點2", "優點3"],
    "weaknesses": ["缺點1", "缺點2", "缺點3"],
    "suggestions": ["改進建議1", "改進建議2", "改進建議3"]
}}

批改標準：
1. 法律概念是否正確（30%）
2. 論述邏輯是否清晰（25%）
3. 法條引用是否適當（25%）
4. 文字表達是否流暢（20%）

請嚴格按照上述標準評分，並提供具體的優缺點和改進建議。只返回JSON格式，不要其他文字。"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # 降低溫度以獲得更一致的評分
                max_tokens=2000,
                response_format={"type": "json_object"} if self.model.startswith("gpt-4") else None
            )

            response_text = response.choices[0].message.content.strip()

            # 嘗試解析 JSON
            try:
                # 移除可能的 markdown 代碼塊標記
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                result = json.loads(response_text)
                return {
                    "score": float(result.get("score", 0)),
                    "max_score": float(result.get("max_score", 100.0)),
                    "feedback": result.get("feedback", ""),
                    "strengths": result.get("strengths", []),
                    "weaknesses": result.get("weaknesses", []),
                    "suggestions": result.get("suggestions", [])
                }
            except json.JSONDecodeError:
                # 如果 JSON 解析失敗，嘗試從文字中提取
                logger.warning("Failed to parse JSON response, extracting from text")
                return self._parse_grading_from_text(response_text)

        except Exception as e:
            logger.error(f"Error grading essay: {str(e)}")
            return {**default_response, "feedback": f"批改時發生錯誤：{str(e)}"}

    def _parse_grading_from_text(self, text: str) -> Dict[str, Any]:
        """從文字回應中解析評分結果（備用方法）"""
        import re
        result = {
            "score": 0.0,
            "max_score": 100.0,
            "feedback": text[:500],
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }

        # 嘗試提取分數
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*分', text)
        if score_match:
            result["score"] = float(score_match.group(1))

        return result

    def generate_mock_exam(self, subject: str, question_count: int = 20, difficulty: str = "medium", exam_year: Optional[int] = None, rag_context: Optional[str] = None) -> Dict[str, Any]:
        """
        生成模擬測驗題目

        Args:
            subject: 科目名稱
            question_count: 題目數量
            difficulty: 難度（easy/medium/hard）
            exam_year: 考試年度（可選）
            rag_context: RAG 檢索的相關內容（可選）

        Returns:
            包含題目列表的字典
        """
        default_response = {
            "questions": [],
            "subject": subject,
            "question_count": question_count
        }

        if not self.is_configured():
            return {**default_response, "error": "AI 服務尚未設定"}

        try:
            context_part = ""
            if rag_context:
                context_part = f"\n\n相關法條與內容參考：\n{rag_context}\n"

            year_part = f"（參考 {exam_year} 年考試風格）" if exam_year else ""

            prompt = f"""請生成 {question_count} 道{subject}的選擇題，難度為{difficulty}{year_part}。

{context_part}
每道題目需要包含：
1. 題目內容（清楚明確）
2. 4個選項（A、B、C、D）
3. 正確答案（標註哪個選項）
4. 解析（簡短說明為什麼是這個答案）

請以 JSON 格式返回，格式如下：
{{
    "questions": [
        {{
            "content": "題目內容",
            "options": [
                {{"label": "A", "text": "選項A內容"}},
                {{"label": "B", "text": "選項B內容"}},
                {{"label": "C", "text": "選項C內容"}},
                {{"label": "D", "text": "選項D內容"}}
            ],
            "correct_answer": "A",
            "explanation": "解析內容"
        }}
    ]
}}

只返回JSON格式，不要其他文字。"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,  # 稍高溫度以獲得更多樣化的題目
                max_tokens=4000,
                response_format={"type": "json_object"} if self.model.startswith("gpt-4") else None
            )

            response_text = response.choices[0].message.content.strip()

            # 解析 JSON
            try:
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                result = json.loads(response_text)
                questions = result.get("questions", [])

                # 確保返回的題目數量不超過請求的數量
                if len(questions) > question_count:
                    questions = questions[:question_count]

                return {
                    "questions": questions,
                    "subject": subject,
                    "question_count": len(questions),
                    "difficulty": difficulty
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse mock exam JSON: {e}")
                return {**default_response, "error": "生成題目格式錯誤"}

        except Exception as e:
            logger.error(f"Error generating mock exam: {str(e)}")
            return {**default_response, "error": f"生成題目時發生錯誤：{str(e)}"}

    def analyze_progress(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析使用者學習進度並生成建議

        Args:
            progress_data: 包含進度數據的字典，例如：
                {
                    "total_questions": 1000,
                    "practiced_questions": 500,
                    "accuracy": 75.5,
                    "subject_breakdown": {
                        "民法": {"practiced": 100, "accuracy": 80},
                        "刑法": {"practiced": 80, "accuracy": 70}
                    },
                    "weak_areas": ["刑法", "行政法"],
                    "recent_trend": "improving"
                }

        Returns:
            包含分析和建議的字典
        """
        default_response = {
            "summary": "無法進行分析",
            "recommendations": [],
            "focus_areas": []
        }

        if not self.is_configured():
            return {**default_response, "summary": "AI 服務尚未設定"}

        try:
            prompt = f"""請分析以下學習進度數據，並提供學習建議：

總題數：{progress_data.get('total_questions', 0)}
已練習：{progress_data.get('practiced_questions', 0)}
整體正確率：{progress_data.get('accuracy', 0)}%

科目分析：
{json.dumps(progress_data.get('subject_breakdown', {}), ensure_ascii=False, indent=2)}

弱項科目：{', '.join(progress_data.get('weak_areas', []))}
近期趨勢：{progress_data.get('recent_trend', 'unknown')}

請提供：
1. 簡短總結（100字以內）
2. 3-5個具體的學習建議
3. 需要重點加強的科目

請以 JSON 格式返回：
{{
    "summary": "學習進度總結",
    "recommendations": ["建議1", "建議2", "建議3"],
    "focus_areas": ["科目1", "科目2"]
}}

只返回JSON格式。"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"} if self.model.startswith("gpt-4") else None
            )

            response_text = response.choices[0].message.content.strip()

            try:
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                result = json.loads(response_text)
                return {
                    "summary": result.get("summary", ""),
                    "recommendations": result.get("recommendations", []),
                    "focus_areas": result.get("focus_areas", [])
                }
            except json.JSONDecodeError:
                return {
                    "summary": response_text[:500],
                    "recommendations": [],
                    "focus_areas": []
                }

        except Exception as e:
            logger.error(f"Error analyzing progress: {str(e)}")
            return {**default_response, "summary": f"分析時發生錯誤：{str(e)}"}

    def get_study_advice(self, user_context: Dict[str, Any]) -> str:
        """
        提供個人化學習建議

        Args:
            user_context: 使用者上下文，例如：
                {
                    "current_subject": "民法",
                    "recent_accuracy": 75,
                    "study_goals": "準備司法官考試",
                    "time_available": "每天2小時"
                }

        Returns:
            學習建議文字
        """
        if not self.is_configured():
            return "AI 服務尚未設定"

        try:
            prompt = f"""根據以下使用者情況，提供個人化的學習建議：

當前科目：{user_context.get('current_subject', '未知')}
最近正確率：{user_context.get('recent_accuracy', 0)}%
學習目標：{user_context.get('study_goals', '未設定')}
可用時間：{user_context.get('time_available', '未設定')}

請提供具體、可執行的學習建議（200-300字）。"""

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error getting study advice: {str(e)}")
            return "無法生成學習建議，請稍後再試。"


# 建立單例
ai_service = AIService()

