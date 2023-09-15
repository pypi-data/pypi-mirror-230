##############################################################################
# UI and dashboards
#
# Components:
# - AuthenticationWidget
# - LogWidget
# - Grid of AssignmentDashboards
#
# Design notes
#
# - Any call from the UI to the model (in particular any git/gitlab
#   interaction) goes through LogWidget.callback(action) which is in
#   charge of running the actions in subthreads, logging them, and
#   handling failures.
##############################################################################

import io
import glob
import logging
import os
import subprocess
import requests
from threading import Thread
from typing import Any, Callable, Dict, Optional, List, Tuple

try:
    from ipywidgets import (  # type: ignore
        Button,
        ToggleButton,
        GridBox,
        HBox,
        VBox,
        Dropdown,
        Label,
        Layout,
        Output,
        Password,
        Text,
        Textarea,
        RadioButtons,
    )
    import ipywidgets
except ImportError:
    raise ImportError("Cannot find ipywidgets. "
          "dashboards needs optional dependencies. "
          "Please install travo with 'pip install travo[jupyter]'." )

import numpy as np    # type: ignore
import pandas as pd   # type: ignore

from .assignment import Assignment
from .course import Course, CourseAssignment

from .gitlab import GitLab, AuthenticationError, ResourceNotFoundError, unknown
from .utils import run
from travo.i18n import _
from . import jupyter_course    # only used by type hints

# TODO: should use the current foreground color rather than black
border_layout = {'border': '1px solid black'}


def HTML(*args: Any, **kwargs: Any) -> ipywidgets.HTML:
    """
    Make ipywidgets.HTML apply standard styling to its content

    See https://github.com/jupyter-widgets/ipywidgets/issues/2813
    """
    html = ipywidgets.HTML(*args, **kwargs)
    html.add_class('jp-RenderedHTMLCommon')
    return html


class AuthenticationWidget(VBox):
    """
    A widget for interactive input of credentials

    It's meant to be included in the UI; it will display itself upon
    request, send the credentials through forge.login, and hide itself
    if authentication succeeds.

    """
    on_login_hooks: List[Callable]

    def __init__(self, forge: GitLab):
        forge.on_missing_credentials = self.on_missing_credentials
        self.forge = forge
        title = Label(_("authentication widget title", url=forge.base_url))
        self.usernameUI = Text(description=_("username"), layout={'width': 'fit-content'})
        self.passwordUI = Password(description=_("password"), layout={'width': 'fit-content'})
        self.button = Button(description=_("sign in"),
                             button_style="primary"
                             )
        self.messageUI = Label()
        self.button.on_click(lambda event: self.login())
        # We don't want to call login each time a new character is typed in!
        # Is there a way to only observe the "Return" key press?
        # self.passwordUI.observe(lambda event: self.login(),
        #                         names='value')
        self.on_login_hooks = []
        super(AuthenticationWidget, self).__init__(
            children=(title,
                      self.usernameUI,
                      self.passwordUI,
                      self.button,
                      self.messageUI),
            layout={'border': '1px solid black',
                    'display': 'none'})

    def show_widget(self, message: str = "") -> None:
        self.messageUI.value = message
        self.layout.display = 'block'

    def hide_widget(self) -> None:
        self.layout.display = 'none'

    def login(self) -> None:
        self.messageUI.value = ""
        self.button.disabled = True
        username = self.usernameUI.value
        password = self.passwordUI.value
        try:
            self.forge.login(username=username,
                             password=password,
                             anonymous_ok=True)
            self.hide_widget()
            for hook in self.on_login_hooks:
                Thread(target=hook).start()
        except AuthenticationError as e:
            self.messageUI.value = str(e)
        finally:
            self.button.disabled = False

    def on_login(self, hook: Callable) -> None:
        self.on_login_hooks.append(hook)

    def on_missing_credentials(self,
                               forge: GitLab,
                               username: Optional[str] = None,
                               password: Optional[str] = None
                               ) -> Tuple[str, str]:
        """
        Display the widget and raise to interrupt login
        """
        message = _("authentication required")
        self.show_widget(message)
        raise AuthenticationError(message)


