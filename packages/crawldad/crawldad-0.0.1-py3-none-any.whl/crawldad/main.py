from page import Page
from crawler import Crawler

def error_listener(page_url):
    return

def soup_listener(soup, page_url):
    if not soup.title:
        return
    print(f'{page_url} ||| {soup.title.text}')

def main():
    entrypoint_url = 'https://technicalwriting.github.io/crawler/'
    crawler = Crawler(entrypoint_url)
    crawler.set_event_listener('error', error_listener)
    crawler.set_event_listener('soup', soup_listener)
    crawler.crawl()

main()
