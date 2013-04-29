# Pist: A Gist Command Line Interface

Pist is a CLI for the [Gist API](https://gits.github.com). Pist implements all APIs for manipulating personal gists.

## Features

* Github account login.
* List user's all gists.
* Display detail information and history of gists.
* Create new gists.
* Delete existing gists.
* Download gists, including downloading a particular version.
* Update gists, including remove files from gists.

## Features (which are not bugs)

* **Can't** access other user's gists.
* **Can't** create anonymous gists.

## Dependencies

Pist is written in Python and powered by [Requests](https://github.com/kennethreitz/requests) and [Clint](https://github.com/kennethreitz/clint).

## Usage

### pist login

* user authenticate
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

```
$ pist list
+ 1234 a.c a.h main.c
+ 4869 mm.py
- 3489 test.md
```

### pist info id

* display gist id, url, files, create time, update time, description and history
* history: version hash, committed at, change set

```
$ pist info 1234
Gist 1234: https://gist.github.com/user/1234
Description: A test gist for pist dev.
Created at: 2013/4/28 10:10 AM
Updated at: 2013/4/28 16:45 PM

[a.c]   1043 bytes
[a.h]   298 bytes
[main.c]    10456 bytes

* 34293478925897159 2013/4/28 10:20 AM ++++++---
* 31295805839758274 2013/4/28 14:04 PM --
```

### pist delete [-f] id

* delete gist with specified id
* confirm before delete

```
$ pist delete 4869
This operation will delete gist 4869, continue? (y/N) y
Gist deleted.
```

### pist create [-p] [-d description] file1 [file2] [file3] …

* create a new gist with files
* default to public

```
$ pist create -p foo.sh bar.sh
Private gist 8888 created: https://gist.github.com/user/8888
```

### pist pull [-f] [-v version] id

* optional specify version hash
* pull all gist files into working directory
* ask if file exists, use -f to force overwrite without asking

```
$ pist pull -f 1234
[a.c] done
[a.h] done
This operation will overwrite main.c, continue? (y/N) Y
[mian.c] done

```

### pist push [-d description] id file1 [file2] [file3] …

* push local files to gist specified with id
* if a file specified but doesn't exist locally, it will be removed from the gist

```
$ pist push 1234 a.c main.c a.h
Gist 1234 updated: ++++++--
```

## Contribution

Be my guest.