#!/usr/bin/env python2
import SimpleHTTPServer
import logging
import sys

from flask import Flask, render_template, send_from_directory
from flask.ext.flatpages import FlatPages
from flask.ext.frozen import Freezer, os
from plumbum import local, cli


log = logging.getLogger(__name__)


def route_index():
    # noinspection PyUnresolvedReferences
    return render_template('index.html', pages=pages)


def route_page(path):
    for specialDir in ['js', 'stylesheets']:
        if path.startswith(specialDir):
            return send_from_directory(specialDir, os.path.basename(path))

    # noinspection PyUnresolvedReferences
    return render_template('page.html', page=pages.get_or_404(path))


def route_tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    # noinspection PyUnresolvedReferences
    return render_template('tag.html', pages=tagged, tag=tag)


def make_app(projectPath):
    app = Flask(__name__)
    app.root_path = str(projectPath)
    app.config.update(
        DEBUG=True,
        FLATPAGES_AUTO_RELOAD=True,
        FLATPAGES_EXTENSION='.md',
        FREEZER_RELATIVE_URLS=True)
    app.add_url_rule('/', 'index', route_index)
    app.add_url_rule('/<path:path>/', 'page', route_page)
    app.add_url_rule('/tag/<string:tag>/', 'tag', route_tag)
    return app


def make_pages(app):
    return FlatPages(app)


class ProjectFinder(object):
    TEMPLATES_DIR = 'templates'
    PAGES_DIR = 'pages'
    BUILD_DIR = 'build'

    def __init__(self, startPath):
        self.startPath = startPath

    def find_root_path(self):
        currentPath = self.startPath
        while currentPath != '/':
            log.debug('look at %s', currentPath)
            if self.is_project_root(currentPath):
                log.info('using project at %s', currentPath)
                return currentPath

            currentPath = currentPath.up()

        raise EnvironmentError(
            'project not found upwards %s' % (self.startPath))

    @classmethod
    def is_project_root(cls, currentPath):
        templatesPath = currentPath / cls.TEMPLATES_DIR
        flatPagesPath = currentPath / cls.PAGES_DIR
        return templatesPath.exists() and flatPagesPath.exists()

    @property
    def rootPath(self):
        return self.find_root_path()


class Sibu(cli.Application):
    PORT = 8000
    path = cli.SwitchAttr(['p', 'path'], default=local.cwd)

    def main(self):
        self._init()

    def _init(self):
        global app
        global pages

        pf = ProjectFinder(self.path)
        app = make_app(pf.rootPath)
        pages = make_pages(app)
        self.projectPath = pf.rootPath
        if not self.nested_command:
            self.nested_command = (SibuDev, ['sibu dev'])


@Sibu.subcommand('dev')
class SibuDev(cli.Application):
    def main(self):
        log.info("press '^C' to stop server")
        app.run(port=self.parent.PORT)


@Sibu.subcommand('build')
class SibuBuild(cli.Application):
    def main(self):
        freezer = Freezer(app)
        freezer.freeze()


@Sibu.subcommand('serve-frozen')
class SibuServeFrozen(cli.Application):
    def main(self):
        log.info("press '^C' to stop server")
        freezerDstPath = self.parent.projectPath / ProjectFinder.BUILD_DIR
        with local.cwd(freezerDstPath):
            sys.argv[1] = self.parent.PORT
            log.info("serve frozen flask from %s at http://localhost:%s",
                     freezerDstPath, self.parent.PORT)
            SimpleHTTPServer.test()


def main():
    try:
        logging.basicConfig(level=logging.DEBUG)
        Sibu.run()
    except KeyboardInterrupt:
        log.info('stopped by user')

if __name__ == '__main__':
    main()