class StatusBar(VBox):
    def __init__(self,
                 authentication_widget: AuthenticationWidget,
                 log: logging.Logger
                 ) -> None:
        minimize_layout = {'flex': '0 0 content'}
        self.authentication_widget = authentication_widget
        self.statusUI = Label(_('ready'),
                              layout={'flex': '1 0 content'})
        self.log_show_UI = ToggleButton(description=_('show log details'),
                                        tooltip=_('show command log'),
                                        value=False,
                                        icon="eye",
                                        layout=minimize_layout)
        self.log_level_UI = Dropdown(options=['WARNING', 'INFO', 'DEBUG'],
                                     tooltip=_('command log level'),
                                     layout=minimize_layout)
        self.logUI = Output(layout={'width': 'fit-content'})
        self.logUI.layout.display = 'none'

        def set_log_show(event: Any) -> None:
            if self.log_show_UI.value:
                self.logUI.layout.display = 'block'
                self.log_show_UI.icon = 'eye-slash'
                self.log_show_UI.description = _('hide log details')
            else:
                self.logUI.layout.display = 'none'
                self.log_show_UI.icon = 'eye'
                self.log_show_UI.description = _('show log details')

        self.log_show_UI.observe(set_log_show, names='value')

        def set_log_level(event: Any) -> None:
            log.setLevel(self.log_level_UI.value)

        self.log_level_UI.observe(set_log_level, names='value')

        super().__init__(
            [HBox([Label(_('status') + ': ',
                         layout=minimize_layout),
                   self.statusUI,
                   self.log_show_UI,
                   self.log_level_UI]),
             self.logUI],
            layout=border_layout)

    def run(self,
            action: str,
            command: Callable,
            kwargs: dict = {},
            on_finished: Optional[Callable] = None,
            on_success: Optional[Callable] = None
            ) -> None:
        self.statusUI.value = action + ": " + _("ongoing")
        exit_status = _("failed")  # in case of unexpected exception
        success = False
        with self.logUI:
            try:
                command(**kwargs)
                success = True
                exit_status = _("finished")
            except (RuntimeError, subprocess.CalledProcessError) as e:
                exit_status = _("failed with error", error=str(e))
            finally:
                if on_finished is not None:
                    on_finished()
                self.statusUI.value = action + ": " + exit_status
            if success and on_success is not None:
                on_success()

    def run_in_subthread(self,
                         action: str,
                         command: Callable,
                         on_finished: Optional[Callable] = None,
                         on_success: Optional[Callable] = None
                         ) -> None:
        Thread(target=lambda: self.run(action=action,
                                       command=command,
                                       on_finished=on_finished,
                                       on_success=on_success)).start()


class AssignmentStudentDashboard(HBox):
    def __init__(self,
                 assignment: Assignment,
                 status_bar: Optional[StatusBar] = None,
                 authentication_widget: Optional[AuthenticationWidget] = None
                 ):
        self.name = assignment.name
        self.assignment = assignment
        if authentication_widget is None:
            authentication_widget = AuthenticationWidget(assignment.forge)
        authentication_widget.on_login(self.update)
        self.authentication_widget = authentication_widget
        if status_bar is None:
            status_bar = StatusBar(authentication_widget=authentication_widget,
                                   log=assignment.log)
        self.status_bar = status_bar

        from ipylab import JupyterFrontEnd  # type: ignore
        self.jupyter_front_end = JupyterFrontEnd()

        layout = Layout(width="initial")
        self.nameUI = HTML(self.name, layout=layout)
        self.fetchUI = Button(
            description=_("fetch"),
            button_style="primary",
            icon="download",
            tooltip=_("fetch assignment", assignment_name=self.name),
            layout=layout,
            disabled=True,
        )
        self.fetchUI.on_click(lambda event: self.fetch())
        self.submitUI = Button(
            description=_("submit"),
            button_style="primary",
            icon="upload",
            tooltip=_("submit assignment", assignment_name=self.name),
            layout=layout,
            disabled=True,
        )
        self.submitUI.on_click(lambda event: self.submit())
        self.work_dir_UI = Button(
            description=_("open"),
            button_style="primary",
            icon="edit",
            tooltip=_("open assignment", assignment_name=self.name),
            layout=layout,
            disabled=True,
        )
        self.work_dir_UI.on_click(self.open_work_dir)
        self.scoreUI = HTML(
            "",
            tooltip=_("browse feedback")
        )

        self.submissionUI = HTML(
            layout=Layout(align_self="center"))

        HBox.__init__(
            self,
            [
                self.nameUI,
                self.fetchUI,
                self.work_dir_UI,
                self.submitUI,
                self.submissionUI,
                self.scoreUI,
            ],
        )
        Thread(target=self.update).start()

    def update(self) -> None:
        # For now, fetching the assignment status requires the user to
        # be logged in. Fails gracefuly if this is not yet the case.
        try:
            status = self.assignment.status()
        except AuthenticationError:
            return
        if status.status == "not released":
            self.nameUI.value = self.name
            self.fetchUI.disabled = True
        else:
            repo = self.assignment.repo()
            self.nameUI.value = (
                f'<a href="{repo.web_url}" target="_blank">{self.name}</a>'
            )
            self.fetchUI.disabled = False

        if status.is_submitted():
            personal_repo = self.assignment.personal_repo()
            assert status.team is not None

            def annotation(username: str) -> str:
                result = ''
                assert status.team is not None
                if len(status.team) == 1:
                    return result
                if username == status.student:
                    result += f' ({_("me")})'
                if username == status.leader_name:
                    result += ' *'
                return result

            self.submissionUI.value = \
                '<div style="line-height: 1.1;">' + \
                '<br>'.join(
                    f'<a href="{status.team[username].web_url}"'
                    f'  target="_blank">{username}</a>'
                    f'{annotation(username)}'
                    for username in sorted(status.team.keys())
                ) + \
                '</div>'
        else:
            self.submissionUI.value = ""

        self.submitUI.tooltip = _("submit assignment", assignment_name=self.name)
        self.submitUI.disabled = True
        self.work_dir_UI.disabled = True
        if self.assignment.assignment_dir is not None and os.path.exists(
                self.assignment.assignment_dir
        ):
            self.work_dir_UI.disabled = False
            if self.assignment.submissions_forked_from_path() is unknown \
               and not status.is_submitted():
                # To be generalized: the current tooltip makes the
                # assumption of a course assignments with student
                # groups
                self.submitUI.tooltip += " (" + _("needs student group") + ")"
            else:
                self.submitUI.disabled = False

        if status.autograde_status == "success":
            # these two s/could be provided by autograde_status
            try:
                badge = personal_repo.fetch_artifact(
                    status.autograde_job,
                    artifact_path="feedback/scores.svg").text
            except requests.HTTPError:
                badge = _("browse")
            assert status.autograde_job is not None
            path_components = self.assignment.personal_repo_path().split('/')
            feedback_url = (
                f"https://{path_components[0]}.{self.assignment.forge.base_url[8:]}-/{'/'.join(path_components[1:])}/-/jobs/{status.autograde_job['id']}/artifacts/feedback/scores.html"
            )
            self.scoreUI.value = f"<a href='{feedback_url}' target='_blank'>{badge}</a>"
        else:
            self.scoreUI.value = ""

        # repo = HTML('<a href="#" class="btn btn-primary btn-lg disabled" role="button" aria-disabled="true">Primary link</a>')
        # need to update repo_path

    def fetch(self) -> None:
        self.fetchUI.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("fetching assignment", assignment_name=self.name),
            command=self.assignment.fetch,
            on_finished=lambda: setattr(self.fetchUI, 'disabled', False),
            on_success=self.update
        )

    def submit(self) -> None:
        self.submitUI.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("submitting assignment", assignment_name=self.name),
            command=self.assignment.submit,
            on_finished=lambda: setattr(self.submitUI, 'disabled', False),
            on_success=self.update
        )

    def open_work_dir(self, event: Any) -> None:
        if self.assignment.assignment_dir is None:
            raise ValueError(_("Can't open work dir: assignment_dir is not set"))
        path = os.path.dirname(self.jupyter_front_end.sessions.current_session['path'])
        # TODO : if README.md does not exist neither, try to open gitlab file browser
        index_files = ["index.md", "index.ipynb", "README.md", "README.ipynb"]
        for x in index_files:
            file = os.path.join(self.assignment.assignment_dir, x)
            if os.path.isfile(file):
                self.jupyter_front_end.commands.execute(
                    "docmanager:open",
                    {
                        "path": path + "/" + file,  # Generalize if there is no index.md
                        "factory": "Notebook",
                        # 'options': {
                        #     'mode': 'split-right'
                        # },
                        "kernelPreference": {
                            "shutdownOnClose": True,
                        },
                    },
                )
                return
        raise FileNotFoundError(_("no index file",
                                  assignment_dir=self.assignment.assignment_dir,
                                  index_files=" ".join(index_files)))


