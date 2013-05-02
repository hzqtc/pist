#!/usr/bin/env python

import getopt
import getpass
import json
import os
import requests
import sys

from datetime import datetime
from clint.textui import colored

token_file = os.path.expanduser('~/.pist_token')
api_root = 'https://api.github.com'
show_max_changed_lines = 10

class GistFile(object):

    def __init__(self):
        self.filename = ''
        self.filetype = ''
        self.language = ''
        self.raw_url = ''
        self.size = 0
        self.content = ''

    @classmethod
    def from_json_obj(cls, obj):
        gf = GistFile()

        gf.filename = obj['filename']
        gf.filetype = obj['type']
        gf.language = obj['language']
        gf.raw_url = obj['raw_url']
        gf.size = obj['size']
        if 'content' in obj:
            gf.content = obj['content']

        return gf

class GistHistory(object):

    def __init__(self):
        self.version = ''
        self.committed_time = None
        self.additions = 0
        self.deletions = 0

    @classmethod
    def from_json_obj(cls, obj):
        gh = GistHistory()
        gh.version = obj['version']
        gh.committed_time = parse_api_time(obj['committed_at'])
        if 'additions' in obj['change_status']:
            gh.additions = obj['change_status']['additions']
        if 'deletions' in obj['change_status']:
            gh.deletions = obj['change_status']['deletions']

        return gh

class Gist(object):

    def __init__(self):
        self.gid = ''
        self.url = ''
        self.files = []
        self.public = True
        self.create_time = None
        self.update_time = None
        self.description = ''
        self.history = []

    @classmethod
    def from_json_obj(cls, obj):
        g = Gist()
        g.gid = obj['id']
        g.url = obj['html_url']
        for f in obj['files'].values():
            g.files.append(GistFile.from_json_obj(f))
        g.public = obj['public']
        g.created_time = parse_api_time(obj['created_at'])
        g.updated_time = parse_api_time(obj['updated_at'])
        g.description = obj['description']
        if 'history' in obj:
            for h in obj['history']:
                g.history.append(GistHistory.from_json_obj(h))

        return g

def parse_api_time(tstr):
    return datetime.strptime(tstr, '%Y-%m-%dT%H:%M:%SZ')

def pist_gettoken():
    return open(token_file).read()

