import os

from travo.assignment import Assignment


def test_fetch_from_empty_personal_repo(standalone_assignment: Assignment,
                                        standalone_assignment_dir: str) -> None:
    assignment = standalone_assignment
    assignment_dir = standalone_assignment_dir
    forge = assignment.forge
    repo = forge.get_project(assignment.repo_path)

    # "Accidently" create an empty personal repository with no fork relation
    my_repo = forge.ensure_project(path=assignment.personal_repo_path(),
                                   name=assignment.personal_repo_name())
    assert my_repo.forked_from_project is None

    # Fetch + submit should recover smoothly
    assignment.fetch(assignment_dir)

    # Content should be recovered from the original repository
    assert os.path.isfile(os.path.join(assignment_dir,
                                       "README.md"))

    assignment.submit(assignment_dir)

    # The personal repo should now have a single branch named master,
    # and be a fork of the assignment repository
    my_repo = forge.get_project(path=assignment.personal_repo_path())
    branch, = my_repo.get_branches()
    assert branch["name"] == "master"
    assert my_repo.forked_from_project is not None
    assert my_repo.forked_from_project.id == repo.id

    # Tear down
    assignment.remove_personal_repo(force=True)
