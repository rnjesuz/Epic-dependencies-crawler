# Setup
Copy the `.env.example` to a `.env` file<br>
Edit the created `.env` file and set its properties:
* SERVER: the URL where your jira server is hosted
* JIRA_USERNAME: email used to access jira
* API_TOKEN: API token for the provided email. One can be generated in account settings
* EPIC_ISSUE: Every epic is represented as a card. Set this parameter with that card's name

# Requirements
```bash
$ pip install graphviz
$ apt install graphviz
```
```bash
$ pip install python-dotenv
```
```bash
$ pip install jira
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