from utils import get_html, set_source, parse_url
from loguru import logger
from project_info.baseobject import BaseObject
from exceptions import htmlError
from datetime import datetime


class Commit(BaseObject):
    """Class for single commit on github."""

    def __init__(self, commit_url, **kwargs):
        """Initialization by commits url"""
        super().__init__(commit_url=commit_url, **kwargs)

        url_kwargs = parse_url(commit_url)
        url_kwargs['source'] = 'commit_url'
        self.set_kwargs(**url_kwargs)

    def set_attrs_by_url(self):
        logger.info('Setting attrs for commit {}'.format(self.commit_title()))
        try:
            html = get_html(self.commit_url())
        except TimeoutError:
            logger.error('Connection failed')
        except htmlError:
            logger.error('html is broken')
        else:
            self.set_attrs_by_html(html)

    @set_source('commit_html')
    def set_attrs_by_html(self, html):

        head = html.find('strong', itemprop='name')
        self.project_url = 'https://github.com{}'.format(head.a['href'])

        self.commit_title = html.find('div', class_='commit-title markdown-title').text

        self.commit_datetime = datetime.strptime(html.find('relative-time')['datetime'], '%Y-%m-%dT%H:%M:%SZ')

        self.commit_id = html.find('span', class_='sha user-select-contain').text
        try:
            self.commit_author_name = html.find('a', class_='commit-author user-mention').text
        except AttributeError:
            logger.error('Probably more than one author')

        # self.branch_name = html.find('li', class_='branch')['a'].text

        # self.pull_request = html.find('li', class_='pull-request')['a'].text

    def __lt__(self, other):
        if self.datetime() is None:
            return True
        elif other.datetime() is None:
            return False
        else:
            return self.datetime() < other.datetime()

