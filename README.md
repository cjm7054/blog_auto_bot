# 24시간 돈 버는 블로그 수익 자동화 프로그램

이 프로젝트는 카카오 PlayMCP 도구 모음(IT 뉴스, 기술 블로그, 세미나 일정)과 AI(OpenAI GPT-4o)를 결합하여 **검색 엔진 최적화(SEO) 및 애드센스 수익에 유리한 양질의 포스팅을 자동으로 생성**하고, 이를 워드프레스(WordPress)에 자동으로 업로드하는 파이프라인입니다.

## 기능 (Features)
1. **데이터 수집 (`data_fetcher.py`)**: `mcporter`를 활용해 PlayMCP-gateway로부터 최신 트렌드를 수집합니다.
2. **콘텐츠 생성 (`content_generator.py`)**: 수집된 뉴스나 블로그 제목 및 링크를 바탕으로 OpenAI API를 호출하여 블로그 포스팅 형태의 HTML 본문을 생성합니다. (제휴 링크 등 포함 가능)
3. **워드프레스 포스팅 (`wordpress_publisher.py`)**: 생성된 콘텐츠를 WordPress REST API를 통해 블로그에 게시합니다. (기본적으로 `draft` 상태로 임시저장됩니다.)
4. **자동화 스케줄링 (`main.py`)**: 24시간 백그라운드로 돌아가면서 설정된 시간(예: 아침 8시, 저녁 6시)에 위 과정을 반복합니다.

---

## 사전 준비 (Prerequisites)

1. **Python 3.8 이상**이 설치되어 있어야 합니다.
2. **PlayMCP 연동 완료**: `mcporter` CLI가 전역으로 설치되어 있으며 `mcp-gateway` 서버가 설정되어 있어야 합니다. (현재 환경에 이미 구성되어 있습니다.)
3. **OpenAI API Key**: 글 작성을 위해 필요합니다. ([OpenAI Platform](https://platform.openai.com)에서 발급 가능)
4. **WordPress 설정**:
   - 워드프레스 관리자 계정에서 **어플리케이션 비밀번호(Application Passwords)**를 생성해야 합니다.
   - 워드프레스 사용자 메뉴 (Users > Profile) 페이지 하단에서 생성할 수 있습니다. (플러그인 없이 워드프레스 5.6 이상에서 기본 지원)

---

## 설치 및 설정 (Setup)

1. **의존성 패키지 설치**:
   이 폴더에서 아래 명령어를 실행합니다.
   ```bash
   pip install -r requirements.txt
   ```

2. **환경변수 설정 (`.env`)**:
   `.env.example` 파일을 복사하여 `.env` 파일을 만들고 설정값을 입력하세요.
   ```bash
   cp .env.example .env
   ```
   
   **.env 파일 내용 예시**:
   ```env
   # 워드프레스 설정
   WP_BASE_URL="https://내워드프레스주소.com"
   WP_USERNAME="관리자_아이디"
   WP_APP_PASSWORD="발급받은_어플리케이션_비밀번호_xxxx_xxxx"

   # AI 설정
   OPENAI_API_KEY="sk-..."

   # 제휴 마케팅 링크 추가를 위한 설정 (선택사항)
   COUPANG_AFFILIATE_ID=""
   ```

---

## 실행 (How to Run)

테스트 목적으로 1회 실행해보시려면 `main.py` 파일 내의 `job()` 함수를 직접 호출하도록 주석을 해제한 뒤 실행하세요.

```bash
python main.py
```

스크립트가 정상적으로 동작하면 다음과 같은 순서로 로그가 출력됩니다:
1. `mcporter`를 통해 데이터 수집
2. OpenAI API를 통해 내용 작성
3. 워드프레스에 임시저장(Draft)으로 업로드 완료 및 글 URL 반환

### 24시간 자동화 배포
현재 PC를 계속 켜두거나, AWS EC2, Raspberry Pi 등의 리눅스 서버에 이 코드를 올린 후 `nohup` 이나 `tmux`, `systemd` 서비스로 등록해두면 완벽한 24시간 자동화가 완성됩니다.
```bash
nohup python main.py &
```
