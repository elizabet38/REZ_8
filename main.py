from commits import Commits

if __name__ == '__main__':
    url = input('insert url in https://github.com/username/projectname/ format:')
    # url = 'https://github.com/raywenderlich/flta-materials/'

    try:
        commits = Commits(url)
    except AttributeError:
        print('Looks like this project is private')
    else:
        for i in range(1, 11):
            try:
                commit, branch = commits.get_commit()
            except ValueError:
                print('There are no that much commits')
            else:
                print('{}:\t "{}"\t commited to\t <{}>\t on\t {}'.format(i, commit.text, branch, commit.date))