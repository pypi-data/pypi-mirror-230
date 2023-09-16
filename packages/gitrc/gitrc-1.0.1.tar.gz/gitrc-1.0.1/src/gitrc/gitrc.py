#!/usr/bin/env python3
import argparse
import github3
import sys
from sys import stdout, stderr


__all__ = [
	'GitRC',
]


class GitRC(object):

	def __init__(self):
		self.parser = argparse.ArgumentParser(
			"gitrc",
			add_help="Remote control of 'git' for things like getting all repos from a "
			"Github user account."
		)
		# create the list of subparsers
		self.subparsers = self.parser.add_subparsers(
			required=True,
			help="Types of commands.",
		)

		# "download" command sub-parser
		self.command_subparser = self.subparsers.add_parser("download")
		self.command_subparser.add_argument(
			"github_username",
			help="Download all repos for this Github user account.",
		)
		self.command_subparser.add_argument(
			'--username',
			required=False,
			default=None,
			help="Github username to authenticate with.",
		)
		self.command_subparser.add_argument(
			'--password',
			required=False,
			type=str,
			default=None,
			help="Github password to authenticate with.",
		)
		self.command_subparser.add_argument(
			'-p',
			required=False,
			default=False,
			action='store_true',
			dest='output_prompt',
			help="If set you will be prompted for a password.",
		)
		self.command_subparser.add_argument(
			'--password_prompt',
			default='Password: ',
		)
		self.command_subparser.add_argument(
			'--url',
			type=str,
			default='https://api.github.com/users/{}/repos',
			help="The URL for the Githb API endpoint.",
		)
		self.command_subparser.set_defaults(func=self.download_cmd)
		self.args = None

	def parse_cmdl_args(self, args=None):
		self.args = self.parser.parse_args(args)
		return self.args

	def download_cmd(self, args):
		"""
		Download all repos for a Github user account.

		:param list args: Command line arguments.
		:rtype: list of str
		:returns: All repos for the given Github user account.
		"""
		if args.username is not None:
			if args.output_prompt:
				gh = github3.github.GitHub(
					username=args.username,
					password=input(args.password_prompt),
				)
			else:
				gh = github3.github.GitHub(
					username=args.username,
					password=args.password,
				)
		else:
			gh = github3.github.GitHub()
		for r in gh.repositories_by(
			args.github_username,
			type='owner',
		):
			sys.stdout.write(f'{r.clone_url}\n')
			sys.stdout.flush()

	def run(self):
		args = self.parse_cmdl_args()
		args.func(args)






