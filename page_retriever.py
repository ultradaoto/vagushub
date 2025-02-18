import os
import re
import time
import random
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
import html
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('page_retrieval.log'),
        logging.StreamHandler()
    ]
)

class ClickFunnelsRetriever:
    def __init__(self):
        self.archive_dir = Path('views/blog/archive')
        self.output_dir = self.archive_dir / 'retrieved'
        self.screenshots_dir = self.output_dir / 'screenshots'
        self.html_dir = self.output_dir / 'html'
        self.images_dir = self.output_dir / 'images'
        
        # Create necessary directories
        for dir in [self.output_dir, self.screenshots_dir, self.html_dir, self.images_dir]:
            dir.mkdir(exist_ok=True, parents=True)
            
        # Track downloaded images to avoid duplicates
        self.downloaded_images = set()
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--window-size=1200,800')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

    def get_page_name(self, url):
        """Extract a clean page name from URL."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        return path if path else 'home'

    def get_image_filename(self, url):
        """Extract original filename from URL."""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        return path.split('/')[-1]

    def download_image(self, url):
        """Download image if not already downloaded."""
        try:
            # Get original filename
            filename = self.get_image_filename(url)
            
            # Skip if already downloaded
            if filename in self.downloaded_images:
                logging.info(f"Skipping already downloaded image: {filename}")
                return filename
            
            # Download image
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                image_path = self.images_dir / filename
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.downloaded_images.add(filename)
                logging.info(f"Downloaded image: {filename}")
                return filename
                
        except Exception as e:
            logging.error(f"Error downloading image {url}: {e}")
            return None

    def setup_driver(self):
        """Create and configure a stealth driver."""
        driver = webdriver.Chrome(options=self.chrome_options)
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

    def take_full_page_screenshot(self, driver, url, output_path):
        """Take a full page screenshot."""
        try:
            # Set initial window size
            driver.set_window_size(1200, 800)
            
            # Wait for content to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page height and resize window
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1200, total_height + 100)
            
            # Scroll to ensure all content loads
            driver.execute_script("""
                window.scrollTo(0, 0);
                let totalHeight = 0;
                let distance = 200;
                let timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= document.body.scrollHeight){
                        clearInterval(timer);
                        window.scrollTo(0, 0);
                    }
                }, 100);
            """)
            
            time.sleep(3)  # Wait for scrolling to complete
            driver.save_screenshot(str(output_path))
            logging.info(f"Screenshot saved to {output_path}")
            
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")

    def clean_html_content(self, soup, page_name):
        """Extract and clean just the main content."""
        # Remove scripts, styles, and hidden elements
        for element in soup.find_all(['script', 'style']):
            element.decompose()
            
        # Find main content container
        content = soup.find('div', class_='containerWrapper') or soup.find('main') or soup.body
        
        if not content:
            return None
            
        # Download images and update their paths
        for img in content.find_all('img', src=True):
            src = img.get('src', '')
            if src.startswith('http'):
                filename = self.download_image(src)
                if filename:
                    # Update image src to local path
                    img['src'] = f'../images/{filename}'
            
        # Create clean HTML structure
        clean_html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>" + (soup.title.string if soup.title else "Page Content") + "</title>",
            "</head>",
            "<body>"
        ]
        
        # Add main content
        clean_html.append(str(content))
        clean_html.extend(["</body>", "</html>"])
        
        return "\n".join(clean_html)

    def extract_text_content(self, soup):
        """Extract meaningful text content."""
        text_content = []
        
        # Get headings
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = tag.get_text().strip()
            if text:
                text_content.append(f"\n### {text} ###\n")
        
        # Get paragraphs and list items
        for tag in soup.find_all(['p', 'li']):
            text = tag.get_text().strip()
            if text:
                text_content.append(text)
        
        # Update image entries to include local path
        for img in soup.find_all('img', src=True):
            src = img.get('src', '')
            alt = img.get('alt', '')
            filename = self.get_image_filename(src) if src.startswith('http') else src
            if filename:
                text_content.append(f"Picture: {filename} (Alt: {alt})")
        
        # Get links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip()
            if href and text:
                text_content.append(f"Link: {href} (Text: {text})")
        
        return text_content

    def aggressively_clean_html(self, soup, page_name):
        """Create an extremely clean version of the HTML with only essential content."""
        try:
            # Remove all scripts, styles, meta tags, and other non-content elements
            for element in soup.find_all(['script', 'style', 'meta', 'link', 'noscript', 'iframe']):
                element.decompose()

            # Remove all hidden elements
            for element in soup.find_all(style=lambda x: x and ('display:none' in x.replace(' ', '') or 'visibility:hidden' in x.replace(' ', ''))):
                element.decompose()
            
            for element in soup.find_all(class_=lambda x: x and any(hidden in x.lower() for hidden in ['hide', 'hidden', 'invisible'])):
                element.decompose()

            # Remove empty containers
            for element in soup.find_all(['div', 'span', 'p']):
                if not element.get_text(strip=True) and not element.find_all(['img', 'video', 'iframe']):
                    element.decompose()

            # Find the main content area
            main_content = None
            possible_content_areas = [
                soup.find('div', class_='containerWrapper'),
                soup.find('main'),
                soup.find('article'),
                soup.find('div', class_=lambda x: x and 'content' in x.lower()),
                soup.find('div', id=lambda x: x and 'content' in x.lower())
            ]
            
            for area in possible_content_areas:
                if area and area.get_text(strip=True):
                    main_content = area
                    break

            if not main_content:
                main_content = soup.body

            # Remove all class names and IDs except for essential ones
            for tag in main_content.find_all(True):
                essential_classes = ['container', 'content', 'header', 'footer', 'nav']
                classes = tag.get('class', [])
                if classes:
                    # Keep only essential classes
                    tag['class'] = [c for c in classes if any(ess in c.lower() for ess in essential_classes)]
                    if not tag['class']:
                        del tag['class']
                
                # Remove all data attributes
                for attr in list(tag.attrs):
                    if attr.startswith('data-') or attr in ['id', 'onclick', 'onload']:
                        del tag[attr]

            # Process images
            for img in main_content.find_all('img', src=True):
                src = img.get('src', '')
                if src.startswith('http'):
                    filename = self.download_image(src)
                    if filename:
                        img['src'] = f'../images/{filename}'
                # Keep only essential image attributes
                allowed_attrs = ['src', 'alt', 'title']
                for attr in list(img.attrs):
                    if attr not in allowed_attrs:
                        del img[attr]

            # Create minimal HTML structure
            clean_html = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<meta charset='utf-8'>",
                "<title>" + (soup.title.string if soup.title else "Page Content") + "</title>",
                "<style>",
                "body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }",
                "img { max-width: 100%; height: auto; }",
                "a { color: #0066cc; text-decoration: none; }",
                "a:hover { text-decoration: underline; }",
                "</style>",
                "</head>",
                "<body>"
            ]

            # Add only the essential content
            clean_html.append(str(main_content))
            clean_html.extend(["</body>", "</html>"])

            return "\n".join(clean_html)

        except Exception as e:
            logging.error(f"Error in aggressive cleaning: {e}")
            return None

    def process_url(self, url):
        """Process a single URL."""
        try:
            url = url.strip()
            if not url:
                return
                
            logging.info(f"Processing URL: {url}")
            page_name = self.get_page_name(url)
            
            driver = self.setup_driver()
            try:
                driver.get(url)
                
                # Take screenshot
                screenshot_path = self.screenshots_dir / f"{page_name}_screenshot.png"
                self.take_full_page_screenshot(driver, url, screenshot_path)
                
                # Get rendered HTML
                rendered_html = driver.page_source
                soup = BeautifulSoup(rendered_html, 'html.parser')
                
                # Save full rendered HTML
                html_path = self.html_dir / f"{page_name}_rendered.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                # Save regular cleaned HTML
                clean_html = self.clean_html_content(soup, page_name)
                if clean_html:
                    clean_path = self.html_dir / f"{page_name}_clean.html"
                    with open(clean_path, 'w', encoding='utf-8') as f:
                        f.write(clean_html)
                
                # Save aggressively cleaned HTML
                super_clean_html = self.aggressively_clean_html(soup, page_name)
                if super_clean_html:
                    super_clean_path = self.html_dir / f"{page_name}_super_clean.html"
                    with open(super_clean_path, 'w', encoding='utf-8') as f:
                        f.write(super_clean_html)
                
                # Extract and save text content
                text_content = self.extract_text_content(soup)
                text_path = self.output_dir / f"{page_name}_cleaned.txt"
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(text_content))
                
                logging.info(f"Successfully processed {url}")
                
            finally:
                driver.quit()
                
        except Exception as e:
            logging.error(f"Error processing URL {url}: {e}")

    def run(self):
        """Process URLs from URL.txt file."""
        url_file = self.archive_dir / 'URL.txt'
        if not url_file.exists():
            logging.error(f"URL file not found: {url_file}")
            return
            
        with open(url_file, 'r') as f:
            urls = f.readlines()
            
        for url in urls:
            url = url.strip()
            if url:
                self.process_url(url)
                time.sleep(random.uniform(2, 4))  # Random delay between requests

def main():
    retriever = ClickFunnelsRetriever()
    retriever.run()

if __name__ == "__main__":
    main() 