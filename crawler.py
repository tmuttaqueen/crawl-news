import concurrent.futures
import encodings
import logging
import queue
import threading
import os
from turtle import tilt
from typing import Dict, List
import requests
import logging
from bs4 import BeautifulSoup
from crawl_config import NEWSPAPER_CONFIG_SELECTOR
from urllib.parse import urljoin, urlparse
import json
# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def config_logger():
    
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('.' + os.sep + 'crawl' + os.sep + 'crawl.log')
    

    # Create formatters and add it to handlers
    c_format = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    f_format = logging.Formatter(fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(c_format)
    file_handler.setFormatter(f_format)
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    



class Database:
    def __init__(self,
            config, 
            save_dir : str, 
            queue_max_size : int = 1000, 
            resume : bool = False, 
            resume_dir: str = None,
            use_selenium: bool = False
        ) -> None:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.use_selenium = use_selenium
        self.config = config
        self.urls_to_crawl = queue.Queue(maxsize=queue_max_size)
        self.urls_seen = set()
        self.webpages_to_analyze = queue.Queue(maxsize=queue_max_size)
        self.save_json_lock = threading.Lock()
        self.file_name = save_dir  + os.sep + 'crawled_pages.json'
        self.counter = 1
        self.forbidden_sub_urls = config['forbidden_url']
        self.event = threading.Event()
        self.event.set()
        if resume:
            pass 
            # to be implemented
        else:
            self.urls_to_crawl.put(config['root_url'])
            self.urls_seen.add(config['root_url'])

    def get_url(self) -> str:
        return self.urls_to_crawl.get() 

    def put_url(self, 
            url : str
        ) -> None:
        self.urls_to_crawl.put(url) 

    def put_urls(self, 
            urls : List[str]
        ) -> None:
        for url in urls:
            self.urls_seen.add(url)
            self.urls_to_crawl.put(url) 

    def get_webpage(self) -> str:
        return self.webpages_to_analyze.get()

    def put_webpage(self, 
            page : str
        ) -> None:
        self.webpages_to_analyze.put(page)

    def save_json(self, 
            crawled_data: Dict[str, object]
        ) -> None:
        with self.save_json_lock:
            with open(self.file_name, 'a') as f:
                f.write(json.dumps(crawled_data) + '\n')

    def url_queue_empty(self):
        return self.urls_to_crawl.empty()
    
    def webpage_queue_empty(self):
        return self.webpages_to_analyze.empty()


def extractor(database : Database):
    total_parsed = 0
    logger.info("Extractor started")
    while not database.event.set() or not database.webpage_queue_empty():
        try:
            page = database.get_webpage()
            logger.info(f"Parsing url: {page.url}")
            soup = BeautifulSoup(page.content, 'html.parser')
            links = set()
            all_a = soup.find_all('a')
            for link in all_a:
                url = link.get('href')
                
                parse_url = True
                if url is None or len(url) <= 0 or url[0] != '/':
                    continue
                url = database.config['root_url'] + url[1:]
                url = urljoin(url, urlparse(url).path)
                
                for forbidden in database.config['forbidden_url']:
                    if url.find(forbidden) != -1:
                        parse_url = False
                
                if url in database.urls_seen or url in links:
                    parse_url = False
                
                if parse_url:
                    links.add( url )
            database.put_urls( list(links) )
            try:
                def to_utf8(text):
                    return text.encode('ascii', 'ignore').decode('ascii')
                created_at = soup.select( database.config['created_at'] )[0].get_text().strip()
                created_at = to_utf8(created_at)
                title = soup.select( database.config['title'] )[0].get_text().strip()
                title = to_utf8(title)
                description = soup.select( database.config['description'] )[0].get_text().strip()
                description = to_utf8(description)
                image = soup.select( database.config['image'] )[0]['data-src']
                image = urljoin(image, urlparse(image).path)
                image = to_utf8(image)
                logger.debug(f"\ncreated_at: {created_at}\ntitle: {title}\ndescription: {description[:20]}...\nimage: {image}")
                database.save_json(
                    {
                        "created_at": created_at,
                        "title": title,
                        "description": description,
                        "image": image,
                    }
                )
                total_parsed += 1
                logger.info(f"Total Parsed News: {total_parsed}")
            except Exception as e:
                logger.exception(e)
            logger.info(f"Parsed url: {page.url}")
        except Exception as e:
            logger.exception(e)
    logger.info("Extractor stopped")



def downloader(database : Database):
    total_downloaded = 0
    logger.info("Downloader started")
    while not database.event.set() or not database.url_queue_empty():
        try:
            url = database.get_url()
            logger.info( f"Downloading url: {url}")
            if database.use_selenium:
                pass 
                # To be implemented
            else:
                page = requests.get(url)
            assert page.status_code == 200, f"Status code is {page.status_code}"
            total_downloaded += 1
            logger.info( f"Downloaded url: {url}, Total Downloaded: {total_downloaded}")
            database.put_webpage(page)
        except Exception as e:
            logger.exception(e)

    logger.info("Downloader stopped")


if __name__ == "__main__":
    config_logger()

    database = Database( config= NEWSPAPER_CONFIG_SELECTOR['tbsnews'], save_dir= '.' + os.sep + 'crawl', use_selenium = False)
    logger.info("Crawling started")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        
        executor.submit(downloader, database )
        executor.submit(extractor, database)
        

