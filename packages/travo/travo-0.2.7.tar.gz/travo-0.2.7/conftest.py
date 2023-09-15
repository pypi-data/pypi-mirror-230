import datetime
import os.path
import pytest  # type: ignore
import random
import string
from typing import Iterator

from travo.gitlab import GitLab, GitLabTest, Group, Project, User
from travo.course import Course
from travo.assignment import Assignment


@pytest.fixture
def gitlab() -> GitLab:
    forge = GitLabTest()
    forge.log.setLevel("DEBUG")
    return forge


@pytest.fixture
def test_run_id() -> str:
    """
    A (statistically) unique id for this test run
    """
    now = datetime.datetime.now().isoformat().replace(":", "-")
    return (
        now + "-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    )


@pytest.fixture
def project_path(test_run_id: str) -> str:
    return f"travo-test-etu/temporary-test-projet-{test_run_id}"


@pytest.fixture
def project_name(test_run_id: str) -> str:
    return f"temporary test projet created at {test_run_id}"


@pytest.fixture
def project(gitlab: GitLab, project_path: str, project_name: str) -> Iterator[Project]:
    project = gitlab.ensure_project(project_path, project_name)
    # TODO: factor out duplication with assignment_repo
    project.ensure_file("README.md")
    yield project
    gitlab.remove_project(project_path, force=True)


@pytest.fixture
def group_path(test_run_id: str) -> str:
    return f"temporary-test-group-{test_run_id}"


@pytest.fixture
def group_name(test_run_id: str) -> str:
    return f"temporary test group created at {test_run_id}"


@pytest.fixture
def group(gitlab: GitLab, group_path: str, group_name: str) -> Iterator[Group]:
    yield gitlab.ensure_group(group_path, group_name)
    gitlab.remove_group(group_path, force=True)

@pytest.fixture
def user_name() -> str:
    return "travo-test-etu"


@pytest.fixture
def user(gitlab: GitLab, user_name: str) -> User:
    return gitlab.get_user(user_name)


@pytest.fixture
def other_user(gitlab: GitLab) -> User:
    return gitlab.get_user("blondin_al")


@pytest.fixture
def fork_path(user_name: str, test_run_id: str) -> str:
    return f"{user_name}/temporary-forked-project-{test_run_id}"


@pytest.fixture
def fork_name(test_run_id: str) -> str:
    return f"temporary forked project created at {test_run_id}"


@pytest.fixture
def standalone_assignment_namespace(gitlab: GitLab) -> Group:
    return gitlab.ensure_group(path="TestGroup",
                               name="Test Group",
                               with_projects=False,
                               visibility="public",
                               )


@pytest.fixture
def standalone_assignment(gitlab: GitLab,
                          user_name: str,
                          standalone_assignment_namespace: Group,
                          test_run_id: str) -> Iterator[Assignment]:
    repo = gitlab.ensure_project(
        f"TestGroup/TestAssignment-{test_run_id}", f"Test assignment - {test_run_id}")
    repo.ensure_file(
        "README.md",
        branch="master")
    yield Assignment(forge=gitlab,
                     log=gitlab.log,
                     repo_path=repo.path_with_namespace,
                     name=repo.path,
                     instructors_path="TestGroup",
                     username=user_name,
                     )
    gitlab.remove_project(repo.path_with_namespace, force=True)


@pytest.fixture
def standalone_assignment_dir(tmp_path: str, test_run_id: str) -> str:
    return os.path.join(tmp_path, f"Assignment-{test_run_id}")


@pytest.fixture
def standalone_assignment_submission(
    standalone_assignment: Assignment
) -> Iterator[Project]:
    project = standalone_assignment.ensure_personal_repo()
    yield project
    standalone_assignment.forge.remove_project(project.path_with_namespace, force=True)


@pytest.fixture
def course() -> Course:
    return Course(name="Test course",
                  forge=GitLabTest(),
                  path="TestCourse",
                  student_dir="~/TestCourse",
                  assignments_group_path="TestCourse/2020-2021"
                  )
    # course.log.setLevel("DEBUG")

@pytest.fixture
def rich_course() -> Course:
    return Course(name="Test course",
                  forge=GitLabTest(),
                  path="TestCourse",
                  session_path="2020-2021",
                  assignments=["Assignment1", "Assignment2"],
                  student_groups=["Group1", "Group2"],
                  student_dir="~/TestCourse",
                  )

@pytest.fixture
def course_assignment_group(course: Course) -> Group:
    course.forge.ensure_group(path=course.path, name=course.name)
    return course.forge.ensure_group(
        path=course.assignments_group_path, name=course.assignments_group_name
    )


@pytest.fixture
def assignment_path(test_run_id: str) -> str:
    return f"temporary-assignment-{test_run_id}"


@pytest.fixture
def assignment_name(test_run_id: str) -> str:
    return f"temporary assignment created at {test_run_id}"


@pytest.fixture
def assignment_repo(
    course: Course,
    course_assignment_group: Group,
    assignment_path: str,
    assignment_name: str,
) -> Iterator[Project]:
    path = course.assignment_repo_path(assignment_path)
    project = course.forge.ensure_project(path, assignment_name)
    project.ensure_file(
        "README.md",
        branch="master")
    yield project
    course.forge.remove_project(path, force=True)


@pytest.fixture
def assignment_personal_repo(
    course: Course, assignment_path: str, assignment_repo: Project
) -> Iterator[Project]:
    project = course.assignment(assignment_path).ensure_personal_repo()
    yield project
    course.forge.remove_project(project.path_with_namespace, force=True)


@pytest.fixture
def student_work_dir(course: Course) -> str:
    return course.ensure_work_dir()
