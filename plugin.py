###
# Copyright (c) 2012, J-P Nurmi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.conf as conf

import glob
import fuzzydict
from pysqlite2 import dbapi2 as sqlite3

class QtAssistant(callbacks.Plugin):
    """Add the help for "@plugin help QtAssistant" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(QtAssistant, self)
        self.__parent.__init__(irc)
        self.dict = fuzzydict.FuzzyDict()

        datadir = conf.supybot.directories.data
        for qchfile in glob.glob(datadir.dirize("*.qch")):
            self.dict.update(self._index(qchfile))

    def _index(self, file):
        dict = fuzzydict.FuzzyDict()
        db = sqlite3.connect(file)
        cursor = db.cursor()
        # IndexTable: Id, Name, Identifier, NamespaceId, FileId, Anchor
        # FileNameTable: FolderId, Name, FileId, Title
        # FolderTable: Id, Name, NamespaceId
        cursor.execute('SELECT * FROM IndexTable, FileNameTable, FolderTable '
                       'WHERE IndexTable.FileId = FileNameTable.FileId')
        rows = cursor.fetchall()
        for row in rows:
            # (200, u'XQuery', u'XQuery', 1, 61, None, 1, u'xmlprocessing.html', 61, u'qtxmlpatterns : XQuery')
            print(row)
#            entry = {}
#            entry['name'] = row[1]
#            entry['id'] = row[2]
#            entry['anchor'] = row[5]
#            entry['file'] = row[7]
#            entry['title'] = row[9]
#            dict[entry['name']] = entry
#            dict[entry['id']] = entry
#            dict[entry['file']] = entry
        return dict

Class = QtAssistant


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
