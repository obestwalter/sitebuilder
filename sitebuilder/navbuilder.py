import logging
import os
from operator import attrgetter
from plumbum import LocalPath


log = logging.getLogger(__name__)


def obj_attr(obj, filterSpecialMethods=True):
    msg = "repr: %s\n" % (repr(obj))
    attrs = [a for a in dir(obj)]
    if filterSpecialMethods:
        attrs = [a for a in attrs if not a.startswith("__")]
    for attr in attrs:
        try:
            value = getattr(obj, attr)
        except Exception as e:
            value = "[EXC] %s" % (e.message)
        msg += "%s=%s\n" % (attr, value)
    return msg


class Node(object):
    TEMPLATES_PATH = str(LocalPath(__file__).up() / "templates")
    ROOT_NAME = "/"
    NODE_PAGE_NAME = "main"
    PAGE_EXT = ".html"
    NODE_PAGE_FILENAME = "%s%s" % (NODE_PAGE_NAME, PAGE_EXT)
    ATTRS_SEP = ";"
    ATTR_VAL_SEP = ":"
    ATTRS = ["weight", "displayName"]

    def __init__(self, path=''):
        self.children = []
        if os.path.isabs(path):
            absPath = path
        else:
            absPath = os.path.join(self.TEMPLATES_PATH, path)
        if absPath.endswith(self.PAGE_EXT):
            self.absPath = absPath
            self.isLeaf = True
        else:
            testPath = absPath + self.PAGE_EXT
            if os.path.exists(testPath):
                self.absPath = testPath
                self.isLeaf = True
            else:
                self.absPath = os.path.join(absPath, self.NODE_PAGE_FILENAME)
                self.isLeaf = False

        templatePath = self.absPath.split(self.TEMPLATES_PATH)[1][1:]
        relPathNoExt = templatePath[:-len(self.PAGE_EXT)]
        if relPathNoExt == self.NODE_PAGE_NAME:
            self.name = self.ROOT_NAME
            self.linkRelUri = "/"
        else:
            self.name = relPathNoExt
            if self.name.endswith(self.NODE_PAGE_NAME):
                self.linkRelUri = "/" + self.name.rpartition("/")[0]
            else:
                self.linkRelUri = "/" + self.name

        if hasattr(self, "displayName") and self.displayName:
            self.linkLabel = self.displayName
        else:
            if self.isLeaf:
                label = self.name.split("/")[-1]
            else:
                label = self.name.split("/")[-2]
            elems = label.replace("_", " ").split(" ")
            self.linkLabel = " ".join([e.capitalize() for e in elems])

    def __str__(self):
        return "%s %s (%s) " % ("NODE" if self.children else "LEAF",
                                self.name,
                                [c.name for c in self.children])

    def __getattr__(self, attr):
        if attr not in self.ATTRS:
            raise AttributeError(
                "%s has no attribute %s" % (self.__class__.__name__, attr))

        return self.infoMap.get(attr)

    def add_child(self, node):
        self.children.append(node)
        self.children.sort(key=attrgetter("weight"))

    @property
    def isRoot(self):
        return self.name == self.ROOT_NAME

    @property
    def infoMap(self):
        if not hasattr(self, "_infoMap"):
            self._infoMap = {}
            if not self.metaInfo:
                return self._infoMap

            items = [i.strip() for i in self.metaInfo.split(self.ATTRS_SEP)]
            for item in items:
                k, v = item.split(self.ATTR_VAL_SEP)
                value = v.strip().decode("utf-8")
                self._infoMap[k] = int(value) if value.isdigit() else value

        return self._infoMap

    @property
    def metaInfo(self):
        if not hasattr(self, "_metaInfo"):
            self._metaInfo = ""
        with open(self.absPath) as f:
            firstLine = f.readline().strip()
        if firstLine.startswith("<!--"):
            self._metaInfo = firstLine[4:-4].strip()

        return self._metaInfo


class Navigator(object):
    def __init__(self, contentRoot=Node.TEMPLATES_PATH,
                 excludeDirs=None, excludeFiles=None):
        self.contentRoot = contentRoot
        self.excludeDirs = excludeDirs or ["old"]
        self.excludeFiles = excludeFiles or ["base%s" % (Node.PAGE_EXT)]
        self.excludes = self.excludeDirs + self.excludeFiles

    def __str__(self):
        return obj_attr(self)

    @property
    def rootNode(self):
        if not hasattr(self, "_rootNode"):
            self._rootNode = self.build_tree(self.contentRoot)
        return self._rootNode

    def traverse_nodes(self, node, func=None):
        self.depth = 0 if node.isRoot else self.depth + 1
        func = func or (lambda node, depth: "%s%s\n" % ("  " * depth, node))
        out = func(node, self.depth)
        for thisNode in node.children:
            out += self.traverse_nodes(thisNode, func)
        self.depth -= 1
        return out

    def build_nav(self, node, depth=None):
        indent = lambda: "  " * self.depth
        self.depth = depth if depth is not None else self.depth
        out = ""
        nodeWrap = ('<ul class="nav nav-list">', '</ul>')
        leafWrap = ('<li><a href="%s">%s</a>', '</li>')
        out += indent() + nodeWrap[0] + '\n'
        self.depth += 1
        out += (indent() +
                leafWrap[0] % (node.linkRelUri, node.linkLabel) + '\n')
        for thisNode in node.children:
            out += self.build_nav(thisNode)
        self.depth -= 1
        out += indent() + nodeWrap[1] + '\n'
        return out

    def build_tree(self, path):
        curNode = Node(path)
        for item in os.listdir(path):
            if item in self.excludes:
                log.debug("[IGNORE] %s in %s", item, path)
                continue

            curPath = os.path.join(path, item)
            if os.path.isdir(curPath):
                log.debug("add %s as NODE", curPath)
                curNode.add_child(self.build_tree(curPath))
            else:
                if Node.NODE_PAGE_NAME in item:
                    log.debug("[IGNORE MAIN] %s in %s" % (item, path))
                    continue

                log.debug("add %s as LEAF", curPath)
                curNode.add_child(Node(curPath))
        return curNode


def make_nav(pathToTemplates, activePage):
    # todo different handling for activePage
    navigator = Navigator(pathToTemplates)
    rootNode = navigator.rootNode
    return navigator.build_nav(rootNode, depth=0)


# ################################# TESTS #####################################


def navigator_test():
    logging.basicConfig(level=logging.DEBUG)

    def textualize(node, depth):
        return (
            "%sname: '%s', weight: '%s', displayName: '%s'\n" %
            ("  " * depth, node.name, node.weight, node.displayName))

    navigator = Navigator()
    rootNode = navigator.rootNode
    log.debug(navigator.traverse_nodes(rootNode, textualize))


if __name__ == "__main__":
    navigator_test()
