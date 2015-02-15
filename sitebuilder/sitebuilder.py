#!/usr/bin/env python2
import logging
import sys

from flask import Flask, render_template
from flask.ext.flatpages import FlatPages
from flask.ext.frozen import Freezer
from plumbum import LocalPath, local


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'pages'
FREEZER_DESTINATION = '_build'


def make_app_and_pages():
    global FLATPAGES_ROOT
    templatesPath, flatPagesPath = find_project_assets()
    app = Flask(__name__, template_folder=str(templatesPath))
    FLATPAGES_ROOT = str(flatPagesPath)
    app.config.from_object(__name__)
    pages = FlatPages(app)
    return app, pages


def find_project_assets():
    projectPath = local.cwd
    while True:
        templatesPath = projectPath / 'templates'
        flatPagesPath = projectPath / 'pages'
        if templatesPath.exists() and flatPagesPath.exists():
            log.info('using project at %s', projectPath)
            return templatesPath, flatPagesPath

        projectPath = projectPath.up()

    raise Exception('no project found')


app, pages = make_app_and_pages()


@app.route('/')
def index():
    return render_template('index.html', pages=pages)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)


@app.route('/<path:path>/')
def page(path):
    return render_template('page.html', page=pages.get_or_404(path))


def export_build():
    # from distutils.dir_util import copy_tree
    # compare build dir to export dir
    # git rm all removed pages
    # git add all new pages
    # ignore .git and all in .gitignore
    # copy_tree(FREEZER_DESTINATION, '../obestwalter.github.io')
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
