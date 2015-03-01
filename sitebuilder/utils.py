import logging


log = logging.getLogger(__name__)


class ProjectFinder(object):
    TEMPLATES_DIR = 'templates'
    PAGES_DIR = 'pages'

    def __init__(self, startPath):
        self.startPath = startPath

    def find_project_root_path(self):
        currentPath = self.startPath
        while currentPath != '/':
            log.debug('look at %s', currentPath)
            if self.is_project_root(currentPath):
                log.info('using project at %s', currentPath)
                return currentPath

            currentPath = currentPath.up()

        raise UtilsError('no project found upwards from %s' % (self.startPath))

    @classmethod
    def is_project_root(cls, currentPath):
        templatesPath = currentPath / cls.TEMPLATES_DIR
        flatPagesPath = currentPath / cls.PAGES_DIR
        return templatesPath.exists() and flatPagesPath.exists()


class UtilsError(Exception):
    pass
