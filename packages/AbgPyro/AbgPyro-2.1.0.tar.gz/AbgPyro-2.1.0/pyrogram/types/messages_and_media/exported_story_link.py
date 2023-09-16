#  Pyrogram - Telegram MTProto API Client Library for Python
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from pyrogram import raw

from ..object import Object


class ExportedStoryLink(Object):
    """Contains information about a story viewers.


    Parameters:
        link (``str``):
            The link of the story.
    """

    def __init__(self, *, link: str):
        super().__init__()

        self.link = link

    @staticmethod
    def _parse(exportedstorylink: "raw.types.ExportedStoryLink") -> "ExportedStoryLink":
        return ExportedStoryLink(link=getattr(exportedstorylink, "link", None))
