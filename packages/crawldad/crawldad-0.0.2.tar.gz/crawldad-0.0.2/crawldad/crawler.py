import sys
import json
from .page import Page

class Crawler():

    def __init__(self, url):
        self._entrypoint_url = url
        self._event_listeners = {}

    def set_event_listener(self, event_name, event_listener):
        self._event_listeners[event_name] = event_listener

    def crawl(self):
        pages = {}
        done = set()
        entrypoint_page = Page(self._entrypoint_url)
        pages[self._entrypoint_url] = entrypoint_page
        queue = [{'url': self._entrypoint_url, 'page': entrypoint_page}]
        while len(queue) > 0:
            item = queue.pop()
            url = item['url']
            done.add(url)
            page = item['page']
            for event_name in self._event_listeners:
                page.set_event_listener(event_name, self._event_listeners[event_name])
            page.visit()
            if not page.ok:
                continue
            for link in page.links:
                link_url = link['url']
                link_page = Page(link_url) if link_url not in pages else pages[link_url]
                # For the case when `link_url` does not yet exist in `pages`.
                # TODO: Maybe just refactor to make that case obvious.
                pages[link_url] = link_page
                link_page.add_backlink(url)
                for event_name in self._event_listeners:
                    link_page.set_event_listener(event_name, self._event_listeners[event_name])
                link_page.visit()
                if not link_page.ok:
                    continue
                # Here we need some kind of indicator that we haven't visited that
                # page yet. `link_url not in pages` is not the right check...
                if link_url.startswith(self._entrypoint_url) and link_url not in done:
                    queue.append({'url': link_url, 'page': link_page})
