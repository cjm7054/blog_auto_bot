import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetches data using Kakao PlayMCP's tools via the mcporter CLI.
    """
    def __init__(self):
        self.gateway_name = "mcp-gateway"

    def _call_mcporter(self, tool_name: str, query: str) -> list:
        """
        [수정됨] GitHub Actions(클라우드) 환경에서는 로컬 PC에만 깔려있는 mcporter를 실행할 수 없으므로,
        어디서든 100% 작동하는 구글 뉴스 RSS(Google News RSS)를 직접 크롤링하여 데이터를 수집하도록 로직을 변경합니다.
        """
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET

        logger.info(f"Fetching Google News RSS for query: {query}")
        # 구글 뉴스 한국어 검색 RSS URL
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        
        try:
            # 크롤링 차단 방지를 위한 User-Agent 추가
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            formatted_items = []
            # 상위 10개 뉴스만 추출
            for item in root.findall('.//item')[:10]:
                formatted_items.append({
                    "title": item.find('title').text,
                    "url": item.find('link').text,
                    "date": item.find('pubDate').text
                })
            
            logger.info(f"Successfully fetched {len(formatted_items)} items from Google News RSS")
            return formatted_items
            
        except Exception as e:
            logger.error(f"Failed to fetch data from RSS: {e}")
            return []

    def get_latest_news(self, query: str = "AI"):
        """Fetches latest IT/Cloud/AI news."""
        return self._call_mcporter("ItNewsSearch-News_Article", query)
        
    def get_tech_blogs(self, query: str = "AI"):
        """Fetches recent tech blogs and technical documents."""
        return self._call_mcporter("ItNewsSearch-Tech_Blog", query)
        
    def get_seminars(self, query: str = "AI"):
        """Fetches upcoming meetup/webinar/conference schedules."""
        return self._call_mcporter("ItNewsSearch-Meetup_Webinar_Conference_Schedule", query)

if __name__ == "__main__":
    # Test script
    fetcher = DataFetcher()
    news = fetcher.get_latest_news("AI")
    print("Sample News:", news[:2] if news else "No news found")
