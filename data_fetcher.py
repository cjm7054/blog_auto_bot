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
        Runs the mcporter command and attempts to parse the JSON array from the output.
        Command format: mcporter call mcp-gateway.ToolName query="value"
        """
        # Note: Depending on OS, 'mcporter' or 'mcporter.cmd' might be needed.
        cmd = ["mcporter", "call", f"{self.gateway_name}.{tool_name}", "query", query, "--timeout", "120000"]
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            # shell=True might be required on Windows to find global npm packages
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True, encoding='utf-8')
            output = result.stdout
            
            # Find JSON object or array in the output string
            start_idx_obj = output.find('{')
            end_idx_obj = output.rfind('}')
            
            start_idx_arr = output.find('[')
            end_idx_arr = output.rfind(']')
            
            if start_idx_obj != -1 and end_idx_obj != -1 and (start_idx_arr == -1 or start_idx_obj < start_idx_arr):
                json_str = output[start_idx_obj:end_idx_obj+1]
                data = json.loads(json_str)
                # If it's a Naver Search response, extract items
                if isinstance(data, dict) and "items" in data:
                    items = data["items"]
                    # Format Naver items to match our expected format
                    formatted_items = []
                    for item in items:
                        formatted_items.append({
                            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                            "url": item.get("link", ""),
                            "date": item.get("pubDate", "")
                        })
                    logger.info(f"Successfully fetched {len(formatted_items)} items from {tool_name}")
                    return formatted_items
                logger.info(f"Successfully fetched object from {tool_name}")
                return [data]
            elif start_idx_arr != -1 and end_idx_arr != -1:
                json_str = output[start_idx_arr:end_idx_arr+1]
                data = json.loads(json_str)
                logger.info(f"Successfully fetched {len(data)} items from {tool_name}")
                return data
            else:
                # If output is not an array, maybe it's a single object or plain text
                logger.warning(f"Failed to find JSON array in output: {output}")
                return []
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error calling mcporter. Exit code: {e.returncode}")
            logger.error(f"Stderr: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
