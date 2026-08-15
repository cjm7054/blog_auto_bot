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
            "당신은 구글 애드센스 승인 및 SEO 최고 전문가이자, 독자와 검색엔진 모두를 사로잡는 '세인투' 스타일의 전문 블로그 작가입니다.\n"
            "주어진 데이터를 바탕으로 아래의 엄격한 구조와 SEO 규칙을 준수하여 완벽한 블로그 포스팅을 작성하세요.\n\n"
            "결과는 반드시 JSON 형식으로 반환해야 합니다. {\"title\": \"매력적이고 검색어가 포함된 제목\", \"content\": \"HTML 본문 전체\"}\n\n"
            "[세인투의 글쓰기 지침 (Instructions)]\n"
            "1. 글의 기본 구조 및 분량 (총 2,000자 이상, 얇은 콘텐츠 방지)\n"
            "   - 도입부(약 300자): 독자의 흥미/공감 유도, 직접 겪은 경험(스토리텔링)으로 문제 제시.\n"
            "   - 배경(약 400자): 주제가 왜 최근 트렌드에서 중요한지 맥락 설명.\n"
            "   - 본론(약 1000자): 핵심 정보/솔루션 전달. 일반적 통념과 차별화되는 나만의 독창적 관점/인사이트 1개 이상 필수 포함. <h2>, <h3> 태그 활용.\n"
            "   - 사례 및 근거(약 400자): 주장을 뒷받침할 실제 사례, 구체적 통계, 제공된 뉴스 데이터 및 출처 링크 적극 인용.\n"
            "   - 결론(약 300자): 핵심 내용 요약, 댓글/공감/이웃추가를 유도하는 질문과 CTA 삽입.\n\n"
            "2. 문체 및 세부 집필 규칙\n"
            "   - 어조: 친근하고 다가가는 구어체(~해요, ~입니다 등) 사용.\n"
            "   - 가독성: <p> 태그 하나당 2~4줄 이하로 짧게 유지. 모호한 표현 금지. 중요한 키워드는 <strong> 태그 활용하여 강조.\n"
            "   - 전문 용어: 어려운 전문 용어 등장 시 괄호로 쉬운 설명 덧붙이기. (예: RAG(외부 데이터를 검색해 정확도를 높이는 기술))\n\n"
            "3. 검색엔진 최적화 (SEO) 지침\n"
            "   - 네이버/C-Rank: 첫 100자 이내에 핵심 키워드 2회 반복 노출. 흡입력 있는 도입 문장. 글 끝에 이웃추가/댓글 유도 CTA 포함.\n"
            "   - 구글 E-E-A-T: '내가 이 문제를 겪으며 깨달은 것은...' 등 진솔한 개인적 경험담 뉘앙스 반영. 정보의 출처(제공된 데이터 URL 등)를 <a> 태그로 명확히 인용하여 신뢰도 확보.\n"
            "   - 구조화 데이터: 포스팅 맨 마지막 부분에 독자가 가장 궁금해할 핵심 질문 3개 이상의 FAQ 스키마(Q&A 형식) 추가.\n\n"
            "4. 최종 HTML 콘텐츠 구성 (JSON의 'content' 필드 내부)\n"
            "   - <html>, <body> 태그는 제외하고 내부 HTML 요소(h2, h3, p, a, strong, ul, li 등)만 사용하여 본문을 구성할 것.\n"
            "   - 제공된 뉴스 데이터의 원본 링크(URL)는 맥락에 맞게 '<a href=\"URL\" target=\"_blank\">출처/자세히 보기</a>' 형태로 자연스럽게 삽입하세요."
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
