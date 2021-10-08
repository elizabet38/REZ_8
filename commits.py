from utils import get_html
from branches import Branch


class Commits(object):
    def __init__(self, url: str, show_progress=False):
        self.project_url = url
        self.src_url = self.get_src()

        self.branches = []
        self.get_branches()

        self.show_progress = show_progress

    def get_src(self):
        commits_url = self.project_url + 'commits/'
        soup = get_html(commits_url)
        details_menu = soup.find('details-menu', class_='SelectMenu SelectMenu--hasFilter')
        return details_menu.get_attribute_list('src')[0]

    def get_branches(self):
        url = 'https://github.com' + self.src_url
        soup = get_html(url)
        branch_items = soup.find_all('a', class_='SelectMenu-item')
        for branch_item in branch_items:
            branch_name = branch_item.find('span').text
            branch_url = branch_item.get_attribute_list('href')[0]
            branch = Branch(branch_url, branch_name)
            self.branches.append(branch)

    def get_commit(self):
        while True:
            max_branch = max(self.branches)
            try:
                commit = max_branch.get_commit()
            except IndexError:
                self.branches.remove(max_branch)
            else:
                if self.show_progress:
                    print('{} / {}'.format(max_branch.call_nums, len(max_branch)))
                return commit, max_branch.name
