#  Copyright (C) 2016 - Yevgen Muntyan
#  Copyright (C) 2016 - Ignacio Casal Quinteiro
#  Copyright (C) 2016 - Arnavion
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.

from gvsbuild.utils.base_builders import CmakeProject
from gvsbuild.utils.base_expanders import Tarball
from gvsbuild.utils.base_project import Project, project_add


@project_add
class Nghttp2(Tarball, CmakeProject):
    def __init__(self):
        Project.__init__(
            self,
            "nghttp2",
            version="1.56.0",
            archive_url="https://github.com/nghttp2/nghttp2/releases/download/v{version}/nghttp2-{version}.tar.xz",
            hash="65eee8021e9d3620589a4a4e91ce9983d802b5229f78f3313770e13f4d2720e9",
            dependencies=[
                "cmake",
                "zlib",
                "ninja",
            ],
            patches=["0001-Define-ssize_t-if-not-defined.patch"],
        )

    def build(self):
        CmakeProject.build(self, use_ninja=True)

        self.install(r".\COPYING share\doc\nghttp2")
