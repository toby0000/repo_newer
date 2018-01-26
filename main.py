# -*- coding: utf-8 -*-
import os
import sys
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

GIT_API_BASE = 'https://api.github.com'
AUTH = ()

class Commit:
    def __init__(self, message, author, date_):
        self.message = message
        self.author = author
        self.date = date_

    def __repr__(self):
        repr_ = '<\n{}\n{}\n{}\n>'.format(self.message, self.date, self.author)
        return repr_


class Repo:
    '''仓库类
    :param repo_name: 如: toby0000/repo_newer
    '''
    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.last_update_time = None
        self.commits = []
        self.fork_origin = None
        self.forks = []
        self.r_session = requests.Session()
        self.r_session.auth = AUTH

    def result_generator(self, url, data=None):
        '''获取该url所有结果'''
        if data:
            data['page'] = 1
        else:
            data = {'page': 1}

        while True:
            resp = self.r_session.get(url, params=data)
            logger.debug(resp.json())
            for commit in resp.json():
                yield commit
            if resp.headers.get('Link') and resp.headers['Link'].find('rel="next"') != -1:
                data['page'] += 1
            else:
                break

    def update_commits(self, since):
        url = '%s/repos/%s/commits' % (GIT_API_BASE, self.repo_name)
        data = {}
        data['since'] = since.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.commits = [Commit(i['commit']['message'], i['commit']['committer']['name'], i['commit']['committer']['date'])
                        for i in self.result_generator(url, data)]

    def update_last_update_time(self):
        url = '%s/repos/%s/commits' % (GIT_API_BASE, self.repo_name)
        resp = self.r_session.get(url)
        logger.debug(resp.json())
        date_time_str = resp.json()[0]['commit']['committer'].get('date')
        self.last_update_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%SZ')

    def update_fork_origin(self):
        url = '%s/repos/%s' % (GIT_API_BASE, self.repo_name)
        resp = self.r_session.get(url)
        logger.debug(resp.json())
        self.fork_origin = resp.json()['parent']['full_name']

    def update_forks(self):
        ready_to_get_list = [self.repo_name]
        for repo_name in ready_to_get_list:
            url = '%s/repos/%s/forks' % (GIT_API_BASE, repo_name)
            for fork_data in self.result_generator(url):
                logger.info(fork_data)
                fork_name = fork_data['full_name']
                ready_to_get_list.append(fork_name)
                self.forks.append(Repo(fork_name))

    def update_all_forks_commits(self, since):
        '''获取比较所有forks(包括自己)的commits'''
        self.update_commits(since)
        for fork_repo in self.forks:
            fork_repo.update_commits(since)

    def display_commits(self):
        print(self.repo_name)
        for commit in self.commits:
            print(commit)
        print()

    def display_all_forks_commits(self):
        self.display_commits()
        for fork_repo in self.forks:
            fork_repo.display_commits()

    def __repr__(self):
        return '<\n{}\n{}\n>'.format(self.repo_name, self.last_update_time, self.fork_origin)


def main(repo_name, since=None):
    my_repo = Repo(repo_name)
    my_repo.update_fork_origin()
    fork_origin = my_repo.fork_origin
    if not since:
        my_repo.update_last_update_time()
        since = my_repo.last_update_time

    origin_repo = Repo(fork_origin)
    origin_repo.update_forks()
    origin_repo.update_all_forks_commits(since+timedelta(seconds=1))
    origin_repo.display_all_forks_commits()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s:%(funcName)s-%(lineno)d:%(levelname)s:%(message)s')
    if len(sys.argv) < 3:
        print('Usage: python main.py <user:passwd> <repo_name> [datetime]')
        exit()
    AUTH = tuple(sys.argv[1].split(':'))
    repo_name = sys.argv[2]
    try:
        since_str = sys.argv[3]
        since = datetime.strptime(since_str, '%Y-%m-%dT%H:%M:%SZ')
    except IndexError:
        since = None
    main(repo_name, since)
