# todoist-to-todotxt

Script to save tasks from Todoist to todo.txt format.

It provides support for export of very limited set of Todoist's task fields (only ones that I'm using), particularly:

- Priority
- Creation date
- Task name and description (merged together into one line)
- Project and section ID (merged together)
- Labels
- Due date
- Recurrence date

Definitely NOT supported:

- Things from Pro subscription
- Sub-tasks (all tasks exported in flat list, so there will be no tree-like structure)
- Completed tasks (it is possible to load only active tasks via API)

Above list may be not complete, as there could be features in Todoist I'm not aware of.

## Install

    $ pip install todoist-to-todotxt

## Usage

Generate API token in your Todoist account [Integrations settings](https://todoist.com/app/settings/integrations/developer).

Launch script with you API token (it will print tasks in todo.txt format to stdout):

    $ todoist-to-todotxt <TODOIST-TOKEN>

## Contributing

Feel free to open bug reports and send pull requests.

