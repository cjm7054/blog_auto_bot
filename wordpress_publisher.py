import os
import requests
import logging
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WordPressPublisher:
    """
    Handles uploading posts to a WordPress site using its REST API.
    """
    def __init__(self):
        self.wp_url = os.getenv("WP_BASE_URL", "").rstrip('/')
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_password = os.getenv("WP_APP_PASSWORD")

    def publish_post(self, title: str, content: str, status: str = "draft") -> str:
        """
        Publishes a post to WordPress via REST API.
        status can be "draft" or "publish".
        Returns the URL of the created post or an error message.
        """
        if not self.wp_url or not self.wp_username or not self.wp_password:
            logger.warning("WordPress credentials not fully configured in .env. Skipping upload.")
            return "Failed: WordPress credentials missing"

        endpoint = f"{self.wp_url}/wp-json/wp/v2/posts"
        
        # Affiliate Marketing Integration (Optional)
        # affiliate_id = os.getenv("COUPANG_AFFILIATE_ID")
        # if affiliate_id:
        #     pass  # Add dynamic banner logic here if needed later

        payload = {
            "title": title,
            "content": content,
            "status": status
        }

        try:
            logger.info(f"Uploading post '{title}' to WordPress (status: {status})...")
            response = requests.post(
                endpoint,
                json=payload,
                auth=HTTPBasicAuth(self.wp_username, self.wp_password)
            )

            if response.status_code in [200, 201]:
                post_url = response.json().get("link")
                logger.info(f"Post successfully created! URL: {post_url}")
                return post_url
            else:
                logger.error(f"Failed to create post. Status Code: {response.status_code}, Response: {response.text}")
                return f"Failed: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error communicating with WordPress: {e}")
            return f"Error: {str(e)}"

if __name__ == "__main__":
    publisher = WordPressPublisher()
    print(publisher.publish_post("Test Post", "<p>Hello World</p>"))
