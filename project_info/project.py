from utils import get_html, parse_url, set_source, is_there_another_page
from project_info.baseobject import BaseObject
from project_info.branches import Branch
from loguru import logger
from exceptions import htmlError
from datetime import datetime


class Project(BaseObject):

    def __init__(self, project_url, time_slice=None, **kwargs):
        super().__init__(project_url=project_url, **kwargs)

        self.min_datetime = datetime.now() - time_slice

        url_kwargs = parse_url(project_url)
        url_kwargs['source'] = 'project_url'
        self.set_kwargs(**url_kwargs)

        self.branches = []
        self.commits = []

    def get_branches(self, active=True, stale=False):
        logger.info('Getting branches in project {}'.format(self.project_name()))
        branches_url = '{}/branches'.format(self.project_url())
        try:
            branches_html = get_html(branches_url)
        except htmlError:
            logger.error('html is broken')
        else:
            self.get_default_branch(branches_html)

        if active:
            active_branches_url = '{}/active'.format(branches_url)
            try:
                active_branches_html = get_html(active_branches_url)
            except htmlError:
                logger.error('html is broken')
            else:
                self.get_active_branches(active_branches_html)

        if stale:
            stale_branches_url = '{}/stale'.format(branches_url)
            try:
                stale_branches_html = get_html(stale_branches_url)
            except htmlError:
                logger.error('html is broken')
            else:
                self.get_stale_branches(stale_branches_html)
        logger.info('Received {} branch(es)'.format(len(self.branches)))

    @set_source('branches_html')
    def get_default_branch(self, html):
        box = html.find('div', class_='Box Box--condensed mb-3')
        kwargs = self.get_branch_info(box, 'default')

        branch = Branch(**kwargs)
        self.branches.append(branch)

    @set_source('active_branches_html')
    def get_active_branches(self, html):
        branches_html = html.find_all('li', class_='Box-row position-relative')
        for branch_html in branches_html:
            kwargs = self.get_branch_info(branch_html, 'active')

            if kwargs['last_update_datetime'] >= self.min_datetime:
                branch = Branch(**kwargs)
                self.branches.append(branch)
            else:
                logger.info('Too old branch')
                return

        is_there, another_page = is_there_another_page(html)
        if is_there:
            try:
                another_html = get_html(another_page)
            except htmlError:
                logger.error('html is broken')
            else:
                self.get_active_branches(another_html)

    @set_source('stale_branches_html')
    def get_stale_branches(self, html):
        branches_html = html.find_all('li', class_='Box-row position-relative')
        for branch_html in branches_html:
            kwargs = self.get_branch_info(branch_html, 'stale')

            if kwargs['last_update_datetime'] >= self.min_datetime:
                branch = Branch(**kwargs)
                self.branches.append(branch)
            else:
                logger.info('Too old branch')
                return

        is_there, another_page = is_there_another_page(html)
        if is_there:
            try:
                another_html = get_html(another_page)
            except htmlError:
                logger.error('html is broken')
            else:
                self.get_stale_branches(another_html)

    def get_branch_info(self, box, status):
        kwargs = {'source': self.source, 'project_url': self.project_url(), 'branch_status': status}

        kwargs['branch_name'] = box.find('a').text

        kwargs['branch_url'] = 'https://github.com{}'.format(box.find('a')['href'])

        kwargs['last_update_datetime'] = datetime.strptime(box.find('time-ago')['datetime'], '%Y-%m-%dT%H:%M:%SZ')

        try:
            kwargs['last_update_author_name'] = box.find('a', class_='Link--muted').text
        except AttributeError:
            logger.error("Probably author's account has been deleted")

        return kwargs

    def get_commits(self, min_datetime=None):
        if min_datetime is None:
            min_datetime = self.min_datetime
        logger.info('Getting commits in project {}'.format(self.project_name()))
        for branch in self.branches:
            branch.get_commits(min_datetime=min_datetime)
            self.commits.extend(branch.commits)
        logger.info('Received {} commit(s)'.format(len(self.commits)))

    def set_commit_attrs(self):
        logger.info('Setting attrs for commits in project {}'.format(self.project_name()))
        for commit in self.commits:
            commit.set_attrs_by_url()

    def set_branch_attrs(self):
        logger.info('Setting attrs for branches in project {}'.format(self.project_name()))
        for branch in self.branches:
            branch.set_attrs_by_url()