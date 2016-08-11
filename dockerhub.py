#
# Copyright 2016 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################

import requests


class DockerHub(object):
    def __init__(self, url=None, version='v2'):
        self.version = version
        self.url = '{0}/{1}'.format(url or 'https://hub.docker.com', self.version)

    def api_url(self, path):
        return '{0}/{1}/'.format(self.url, path)

    def search(self, term):
        next = None
        resp = requests.get(self.api_url('search/repositories'), {'query': term})

        while True:
            if next:
                resp = requests.get(next)

            resp = resp.json()

            for i in resp['results']:
                yield i

            if resp['next']:
                next = resp['next']
                continue

            return

    def get_repository(self, name, user='library'):
        resp = requests.get(self.api_url('repositories/{0}/{1}'.format(user, name)))
        code = resp.status_code
        if code == 200:
            return resp.json()
        elif code == 404:
            raise ValueError('{0} repository does not exist'.format(name))
        else:
            raise ConnectionError('{0} download failed with status {1}'.format(name, code))

    def get_user(self, name):
        resp = requests.get(self.api_url('users/{0}/'.format(name)))
        return resp.json()
