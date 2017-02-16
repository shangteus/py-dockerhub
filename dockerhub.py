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

import os
import requests


class DockerHub(object):
    def __init__(self, url=None, version='v2'):
        self.version = version
        self.url = '{0}/{1}'.format(url or 'https://hub.docker.com', self.version)
        self._session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _do_requests_get(self, address, **kwargs):
        try:
            resp = self._session.get(address, params=kwargs, timeout=(5, 15))
        except requests.exceptions.Timeout as e:
            raise TimeoutError('Connection Timeout. Download failed: {0}'.format(e))
        except requests.exceptions.RequestException as e:
            raise ConnectionError('Connection Error. Download failed: {0}'.format(e))
        else:
            return resp

    def _get_item(self, name, subitem=''):
        user = 'library'
        if '/' in name:
            user, name = name.split('/', 1)

        resp = self._do_requests_get(os.path.join(self.api_url('repositories/{0}/{1}'.format(user, name)), subitem))

        code = resp.status_code
        if code == 200:
            j = resp.json()
            return j
        elif code == 404:
            raise ValueError('{0} repository does not exist'.format(name))
        else:
            raise ConnectionError('{0} download failed: {1}'.format(name, code))

    def _iter_item(self, address, **kwargs):
        next = None
        resp = self._do_requests_get(address, **kwargs)

        while True:
            if next:
                resp = self._do_requests_get(next)

            resp = resp.json()

            for i in resp['results']:
                yield i

            if resp['next']:
                next = resp['next']
                continue

            return

    def api_url(self, path):
        return '{0}/{1}/'.format(self.url, path)

    def search(self, term):
        return self._iter_item(self.api_url('search/repositories'), query=term)

    def get_repositories(self, user):
        return self._iter_item(self.api_url('repositories/{0}'.format(user)))

    def get_repository(self, name):
        return self._get_item(name)

    def get_tag(self, name, tag):
        return self._get_item(name, 'tags/{0}'.format(tag))

    def get_dockerfile(self, name):
        return self._get_item(name, 'dockerfile')['contents']

    def get_user(self, name):
        resp = self._do_requests_get(self.api_url('users/{0}'.format(name)))
        return resp.json()

    def close(self):
        self._session.close()