class CourseStudentDashboard(VBox):
    """
    A Jupyter-widget based course dashboard for students

    This class currently assumes that the user is logged in.
    """
    student_group_UI: Dropdown
    assignments: Tuple[str, ...] = ()
    assignment_dashboards: Dict[str, AssignmentStudentDashboard]

    def __init__(self,
                 course: Course,
                 student_group: Optional[str] = None):
        self.course = course

        self.header = HBox(
            [HTML(f'<a href="{course.url}" target="_blank">{course.name}</a>',
                  layout={'flex': '1 0 content'})],
            layout=border_layout)
        if self.course.student_groups is not None:
            self.student_group_UI = Dropdown(
                description=_('student group'),
                value=student_group,
                options=course.student_groups,
            )
            self.header.children += (self.student_group_UI,)
            self.student_group_UI.observe(lambda change: self.update_student_group(),
                                          names='value')
        else:
            self.student_group_UI = Dropdown()

        self.authentication_widget = AuthenticationWidget(
            forge=self.course.forge)

        self.grid = GridBox(
            layout=Layout(
                grid_template_columns='repeat(6, max-content)',
                grid_gap='5px 5px',
                border=border_layout['border']
            )
        )
        self.assignment_dashboards = {}

        self.status_bar = StatusBar(authentication_widget=self.authentication_widget,
                                    log=self.course.log)

        super().__init__([self.authentication_widget,
                          self.header,
                          self.grid,
                          self.status_bar],
                         layout={'width': 'fit-content'},
                         )
        self.update(update_assignment_list=True)
        try:
            self.course.forge.login()
        except AuthenticationError:
            pass

    def update_student_group(self) -> None:
        student_group = self.student_group_UI.value
        for assignment_name in self.assignments:
            assignment_dashboard = self.assignment_dashboards[assignment_name]
            assignment = assignment_dashboard.assignment
            assert isinstance(assignment, CourseAssignment)
            assignment.student_group = student_group
            assignment_dashboard.update()

    def update(self, update_assignment_list: bool = False) -> None:
        student_group = self.student_group_UI.value
        # if student_group is None:
        #    self.center = None
        if update_assignment_list:
            if self.course.assignments is not None:
                assignments = self.course.assignments
            else:
                assignments = self.course.get_released_assignments()
            if tuple(assignments) != self.assignments:
                self.assignments = tuple(assignments)
            else:
                update_assignment_list = False

        for assignment in self.assignments:
            if assignment not in self.assignment_dashboards:
                self.assignment_dashboards[assignment] = AssignmentStudentDashboard(
                    self.course.assignment(
                        assignment, student_group=student_group
                    ),
                    status_bar=self.status_bar,
                    authentication_widget=self.authentication_widget
                )

        if update_assignment_list:
            self.grid.children = [
                Label(label)
                for j, label in enumerate(
                        [_('assignment'),
                         '',
                         _('work directory'),
                         '',
                         _('submission'),
                         _('score'),
                         ])
            ] + [widget
                 for assignment in self.assignments
                 for widget in self.assignment_dashboards[assignment].children]


