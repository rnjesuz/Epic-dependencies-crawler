import os
import platform
import subprocess
import sys
from pathlib import Path

import graphviz
from PyQt5.QtCore import QObject, QThread, QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QWidget, QFormLayout
from dotenv import load_dotenv, set_key
from jira import JIRA

global server
global jira_username
global jira_api_token
global provided_epic_issue
global jira
epics = {}
digraph = graphviz.Digraph(filename='epic_dependencies_graph', format='png')

env_file = Path('.env')
env_file.touch(exist_ok=True)


class Issue:
    def __init__(self, status, name, epic_issue):
        self.status = status
        self.name = name
        self.epic_issue = epic_issue


class Epic:
    def __init__(self, epic_issue, epic_title):
        self.epic_issue = epic_issue
        self.epic_title = epic_title


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.worker = Worker()
        self.thread = QThread()
        self.setMinimumSize(QSize(330, 200))
        self.setWindowTitle("Jira Dependencies Crawler")

        self._init_ui()

    def _init_ui(self):

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QFormLayout(self.central_widget)

        self.serverLabel = QLabel(self)
        self.serverLabel.setText('Server URL:')
        self.serverLine = QLineEdit(self)
        self.serverLine.setText(server)

        self.usernameLabel = QLabel(self)
        self.usernameLabel.setText('Email:')
        self.usernameLine = QLineEdit(self)
        self.usernameLine.setText(jira_username)

        self.tokenLabel = QLabel(self)
        self.tokenLabel.setText('API Token:')
        self.tokenLine = QLineEdit(self)
        self.tokenLine.setEchoMode(QLineEdit.Password)
        self.tokenLine.setText(jira_api_token)

        self.epicLabel = QLabel(self)
        self.epicLabel.setText('Epic\'s issue:')
        self.epicLine = QLineEdit(self)
        self.epicLine.setText(provided_epic_issue)

        self.button = QPushButton('Start', self)
        self.button.clicked.connect(self.start_processing)

        self.layout.addRow(self.serverLabel)
        self.layout.addRow(self.serverLine)
        self.layout.addRow(self.usernameLabel)
        self.layout.addRow(self.usernameLine)
        self.layout.addRow(self.tokenLabel)
        self.layout.addRow(self.tokenLine)
        self.layout.addRow(self.epicLabel)
        self.layout.addRow(self.epicLine)
        self.layout.addRow("   ", None)
        self.layout.addRow(self.button)

    def server_value(self):
        return self.serverLine.text()

    def username_value(self):
        return self.usernameLine.text()

    def token_value(self):
        return self.tokenLine.text()

    def epic_value(self):
        return self.epicLine.text()

    def disable_button(self):
        self.button.setEnabled(False)
        self.button.setStyleSheet("background-color: grey")
        self.button.setText('Processing')

    def enable_button(self):
        self.button.setEnabled(True)
        self.button.setStyleSheet("background-color: white")
        self.button.setText('Start')

    def start_processing(self):
        global server
        server = self.server_value()
        set_key('.env', "SERVER", server)
        global jira_username
        jira_username = self.username_value()
        set_key('.env', "JIRA_USERNAME", jira_username)
        global jira_api_token
        jira_api_token = self.token_value()
        set_key('.env', "API_TOKEN", jira_api_token)
        global provided_epic_issue
        provided_epic_issue = self.epic_value()
        set_key('.env', "EPIC_ISSUE", provided_epic_issue)

        self.disable_button()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.thread.finished.connect(
            # lambda: self.enable_button()
            lambda: exit(0)
        )


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        build_dependencies()
        self.finished.emit()


def main():
    load_dotenv()
    global server
    server = os.getenv('SERVER')
    global jira_username
    jira_username = os.getenv('JIRA_USERNAME')
    global jira_api_token
    jira_api_token = os.getenv('API_TOKEN')
    global provided_epic_issue
    provided_epic_issue = os.getenv('EPIC_ISSUE')

    app = QApplication(sys.argv)
    window = Window()

    window.show()
    sys.exit(app.exec())


def build_dependencies():
    global jira
    jira = JIRA(server=server, basic_auth=(jira_username, jira_api_token))
    issues_in_epic = jira.search_issues("'Epic Link' = " + provided_epic_issue)
    epic_title = get_epic_title_from_epic_issue(provided_epic_issue)

    digraph.attr(label=epic_title)
    digraph.attr(labelloc='t')

    epic_dependencies = {}
    for issue_in_epic in issues_in_epic:
        issue = \
            Issue(
                issue_in_epic.fields.status.name,
                issue_in_epic.key,
                get_epic_issue_from_issue(issue_in_epic)
            )

        epic_dependencies[issue] = []
        blocked_issues = jira.search_issues("issueIsBlockedBy = " + issue_in_epic.key)
        for blocked_issue in blocked_issues:
            epic_dependencies[issue].append(
                Issue(
                    blocked_issue.fields.status.name,
                    blocked_issue.key,
                    get_epic_issue_from_issue(blocked_issue)))

    build_epics(epic_title, epic_dependencies)
    write_dependencies(digraph, epic_dependencies, provided_epic_issue)

    digraph.unflatten()
    digraph.render()

    open_image()


def open_image():
    filename = 'epic_dependencies_graph.png'
    if platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', filename], check=True)
    elif platform.system() == 'Windows':  # Windows
        os.startfile(filename)
    else:  # linux variants
        subprocess.run(['xdg-open', filename], check=True)


def get_epic_title_from_epic_issue(epic_issue):
    return jira.issue(epic_issue, fields='summary').fields.summary


def get_epic_issue_from_issue(issue):
    return issue.fields.parent.key


def build_epics(provided_epic_title, dependencies):
    epics[provided_epic_issue] = Epic(provided_epic_issue, provided_epic_title)
    for values in dependencies.values():
        for dependency in values:
            if dependency.epic_issue != provided_epic_issue and dependency.epic_issue not in epics:
                epics[dependency.epic_issue] =\
                    Epic(dependency.epic_issue, get_epic_title_from_epic_issue(dependency.epic_issue))


def write_dependencies(graph, epic_dependencies, epic_name):
    for node in epic_dependencies:
        graph.node(node.name, style='filled', fillcolor=color_switch(node.status))
        for dependency in epic_dependencies[node]:
            graph.edge(node.name, dependency.name)
            if dependency.epic_issue != epic_name:
                with graph.subgraph(name='cluster_' + dependency.epic_issue) as cluster:
                    cluster.attr(label=epics[dependency.epic_issue].epic_title)
                    cluster.node(dependency.name)


def color_switch(status):
    switcher = {
        'In Progress': 'yellow',
        'Code Review': 'yellow',
        'Master': 'green',
        'In CI': 'green',
        'In QA': 'green',
        'Testing': 'green',
        'Ready To Go': 'green',
        'Finished': 'green',
    }
    return switcher.get(status, 'white')


if __name__ == '__main__':
    exit(main())
