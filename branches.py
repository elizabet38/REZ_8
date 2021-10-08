from utils import get_html, comment_to_date


class Commit(object):
    """

    """
    def __init__(self, html):
        self.html = html
        self.text = None
        self.get_text()
        self.date = None
        self.get_date()

    def get_text(self):
        html = self.html.find('p')
        texts = html.find_all('a')
        self.text = ''
        for text in texts:
            self.text += (' ' + text.text) if self.text != '' else text.text

    def get_date(self):
        html = self.html.find('div', class_='f6 color-text-secondary min-width-0')
        self.date = html.find('relative-time').get_attribute_list('datetime')[0]

    def __lt__(self, other):
        return self.date < other.date


class Block(object):
    def __init__(self, html):
        self.html = html
        self.date = None
        self.get_date()
        self.commits = []
        self.get_commits()

        self.current_id = 0
        self.current_commit = self.commits[self.current_id]

    def get_date(self):
        comment = self.html.find('h2', class_='f5 text-normal').text
        self.date = comment_to_date(comment)

    def get_commits(self):
        commits_html = self.html.find_all('div', class_='flex-auto min-width-0')
        for commit_html in commits_html:
            commit = Commit(commit_html)
            self.commits.append(commit)

    def get_commit(self):
        self.current_commit = self.commits[self.current_id]
        commit = self.current_commit
        self.current_id += 1
        return commit

    def __len__(self):
        return len(self.commits)

    def __lt__(self, other):
        return self.current_commit < other.current_commit


class Branch(object):
    def __init__(self, url: str, name: str):
        self.branch_url = url
        self.name = name
        self.blocks = []
        self.get_blocks()

        self.current_id = 0
        self.current_block = self.blocks[self.current_id]

        self.call_nums = 0

    def get_blocks(self):
        soup = get_html(self.branch_url)
        html_blocks = soup.find_all('div', class_='TimelineItem-body')
        for html_block in html_blocks:
            block = Block(html_block)
            self.blocks.append(block)

    def get_commit(self):
        self.call_nums += 1
        try:
            commit = self.current_block.get_commit()
        except IndexError:
            self.current_id += 1
            self.current_block = self.blocks[self.current_id]
            commit = self.current_block.get_commit()
        return commit

    def __len__(self):
        return sum([len(block) for block in self.blocks])

    def __lt__(self, other):
        return self.current_block < other.current_block

