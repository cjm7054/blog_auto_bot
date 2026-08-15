import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    Uses LLM (Google Gemini) to generate SEO-optimized HTML blog posts.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in .env. Content generation will fail if called.")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_blog_post(self, topic: str, data: list) -> dict:
        """
        Generates an SEO-optimized HTML blog post based on fetched data.
        Returns a dict containing 'title' and 'content' (HTML).
        """
        if not self.client:
            return {"title": "API Error", "content": "<p>Please configure GEMINI_API_KEY in .env</p>"}

        if not data:
            return {"title": "No Data", "content": "<p>No data found to generate a post.</p>"}

        # Format data to pass to the prompt
        formatted_data = ""
        for i, item in enumerate(data[:5]):  # Use top 5 items for context to save tokens
            title = item.get('title', 'No Title')
            url = item.get('url', '#')
            date = item.get('date', 'Unknown')
            formatted_data += f"{i+1}. [{date}] {title} - {url}\n"

        system_prompt = (
            "당신은 구글 애드센스 승인 및 SEO(검색엔진최적화) 최고 전문가이자 전문 블로거입니다. "
            "주어진 데이터를 바탕으로 구글 애드센스 승인 규정 및 고수익화에 완벽히 부합하는 블로그 포스팅을 작성하세요.\n\n"
            "[애드센스 승인 및 SEO 필수 작성 규칙]\n"
            "1. **형식**: 결과는 반드시 JSON 형식으로 반환하세요. 구조: {\"title\": \"매력적이고 검색어(키워드)가 포함된 제목\", \"content\": \"HTML 본문\"}\n"
            "2. **글자 수 (Thin Content 방지)**: 본문 내용은 반드시 한국어 기준 '공백 제외 1,500자 이상'의 충분하고 정보성 있는 긴 글로 작성하세요. 내용이 짧으면 애드센스 승인이 거절됩니다.\n"
            "3. **구조화된 HTML (SEO 최적화)**: <html>, <body> 태그는 제외하고 내부 태그만 사용하세요. 글의 뼈대는 반드시 <h2>(대주제)와 <h3>(소주제)를 사용하여 논리적으로 나누세요. (<h1>은 사용 금지)\n"
            "4. **가독성 및 체류시간 증가**: <p> 태그 하나당 2~3문장 이내로 짧게 끊어 쓰고, 문단 사이에 적절히 여백을 두어 모바일 가독성을 높이고 중간 광고(본문 내 광고) 삽입이 쉽도록 만드세요. 중요한 키워드는 <strong> 태그로 강조하세요.\n"
            "5. **독창성 및 정보성 (가치 창출)**: 주어진 단순 뉴스 데이터를 그대로 나열하지 말고, 독자에게 인사이트를 제공하는 '서론(문제제기/흥미유발) - 본론(상세 분석 및 정보 전달) - 결론(요약 및 전망)'의 탄탄한 구조로 살을 붙여서 작성하세요. 어색한 번역투나 AI 특유의 기계적인 말투를 버리고 사람이 직접 쓴 것처럼 자연스러운 전문용어와 문체를 사용하세요.\n"
            "6. **출처 연동**: 제공된 데이터의 원본 링크(URL)는 글의 맥락에 자연스럽게 녹여내어 '<a href=\"URL\" target=\"_blank\">자세히 보기</a>' 등의 형태로 출처를 남기세요."
        )

        user_prompt = f"주제: {topic}\n\n[수집된 최신 정보]\n{formatted_data}\n\n위 정보를 바탕으로 독자에게 유용하고 흥미로운 블로그 글을 작성해 주세요."

        try:
            logger.info(f"Generating content for topic: {topic}")
            
            # Simple retry logic for 503 errors
            max_retries = 3
            import time
            
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            response_mime_type="application/json",
                            temperature=0.7
                        )
                    )
                    result_json = response.text
                    return json.loads(result_json)
                except Exception as e:
                    if "503" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Google Server 503 overload. Retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(5)
                    else:
                        raise e
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            return {"title": "Error Generating Content", "content": f"<p>Error: {str(e)}</p>"}

if __name__ == "__main__":
    generator = ContentGenerator()
    sample_data = [{"title": "Test News", "url": "http://example.com", "date": "2026-08-15"}]
    print(generator.generate_blog_post("AI 테스트", sample_data))
