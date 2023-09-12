#!/usr/bin/env python3

import sys
import requests

from requests.adapters import HTTPAdapter, Retry

def cli():
    if len(sys.argv) == 1:
        print("Please, provide Todoist API token to proceed. Abort.")
        sys.exit()

    execute(sys.argv[1])

def clean(line):
    return line.replace(" ", "_")

def get_project(project_id, section_id, projects, sections):
    line = ''
    for project in projects:
        if project["id"] == project_id:
            line = project["name"]
            break

    for section in sections:
        if section["id"] == section_id:
            line += ":" + section["name"]
            break

    return clean(line)

def execute(token):
    retry_strategy = Retry(
        total=5,
        backoff_factor=5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    tasks_r = http.get('https://api.todoist.com/rest/v2/tasks',
                         headers={"Authorization": "Bearer " + token})
    tasks_r.raise_for_status()
    tasks = tasks_r.json()

    projects_r = http.get('https://api.todoist.com/rest/v2/projects',
                            headers={"Authorization": "Bearer " + token})
    projects_r.raise_for_status()
    projects = projects_r.json()

    sections_r = http.get('https://api.todoist.com/rest/v2/sections',
                            headers={"Authorization": "Bearer " + token})
    sections_r.raise_for_status()
    sections = sections_r.json()

    for task in tasks:
        line = ""

        # priority
        if task["priority"] > 1:
            line += "(" + {4: "A", 3: "B", 2: "C"}.get(task["priority"]) + ") "

        # creation date
        line += task["created_at"][:10] + " "

        # content
        line += task["content"]

        if task["description"]:
            line += " (" + task["description"] + ")"

        # project
        line += " +" + get_project(task["project_id"], task["section_id"],
                                   projects, sections)

        # context
        if task["labels"]:
            for label in task["labels"]:
                line += " @" + clean(label)

        # additional metadate: due and rec
        if task["due"]:
            line += " due:" + task["due"]["date"]

            if task["due"]["is_recurring"]:
                line += " rec:" + clean(task["due"]["string"])

        # result
        print(line)

if __name__ == "__main__":
    cli()

