import logging
import os.path
from dataclasses import dataclass, field
from deprecation import deprecated  # type: ignore
import re
import subprocess
from typing import List, Optional, Tuple, Union

from .utils import getLogger, run
from .gitlab import Forge, GitLabTest, Project, Resource, ResourceNotFoundError,\
    unknown, Unknown, AnonymousUser
from .assignment import Assignment
from .i18n import _
from . import __version__


def missing_course() -> 'Course':
    raise ValueError("missing required argument: 'course'")


"""
Characters that are forbidden in GitLab group names

https://docs.gitlab.com/ee/user/reserved_names.html#limitations-on-project-and-group-names

Test:

    >>> re.sub(forbidden_in_gitlab_group_name, " ", "a-s+d o_98#(*&$'sadf.)")
    '-a+sd o_98 (    sadf.)'
"""
forbidden_in_gitlab_group_name = re.compile(r"[^.()\w+-]")


@dataclass
class CourseAssignment(Assignment):
    # Until Python 3.10 and keyword only fields, a subdataclass
    # can't add mandatory arguments. We fake `course` being
    # mandatory by providing a default factory raising an error.
    # https://medium.com/@aniscampos/python-dataclass-inheritance-finally-686eaf60fbb5

    course: 'Course' = field(default_factory=missing_course)
    student_group: Optional[str] = None                       # Meant to be mutable

    def personal_repo_path_components(self,
                                      username: Optional[str] = None
                                      ) -> Tuple[str, ...]:
        """
        Return the components from which the path of the student's submission is built

        Example:

            >>> course = getfixture("rich_course")
            >>> assignment = course.assignment("SubCourse/Assignment1")

            >>> assignment.personal_repo_path_components()
            ('travo-test-etu', 'TestCourse', '2020-2021', 'SubCourse', 'Assignment1')

            >>> assignment.personal_repo_path_components(username="john.doo")
            ('john.doo', 'TestCourse', '2020-2021', 'SubCourse', 'Assignment1')

            >>> course.group_submissions = True
            >>> assignment.personal_repo_path_components(username="john.doo")
            ('john_doo_travo', 'TestCourse', '2020-2021', 'SubCourse', 'Assignment1')

            >>> course.path='TestModule/TestCourse'
            >>> assignment.personal_repo_path_components()
            ('travo-test-etu_travo', 'TestModule', 'TestCourse', '2020-2021', 'SubCourse', 'Assignment1')
        """
        root = self.get_username(username)
        if self.course.group_submissions:
            root = root.replace(".", "_") + "_travo"
        components = [root, *self.course.path.split('/')]
        if self.course.session_path is not None:
            components.append(self.course.session_path)
        components.extend(self.name.split('/'))
        return tuple(components)

    def personal_repo_path(self,
                           username: Optional[str] = None
                           ) -> str:
        """
        Return the path on the forge of the student's submission for this assignment

        Examples:

            >>> course = getfixture("course")
            >>> course.assignment("SubCourse/Assignment1").personal_repo_path()
            'travo-test-etu/TestCourse-SubCourse-Assignment1'

            >>> course = getfixture("rich_course")
            >>> course.assignment("SubCourse/Assignment1").personal_repo_path()
            'travo-test-etu/TestCourse-2020-2021-SubCourse-Assignment1'
            >>> course.assignment("SubCourse/Assignment1",
            ...                   student_group="Group1").personal_repo_path()
            'travo-test-etu/TestCourse-2020-2021-SubCourse-Assignment1'

        More examples with grouped submissions:

            >>> course.group_submissions = True
            >>> assignment = course.assignment("SubCourse/Assignment1")
            >>> assignment.personal_repo_path()
            'travo-test-etu_travo/TestCourse/2020-2021/SubCourse/Assignment1'
            >>> assignment.personal_repo_path(username="john.doo")
            'john_doo_travo/TestCourse/2020-2021/SubCourse/Assignment1'
        """
        components = self.personal_repo_path_components(username)
        if self.course.group_submissions:
            return '/'.join(components)
        else:
            return components[0] + '/' + '-'.join(components[1:])

    def personal_repo_name_components(self) -> Tuple[str, ...]:
        """
        Return the components from which the path of the student's submission is built

        Precondition: the user must be logged in, non anymously.

        Examples:

            >>> course = getfixture("rich_course")
            >>> course.forge.login()
            >>> assignment = course.assignment("SubCourse/Assignment1")

            >>> assignment.personal_repo_name_components()
            ('Étudiant de test pour travo',
             'Test course', '2020-2021', 'SubCourse', 'Assignment1')

            >>> course.group_submissions = True
            >>> assignment.personal_repo_name_components()
            (...Étudiant de test pour travo...,
             'Test course', '2020-2021', 'SubCourse', 'Assignment1')

        Test:

            >>> name = assignment.personal_repo_name_components()[0]
            >>> from travo.i18n import _
            >>> expected = _('submission group name', 
            ...              name='Étudiant de test pour travo')
            >>> assert name == expected
        """
        user = self.forge.get_current_user()
        assert not isinstance(user, AnonymousUser)
        assert user.name is not None
        name = user.name

        # Replace forbidden characters by spaces
        name = re.sub(forbidden_in_gitlab_group_name, " ", name)

        if self.course.group_submissions:
            name = _('submission group name', name=user.name)
        components = [name, self.course.name]
        if self.course.session_name:
            components.append(self.course.session_name)
        components.extend(self.name.split('/'))
        return tuple(components)

    def personal_repo_name(self) -> str:
        """
        Return the name of the student's personal repository for the given assignment

        Precondition: the user must be logged in, non anymously.

        Example:

            >>> course = getfixture("course")
            >>> course.forge.login()
            >>> course.assignment("SubCourse/Assignment1").personal_repo_name()
            'Test course - SubCourse - Assignment1'

            >>> course = getfixture("rich_course")
            >>> course.forge.login()
            >>> course.assignment("SubCourse/Assignment1").personal_repo_name()
            'Test course - 2020-2021 - SubCourse - Assignment1'
        """
        components = self.personal_repo_name_components()
        if self.course.group_submissions:
            return components[-1]
        else:
            return ' - '.join(components[1:])

    def ensure_personal_repo(self,
                             leader_name: Optional[str] = None) -> Project:
        """
        Return the personal repository for this assignment

        Creating it and configuring it if needed.

        """
        if self.course.group_submissions:
            path_components = self.personal_repo_path_components()
            name_components = self.personal_repo_name_components()
            current_path = ""
            for (path, name) in list(zip(path_components, name_components))[:-1]:
                if current_path:
                    current_path += "/"
                current_path += path
                self.forge.ensure_group(current_path,
                                        name=name,
                                        visibility="private")
        return super().ensure_personal_repo(leader_name=leader_name)

    def submissions_forked_from_path(self) -> Union[str, Unknown]:
        """Return the path of the repository that submissions should be a fork of.

        If the course has student groups and the student group is not
        specified, then the student repo should be a fork of some
        unknown fork of `repo`. We won't have enough information to
        create the student submission, but if it already exists, we
        can still fetch, submit, etc.

            >>> course = getfixture("rich_course")
            >>> course.assignment("SubCourse/Assignment1").submissions_forked_from_path()
            unknown
            >>> course.assignment("SubCourse/Assignment1",
            ...                   student_group="Group1").submissions_forked_from_path()
            'TestCourse/2020-2021/SubCourse/Group1/Assignment1'
        """
        if self.leader_name is not None:
            return super().submissions_forked_from_path()
        if self.course.student_groups is not None and self.student_group is None:
            return unknown
        return self.course.assignment_repo_path(self.name,
                                                student_group=self.student_group)

    def submissions_forked_from_missing(self) -> None:
        """Callback when forked_from must be known but is not
        """
        assert self.course.student_groups is not None and self.student_group is None
        self.course.check_student_group(self.student_group)

    def submissions_search_from(self) -> Tuple[Project, int]:
        """Return a project `p` and an int `d` such that the submissions for
        this assignment are all the forks of `p` of depth `d`
        """
        path = self.submissions_forked_from_path()
        if path is unknown:
            return (self.repo(), 2)
        else:
            repo = self.forge.get_project(path)
            return (repo, 1)

    def get_submission_username(self, project: Project) -> Optional[str]:
        """Return the username for the given submission

        Example:

            >>> course = getfixture("course")
            >>> assignment_path = getfixture("assignment_path")
            >>> assignment = course.assignment(assignment_path)
            >>> assignment_personal_repo = getfixture("assignment_personal_repo")

            >>> assignment.get_submission_username(assignment.repo())
            >>> assignment.get_submission_username(assignment_personal_repo)
            'travo-test-etu'

        TODO: test with a rich course and the assignment fork for a student group
        """
        if project.path_with_namespace.startswith(self.course.assignments_group_path):
            return None
        else:
            return project.get_creator().username


