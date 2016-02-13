from flask import Flask, send_file, render_template
from markdown import markdown as md
from random import randint
from jinja2 import Markup
import webbrowser
import os


ALLOWED_IMAGE_EXTENSIONS = ["gif", "jpeg", "jpg", "bmp", "png"]
INDEX_PAGES = ["index.md", "readme.md", "README.md", "Readme.md"]

app = Flask(__name__)


# Initialization functions
# The below 3 function need to be refactored
def build_tree(root_dir='.', depth=4):
    """
    Searches the current folder for directories and files, up to
    n (4 default) levels deep and stores the structure.
    This stricture is used later, when the server is running.
    """
    for dir_name, subdir_list, file_list in os.walk(root_dir):
        dir_contents = get_dir_contents(file_list)
        path_nodes = dir_name.split("/") if dir_name != "." else []
        if path_nodes:
            own_node = path_nodes[-1]
            get_parent(path_nodes)[own_node] = dir_contents
        else:
            app.file_tree = dir_contents


def get_parent(path_nodes):
    current_parent = app.file_tree
    for parent in path_nodes[1:-1]:
        current_parent = current_parent[parent]
    return current_parent


def get_dir_contents(file_list):
    content = {}
    for fname in file_list:
        name_components = fname.split(".")
        extension = name_components[-1] if len(name_components) > 1 else None
        content[fname] = {"extension": extension}
    return content


def run_server(open_browser=True):
    """
    Simply starts the http server that the provide the contents
    of the md files
    """
    port = randint(2000, 65000)
    if open_browser:
        browser = webbrowser.get()
        browser.open("http://localhost:{}".format(port))
    app.run(port=port, use_reloader=False, debug=True)


# Helpers
def get_index_file(obj):
    for name in INDEX_PAGES:
        if obj.get(name, ""):
            return name
    return ""


def get_html_version(file_path):
    with open("./{}".format(file_path)) as f:
        html = Markup(md(f.read(), extensions=['gfm']))
    return html


# Flask Routes, executed per request
@app.route("/")
def index():
    """ Servers the page the the wieframes / iframes"""
    indexpage = get_index_file(app.file_tree)
    return render_template("index.html", indexpage=indexpage)


@app.route("/<path:file_path>")
def show(file_path):
    """ Servers the html version of the files if they exist"""
    path_elements = file_path.split("/")
    node = app.file_tree
    for elem in path_elements:
        node = node.get(elem, {})
    if node:
        if node.get("extension", "") in ALLOWED_IMAGE_EXTENSIONS:
            return send_file(file_path,
                             mimetype='image/{}'.format(node["extension"]))
        # Still need to add the case where it is not an allowed file type
        else:
            if node.get("extension", "") == "md":
                content = get_html_version(file_path)
            else:
                ifile = get_index_file(node)
                content = get_html_version("{}/{}".format(file_path, ifile))

            return render_template("document.html",
                                   content=content,
                                   file_path=file_path)
    else:
        return "Not Found"


# Entry points
def execute():
    """Function to be called from the commandline"""
    build_tree()
    run_server()


if __name__ == '__main__':
    # Used for easily running in development
    execute()
