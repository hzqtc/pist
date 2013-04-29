# Pist: A Gist Command Line Interface

Pist is a CLI for the [Gist API](https://gits.github.com). Pist implements all APIs for manipulating personal gists.

## Features

* Github account login
* List all gists
* Display detail information and history of gists
* Create new gists
* Delete existing gists
* Download gists, including downloading a particular version
* Update gists, including remove files from gists

## Dependencies

Pist is written in Python and powered by [Requests](http://python-requests.org/).

## Usage

### pist login

* authenticate 
* access token save in ~/.pist

```
$ pist login
Github username: user
Password: pwd
Login successful! Now try "pist list" to see all your gists.
```


### pist list

* list all gists
* public/private, id and file list
* `+` for public and `-` for private
* sample output:

```
$ pist list
+ 1234 a.c a.h main.c
+ 4869 mm.py
- 3489 test.md
```

### pist info id

* specify gist id 
* display gist id, url, files, create time, update time, description and history
* history: version hash, committed at, change set

```
$ pist info 1234
Gist 1234: https://gist.github.com/user/1234
Files: a.c a.h main.c
Descript: A test gist for pist dev.
Create: 2013/4/28 10:10 AM Update: 2013/4/28 16:45 PM

* 34293478925897159 2013/4/28 10:20 AM ++++++---
* 31295805839758274 2013/4/28 14:04 PM --
```


### pist delete [-f] id

* delete gist with specified id
* confirm before delete

```
$ pist delete 4869
Gist 4869: https://gist.github.com/user/4869
Files: mm.py
Descript: A test gist for pist dev.
Create: 2013/4/28 10:10 AM Update: 2013/4/28 16:45 PM

Are you sure to delete this gist? (y/N)
```


### pist create [-p] [-d description] file1 [file2] [file3] …

* create a new gist with files
* default to public

```
$ pist create -p foo.sh bar.sh
Private gist 8888 created: https://gist.github.com/user/8888
Files: foo.sh bar.sh
```


### pist pull [-f] [-v version] id

* optional specify version hash
* pull all gist files into working directory
* ask if file exists, use -f to force overwrite without asking

```
$ pist pull -f 1234
Gist 1234: https://gist.github.com/user/1234
Files: a.c a.h main.c
Descript: A test gist for pist dev.
Create: 2013/4/28 10:10 AM Update: 2013/4/28 16:45 PM

a.c created
a.h created
main.c exists, overwritten (y/N) Y

```


### pist push [-d description] id file1 [file2] [file3] …

* push local files to gist specified with id
* if a file specified but doesn't exist locally, it will be removed from the gist

```
$ pist push 1234 a.c main.c a.h
a.h doesn't exist, it will be removed from this gist. Continue? (y/N)

Gist 1234: https://gist.github.com/user/1234
Files: a.c a.h main.c
Descript: A test gist for pist dev.
Create: 2013/4/28 10:10 AM Update: 2013/4/28 16:45 PM
```