@dataclass
class Course:
    """Model a course

    Example:

        >>> from travo.gitlab import GitLab
        >>> GitLab.home_dir = getfixture('tmp_path')  # for CI

        >>> forge = GitLab("https://gitlab.dsi.universite-paris-saclay.fr")
        >>> course = Course(forge=forge,
        ...                 path="Info111",
        ...                 name="Info 111 Programmation Impérative",
        ...                 session_path="2022-2023",
        ...                 student_dir="~/ProgImperative",
        ...                 student_groups=["MI1", "MI2", "MI3"],
        ...                 expires_at="2023-12-31",
        ...                 mail_extension="universite-paris-saclay.fr")

    - `expires_at` (optional): date at which instructors will loose access
      to the student repositories, as a YEAR-MONTH-DAY date string.

    With this example, assignments will be stored in Info111/2022-2023,
    with one fork for each student group in, e.g. Info111/2022-2023/MI3

       >>> course.assignments_group_path
       'Info111/2022-2023'
       >>> course.assignments_group_name
       '2022-2023'
       >>> assignment = course.assignment("Semaine2", student_group="MI3")
       >>> assignment.repo_path
       'Info111/2022-2023/Semaine2'
       >>> assignment.submissions_forked_from_path()
       'Info111/2022-2023/MI3/Semaine2'

    If you wish to use another course layout, you can set the
    above variables directly.
    """
    forge:           Forge
    path:            str
    name:            str
    student_dir:     str
    assignments_group_path: str = ""
    assignments_group_name: str = ""
    session_path:    Optional[str] = None
    session_name:    Optional[str] = None  # Will be defined as soon as session_path is
    assignments:     Optional[List[str]] = None
    student_groups:  Optional[List[str]] = None
    script:          str = "travo"
    url:             Optional[str] = None
    jobs_enabled_for_students: bool = False
    log:             logging.Logger = field(default_factory=getLogger)
    mail_extension:  str = ""
    expires_at:      Optional[str] = None
    group_submissions: bool = False

    def __post_init__(self) -> None:
        # TODO: "Check that: name contains only letters, digits, emojis, '_', '.', dash, space. It must start with letter, digit, emoji or '_'."
        if self.session_path is not None:
            self.assignments_group_path = os.path.join(
                self.path,
                self.session_path)
            if self.session_name is None:
                self.session_name = self.session_path

        if self.session_name is not None:
            self.assignments_group_name = self.session_name

        if not self.assignments_group_path:
            self.assignments_group_path = self.path
        if not self.assignments_group_name:
            self.assignments_group_name = os.path.basename(self.assignments_group_path)

    def work_dir(self,
                 assignment: Optional[str] = None,
                 role: str = "student") -> str:
        """
        Return the absolute work directory for all (git) commands

        Examples:

        Let's create a dummy course::

            >>> forge = getfixture("gitlab")
            >>> course = Course(forge=forge,
            ...                 path="...", name="...",
            ...                 student_dir="~/ProgImperative")

        The work directory for a student, for example to clone a new
        assignment, is given by the `student_dir` attribute of the
        course, with the home dir ("~/") expanded:

            >>> course.work_dir(role="student")
            '/.../ProgImperative'

        (where ... is the student's home directory). To work inside a
        given assignment, for example to run `git push` or `git
        pull`, the work directory is::

            >>> course.work_dir(role="student", assignment="Week1")
            '/.../ProgImperative/Week1'

        When `student_dir` is set to ".", the user is in charge of
        being in the appropriate directory for the current operation.
        So this always return "." for the current directory::

            >>> course = Course(forge=forge,
            ...                 path="...", name="...",
            ...                 student_dir=".")
            >>> course.work_dir(role="student")
            '.'
            >>> course.work_dir(role="student", assignment="Week1")
            '.'

        .. CAVEAT::

            This default implementation follows the convention that
            the work directory for an assignment is obtained by
            joining the assignment name to the root work directory.
            Some methods (e.g. assignment_clone) assume that this
            convention is followed and will need to be generalized
            should some course want to use another one.
        """
        assert role == "student"
        dir = self.student_dir
        if dir == ".":
            return "."
        if dir[:2] == "~/":
            dir = os.path.join(self.forge.home_dir, dir[2:])
        if assignment is not None:
            dir = os.path.join(dir, assignment)
        return dir

    def ensure_work_dir(self) -> str:
        """
        Ensure the existence of the student's work directory

        Return the work directory.

        Examples:

            >>> import os.path
            >>> course = getfixture("course")

            >>> work_dir = course.work_dir(); work_dir
            '/.../TestCourse'
            >>> assert not os.path.exists(work_dir)

            >>> course.ensure_work_dir()
            '/tmp/.../TestCourse'

            >>> assert os.path.isdir(work_dir)

        This is an idempotent operation:

            >>> course.ensure_work_dir()
            '/tmp/.../TestCourse'
            >>> assert os.path.isdir(work_dir)
        """
        work_dir = self.work_dir()
        if not os.path.isdir(work_dir):
            self.log.info(_("creating work dir", work_dir=work_dir))
            assert os.path.isabs(work_dir)
            run(["mkdir", "-p", work_dir])
        return work_dir

    def check_student_group(self,
                            student_group: Optional[str],
                            none_ok: bool = False
                            ) -> None:
        """
        Check that the given student group name is valid

        Raise on error; otherwise return nothing.
        """
        if self.student_groups is None or student_group in self.student_groups:
            return
        if none_ok and student_group is None:
            return
        message = ""
        if student_group is not None:
            message += _('unknown group', student_group=student_group) + "\n"
        message += _('specify group',
                     student_groups=', '.join(self.student_groups)) + "\n"
        # message += _('help', script=self.script)

        raise RuntimeError(message)

    def check_assignment(self, assignment: str) -> None:
        """
        Check whether assignment is a valid assignment

        This current default implementation does nothing.
        Alternatively, it could check whether the assignment exists on
        the forge.

        Courses may override it.
        """
        pass

    def assignment_repo_path(self,
                             assignment: str,
                             student_group: Optional[str] = None) -> str:
        """
        Return the path on the forge for the repository holding the
        student version of the given assignment.

        If `group` is provided, then the path of the student_groups' fork
        thereof is returned instead.

        This method may typically be overriden by the course.

        Example:

            >>> course = getfixture("course")
            >>> course.assignment_repo_path("Assignment1")
            'TestCourse/2020-2021/Assignment1'
            >>> course.assignment_repo_path("Subcourse/Assignment1")
            'TestCourse/2020-2021/Subcourse/Assignment1'

            >>> course.assignment_repo_path("Assignment1", student_group="MI1")
            'TestCourse/2020-2021/MI1/Assignment1'
            >>> course.assignment_repo_path("Subcourse/Assignment1", student_group="MI1")
            'TestCourse/2020-2021/Subcourse/MI1/Assignment1'
        """
        result = [self.assignments_group_path]
        dirname  = os.path.dirname(assignment)
        assignment = os.path.basename(assignment)
        if dirname:
            result.append(dirname)
        if student_group:
            result.append(student_group)
        result.append(assignment)
        return '/'.join(result)

    def assignment_repo_name(self, assignment: str) -> str:
        """
        Return the name of the student repository for the given assignment

        This method may typically be overriden by the course.

        Example:

            >>> course = getfixture("course")
            >>> course.assignment_repo_name("SubCourse/Assignment1")
            'Assignment1'
        """
        return os.path.basename(assignment)

    @deprecated(deprecated_in="0.2", removed_in="1.0",
                current_version=__version__,
                details="Use course.assignment(...).personal_repo_path() instead")
    def assignment_personal_repo_path(self,
                                      assignment_name: str,
                                      username: Optional[str] = None
                                      ) -> str:
        """
        Return the path on the forge of the student's personal repository for the given assignment
        """
        return self.assignment(assignment_name,
                               username=username).personal_repo_path()

    @deprecated(deprecated_in="0.2", removed_in="1.0",
                current_version=__version__,
                details="Use course.assignment(...).personal_repo_name() instead")
    def assignment_personal_repo_name(self, assignment_name: str) -> str:
        """
        Return the name of the student's personal repository for the given assignment
        """
        return self.assignment(assignment_name).personal_repo_name()

    Assignment = CourseAssignment

    def assignment(self,
                   assignment_name: str,
                   student_group: Optional[str] = None,
                   leader_name: Optional[str] = None,
                   username: Optional[str] = None
                   ) -> CourseAssignment:
        """
        Return the assignment `assignment` for the given user

        By default, the user is the current user.
        """
        # The path of the original assignment; not the fork of the student groups
        repo_path = self.assignment_repo_path(assignment_name)
        self.check_student_group(student_group,
                                 none_ok=True)
        return self.Assignment(
                          forge=self.forge,
                          course=self,
                          log=self.log,
                          name=assignment_name,
                          instructors_path=self.assignments_group_path,
                          script=self.script,
                          expires_at=self.expires_at,
                          repo_path=repo_path,
                          student_group=student_group,
                          leader_name=leader_name,
                          username=username,
                          assignment_dir=self.work_dir(assignment_name),
                          jobs_enabled_for_students=self.jobs_enabled_for_students,
                          )

    @deprecated(deprecated_in="0.2", removed_in="1.0",
                current_version=__version__,
                details="Use course.assignment(...).personal_repo() instead")
    def assignment_personal_repo(self,
                                 assignment_name: str,
                                 student_group: Optional[str] = None) -> Project:
        """
        Return the personal repository for this assignment
        """
        assignment = self.assignment(assignment_name,
                                     student_group=student_group)
        return assignment.ensure_personal_repo()

    def remove_assignment_personal_repo(self,
                                        assignment: str,
                                        force: bool = False) -> None:
        """
        Remove the users' personal repository for this assignment
        """
        self.assignment(assignment).remove_personal_repo(force=force)

    def fetch(self, assignment: str,
              student_group: Optional[str] = None,
              force: bool = False) -> None:
        """
        fetch the given assignment
        """
        self.ensure_work_dir()
        assignment_dir = self.work_dir(assignment=assignment)
        return self.assignment(assignment, student_group=student_group).fetch(assignment_dir=assignment_dir,
                                                                              force=force)

    def submit(self,
               assignment: str,
               student_group: Optional[str] = None,
               leader_name: Optional[str] = None) -> None:
        """
        submit the given assignment
        """
        self.check_assignment(assignment)
        the_assignment = self.assignment(assignment,
                                         student_group=student_group,
                                         leader_name=leader_name)
        assignment_dir = self.work_dir(assignment)
        the_assignment.submit(assignment_dir=assignment_dir,
                              leader_name=leader_name)

    def share_with(self,
                   assignment_name: str,
                   username: str,
                   access_level: Union[int, Resource.AccessLevels] = Resource.AccessLevels.DEVELOPER,
                   ) -> None:
        try:
            repo = self.assignment(assignment_name).personal_repo()
        except ResourceNotFoundError:
            raise RuntimeError(_("no submission; please submit", assignment_name=assignment_name))
        user = self.forge.get_user(username)
        repo.share_with(user, access=access_level)

    def release(self, assignment: str, visibility: str = "public") -> None:
        """
        Release the student version of the given assignment on the forge

        Assumption: the current working directory holds the student
        version of the assignment, as a git repository

        This sets up the student repository on the forge, if it does
        not yet exist, and pushes all branches to this repository
        (`push --all`).

        In addition, for each student group, it sets up a fork of the
        above directory and pushes there.

        .. CAVEAT::

            Backward incompatible change with the shell version:
            Release is now meant to be run from the assignment
            directory rather than the root directory of the course, to
            make no hypothesis on the layout of the latter.
        """

        self.check_assignment(assignment)
        self.log.info(f"Publish the assignment {assignment} with visibility {visibility}.")

        # travo_gitlab_remove_project "${repo}"
        attributes = dict(
            visibility = visibility,
            issues_enabled = False,
            merge_requests_enabled = False,
            container_registry_enabled = False,
            wiki_enabled = False,
            snippets_enabled = False,
            lfs_enabled = False,
        )

        path = self.assignment_repo_path(assignment)
        name = self.assignment_repo_name(assignment)
        project = self.forge.ensure_project(path=path, name=name, **attributes)
        try:
            project.unprotect_branch(project.default_branch)
        except RuntimeError:
            pass
        self.log.info(f"- Publishing to {path}.")
        self.forge.git(["push", "--all", project.http_url_to_repo])

        if self.student_groups is None:
            return

        for student_group in self.student_groups:
            path = self.assignment_repo_path(assignment, student_group=student_group)
            name = self.assignment_repo_name(assignment)
            self.log.info(f"- Publishing to the student group {student_group}' fork {path}.")
            self.forge.ensure_group(os.path.dirname(path),
                                    name=student_group,
                                    visibility="public")

            fork = project.ensure_fork(path=path,
                                       name=name,
                                       jobs_enabled=False,
                                       **attributes)
            try:
                fork.unprotect_branch(project.default_branch)
            except RuntimeError:
                pass
            self.forge.git(["push", "--all", fork.http_url_to_repo])

    def remove_assignment(self, assignment: str, force: bool = False) -> None:
        """
        Remove the assignment on the forge (DANGEROUS!)

        This is an irreversible operation!
        """
        self.forge.login()
        self.check_assignment(assignment)
        self.log.info(f"Unpublish the assignment {assignment}.")

        if self.student_groups is not None:
            for student_group in self.student_groups:
                a = self.assignment(assignment, student_group=student_group)
                path = a.submissions_forked_from_path()
                assert path is not unknown
                try:  # Don't fail if this fork does not exist (any more)
                    repo = self.forge.get_project(path)
                except ResourceNotFoundError:
                    pass
                else:
                    self.forge.remove_project(path, force=force)

        repo = self.assignment(assignment).repo()
        # Only the main repo has pipelines set
        repo.remove_pipelines()
        self.forge.remove_project(repo.path_with_namespace, force=force)

    def collect(self,
                assignment:    str,
                student_group: Optional[str] = None,
                student:       Optional[str] = None,
                template:      str = "{username}",
                date:          Optional[str] = None) -> None:
        """
        Collect the student's assignments

        Examples:

        Collect all students submissions in the current directory::

            course.collect("Assignment1")

        Collect all students submissions for a given student group,
        laying them out in nbgrader's format, with the student's group
        appended to the username:

            course.collect("Assignment1",
                           student_group="MP2",
                           template="exchange/Course/submitted/MP2-{username}/{path}")
        """
        path = self.assignment_repo_path(assignment, student_group)
        self.forge.collect_forks(path,
                                 username=student,
                                 template=template,
                                 date=date)

    def ensure_instructor_access(self,
                assignment:    str,
                student_group: Optional[str] = None) -> None:
        """
        Ensure instructor access to the student repositories.

        """
        self.forge.login()
        path = self.assignment_repo_path(assignment, student_group)
        project = self.forge.get_project(path)
        forks = project.get_forks(recursive=True)
        for fork in forks:
            self.log.info(_("ensure instructor access", path=fork.path_with_namespace))
            instructors = self.forge.get_group(self.assignments_group_path)
            member_ids = [user['id'] for user in fork.get_members()]
            for instructor in instructors.get_members():
                if instructor.id not in member_ids:
                    fork.share_with(instructor,
                                    access=fork.AccessLevels.MAINTAINER,
                                    expires_at=None)

    def run(self, *args: str) -> subprocess.CompletedProcess:
        """Run an arbitrary shell command"""
        return run(args)

    def get_released_assignments(self, level: str = "", order_by: str = "created_at") -> List[str]:
        group_path = self.assignments_group_path
        if level:
            group_path += "/" + level
            level += "/"
        group = self.forge.get_group(group_path)
        projects = group.get_projects(simple=True,
                                      with_shared=False,
                                      order_by=order_by,
                                      sort='asc')
        return [level + p.path for p in projects]
