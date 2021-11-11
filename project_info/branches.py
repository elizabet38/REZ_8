from utils import get_html, set_source, is_there_another_page, parse_url
from project_info.baseobject import BaseObject
from loguru import logger
from project_info.commits import Commit
from exceptions import htmlError
from datetime import datetime


class Branch(BaseObject):
    def __init__(self, branch_url, **kwargs):
        super().__init__(branch_url=branch_url, **kwargs)

        self.min_datetime = None

        url_kwargs = parse_url(branch_url)
        url_kwargs['source'] = 'branch_url'
        self.set_kwargs(**url_kwargs)

        self.commits = []

    def set_attr_by_url(self):
        logger.info('Setting attrs in branch: {0}'.format(self.branch_name()))

        try:
            html = get_html(self.branch_url())
        except TimeoutError:
            logger.error('Connection failed')
        except htmlError:
            logger.error('html is broken')
        else:
            self.set_attr_by_html(html)

    @set_source('branch_html')
    def set_attr_by_html(self, html):
        logger.info('Start parsing html')

        head = html.find('strong', itemprop='name')
        self.project_url = 'https://github.com{}'.format(head.a['href'])

        button = html.find('summary', class_='btn css-truncate')
        self.branch_name = button.find('span', class_='css-truncate-target').text

    def get_commits(self, url=None, min_datetime=None):
        self.min_datetime = min_datetime
        logger.info('Getting commits from branch {0}'.format(self.branch_name()))
        if url is None:
            url = '{0}/commits/{1}'.format(self.project_url(), self.branch_name())
        self.get_commits_by_url(url)
        self.min_datetime = None

    def get_commits_by_url(self, url):
        logger.info('Getting commits from {0}'.format(url))

        try:
            html = get_html(url)
        except htmlError:
            logger.error('Unable to get commits')
        else:
            stop = self.get_commits_by_html(html)
            if not stop:
                is_there, another_page = is_there_another_page(html)
                if is_there:
                    self.get_commits_by_url(another_page)

    def get_commits_by_html(self, html):
        commits_html = html.find_all('div', class_='flex-auto min-width-0')
        for commit_html in commits_html:
            kwargs = {'source': 'branch_html', 'branch_name': self.branch_name(), 'project_url': self.project_url()}

            kwargs['commit_url'] = 'https://github.com{}'.format(commit_html.p.a['href'])

            kwargs['commit_title'] = commit_html.p.a.text
            try:
                kwargs['commit_author_name'] = commit_html.find('a', class_='commit-author user-mention').text
            except AttributeError:
                try:
                    kwargs['commit_author_name'] = commit_html.find('span', class_='commit-author user-mention').text
                except AttributeError:
                    logger.error('Probably more than one author')

            kwargs['commit_datetime'] = datetime.strptime(
                commit_html.find('relative-time')['datetime'],
                '%Y-%m-%dT%H:%M:%SZ',
            )

            if kwargs['commit_datetime'] < self.min_datetime:
                logger.info('Too old commit')
                return True
            commit = Commit(**kwargs)
            self.commits.append(commit)
        return False

    def set_commit_attrs(self):
        logger.info('Setting attrs for commits in branch {}'.format(self.branch_name()))
        for commit in self.commits:
            commit.set_attrs_by_url()
