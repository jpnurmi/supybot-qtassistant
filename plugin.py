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

import os
import glob
import fnmatch
import fuzzydict
from pysqlite2 import dbapi2 as sqlite3

class QtAssistant(callbacks.Plugin):
    """Add the help for "@plugin help QtAssistant" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(QtAssistant, self)
        self.__parent.__init__(irc)

        self.dict = {}
        datadir = conf.supybot.directories.data
        for qchfile in glob.glob(datadir.dirize("*.qch")):
            module = os.path.splitext(os.path.basename(qchfile))[0]
            self.dict[module] = self._index(qchfile)

    def _index(self, file):
        entries = fuzzydict.FuzzyDict(cutoff=0.8)
        db = sqlite3.connect(file)
        cursor = db.cursor()
        # IndexTable: Id, Name, Identifier, NamespaceId, FileId, Anchor
        # FileNameTable: FolderId, Name, FileId, Title
        # FolderTable: Id, Name, NamespaceId
        cursor.execute('SELECT IndexTable.Name, IndexTable.Identifier, IndexTable.Anchor, FileNameTable.Name, FileNameTable.Title, FolderTable.Name '
                       'FROM IndexTable, FileNameTable, FolderTable '
                       'WHERE IndexTable.FileId = FileNameTable.FileId AND FileNameTable.FolderId = FolderTable.Id')
        rows = cursor.fetchall()
        for row in rows:
            entry = {}
            entry['name'] = row[0]
            entry['id'] = row[1]
            entry['anchor'] = row[2]
            entry['file'] = row[3]
            entry['title'] = row[4]
            entry['folder'] = row[5]
            # entries[entry['name']] = entry
            entries[entry['id']] = entry
            entries[entry['file']] = entry
        return entries

    def rtfm(self, irc, msg, args, query):
        """ <keyword(s)>

        Searches the Qt documentation for <keyword(s)> and returns the
        corresponding online documentation URL if matched.
        """

        if query == None:
            query = 'index.html'

        result = {'item': None, 'ratio': 0.0}
        for module, index in self.dict.iteritems():
            try:
                matched, key, item, ratio = index._search(query)
                if matched and ratio > result['ratio']:
                    result['item'] = item
                    result['ratio'] = ratio
            except:
                matched = False

        item = result['item']
        if not item:
            return irc.reply('No matches for: \'%s\'' % query)

        url = '%s/%s/%s' % (self.registryValue('doc.url'), item['folder'], item['file'])
        if item['anchor'] != None:
            url = '%s#%s' % (url, item['anchor'])
        irc.reply('%s - %s' % (item['title'], url))

    rtfm = wrap(rtfm, [additional('text')])

    def src(self, irc, msg, args, query):
        """ <keyword>

        Searches the Qt sources for <keyword> and returns the
        corresponding online source URL if matched.
        """

        url = self.registryValue('src.url')
        if query == None:
            return irc.reply(url)

        result = []
        blobs = self.registryValue('src.blobs')
        datadir = conf.supybot.directories.data
        for listfile in glob.glob(datadir.dirize("*.files")):
            module = os.path.splitext(os.path.basename(listfile))[0]
            f = open(listfile)
            for line in f.readlines():
                line = line.strip()
                if fnmatch.fnmatch(os.path.basename(line), query):
                    result.append("%s/%s/%s/%s" % (url, module, blobs, line))
            f.close()

        if not result:
            return irc.reply('No such file: \'%s\'' % query)
        irc.replies(result)

    src = wrap(src, [additional('text')])

Class = QtAssistant


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
