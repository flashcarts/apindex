#!/usr/bin/env python3

#
# apindex
# Script that, given `tree -Js`, creates a static HTML directory listing
#
# Copyright (C) 2017 Ognjen Galic
# Copyright (C) 2023 lifehackerhansol
# SPDX-License-Identifier: BSD-2-Clause
#

import argparse
import base64
import json
import os
from xml.dom.minidom import parseString


VERSION = "@CPACK_PACKAGE_VERSION_MAJOR@.@CPACK_PACKAGE_VERSION_MINOR@"
PREFIX = "@CMAKE_INSTALL_PREFIX@"


def parseIconsDescription():
    with open(f"{PREFIX}/share/apindex/icons.xml", "r") as f:
        doc = parseString(f.read())
    icons = []
    for icon in doc.getElementsByTagName("icon"):
        i = Icon(icon.getAttribute("file"))
        for ex in icon.getElementsByTagName("ex"):
            i.extensions.append(str(ex.firstChild.nodeValue))
        icons.append(i)
    return icons


def readIconBase64(iconPath):
    with open(iconPath, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("ascii")


class Icon:
    def __init__(self, file):
        self.file = file
        self.extensions = []


class File():
    def __init__(self, file, baseurl, curpath, ignoredextension, output):
        self.file = file
        self.baseurl = baseurl
        self.curpath = curpath.replace("./", "/")
        self.ignoredextension = ignoredextension
        self.output = output

    icons = parseIconsDescription()

    html = f"{PREFIX}/share/apindex/file.template.html"

    def isDirectory(self):
        return self.file["type"] == "directory"

    def getIcon(self):
        if self.getFileName() == "..":
            return readIconBase64(f"{PREFIX}/share/apindex/img/back.png")

        if self.isDirectory():
            return readIconBase64(f"{PREFIX}/share/apindex/img/folder.png")

        for icon in self.icons:
            for ex in icon.extensions:
                if self.getFileName().endswith(ex):
                    return readIconBase64(f"{PREFIX}/share/apindex/img/{icon.file}")

        return readIconBase64(f"{PREFIX}/share/apindex/img/file.png")

    def getFileName(self) -> str:
        return self.file["name"]

    def getPath(self):
        if self.isDirectory() or [True if self.getFileName().endswith(ext) else False for ext in self.ignoredextension]:
            return f"{self.curpath}/{self.getFileName()}"
        else:
            return f"{self.baseurl}/{self.getFileName()}"

    def getSize(self) -> str:
        if self.isDirectory():
            return "-"
        byte_size: int = self.file["size"]
        ret = "0 B"
        if byte_size > (1 << 30):  # GiB
            ret = f"{round(byte_size / (1 << 30), 2)} GiB"
        elif byte_size > (1 << 20):  # MiB
            ret = f"{round(byte_size / (1 << 20), 2)} MiB"
        elif byte_size > (1 << 10):  # KiB
            ret = f"{round(byte_size / (1 << 10), 2)} KiB"
        else:
            ret = f"{byte_size} B"
        return ret

    def genHTMLEntry(self):
        with open(self.html, 'r') as f:
            htmlEntry = f.read()
        htmlEntry = htmlEntry.replace("#FILENAME", self.getFileName())
        htmlEntry = htmlEntry.replace("#FILEPATH", self.getPath())
        htmlEntry = htmlEntry.replace("#SIZE", self.getSize())
        htmlEntry = htmlEntry.replace("#IMAGE", self.getIcon())
        return htmlEntry


class Directory():
    def __init__(self, directory, baseurl, curpath, ignoredextension, output):
        self.directory = directory
        self.baseurl = baseurl
        self.curpath = curpath
        self.ignoredextension = ignoredextension
        self.output = output
        try:
            os.mkdir(output)
        except FileExistsError:
            pass

    html_head = f"{PREFIX}/share/apindex/index.template.html"
    html_foot = f"{PREFIX}/share/apindex/footer.template.html"

    def getDirName(self):
        return self.directory["name"]

    def write(self):
        with open(self.html_head, 'r') as f:
            htmlContent = f.read()

        # initial setup
        htmlContent = htmlContent.replace("#DIR", self.curpath)
        htmlContent = htmlContent.replace("#TITLE", self.curpath)
        htmlContentDir = ""
        htmlContentFile = ""

        # add link to go to previous dir
        back_directory = File({"type": "directory", "name": ".."}, self.baseurl, self.curpath, self.ignoredextension, self.output)
        htmlContentDir += back_directory.genHTMLEntry()

        # check if directory actually has anything to add
        if "contents" in self.directory:
            # loop through files and dirs
            for i in self.directory["contents"]:
                file = File(i, self.baseurl, self.curpath, self.ignoredextension, self.output)
                if file.isDirectory():
                    # spawn new class and write those first
                    subdirectory = Directory(i, f"{self.baseurl}/{i['name']}", f"{self.curpath}/{i['name']}", self.ignoredextension, f"{self.output}/{i['name']}")
                    subdirectory.write()
                    htmlContentDir += file.genHTMLEntry()
                else:
                    htmlContentFile += file.genHTMLEntry()

        htmlContent = htmlContent.replace("#GEN_DIRS", htmlContentDir)
        htmlContent = htmlContent.replace("#GEN_FILES", htmlContentFile)

        with open(self.html_foot, "r") as f:
            htmlContent = htmlContent.replace("#FOOTER", f.read()).replace("#VERSION", VERSION)
        with open(f"{self.output}/index.html", "w") as f:
            f.write(htmlContent)


if __name__ == "__main__":
    description = "apindex - Script that, given `tree -Js`, creates a static HTML directory listing"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("tree",
                        metavar="<output of `tree -Js`>",
                        type=str,
                        nargs=1,
                        help="root directory of files"
                        )
    parser.add_argument("-b",
                        "--baseurl",
                        metavar="http://localhost/",
                        type=str,
                        nargs=1,
                        help="Optional: baseurl, use if file is on another host from dir list"
                        )
    parser.add_argument("--basepath",
                        metavar=".",
                        type=str,
                        nargs=1,
                        help="Optional: basepath, use if you intend to publish apindex-generated html files in a subdirectory"
                        )
    parser.add_argument("--ignoredextension",
                        metavar=".",
                        type=str,
                        nargs=1,
                        help="Optional: ignoreextension, command delimited; use if you want to ship certain files directly from the host site. Useful for images or text files"
                        )
    parser.add_argument("-o",
                        "--out",
                        metavar="site",
                        type=str,
                        nargs=1,
                        help="Output directory (default: 'site')"
                        )

    args = parser.parse_args()

    baseurl = "."
    if args.baseurl:
        baseurl = args.baseurl[0]

    curpath = "."
    if args.basepath:
        curpath = f"/{args.basepath[0]}"

    ignoredextension = []
    if args.ignoredextension:
        ignoredextension = args.ignoredextension[0].rsplit(',')

    output = "site"
    if args.out:
        output = args.out[0]

    with open(args.tree[0], 'r') as f:
        dirtree = json.load(f)

    rootdir = Directory(dirtree[0], baseurl, curpath, ignoredextension, output)
    rootdir.write()
