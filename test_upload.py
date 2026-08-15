import logging
from wordpress_publisher import WordPressPublisher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_mock_post():
    publisher = WordPressPublisher()
    
    title = "[IT 트렌드] 구글 제미나이 3.7 플래시 공개 및 AI 업무 자동화 동향"
    content = """
<h2>AI 기술 트렌드 및 최신 동향 요약</h2>
<p>최근 AI 모델들의 발전과 함께 업무 자동화 시장이 빠르게 성장하고 있습니다. 오늘은 주목할 만한 주요 최신 IT 뉴스들을 정리해 보았습니다.</p>

<h3>1. 구글, 제미나이 3.7 플래시 공개</h3>
<p>구글이 개발자 피드백과 추론 알고리즘 개선을 거친 최신 경량 AI인 '제미나이 3.7 플래시(Gemini 3.7 Flash)'를 공개했습니다. 눈에 띄는 점은 이전 모델 대비 API 가격을 절반으로 낮췄다는 것입니다. 이로써 기업들의 초거대 AI 도입 장벽이 한층 낮아질 전망입니다.</p>
<p><a href="https://www.seoulfn.com/news/articleView.html?idxno=635722" target="_blank">관련 기사 자세히 보기</a></p>

<h3>2. 큐원(Qwen) 3.6 27B 오픈소스 모델 발표</h3>
<p>큐원(Qwen) 팀이 27B(270억 개) 파라미터 규모의 멀티모달 모델인 '큐원 3.6-27B'를 공개했습니다. 이 모델은 코딩과 업무 자동화에 특화되어 있으며, 누구나 상업적으로 활용할 수 있습니다.</p>

<h3>3. 앤트로픽 AI 에이전트의 충돌 이슈와 보안</h3>
<p>다중 에이전트 환경에서 앤트로픽의 AI 에이전트들이 같은 저장소에 접근할 때 서로 방해하는 현상이 보고되었습니다. 보안 업체 루브릭 등은 이를 대비해 자동화 범위와 사람 개입 지점을 새로 개편하며 대응하고 있습니다. 에이전트에게 많은 권한이 주어질수록 충돌 및 보안 관리가 핵심 과제가 될 것으로 보입니다.</p>

<h3>결론: AI를 활용한 업무 자동화의 가속화</h3>
<p>새로운 모델들이 저렴한 비용과 높은 성능으로 끊임없이 등장하면서, AI 기술은 단순한 질문/답변을 넘어 실제 <b>업무 혁신(AX) 및 블로그 자동화</b>와 같은 새로운 수익 모델로 이어지고 있습니다.</p>
    """
    
    result = publisher.publish_post(title, content, status="publish")
    print(f"Upload result: {result}")

if __name__ == "__main__":
    upload_mock_post()
