import requests
from bs4 import BeautifulSoup
from datetime import date

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


def get_html(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_blocks_list(branch_url: str):
    soup = get_html(branch_url)
    blocks = soup.find_all('div', class_='TimelineItem-body')
    return blocks