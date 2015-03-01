#!/usr/bin/env python2
import logging
import sys

from flask import Flask, render_template, send_from_directory
from flask.ext.flatpages import FlatPages
from flask.ext.frozen import Freezer, os
from plumbum import local

from utils import ProjectFinder, UtilsError


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
try:
    PROJECT_PATH = ProjectFinder(local.cwd).find_project_root_path()
except UtilsError as e:
    print "Error: %s" % (e.message)
    sys.exit(1)

# APPLICATION_ROOT = str(PROJECT_PATH)
app = Flask(__name__)
app.root_path = str(PROJECT_PATH)
app.config.from_object(__name__)
pages = FlatPages(app)


@app.route('/')
def index():
    return render_template('index.html', pages=pages)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


@app.route('/<path:path>/')
def page(path):
    for specialDir in ['js', 'stylesheets']:
        if path.startswith(specialDir):
            return send_from_directory(specialDir, os.path.basename(path))

    return render_template('page.html', page=pages.get_or_404(path))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer = Freezer(app)
        freezer.freeze()
    else:
        if not ProjectFinder.is_project_root(local.cwd):
            log.error('%s is not a sitebuilder project', local.cwd)
            return 1

        log.info("press '^C' to stop server")
        app.run(port=8000)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print "Error: %s" % (e.message)

    sys.exit(1)
