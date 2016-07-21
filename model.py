#!/usr/bin/python

def process_todoist_projects(project_dict):
    output_lines = []
    rows_to_remove = [
        # \xef\xbb\xbf appeared when importing the csv files using the csv module
        ['\xef\xbb\xbfTYPE', 'CONTENT', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE'],
        ['TYPE', 'CONTENT', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE'],
        ['', '', '', '', '', '', '', '', '']
    ]

    for k in project_dict:
        # Remove any all empty or CSV identifier rows
        for i, row in enumerate(project_dict[k]):
            if row in rows_to_remove:
                # Remove the row
                project_dict[k].pop(i)

        # Get the project named without the file extension or Todoist project ID
        project_name = k[:-16] # " [XXXXXXXXX].csv" is 16 characters

        # Process each project and add the resulting Org lines onto the end of
        # output_lines
        output_lines.extend(translate_todoist_project(project_name, project_dict[k]))
        
    return output_lines

def translate_todoist_project(project_name, csv_rows):
    """Translate a Todoist project and return a list of lines to add to the
    output Org file"""
    output_lines = [
        "** %s" % project_name,
        "#+CATEGORY: %s" % project_name,
    ]

    # Collect tasks and their comments for processing
    items = []
    latest_task = -1
    for i, row in enumerate(csv_rows):
        _type, content, _, indent, _, _, _, _, _ = row
        if _type == "task":
            items.append([row, []])
            latest_task += 1
        elif _type == "note":
            items[latest_task][1].append(content)

    for task, notes in items:
        output_lines.extend(translate_project_task(task, notes))

    return output_lines

def translate_project_task(task, notes):
    # The Todoist CSV column identifiers are as below
    # TYPE, CONTENT, PRIORITY, INDENT, AUTHOR, RESPONSIBLE, DATE, DATE_LANG, TIMEZONE
    _type, content, priority, indent, _, _, date, _, _ = task
    assert _type == "task" # Comments should be in the notes list
    result = []

    # Generate the stars using the indent value
    stars = "**"
    for x in range(0, int(indent)):
        stars += "*"
    # Make an equivalent indentation string using spaces for lines like
    # "  SCHEDULED: <2016-07-22 Fri>"
    spaces = stars.replace("*", " ")

    # Deal with priorities
    priority = {
        "1": "[#A] ",
        "2": "[#B] ",
        "3": "[#C] ",
        # Todoist does not display priority 4 tasks as having any priority
        "4": "",
    }[priority]

    # Add lines to the result list
    result.append("%s TODO %s%s" % (stars, priority, content))
    if date != "":
        result.append("%s SCHEDULED: %s" % (spaces, org_timestamp(date)))

    # Text under headings appears to be placed after the lines normally
    # generated by Org mode, such as DEADLINE and SCHEDULED
    # Todoist comments will be placed here
    for note in notes:
        result.append("%s %s" % (spaces, note))

    result.append("") # Add an empty line after each heading's content
    return result

def org_timestamp(todoist_date):
    return todoist_date