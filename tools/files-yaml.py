# get the list of files in Canvas as a YAML file
# a lot is hard coded...
# this is taken from the old CourseTools canvas.py
import canvas
from utils import isoparse
import yaml
import datetime
import dateutil
def getFilesYAML(c : canvas.Canvas, fname="files.yaml",
                 ignoreFolders=["LectureNotes-2021"]):
    # get the folders ahead of time...
    folders = c.creq("folders")
    folderDict = {f["id"]:f for f in folders}

    files = {}
    for f in c.creq("files"):
        name = f["filename"]
        folder = ""
        if f["folder_id"] in folderDict:
            folder = folderDict[f["folder_id"]]
        if not(folder["name"] in ignoreFolders):
            if name in files:
                print("WARNING: {} appears twice!".format(name))
                print("   folder was:",files[name]["folder_path"])
                print("   folder will be:",folderDict[f["folder_id"]]["full_name"])
            files[name] = {
                "url" : f["url"],
                "url_nodl" : f["url"].split("download?")[0],
                "filename" : name,
                "size" : f["size"],
                "size_str": "{:.1f}mb".format(f["size"]/1000000.0),
                "updated" : isoparse(f["updated_at"])
            }
            if folder:
                files[name]["folder"] = folder["name"]
                files[name]["folder_path"] = folder["full_name"]
            else:
                files[name]["folder"] = "/"
                files[name]["folder_path"] = "/"

    with open(fname, "w") as fo:
        fo.write("# Fetched from Canvas {}\n".format(datetime.datetime.now().strftime("%b %d, %Y - %I:%M%p")))
        fo.write(yaml.dump(files))

if __name__ == "__main__":
    c = canvas.Canvas()
    getFilesYAML(c)