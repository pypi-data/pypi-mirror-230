# gitrc

A simple command line utility to write all repos from Github for a given user 
or organization to standard output.  Github credentials are optional.  But, 
providing `username` and `password` increases the number of repos you can 
download at one time due to Github's rate limiting policy.  To use `gitrc` in 
shell scripts the `password` can be passed via standard input, for better 
security practices.

## Installation

```shell script
pip install gitrc
```

## Usage

```shell script
$ gitrc download -h
usage: gitrc download [-h] [--username USERNAME] [--password PASSWORD] [-p] [--password_prompt PASSWORD_PROMPT] [--url URL] github_username

positional arguments:
  github_username       Download all repos for this Github user account.

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   Github username to authenticate with.
  --password PASSWORD   Github password to authenticate with.
  -p                    If set you will be prompted for a password.
  --password_prompt PASSWORD_PROMPT
  --url URL             The URL for the Githb API endpoint.
```


