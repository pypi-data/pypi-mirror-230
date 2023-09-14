"""Parse HTML for links."""
from html.parser import HTMLParser
import urllib.parse


class LinkParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ['href', 'src']:
                value = self.remove_internal_link(value)
                if value and not 'mailto:' in value:
                    self.links.append(value)

    def make_link_absolute(self, base, url):
        return urllib.parse.urljoin(base, url)

    def make_links_absolute(self, base):
        self.links = [
            self.make_link_absolute(
                base, link) for link in self.links]

    def remove_internal_link(self, url):
        return url.split('#')[0]

