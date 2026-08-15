import schedule
import time
import logging
from data_fetcher import DataFetcher
from content_generator import ContentGenerator
from wordpress_publisher import WordPressPublisher
from blogger_publisher import BloggerPublisher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("Starting automated blog posting job...")
    
    fetcher = DataFetcher()
    generator = ContentGenerator()
    wp_publisher = WordPressPublisher()
    blogger_publisher = BloggerPublisher()
    
    # 1. Fetch Data
    topic = "AI 및 IT 최신 기술 트렌드"
    logger.info(f"Step 1: Fetching data for topic: '{topic}'")
    news_items = fetcher._call_mcporter("NaverSearch-search_news", topic)
    
    if not news_items:
        logger.warning("No news items fetched. Aborting job.")
        return
        
    # 2. Generate Content
    logger.info("Step 2: Generating content via LLM")
    generated_content = generator.generate_blog_post(topic, news_items)
    
    if not generated_content:
        logger.error("Content generation failed. Aborting job.")
        return
        
    title = generated_content.get("title")
    html_content = generated_content.get("content")
    
    if not title or not html_content:
        logger.error("Generated content is missing title or html_content.")
        return
        
    # 3. Publish to WordPress
    logger.info("Step 3: Publishing to WordPress")
    wp_result = wp_publisher.publish_post(title=title, content=html_content, status="publish")
    logger.info(f"WordPress Job Result: {wp_result}")
    
    # 4. Publish to Blogger
    logger.info("Step 4: Publishing to Blogger")
    blogger_result = blogger_publisher.publish_post(title=title, content=html_content, is_draft=False)
    logger.info(f"Blogger Job Result: {blogger_result}")

import os

def main():
    logger.info("Blog Auto Bot Scheduler Started!")
    
    # Check if running in GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        logger.info("Running in GitHub Actions mode. Executing job once...")
        job()
        return

    logger.info("Configured to run daily at 08:00 and 18:00")
    
    # Schedule the jobs
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("18:00").do(job)
    
    # Uncomment the following line to run the job immediately for testing:
    # job()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped manually.")

if __name__ == "__main__":
    main()
