# Quick Start

Install Python 3\
<https://www.python.org/downloads/>

Install Pip\
<https://pip.pypa.io/en/stable/installation/#get-pip-py>

Install requirements
```bash
$ pip install .
```

Run the program
```bash
$ python3 epic_dependencies_crawler.py 
```

# Environment Variables
Automatically created (and updated) by the program.

For manual setup:<br>
* Copy the `.env.example` to a `.env` file<br>
* Edit the created `.env` file and set its properties

SERVER: the URL where your jira server is hosted<br>
JIRA_USERNAME: email used to access jira<br>
API_TOKEN: API token for the provided email. One can be generated in account settings<br>
EPIC_ISSUE: Every epic is represented as a card. Set this parameter with that card's name<br>

# Requirements
python 3.6.0<br>
jira 3.0.1<br>
python-dotenv 0.19.2<br>
graphviz 0.18<br>
setuptools 58.2.0<br>
PyQt5 5.15.6

To install run this in the project's root folder. Pip will execute `setup.py` and install defined dependencies. 
```bash
$ pip install .
```

# Execution
```bash
$ python3 epic_dependencies_crawler.py 
```

# Output
2 Files in the script's folder:
* epic_dependencies_graph: DOT representation of the graph
* epic_dependencies_graph.png: Image generated from the epic_dependencies_graph file

The DOT file can be manually edited. The image can be regenerated using:
```bash
$ dot -T<format> epic_dependencies_graph > <new_file>.<format>
```
Example
```bash
$ dot -Tpng epic_dependencies_graph > teste.png
```