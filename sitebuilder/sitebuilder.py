#!/usr/bin/env python2
import logging
import sys

from flask import Flask, render_template, send_from_directory
from flask.ext.flatpages import FlatPages
from flask.ext.frozen import Freezer, os
from plumbum import local


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def find_project_assets():
    projectPath = local.cwd
    while projectPath != '/':
        log.debug('look at %s', projectPath)
        templatesPath = projectPath / 'templates'
        flatPagesPath = projectPath / 'pages'
        if templatesPath.exists() and flatPagesPath.exists():
            log.info('using project at %s', projectPath)
            return projectPath

        projectPath = projectPath.up()

    raise Exception('no project found')

projectPath = find_project_assets()

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
APPLICATION_ROOT = str(projectPath)
app = Flask(__name__)
app.root_path = str(projectPath)
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


def export_build():
    # from distutils.dir_util import copy_tree
    # compare build dir to export dir
    # git rm all removed pages
    # git add all new pages
    # ignore .git and all in .gitignore
    # copy_tree('_build', '../obestwalter.github.io')
    pass


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer = Freezer(app)
        freezer.freeze()
        export_build()
    else:
        log.info("press '^C' to stop server")
        app.run(port=8000)


if __name__ == '__main__':
    main()