class AssignmentInstructorDashboard(HBox):
    def __init__(self,
                 course: 'jupyter_course.JupyterCourse',
                 assignment: Assignment,
                 force_autograding: bool,
                 new_score_policy: str,
                 student_group: Optional[Any] = None,
                 release_mode: Optional[Any] = None,
                 status_bar: Optional[StatusBar] = None,
                 authentication_widget: Optional[AuthenticationWidget] = None
                 ):
        self.course = course
        self.student_group = student_group
        self.release_mode = release_mode
        self.force_autograding = force_autograding
        self.new_score_policy = new_score_policy
        # TODO: find better way to recover the assignment name
        self.name = assignment.name
        self.assignment = assignment
        if authentication_widget is None:
            authentication_widget = AuthenticationWidget(assignment.forge)
        self.authentication_widget = authentication_widget
        self.authentication_widget.on_login(self.update)
        if status_bar is None:
            status_bar = StatusBar(authentication_widget=authentication_widget,
                                   log=assignment.log)
        self.status_bar = status_bar

        from ipylab import JupyterFrontEnd  # type: ignore
        self.jupyter_front_end = JupyterFrontEnd()

        layout = Layout(width="initial")
        self.nameUI = Label(self.name)
        self.assignmentUI = HTML()  # layout=layout)
        self.generateButton = Button(
            description="generate",
            button_style="primary",
            icon="cog",
            tooltip=_("generate_assignment assignment", assignment_name=self.name),
            layout=layout,
            disabled=False)
        self.generateButton.on_click(lambda event: self.generate())
        self.generateStatus = Textarea(self.generate_status_cmd(), layout=layout)
        self.generateUI = VBox([self.generateButton, self.generateStatus])

        self.releaseButton = Button(
            description="release",
            button_style="primary",
            icon="angle-double-up",
            tooltip=_("release assignment", assignment_name=self.name),
            layout=layout,
            disabled=False,
        )
        self.releaseButton.on_click(lambda event: self.release(self.release_mode))
        self.releaseStatus = Textarea(self.release_status_cmd(), layout=layout)
        self.releaseUI = VBox([self.releaseButton, self.releaseStatus])

        self.collectButton = Button(
            description="collect",
            button_style="primary",
            icon="angle-double-down",
            tooltip=_("collect assignment", assignment_name=self.name),
            layout=layout,
            disabled=False,
        )
        self.collectButton.on_click(lambda event: self.collect())
        self.collectStatus = Textarea(self.count_submissions_cmd(submitted_directory="submitted"), layout=layout)
        self.collectUI = VBox([self.collectButton, self.collectStatus])

        self.formgraderButton = Button(
            description="formgrader",
            button_style="primary",
            icon="book",
            tooltip=_("formgrader assignment", assignment_name=self.name),
            layout=layout,
            disabled=False,
        )
        self.formgraderButton.on_click(lambda event: self.open_formgrader_cmd(event))
        self.formgraderStatus = Textarea(self.count_submissions_need_manual_grade_cmd(),
                                         layout=layout)
        self.formgraderUI = VBox([self.formgraderButton, self.formgraderStatus])

        self.feedbackButton = Button(
            description="feedback",
            button_style="primary",
            icon="paper-plane",
            tooltip=_("feedback assignment", assignment_name=self.name),
            layout=layout,
            disabled=False,
        )
        self.feedbackButton.on_click(lambda event: self.feedback())
        self.feedbackStatus = Textarea(self.release_feedback_status_cmd(self.student_group), layout=layout)
        self.feedbackUI = VBox([self.feedbackButton, self.feedbackStatus])

        HBox.__init__(
            self,
            [
                self.nameUI,
                self.assignmentUI,
                self.generateUI,
                self.releaseUI,
                self.collectUI,
                self.formgraderUI,
                self.feedbackUI,
            ],
        )
        Thread(target=self.update).start()

    def update(self) -> None:
        self.generateStatus.value = self.generate_status_cmd()
        if self.release_mode is None:
            self.releaseButton.tooltip += "(needs release mode)"
            self.releaseButton.disabled = True
        # For now, fetching the assignment status requires the user to
        # be logged in. Fails gracefuly if this is not yet the case.
        try:
            status = self.assignment.status()
        except AuthenticationError:
            return
        if status.status == "not released":
            self.assignmentUI.value = ""
            self.collectButton.disabled = True
            self.feedbackButton.disabled = True
            self.formgraderButton.disabled = True
        else:
            repo = self.assignment.repo()
            self.assignmentUI.value = (
                f'<a href="{repo.web_url}" target="_blank">{_("browse")}</a>'
            )
            # self.generateButton.disabled = False
            self.releaseStatus.value = self.release_status_cmd()
        if self.student_group is None:
            self.collectButton.disabled = True
            self.feedbackButton.disabled = True
        else:
            self.collectButton.disabled = False
            self.feedbackButton.disabled = False
            self.formgraderButton.disabled = False

        self.collectStatus.value = self.count_submissions_cmd(submitted_directory="submitted")
        self.formgraderStatus.value = self.count_submissions_need_manual_grade_cmd()
        self.feedbackStatus.value = self.release_feedback_status_cmd(self.student_group)

    def generate(self) -> None:
        self.generateButton.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("generating assignment", assignment_name=self.name),
            command=self.course.generate_assignment,
            kwargs={"assignment_name": self.name},
            on_finished=lambda: setattr(self.generateButton, 'disabled', False),
            on_success=lambda: self.update
        )

    def release(self, release_mode: Optional[Any] = None) -> None:
        if release_mode not in ["public", "private"]:
            self.course.log.error("Please set release mode: public or private.")
            return
        self.releaseButton.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("releasing assignment", assignment_name=self.name),
            command=self.course.release,
            kwargs={"assignment_name": self.name, "visibility": release_mode},
            on_finished=lambda: setattr(self.releaseButton, 'disabled', False),
            on_success=lambda: self.update
        )

    def collect(self) -> None:
        self.collectButton.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("collect assignment", assignment_name=self.name),
            command=self.collect_cmd,
            on_finished=lambda: setattr(self.collectButton, 'disabled', False),
            on_success=lambda: self.update
        )

    def formgrader(self) -> None:
        self.status_bar.run(  # run_in_subthread(
            action=_("open formgrader", assignment_name=self.name),
            command=self.open_formgrader_cmd,
            kwargs={},
            on_finished=lambda: setattr(self.formgraderButton, 'disabled', False),
            on_success=lambda: self.update
        )

    def feedback(self) -> None:
        self.feedbackButton.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("feedbacking assignment", assignment_name=self.name),
            command=self.feedback_cmd,
            kwargs={"tag": '*'},
            on_finished=lambda: setattr(self.feedbackButton, 'disabled', False),
            on_success=lambda: self.update
        )

    def collect_cmd(self) -> None:
        if self.student_group is None:
            self.course.log.error("Must choose a student_group value.")
            return
        self.course.collect_for_nbgrader(assignment_name=self.name, student_group=self.student_group)
        self.course.ensure_autograded(assignment_name=self.name, student_group=self.student_group,
                                      force_autograde=self.force_autograding)
        self.course.collect_autograded(assignment_name=self.name, student_group=self.student_group)
        self.course.merge_autograded_db(assignment_name=os.path.basename(self.name), on_inconsistency="WARNING", back=False,
                                        new_score_policy=self.new_score_policy)
        self.course.clear_needs_manual_grade(os.path.basename(self.name))

    def feedback_cmd(self, tag: str = '*') -> None:
        if self.student_group is None:
            self.course.log.error("Must choose a student_group value.")
            return
        self.course.generate_feedback(os.path.basename(self.name), tag=tag,
                                      new_score_policy=self.new_score_policy)
        # self.course.merge_autograded_db(os.path.basename(self.name), back=True, on_inconsistency="WARNING",
        #                                tag=tag, new_score_policy=self.new_score_policy.value)
        self.course.release_feedback(self.name, student_group=self.student_group)

    def open_formgrader_cmd(self, event: Any) -> None:
        try:  # jupyterlab
            from ipylab import JupyterFrontEnd  # type: ignore

            # if self.assignment.assignment_dir is None:
            #    raise ValueError("Can't open work dir if assignment_dir is not set")
            path = os.path.dirname(self.jupyter_front_end.sessions.current_session['path'])
            file = self.course.formgrader(os.path.basename(self.name), in_notebook=False)
            import pdb
            pdb.pm()
            self.jupyter_front_end.commands.execute(
                "docmanager:open",
                {
                    "path": os.path.join(path, file),  # Generalize if there is no index.md
                    "factory": "Notebook",
                    # 'options': {
                    #     'mode': 'split-right'
                    # },
                    "kernelPreference": {
                        "shutdownOnClose": True,
                    },
                },
            )
        except KeyError:  # jupyter notebook
            from IPython.display import display   # type: ignore
            display(self.course.formgrader(os.path.basename(self.name), in_notebook=True))   # type: ignore

    def generate_status_cmd(self) -> str:
        try:
            path = os.path.join(self.course.release_directory, os.path.basename(self.assignment.name))
            date = subprocess.run(['git', 'log', '-1', '--format=%ai'], check=True, text=True, capture_output=True,
                                  cwd=path).stdout
            status = f"last generation: {date}"
        except:
            status = "not generated"
        return status

    def count_submissions_cmd(self, submitted_directory: str = "submitted") -> str:
        status = ""
        number_of_copies = len(glob.glob(f"{submitted_directory}/*/{os.path.basename(self.assignment.name)}",
                                         recursive=True))
        if number_of_copies > 0:
            status += f"#submissions: {number_of_copies}\n"
        return status

    def count_submissions_need_manual_grade_cmd(self) -> str:
        status = ""
        try:
            # Create the connection to the database
            from nbgrader.api import Gradebook, MissingEntry  # type: ignore
            with Gradebook('sqlite:///.gradebook.db') as gb:
                grades = []
                counts = 0
                total = 0
                # Loop over each assignment in the database
                for student in gb.students:
                    # Try to find the submission in the database. If it doesn't exist, the
                    # `MissingEntry` exception will be raised, which means the student
                    # didn't submit anything, so we assign them a score of zero.
                    try:
                        submission = gb.find_submission(os.path.basename(self.assignment.name), student.id)
                    except MissingEntry:
                        pass
                    else:
                        total += 1
                        score = submission.score
                        grades.append(score)
                        if submission.needs_manual_grade:
                            counts += 1
                if len(grades) > 0:
                    status += f"Needs manual grading: {counts}\nGrades: {np.mean(grades):.2f}+/-{np.std(grades):.2f}\n"
                else:
                    status = "No grades"
        except:
            pass
        return status

    def release_status_cmd(self) -> str:
        try:
            p = self.course.forge.get_project(self.assignment.repo_path)
            status = f"last release: {p.visibility}\n{p.last_activity_at}"
        except ResourceNotFoundError:
            status = "not released"
        return status

    def release_feedback_status_cmd(self, student_group: Optional[Any]) -> str:
        try:
            url = self.course.forge.get_project(self.course.assignment(self.assignment.name,
                                                                       student_group=student_group).repo_path).http_url_to_repo
            url = "go to " + url.replace(".git", "/-/forks")
        except ResourceNotFoundError:
            url = "not released"
        return url


