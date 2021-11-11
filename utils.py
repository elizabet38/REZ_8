import requests
from bs4 import BeautifulSoup
from datetime import date
from loguru import logger
from exceptions import PageNotFoundError, AbuseError

MONTHS = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}


def comment_to_date(comment: str):
    words = comment.split(sep=' ')
    month = MONTHS[words[2]]
    day = int(words[3][:-1])
    year = int(words[4])
    return date(year, month, day)


def html_check(html):
    if html.find('title', text='Page not found · GitHub · GitHub') is not None:
        logger.error('Page not found')
        raise PageNotFoundError
    else:
        if html.find('h1', text='Whoa there!') is not None:
            logger.error('Abuse detection mechanism')
            raise AbuseError
        else:
            pass
            # logger.info('html check passed!')


def get_html(url: str, timeout=10):
    """Downloading html from url"""
    logger.info('Getting html from {}'.format(url))
    if not url[:5] == 'https':
        url = 'https://{0}'.format(url)
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        logger.error('Timeout exceeded ({0} seconds)'.format(timeout))
        raise TimeoutError
    else:
        logger.info('Successfully got for {} seconds'.format(response.elapsed.total_seconds()))
        soup = BeautifulSoup(response.text, 'lxml')
        html_check(soup)
        with open('last_html.html', 'w', encoding='utf-8') as file:
            file.write(str(soup))
        return soup


def get_blocks_list(branch_url: str):
    soup = get_html(branch_url)
    blocks = soup.find_all('div', class_='TimelineItem-body')
    return blocks


def set_source(source):
    def set_source_(func):
        def wrapped_func(self, *args, **kwargs):
            self.update_source = source
            func(self, *args, **kwargs)
            self.update_source = None

        return wrapped_func

    return set_source_


def is_there_another_page(html):
    button = html.find('a', rel='nofollow', text='Older')
    if button is not None:
        return True, button['href']
    else:
        button = html.find('a', rel='nofollow', text='Next')
        if button is not None:
            return True, button['href']
        else:
            return False, None


def parse_url(url):
    # logger.debug('Parsing url: {}'.format(url))
    words = url.split('/')
    if not words[0] == 'https:' and words[1] == '':
        logger.error('Url {} is not an url'.format(url))
        return
    kwargs = {'resource': words[2], 'project_owner': words[3], 'project_name': words[4]}
    if len(words) >= 7:
        if words[5] == 'commit':
            kwargs['commit_name'] = words[6]
        if words[5] == 'tree' or 'commits':
            kwargs['branch_name'] = words[6]
    return kwargs
