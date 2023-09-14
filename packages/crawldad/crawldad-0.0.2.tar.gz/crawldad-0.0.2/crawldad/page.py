import bs4
import requests
import json
import urllib

class Page:

    @property
    def links(self):
        return self._links

    @property
    def fragments(self):
        return self._fragments
    
    @property
    def url(self):
        return self._final_url

    @property
    def ok(self):
        return self._ok

    @property
    def backlinks(self):
        return list(self._backlinks)

    def set_event_listener(self, event_name, event_listener):
        self._event_listeners[event_name] = event_listener

    def debug(self):
        print(f'==================================================')
        print(f'Original URL: {self._original_url}')
        print(f'Final URL:    {self._final_url}')
        print(f'OK:           {self._ok}')
        print(f'==================================================')
        for item in self._links:
            href = item['href']
            url = item['url']
            print(f'Link href:    {href}')
            print(f'Link URL:     {url}')
            print(f'---')
        print()

    def add_backlink(self, url):
        self._backlinks.add(url)
 
    # TODO: Set backlink on init? Because we could use it when the page is not OK...
    def __init__(self, url):
        self._original_url = url
        self._backlinks = set()
        self._event_listeners = {
            'error': lambda page_url: None,
            'soup': lambda soup, page_url: None
        }

    def visit(self):
        # New event listener API suggests that visit should be a public method that's
        # manually invoked after event listeners have been set.
        try:
            self._visit_url()
        except Exception as e:
            self._ok = False
            self._event_listeners['error'](self._original_url)
            self._final_url = self._original_url
            return
        # Components should be generated from the final URL, not the user-provided original URL.
        # The original URL might have relative paths e.g. https://pigweed.dev/pw_tokenizer/../pw_build/
        # that can introduce bugs.
        self._components = urllib.parse.urlparse(self._final_url)
        self._parse_fragments()
        self._parse_hrefs()
        self._synthesize_links()
    
    def _visit_url(self):
        response = requests.get(self._original_url)
        self._ok = response.ok
        if not response.ok:
            self._event_listeners['error'](self._original_url)
        self._final_url = response.url
        self._content_type = response.headers['Content-Type']
        self._html = response.text # TODO: Only do this for HTML content.
        self._soup = bs4.BeautifulSoup(response.text, 'html.parser') # TODO: Only do this for HTML content.
        self._event_listeners['soup'](self._soup, self._final_url)
   
    # TODO: Record the text of each <a> element.
    def _parse_hrefs(self):
        hrefs = set()
        for node in self._soup.find_all('a', href=True):
            href = node['href']
            hrefs.add(href)
        self._hrefs = hrefs
    
    def _parse_fragments(self):
        ids = set()
        for node in self._soup.find_all(id=True):
            ids.add(node['id'])
        self._ids = ids

    def _resolve_dots(self, path):
        if '../' not in path:
            return path
        tokens = path.split('/')
        final_tokens = []
        for token in tokens:
            if token == '..':
                final_tokens.pop()
            else:
                final_tokens.append(token)
        final_path = '/'.join(final_tokens)
        return final_path

    def _build_intrasite_url_from_absolute_path(self, child):
        params = ''
        query = ''
        fragment = ''
        return urllib.parse.urlunparse((
            self._components.scheme,
            self._components.netloc,
            self._resolve_dots(child.path),
            params,
            query,
            fragment
        ))

    # Repro: https://pigweed.dev/../pw_multisink/docs.html or https://pigweed.dev/pw_multisink/
    def _build_intrasite_url_from_relative_path(self, child):
        params = ''
        query = ''
        fragment = ''
        # Builds up an absolute path from the known-absolute path of this
        # page and the incomplete portion of a path that we are provided from
        # the child. E.g. if the current page is https://pigweed.dev/pw_tokenizer/docs.html
        # and the provided href is api.html then we need to deduce that the full URL
        # should be https://pigweed.dev/pw_tokenizer/api.html
        if '/' in self._components.path:
            end_index = self._components.path.rindex('/') + 1
            parent_dir = self._components.path[0:end_index]
            path = f'{parent_dir}{child.path}'
        else:
            path = child.path
        return urllib.parse.urlunparse((
            self._components.scheme,
            self._components.netloc,
            self._resolve_dots(path),
            params,
            query,
            fragment
        ))

    def _build_intrasite_url_from_fragment(self, child):
        params = ''
        query = ''
        fragment = ''
        return urllib.parse.urlunparse((
            self._components.scheme,
            self._components.netloc,
            self._components.path,
            params,
            query,
            fragment
        ))
    
    def _synthesize_links(self):
        links = []
        for href in self._hrefs:
            link = {'href': href}
            components = urllib.parse.urlparse(href)
            if components.scheme.startswith('http'):
                link['url'] = href
            elif components.path.startswith('/'):
                link['url'] = self._build_intrasite_url_from_absolute_path(components)
            elif components.path != '':
                link['url'] = self._build_intrasite_url_from_relative_path(components)
            elif href.startswith('#'):
                link['url'] = self._build_intrasite_url_from_fragment(components)
            else:
                link['url'] = None
            links.append(link)
        self._links = links
