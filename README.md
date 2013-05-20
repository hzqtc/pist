# Pist: A Gist Command Line Interface

Pist is a CLI for the [Gist API](https://gits.github.com). You can easily
access, create and update your gists from the command line.

## Features

* Github account login.
* List authorized user's all gists.
* Display detail information and version history of gists.
* Create new gists.
* Delete existing gists.
* Download gists, including downloading a particular version.
* Upload gists.
* Remove files from gists (see `gist push`).

## Features (which are not bugs)

* **Can't** access other user's gists.
* **Can't** create anonymous gists.

## Dependencies

Pist is written in Python and it is powered by
[Requests](https://github.com/kennethreitz/requests).

## Usage

### pist login

* user authenticate
* access token save in `~/.pist_token`
* revoke access anytime at <https://github.com/settings/applications>

```
$ pist login
Github username: user
Password: pwd
Login successful! Now try "pist list" to see all your gists.
```

### pist list

* list all your gists, both public and private
* public/private, id, files and URL
* `+` for public and `-` for private

```
$ pist list
+ 1234 a.c a.h main.c
  https://gist.github.com/1234
+ 4869 mm.py
  https://gist.github.com/4869
- 3489 test.md
  https://gist.github.com/3489
```

### pist info id

* display detail information of a gist
* history: version hash, committed time and changeset

```
$ pist info 1234
Gist 1234: https://gist.github.com/user/1234
Description: A test gist for pist dev.
Created at: 2013/4/28 10:10 AM
Updated at: 2013/4/28 16:45 PM

a.c   1043 bytes
a.h   298 bytes
main.c    10456 bytes

* 34293478925897159 2013/4/28 10:20 AM 11 ++++++-----
* 31295805839758274 2013/4/28 14:04 PM  2 --
```

### pist delete [-f] id

* delete gist with specified id
* confirm before delete unless `-f` is specified

```
$ pist delete 4869
This operation will delete gist 4869, continue? (y/N) y
Gist deleted.
```

### pist create [-p] [-d description] file1 [file2] [file3] ...

* create a new gist with files
* new gist will be public unless `-p` is specified

```
$ pist create -p foo.sh bar.sh
Private gist 8888 created: https://gist.github.com/user/8888
```

### pist pull [-f] [-v version] id

* pull all gist files into working directory
* ask if file exists, use `-f` to force overwrite without asking
* download a particular version with `-v`

```
$ pist pull -f 1234
a.c done
a.h done
This operation will overwrite main.c, continue? (y/N) Y
main.c done
```

### pist push [-d description] id file1 [file2] [file3] ...

* upload local files to a gist
* if a file specified doesn't exist locally, it will be removed from the gist

```
$ pist push 1234 a.c main.c a.h
Gist 1234 updated: ++++++--
```

## Contribution

Be my guest.
