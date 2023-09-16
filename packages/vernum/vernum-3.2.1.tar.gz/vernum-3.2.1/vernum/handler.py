
import os
from subprocess import run
from argparse import ArgumentParser
import re
from dataclasses import dataclass

FORMAT = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

LEVELS = ['major','minor','patch']

@dataclass
class Handler:

    dry_run:bool = False
    push_tag:bool = False

    def git(self, command, dry_ok=False):
        print('git ' + command)
        if dry_ok or not self.dry_run:
            result = run(['git'] + command.split(),
                                    capture_output=True, text=True)
            if result.returncode != 0:
                raise SystemExit(result.stderr)
            return result.stdout.strip()

    def get_previous_version(self):
        branch = self.git("branch --show-current", dry_ok=True)
        tags = self.git(f"tag --merged {branch}", dry_ok=True)
        result = (0,0,0)
        for tag in tags.split('\n'):
            if match:=FORMAT.match(tag):
                version = tuple(int(x) for x in match.groups())
                if version > result:
                    result = version
        return result
                        

    def update_version(self, level):
        major, minor, patch = self.get_previous_version()
        if level == 'major':
            major += 1
            minor = 0
            patch = 0
        elif level == 'minor':
            minor += 1
            patch = 0
        else: patch += 1
        newversion = '%i.%i.%i' % (major, minor, patch)
        if self.dry_run:
            print(f"Write {newversion} to .version")
        else:
            with open('.version', 'w') as versionfile:
                versionfile.write(newversion)
        return newversion

    def do(self, level=None):
        status = self.git('status -s')
        if status:
            raise SystemExit('Git working tree must be clean to update version')
        version = self.update_version(level)
        print('Version updated to ' + version)
        if self.push_tag:
            print(self.git(f"tag -a v{version} -m v{version}"))
            print(self.git('push --tags'))
        print('Release complete')

def main():
    parser = ArgumentParser()
    parser.add_argument('level', choices=LEVELS, default='patch', nargs='?')
    parser.add_argument('--dry-run', '-n', action='store_true')
    parser.add_argument('--push-tag', '-t', action='store_true')
    namespace = parser.parse_args()
    handler = Handler(namespace.dry_run, namespace.push_tag)
    handler.do(namespace.level)