class CourseInstructorDashboard(VBox):
    """
    A Jupyter-widget based course dashboard for instructors

    This class currently assumes that the user is logged in.
    """

    def __init__(self,
                 course: 'jupyter_course.JupyterCourse',
                 student_group: Optional[str] = None):
        self.course = course
        self.course.forge.login()

        self.release_mode = RadioButtons(description="", value=None, options=["public", "private"],
                                         layout={'width': 'fit-content'})
        self.force_autograding = RadioButtons(description="", value=False, options=[False, True],
                                              layout={'width': 'fit-content'})
        self.new_score_policy = RadioButtons(description="", value="only_greater",
                                             options=["only_empty", "only_greater", "force_new_score"],
                                             layout={'width': 'fit-content'})

        self.header = HBox(
            [HTML(f'<a href="{course.url}" target="_blank">{course.name}</a>',
                  layout={'flex': 'flex-start'}),
             VBox([Label("release mode"), self.release_mode], width="10px"),
             VBox([Label("collect:\nforce new autograde"), self.force_autograding]),
             VBox([Label("new score policy"), self.new_score_policy])],
            layout=Layout(border='1px solid black', grid_gap='5px 40px'))
        if self.course.student_groups is not None:
            self.student_group_UI = Dropdown(
                description="",
                value=student_group,
                options=course.student_groups,
            )
            self.header.children += (VBox([Label(_('student group')), self.student_group_UI]),)
            self.student_group_UI.observe(lambda change: self.update(),
                                          names='value')
        self.release_mode.observe(lambda change: self.update(),
                                  names='value')
        self.new_score_policy.observe(lambda change: self.update(),
                                      names='value')

        self.authentication_widget = AuthenticationWidget(
            forge=self.course.forge)

        self.grid = GridBox(
            layout=Layout(
                grid_template_columns='repeat(7, max-content)',
                grid_gap='5px 5px',
                border=border_layout['border']
            )
        )

        self.status_bar = StatusBar(authentication_widget=self.authentication_widget,
                                    log=self.course.log)

        super().__init__([self.authentication_widget,
                          self.header,
                          self.grid,
                          self.status_bar],
                         layout={'width': 'fit-content'}
                         )
        self.make_grid()
        try:
            self.course.forge.login()
        except AuthenticationError:
            pass

    def update(self) -> None:
        self.make_grid()
        # Once it will be possible to update on the fly the student group of a course
        # assignment (which means updating the assignment repo and the fork_of_fork field,
        # it will be posible to simply update the assignment dashboards:
        # for assignment_dashboard in self.assignment_dashboards:
        #     Thread(target=assignment_dashboard.update).start()

    def make_grid(self) -> None:
        if self.student_group_UI.value is None:
            self.center = None
        if self.course.assignments is None:
            self.course.assignments = self.course.get_released_assignments()
        self.assignment_dashboards = [
            AssignmentInstructorDashboard(
                self.course,
                self.course.assignment(
                    assignment_name, student_group=self.student_group_UI.value
                ),
                student_group=self.student_group_UI.value,
                release_mode=self.release_mode.value,
                force_autograding=self.force_autograding.value,
                new_score_policy=self.new_score_policy.value,
                status_bar=self.status_bar,
                authentication_widget=self.authentication_widget
            )
            for assignment_name in self.course.assignments
        ]
        self.grid.children = [
                                 Label(label)
                                 for j, label in enumerate(
                                    [_('assignment'),
                                     _('assignment repository'),
                                     'Gestion du cours', '',
                                     'Evaluations', '', '',
                                     ])
                             ] + [widget
                                  for assignment_dashboard in self.assignment_dashboards
                                  for widget in assignment_dashboard.children]


