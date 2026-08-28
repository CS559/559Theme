# get the list of assignments as a YAML file
# this used to be in each course file
import canvas
import dateutil.parser
import datetime
import yaml
import csv
import pandas as pd
import os
from utils import isoparse

# generally useful
def slugify(title):
    return title.replace("–","-").replace(" - ","-").replace("?","").replace(" ","-").lower()

def getAssignmentDetails(c:canvas.Canvas, fname="assignments.csv"):
    assigns = []
    for a in c.creq("assignments"):
        print(a["name"])
        slug = slugify(a["name"].split(":")[0].lstrip().rstrip())
        due = datetime.datetime(2024,1,1)
        if a["due_at"]:
           due = isoparse(a["due_at"])
        else:
            print("Warning {} has no due date!".format(slug))
        lock = datetime.datetime(2024,1,1)
        if a["lock_at"]:
            lock = isoparse(a["lock_at"])
        else:
            print("Warning {} has no lock date!".format(slug))

        cols = ["name", "open", "due", "lock", "group", "type", "points", "allow_liking", "response_needed", "anon"]

        if "quiz_id" in a:
            record = {
                "name" : a["name"],
                "open": a["unlock_at"],
                "due" : "{}".format(due),
                "lock": "{}".format(lock),
                "group": a["assignment_group_id"],
                "type": "quiz",
                "points": a["points_possible"],
                "allow_liking": None,
                "response_needed": None,
                "anon": a["anonymize_students"]
            }
        elif "discussion_topic" in a: 
            record = {
                "name" : a["name"],
                "open": a["unlock_at"],
                "due" : "{}".format(due),
                "lock": "{}".format(lock),
                "group": a["assignment_group_id"],
                "type": "discussion",
                "points": a["points_possible"],
                "allow_liking": a["discussion_topic"]["allow_rating"],
                "response_needed": a["discussion_topic"]["require_initial_post"],
                "anon": None
            }
        else:
            record = {
                "name" : a["name"],
                "open": a["unlock_at"],
                "due" : "{}".format(due),
                "lock": "{}".format(lock),
                "group": a["assignment_group_id"],
                "type": "other",
                "points": a["points_possible"],
                "allow_liking": None,
                "response_needed": None,
                "anon": None
            } 

        assigns.append(record)
    with open(fname,"w",newline='') as fo:
        writer = csv.writer(fo)
        writer.writerow(cols)
        for r in assigns:
            writer.writerow([r[c] for c in cols])

def makeAssignmentsYAML(c:canvas.Canvas, fname="assigns.yaml"):
    """
    :param fname:
    :return:
    """
    assigns = {}
    for a in c.creq("assignments"):
        slug = slugify(a["name"].split(":")[0].lstrip().rstrip())
        due = datetime.datetime(2024,1,1)
        if a["due_at"]:
            due = isoparse(a["due_at"])
            # print("a[due_at] = ",a["due_at"])
            # print("      due = ",due)
        else:
            print("Warning {} has no due date!".format(slug))
        lock = due
        if a["lock_at"]:
            lock = isoparse(a["lock_at"])
        else:
            print("Warning {} has no lock date!".format(slug))
        record = {
            "name" : a["name"],
            "shortname": a["name"].split(":")[0],
            "url" : a["html_url"],
            "due" : "{}".format(due),   # for some reason, YAML doesn't convert?
            "due_string" : "{:%a, %b %d}".format(due),  ## original had #b #d
            "lock": "{}".format(lock),
            "lock_string": "{:%a, %b %d}".format(lock)
        }
        assigns[slug] = record
    with open(fname,"w") as fo:
        fo.write(yaml.dump(assigns))
        # toml.dump(assigns,fo)
        print("Wrote Assignments YAML file {}".format(fname))

def getStudentSubmissionData(c:canvas.Canvas, fname="people.csv"):
    students = []
    cols = ["name", "email", "ID"]

    for a in c.creq("assignments"):
        cols.append(a["name"])

    with open(fname,"w",newline='') as fo:
        print(students)
        #fo.write(yaml.dump(assigns))
        writer = csv.writer(fo)
        writer.writerow(cols)
        for r in students:
            writer.writerow([r[c] for c in cols])
        # toml.dump(assigns,fo)



if __name__ == "__main__":
    c = canvas.Canvas()
    makeAssignmentsYAML(c)