def pist_login():
    user = raw_input('Github account: ')
    passwd = getpass.getpass()

    postdata = {
        'scopes': [
            'gist'
        ],
        'note': 'Pist',
        'note_url': 'https://github.com/hzqtc/pist'
    }
    url = '%s/%s' % (api_root, 'authorizations')
    r = requests.post(url, data = json.dumps(postdata), auth=(user, passwd))

    if r.status_code == requests.codes.created:
        token = r.json()['token']
        open(token_file, 'w').write(token)
        print 'Login successfully! Now try "pist list" to see all your gists.'
    else:
        print colored.red('Login failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def pist_list():
    token = pist_gettoken()
    url = '%s/%s' % (api_root, 'gists')
    r = requests.get(url, headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.ok:
        for o in r.json():
            gist = Gist.from_json_obj(o)
            print '%s %s: %s' % (colored.green('+') if gist.public else colored.red('-')
                    , colored.blue(gist.gid), ' '.join(map(lambda f: f.filename, gist.files)))
    else:
        print colored.red('Listing gists failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def pist_info(gid):
    token = pist_gettoken()
    url = '%s/%s/%s' % (api_root, 'gists', gid)
    r = requests.get(url, headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.ok:
        gist = Gist.from_json_obj(r.json())
        print 'Gist %s: %s' % (colored.blue(gist.gid), colored.yellow(gist.url))
        print 'Description: %s' % colored.yellow(gist.description)
        print 'Created at: %s' % colored.cyan(gist.created_time.strftime('%Y/%m/%d %H:%M:%S'))
        print 'Updated at: %s' % colored.cyan(gist.updated_time.strftime('%Y/%m/%d %H:%M:%S'))
        print ''
        for f in gist.files:
            print '%s\t%d bytes' % (colored.blue(f.filename), f.size)
        print ''
        for h in gist.history:
            a = h.additions
            if a > show_max_changed_lines:
                a = show_max_changed_lines
            d = h.deletions
            if d > show_max_changed_lines:
                d = show_max_changed_lines
            print '* %s %s %s%s' % (colored.yellow(h.version), colored.cyan(h.committed_time.strftime('%Y/%m/%d %H:%M:%S')),
                    colored.green('+' * a), colored.red('-' * d))
    else:
        print colored.red('Getting gist failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def pist_delete(gid, force = False):
    if force == False:
        ans = raw_input('This operation will delete gist %s, continue? (y/N) ' % gid).upper()
        if ans != 'Y':
            return

    token = pist_gettoken()
    url = '%s/%s/%s' % (api_root, 'gists', gid)
    r = requests.delete(url, headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.no_content:
        print 'Gist %s deleted.' % colored.blue(gid)
    else:
        print colored.red('Delete gist failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def pist_create(files, private = False, description = ''):
    token = pist_gettoken()
    url = '%s/%s' % (api_root, 'gists')
    postdata = {
        'description': description,
        'public': not private,
        'files': {}
    }
    for f in files:
        try:
            postdata['files'][f] = { 'content': open(f).read() }
        except IOError as e:
            print colored.red('Cannot read %s: %s' % (f, e.msg))
            return
    r = requests.post(url, data = json.dumps(postdata), headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.created:
        gist = Gist.from_json_obj(r.json())
        print '%s gist %s created: %s' % ('Public' if gist.public else 'Private', colored.blue(gist.gid), colored.yellow(gist.url))
    else:
        print colored.red('Creating gist failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))


def pist_pull(gid, force = False, version = ''):
    token = pist_gettoken()
    if version:
        url = '%s/%s/%s/%s' % (api_root, 'gists', gid, version)
    else:
        url = '%s/%s/%s' % (api_root, 'gists', gid)
    r = requests.get(url, headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.ok:
        gist = Gist.from_json_obj(r.json())
        for f in gist.files:
            if os.path.exists(f.filename) and force == False:
                ans = raw_input('This operation will overwrite %s, continue? (y/N) ' % f.filename).upper()
                if ans != 'Y':
                    print '%s skipped' % colored.blue(f.filename)
                    continue
            try:
                open(f.filename, 'w').write(f.content.encode('utf-8'))
                print '%s done' % colored.green(f.filename)
            except IOError as e:
                print '%s error: %s' % (colored.red(f.filename), e.msg)
                continue
    else:
        print colored.red('Getting gist failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def pist_push(gid, files, description = ''):
    token = pist_gettoken()
    url = '%s/%s/%s' % (api_root, 'gists', gid)
    postdata = {
        'files': {}
    }
    if description:
        postdata['description'] = description
    for f in files:
        if os.path.exists(f):
            try:
                postdata['files'][f] = { 'content': open(f).read() }
            except IOError as e:
                print colored.red('Cannot read %s: %s' % (f, e.msg))
                return
        else:
            postdata['files'][f] = None
    r = requests.patch(url, data = json.dumps(postdata), headers = {'Authorization': 'token ' + token})

    if r.status_code == requests.codes.ok:
        gist = Gist.from_json_obj(r.json())
        a = gist.history[0].additions
        if a > show_max_changed_lines:
            a = show_max_changed_lines
        d = gist.history[0].deletions
        if d > show_max_changed_lines:
            d = show_max_changed_lines
        print 'Gist %s updated: %s%s' % (colored.blue(gist.gid), colored.green('+' * a), colored.red('-' * d))
    else:
        print colored.red('Updating gist failed! HTTP status code: %d, message: %s' % (r.status_code, r.json()['message']))

def usage():
    print "Pist: A Gist Command Line Interface."
    print 'Usage: pist <command> [options] [id] [files]'
    print '  pist login                                 Login with your github account.'
    print '  pist list                                  List all your gists.'
    print '  pist info <id>                             Display detail information for a gist.'
    print '  pist delete <id>                           Delete one of your gists.'
    print '  pist create [-p] [-d description] <files>  Create a new gist with local files.'
    print '    -p, --private                            Create a private gist [default to public].'
    print '    -d, --description=STRING                 Set gist description.'
    print '  pist pull [-f] [-v version] <id>           Download files of a gist to the working directory.'
    print '    -f, --force                              Force overwrite local file.'
    print '    -v, --version=STRING                     Download a specified version instead of the latest.'
    print '  pist push [-d description] <files>         Upload local files and overwriten corresponding remote files.'
    print '    -d, --description=STRING                 Edit gist description.'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit()
    else:
        cmd = sys.argv[1]

    try:
        opts, args = getopt.getopt(sys.argv[2:], 'pd:fv:', ['private', 'description=', 'force', 'version='])
    except getopt.GetoptError as err:
        print colored.red('Syntax error: %s.' % str(err))
        usage()
        sys.exit(2)

    private = False
    description = ''
    force = False
    version = ''

    for o, a in opts:
        if o in ('-p', '--private'):
            private = True
        elif o in ('-d', '--description'):
            description = a
        elif o in ('-f', '--force'):
            force = True
        elif o in ('-v', '--version'):
            version = a

    if cmd in ('info', 'delete', 'pull', 'push'):
        if args:
            gid = args[0]
        else:
            print colored.red('Syntax error: gist id cannot be empty.')
            usage()
            sys.exit(2)

    if cmd in ('create', 'push'):
        if args:
            files = args
        else:
            print colored.red('Syntax error: file list cannot be empty.')
            usage()
            sys.exit(2)

    if cmd == 'login':
        pist_login()
    elif cmd == 'list':
        pist_list()
    elif cmd == 'info':
        pist_info(gid)
    elif cmd == 'delete':
        pist_delete(gid, force)
    elif cmd == 'create':
        pist_create(files, private, description)
    elif cmd == 'pull':
        pist_pull(gid, force, version)
    elif cmd == 'push':
        pist_push(gid, files, description)
    else:
        usage()