class CourseGradeDashboard(VBox):
    """
    A Jupyter-widget based course dashboard for grade managing.

    This class currently assumes that the user is logged in.
    """

    def __init__(self, course: 'jupyter_course.JupyterCourse') -> None:
        self.course = course
        self.course.forge.login()

        layout = Layout(width="initial")
        self.dashboard_grade_filename = "dashboard-grades.csv"
        if self.course.assignments is None:
            self.course.assignments = self.course.get_released_assignments()
        self.assignments_UI = Dropdown(description="assignments", value=None,
                                       options=["all"] + [a for a in self.course.assignments], width="350px")

        self.get_scores_UI = Button(description="update scores",
                                   button_style="primary",
                                   icon="book",
                                   layout=layout)
        self.get_scores_UI.on_click(lambda event: self.get_scores())

        self.clear_csv_UI = Button(description="clear scores",
                                   button_style="primary",
                                   icon="trash",
                                   layout=layout)
        self.clear_csv_UI.on_click(lambda event: self.clear_csv())

        self.copy_UI = Button(description="copy",
                              button_style="primary",
                              icon="clipboard",
                              layout=layout)
        self.copy_UI.on_click(lambda event: self.copy_dataframe())

        self.header = HBox(
            [self.assignments_UI, self.get_scores_UI, self.clear_csv_UI, self.copy_UI],
            layout=border_layout)
        if self.course.student_groups is not None:
            self.student_group_UI = Dropdown(
                description=_('student group'),
                value=None,
                options=["all"] + list(self.course.student_groups),
            )
            self.header.children = (self.student_group_UI,) + self.header.children

        self.authentication_widget = AuthenticationWidget(
            forge=self.course.forge)
        self.make_grid()
        self.status_bar = StatusBar(authentication_widget=self.authentication_widget,
                                    log=self.course.log)

        super().__init__([self.authentication_widget,
                          self.header,
                          self.grid,
                          self.status_bar],
                         layout={'width': 'fit-content'},
                         )

        try:
            self.course.forge.login()
        except AuthenticationError:
            pass

    def update(self) -> None:
        self.refresh_scores()
        self.grid.data = self.df

    def make_grid(self) -> None:
        from ipydatagrid import DataGrid, TextRenderer, Expr  # type: ignore
        self.df = self.refresh_scores()

        renderers = {}
        for col in self.df.columns:
            if "note" in col and "/0" not in col:
                renderers[col] = TextRenderer(text_color="black", background_color=Expr(_format_note))
            elif "status" in col:
                renderers[col] = TextRenderer(text_color="black", background_color=Expr(_format_status))

        grid_layout = {"height": "300px"}
        self.grid = DataGrid(self.df, base_column_size=200, base_header_size=200, layout=grid_layout, editable=True,
                             renderers=renderers)
        self.grid.auto_fit_params = {"area": "all", "padding": 100}
        self.grid.auto_fit_columns = True

    def refresh_scores(self) -> Any:  # pandas.DataFrame
        if os.path.isfile(self.dashboard_grade_filename):
            df = pd.read_csv(self.dashboard_grade_filename, index_col=0)
        else:
            df = pd.DataFrame()
        col_students = ["group", "email"]
        col_assignments = [col for col in df.columns if "-" in col]
        self.df = df.reindex(col_students + sorted(col_assignments), axis=1)
        return self.df

    def get_scores(self) -> None:
        self.get_scores_UI.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("get scores"),
            command=self.get_scores_cmd,
            on_finished=lambda: setattr(self.get_scores_UI, 'disabled', False),
            on_success=lambda: self.update
        )

    def clear_csv(self) -> None:
        self.clear_csv_UI.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("clear grades"),
            command=self.clear_csv_cmd,
            on_finished=lambda: setattr(self.clear_csv_UI, 'disabled', False),
            on_success=lambda: self.update
        )

    def copy_dataframe(self) -> None:
        self.copy_UI.disabled = True
        self.status_bar.run(  # run_in_subthread(
            action=_("clear grades"),
            command=self.copy_cmd,
            on_finished=lambda: setattr(self.copy_UI, 'disabled', False),
            on_success=None
        )

    def get_scores_cmd(self) -> None:
        """Load all the grades for an assignment and student group.

        Grades are always exported in file dashboard-grades.csv.

        """
        # load the requested assignments
        if self.assignments_UI.value is None or self.assignments_UI.value == "all":
            assignments = [assignment_name for assignment_name in self.assignments_UI.options[1:]]
        else:
            assignments = [self.assignments_UI.value]
        # load the requested groupes
        if self.student_group_UI.value is None or self.student_group_UI.value == "all":
            student_groups = [student_group for student_group in self.student_group_UI.options[1:]]
        else:
            student_groups = [self.student_group_UI.value]

        # load previous scores from dashboard-grades.csv
        d = {}
        if os.path.isfile(self.dashboard_grade_filename):
            df2 = pd.read_csv(self.dashboard_grade_filename, index_col=0)
            d = df2.to_dict("index")

        self.course.forge.login()
        for assignment in assignments:
            total = 0
            total_bad = 0
            for student_group in student_groups:
                # path = course.assignment_repo_path(assignment, student_group)
                try:
                    # project = course.forge.get_project(path)
                    # forks = project.get_forks(recursive=True)
                    submissions_status = self.course.assignment(assignment_name=assignment,
                                                                student_group=student_group).collect_status()
                    # course.log.info(f"Collecting autograded for {len(submissions_status)} students")
                    bad_projects = []
                    if len(submissions_status) == 0:
                        continue
                    for status in submissions_status:
                        student = status.student
                        if student is not None:
                            if student not in d.keys():
                                d[student] = {"group": student_group}
                                # for assignment in assignments:
                            d[student]["email"] = student + "@" + self.course.mail_extension
                            d[student][assignment + "-status"] = "as " + student_group + " with autograding=" + status.autograde_status
                            if status.autograde_status != "success":
                                self.course.log.info(f"missing successful autograde for {student}")
                                bad_projects.append(student)
                                continue
                            self.course.log.info(f"fetching scores for {student}")
                            if status.submission is not None:
                                repo = status.submission.repo
                                job = status.autograde_job
                                path = f"feedback/scores.csv"
                                scores_txt = repo.fetch_artifact(job, artifact_path=path).text
                                scores = pd.read_csv(io.StringIO(scores_txt))
                                total_score = np.sum(scores["total_score"].values)
                                manual_score = np.nansum(scores["manual_score"].values)
                                max_manual_score = np.sum(scores["max_manual_score"].values)
                                if np.all(np.isnan(scores["manual_score"].values)) and ~np.isnan(max_manual_score) and max_manual_score > 0:
                                    d[student][assignment + f"-note (/{int(scores['max_total_score'].values[0])})"] = "attente notation manuelle"
                                else:
                                    d[student][assignment + f"-note (/{int(scores['max_total_score'].values[0])})"] = total_score
                            else:
                                self.course.log.info(f"missing submission for {student}")
                                bad_projects.append(student)
                                continue
                    if len(bad_projects) > 0:
                        self.course.log.warning(f"{len(bad_projects)} dépôt(s) avec autograde_status!=success:")
                        for student in bad_projects:
                            self.course.log.warning(f"student={student}, status={d[student][assignment + '-status']}")
                    total += len(submissions_status)
                    total_bad += len(bad_projects)
                    self.course.log.warning(
                        f"{len(submissions_status)} projets soumis pour {assignment}, groupe {student_group},"
                        f" {len(bad_projects)} dépôt(s) corrompu(s).")
                except ResourceNotFoundError:
                    pass
            self.course.log.info(f"{total} projets soumis pour {assignment}, {total_bad} dépôt(s) corrompu(s).")

        self.df = pd.DataFrame.from_dict(d, orient="index")
        self.df.index.name = "student_id"
        self.df.to_csv(self.dashboard_grade_filename)
        self.df = self.refresh_scores()
        self.update()

    def clear_csv_cmd(self) -> None:
        run(["rm", "-rf", self.dashboard_grade_filename])
        self.update()

    def copy_cmd(self) -> None:
        df2 = self.df.replace("attente notation manuelle", np.nan)
        df2.to_clipboard(excel=True)


def _format_note(cell: Any) -> str:
    return ("yellow" if cell.value == "attente notation manuelle" else "white")


def _format_status(cell: Any) -> str:
    if "autograding=success" in cell.value:
        return "lightgreen"
    elif "autograding=none" in cell.value:
        return "red"
    else:
        return "white"
