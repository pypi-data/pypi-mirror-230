"""
Implementation of the console scripts for travo

- travo
- travo_echo_travo_token
"""

import os
from typing import Any, Optional
from travo import Assignment
from travo.script import CLI
from travo.utils import git_get_origin
from travo import Homework


class Travo:
    """
    This class defines the command line interface for the travo script
    """

    def info(
        self,
        url: str = ".",
        fixup: bool = False,
        group: Optional[str] = None,
        copy: Optional[str] = None,
    ) -> None:
        """
        Get, check and print information on the repository.

        The repository can be either the instructor's assignment or a student submission.
        If the former case, the information is iterated on all student copies.

        --group indicates the correction group to check (if any)

        --fixup tries to fix configuration mismatch (visibility, etc.)

        --copy indicate to work on the given copy (and not all)
        """

        homework = Homework(url)
        if group is not None:
            homework.get_group(group)
        if copy is None:
            forks = homework.get_copies()
        else:
            homework.assignment = homework.project  # assume assigment
            forks = [homework.get_project(copy)]

        for fork in forks:
            homework.print_info(fork, fixup=fixup)

    def search_forks(
        self,
        url: str = ".",
        fixup: bool = False,
        deep: bool = False,
        group: Optional[str] = None,
    ) -> None:
        """
        Search for possible missing forks [instructor]

        For some reason, the fork relationship can be lost with gitlab, for instance
        the `fork` button was not used or fork was made private.

        Note: the search of forks can be slow.

        --deep indicates to search among more potential projects.

        --group indicates the correction group to check (if any)

        --fixup tries to fix configuration mismatch (visibility, etc.)
        """

        homework = Homework(url)
        homework.assignment = homework.project  # assume assigment
        if group is not None:
            homework.get_group(group)

        forks = homework.project.get_possible_forks(deep=deep, progress=True)
        for fork in forks:
            homework.print_info(fork, fixup=fixup)

    def collect(self, url: str = ".", dir: str = "forks") -> None:
        """
        Collect the student repositories [instructor]

        Either a single copy, or all the students' copies if the instructor's assignment is used.

        --dir is the target directory.
        """
        # TODO: merge with Assignment.collect_forks
        homework = Homework(url)
        forks = homework.get_copies()
        template = "{user}-{id}"

        for fork in forks:
            if fork.owner is None:
                continue
            path = os.path.join(
                dir, template.format(user=fork.owner.username, id=fork.id)
            )
            homework.print_info(fork)
            fork.clone_or_pull(path)

    def fetch(self, url: str = ".", assignment_dir: Optional[str] = None) -> None:
        """
        Fetch the assignment [student]

        Fetch assignment from URL, optionally specifying an assignment_dir:

            Travo.fetch(url)
            Travo.fetch(url, assignment_dir)

        Update an already fetched assignment:

            Travo.fetch(assignment_dir)
        """
        if not url.startswith("https:"):
            assert assignment_dir is None
            assignment_dir = url
            url = git_get_origin(assignment_dir)

        assignment = Assignment.from_url(url)

        if assignment_dir is None:
            assignment_dir = os.path.basename(assignment.repo_path)

        assignment.fetch(assignment_dir)

    def submit(self, assignment_dir: str = ".") -> None:
        """
        Submit the copy [student]
        """

        url = git_get_origin(assignment_dir)
        assignment = Assignment.from_url(url)
        assignment.submit(assignment_dir)

    @staticmethod
    def formgrader(assignment: Optional[str] = None, in_notebook: bool = False) -> Any:
        """
        Launch nbgrader's formgrader
        """
        from travo.jupyter_course import JupyterCourse

        return JupyterCourse.formgrader(assignment, in_notebook)

    @staticmethod
    def validate(*files: str) -> None:
        """
        Launch nbgrader's validate
        """
        from travo.jupyter_course import JupyterCourse

        return JupyterCourse.validate(*files)


def test_travo(standalone_assignment: Assignment, tmp_path: str) -> None:
    url = standalone_assignment.repo().http_url_to_repo
    assignment_dir = os.path.join(tmp_path, "Assignment")

    travo = Travo()
    travo.fetch(url, assignment_dir)

    travo.fetch(assignment_dir)
    travo.submit(assignment_dir)

    # Tear down
    standalone_assignment.remove_personal_repo()


usage = """travo [fetch|submit] ...

For students

Fetch the latest version of the assignment:

    travo fetch <url> <dir>
    travo fetch <url>
    travo fetch <dir>

Submit the assignment:

    travo submit <dir>

where `<url>` is the url of the Git repository holding the
assignment, and <dir> is the (to be created) local working copy
for the assignment. By default, the working copy is created in a
subdirectory of current working directory with basename matching
that of the assignment.

More help:

    travo --help
"""


def travo() -> None:
    """
    Entrypoint for the main `travo` console script
    """
    CLI(Travo(), usage=usage)


def travo_echo_travo_token() -> None:
    """
    Entrypoint for the `travo-echo-travo-token console script

    This script is used as GIT_ASKPASS callback to provide the gitlab
    authentication token to git
    """
    print(os.environ["TRAVO_TOKEN"])
