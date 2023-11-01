# Copyright 2023 Yubico AB

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from gitbark.git import Commit
from gitbark.rule import BranchRule, RuleViolation
from gitbark.util import cmd
from gitbark.cli.util import click_prompt


def is_descendant(prev: Commit, new: Commit) -> bool:
    """Checks that the current tip is a descendant of the old tip"""

    _, exit_status = cmd(
        "git",
        "merge-base",
        "--is-ancestor",
        prev.hash.hex(),
        new.hash.hex(),
        check=False,
    )

    return exit_status == 0


class ForcePush(BranchRule):
    """Prevents force pushing (non-linear history)."""

    def _parse_args(self, args):
        self.allow = args.get("allow", False)

    def validate(self, commit: Commit, branch: str):
        if not self.allow:
            prev_head_hash = self.repo.branches[branch].target.raw
            prev_head = Commit(prev_head_hash, self.repo)
            if not is_descendant(prev_head, commit):
                raise RuleViolation(
                    f"Commit is not a descendant of {prev_head_hash.hex()}"
                )

    @staticmethod
    def setup():
        allow = click_prompt(prompt="Allow force pushing to branch", type=bool)
        return {"force_push": {"allow": allow}}
