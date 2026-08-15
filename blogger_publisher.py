import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/blogger']

class BloggerPublisher:
    """
    Handles uploading posts to a Google Blogger (Blogspot) site.
    """
    def __init__(self):
        self.blog_id = os.getenv("BLOGGER_BLOG_ID")
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        if not self.blog_id:
            logger.warning("BLOGGER_BLOG_ID not found in .env. Blogger upload will be skipped.")
            return

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}. Re-authenticating...")
                    self.creds = None

            if not self.creds:
                if not os.path.exists('client_secret.json'):
                    logger.error("client_secret.json not found! You must download OAuth 2.0 client credentials from Google Cloud Console.")
                    return
                
                logger.info("Starting browser authentication flow for Blogger...")
                # Run local server to catch the callback
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.service = build('blogger', 'v3', credentials=self.creds)
        except Exception as e:
            logger.error(f"Failed to build Blogger service: {e}")

    def publish_post(self, title: str, content: str, is_draft: bool = True) -> str:
        """
        Publishes a post to Blogger.
        Returns the URL of the created post or an error message.
        """
        if not self.service or not self.blog_id:
            return "Failed: Blogger not configured or not authenticated."

        # Note: Blogger V3 API requires content to be valid HTML.
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content
        }

        try:
            logger.info(f"Uploading post '{title}' to Blogger (draft: {is_draft})...")
            # isDraft=True sets the post as a draft instead of publishing it immediately
            posts = self.service.posts()
            request = posts.insert(blogId=self.blog_id, body=body, isDraft=is_draft)
            response = request.execute()

            post_url = response.get("url")
            # Drafts don't always return a public URL, they return a selfLink
            if not post_url:
                post_url = f"Draft created (ID: {response.get('id')})"

            logger.info(f"Blogger Post successfully created! URL/ID: {post_url}")
            return post_url

        except Exception as e:
            logger.error(f"Error communicating with Blogger API: {e}")
            return f"Error: {str(e)}"
