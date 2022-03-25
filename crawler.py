import concurrent.futures
import logging
import queue
import threading
import os
from typing import Dict, List
import requests
import logging
from bs4 import BeautifulSoup

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
            root_url : str,
            forbidden_urls : List[str], 
            save_dir : str, 
            queue_max_size : int = 1000, 
            resume : bool = False, 
            resume_dir: str = None
        ) -> None:

        self.urls_to_crawl = queue.Queue(maxsize=queue_max_size)
        self.urls_crawled = set()
        self.webpages_to_analyze = queue.Queue(maxsize=queue_max_size)
        self.webpage_lock = threading.Lock()
        self.save_json_lock = threading.Lock()
        self.file_name = save_dir  + os.sep + 'crawled_pages.json'
        self.counter = 1
        self.forbidden_sub_urls = forbidden_urls
        self.event = threading.Event()
        self.event.set()
        if resume:
            pass 
            # to be implemented
        else:
            self.urls_to_crawl.put(root_url)

    def get_url(self) -> str:
        return self.urls_to_crawl.get() 

    def put_url(self, 
            url : str
        ) -> None:
        self.urls_to_crawl.put(url) 

    def put_urls(self, 
            urls : List[str]
        ) -> None:
        pass 

    def get_webpage(self) -> str:
        return self.webpages_to_analyze.get()

    def put_webpage(self, 
            page : str
        ) -> None:
        self.webpages_to_analyze.put(page)

    def save_json(self, 
            crawled_data: Dict[str, object]
        ) -> None:
        pass 

    def url_queue_empty(self):
        return self.urls_to_crawl.empty()
    
    def webpage_queue_empty(self):
        return self.webpages_to_analyze.empty()


def extractor(database : Database):
    logger.info("Extractor started")
    while not database.event.set() or not database.webpage_queue_empty():
        page = database.get_webpage()
        soup = BeautifulSoup(page.content, 'html.parser')
    logger.info("Extractor stopped")



def downloader(database : Database):

    logger.info("Downloader started")
    while not database.event.set() or not database.url_queue_empty():
        url = database.get_url()
        try:
            logger.info( f"Downloading url: {url}")
            page = requests.get(url)
            logger.info( f"Downloaded url: {url}")
            assert page.status_code == 200, f"Status code is {page.status_code}"
            database.put_webpage(page)
        except Exception as e:
            logger.exception(e)

    logger.info("Downloader stopped")


if __name__ == "__main__":
    config_logger()
    
    root_url = 'https://www.tbsnews.net/'
    forbidden_sub_urls = ['https://www.tbsnews.net/bangla/']

    database = Database(  root_url=root_url, forbidden_urls=forbidden_sub_urls, save_dir= '.' + os.sep + 'crawl')
    logger.info("Crawling started")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        
        executor.submit(downloader, database )
        executor.submit(extractor, database)
        

