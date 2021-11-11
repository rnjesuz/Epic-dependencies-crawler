import os
from dotenv import load_dotenv
from jira import JIRA
import graphviz


load_dotenv()
server = os.getenv('SERVER')
jira_username = os.getenv('JIRA_USERNAME')
jira_api_token = os.getenv('API_TOKEN')
provided_epic_issue = os.getenv('EPIC_ISSUE')

jira = JIRA(server=server, basic_auth=(jira_username, jira_api_token))
epics = {}
digraph = graphviz.Digraph(filename='epic_dependencies_graph', format='png')


class Issue:
    def __init__(self, status, name, epic_issue):
        self.status = status
        self.name = name
        self.epic_issue = epic_issue


class Epic:
    def __init__(self, epic_issue, epic_title):
        self.epic_issue = epic_issue
        self.epic_title = epic_title


def main():
    issues_in_epic = jira.search_issues("'Epic Link' = " + provided_epic_issue)

    epic_title = get_epic_title_from_epic_issue(provided_epic_issue)

    digraph.attr(label=epic_title)
    digraph.attr(labelloc='t')

    epic_dependencies = {}
    for issue_in_epic in issues_in_epic:
        issue = Issue(issue_in_epic.fields.status.name, issue_in_epic.key, get_epic_issue_from_issue(issue_in_epic))

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


def get_epic_title_from_epic_issue(epic_issue):
    return jira.issue(epic_issue, fields='customfield_10011').fields.customfield_10011


def get_epic_issue_from_issue(issue):
    return issue.fields.customfield_10014


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
