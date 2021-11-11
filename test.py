from project_info.commits import Commit
from project_info.branches import Branch
from project_info.project import Project
from loguru import logger
from datetime import timedelta

test_commits_urls = [
    'https://github.com/blitz-js/babel-plugin-superjson-next/commit'
    '/042ef6cda9fd81000b78c15edd9f4f73d625907f',
    'https://github.com/misterokaygo/MapAssist/commit/c6371feeee14a5457bb8dfae1ad59e70e5e0600e',
    'https://github.com/questdb/questdb/commit/277326f46b697d19d613cb6b7b555f1b0f351104',
    'https://github.com/babysor/MockingBird/commit/9f30ca8e928ae919bdcbb60ba969e8102d1bbbdf'
]

test_branches_urls = [
    'https://github.com/VSPlekhanov/OpenSourceProjectsAnalyzer/tree/vsplekhanov_comiits_frequency',
    'https://github.com/babysor/MockingBird/tree/Add-GST',
    'https://github.com/questdb/questdb/tree/compiled-filters',
    'https://github.com/blitz-js/babel-plugin-superjson-next/tree/main'
]

test_project_urls = [
    'https://github.com/elizabet38/REZ_8',
    'https://github.com/VSPlekhanov/OpenSourceProjectsAnalyzer',
    'https://github.com/misterokaygo/MapAssist',
    'https://github.com/blitz-js/babel-plugin-superjson-next',
    'https://github.com/questdb/questdb',
    'https://github.com/babysor/MockingBird'
]


def commit_test():
    for commit_url in test_commits_urls:
        commit = Commit(commit_url)
        logger.debug('*' * 128 + '\n')
        logger.debug('Debugging commit: {}'.format(commit_url))
        commit.get_info()

        logger.debug('\n')


def branch_test():
    for branch_url in test_branches_urls:
        logger.debug('*' * 128 + '\n')
        logger.debug('Debugging branch: {}'.format(branch_url))
        branch = Branch(branch_url)
        branch.set_attr_by_url()
        branch.get_commits()
        branch.get_info()
        branch.set_commit_attrs()

        logger.debug('\n')

        logger.debug('Total commits: {}'.format(len(branch.commits)))
        for commit in branch.commits:
            commit.get_info()


def project_test():
    for project_url in test_project_urls:
        logger.debug('*' * 128 + '\n')
        logger.debug('Debugging project: {}'.format(project_url))

        project = Project(project_url, time_slice=timedelta(days=90))
        project.get_branches()
        project.get_commits()


# commit_test()
# branch_test()
project_test()