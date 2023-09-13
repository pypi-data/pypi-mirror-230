# SPDX-FileCopyrightText: 2023 Matthias Riße <m.risse@fz-juelich.de>
#
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess

from .git import GitRepo


class GitAnnexRepo(GitRepo):
    @classmethod
    def private_clone(cls, git_url, target_directory):
        repo = cls.clone(git_url, target_directory)
        repo.set_config("annex.private", "true")
        repo.init()
        return repo

    def init(self):
        cmd = ["git", "-C", str(self.path), "annex", "init"]
        subprocess.run(cmd, capture_output=True, check=True)

    def get(self, path):
        cmd = ["git", "-C", str(self.path), "annex", "get", str(path).lstrip("/")]
        subprocess.run(cmd, capture_output=True, check=True)

    def get_num_bytes(self, path, n):
        cmd = [
            "git",
            "-C",
            str(self.path),
            "annex",
            "get",
            "--json-progress",
            str(path).lstrip("/"),
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            progress = process.stdout.readline()
            progress = json.loads(progress)
            if int(progress["byte-progress"]) >= n:
                break
        process.terminate()

    def drop(self, path):
        cmd = ["git", "-C", str(self.path), "annex", "drop", str(path).lstrip("/")]
        subprocess.run(cmd, capture_output=True, check=True)

    def info(self, path):
        cmd = [
            "git",
            "-C",
            str(self.path),
            "annex",
            "info",
            "--json",
            "--bytes",
            str(path).lstrip("/"),
        ]
        result = subprocess.run(cmd, capture_output=True, check=True)
        info_data = json.loads(result.stdout)
        return info_data
