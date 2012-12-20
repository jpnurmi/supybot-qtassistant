###
# Copyright (c) 2009, J-P Nurmi
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

import fuzzydict
from supybot.commands import *
import supybot.callbacks as callbacks
from pysqlite2 import dbapi2 as sqlite3

class Rtfm2(callbacks.Plugin):
    """Add the help for "!help Rtfm2" here."""
    
    def __init__(self, irc):
        self.__parent = super(Rtfm2, self)
        self.__parent.__init__(irc)
        self.dict = fuzzydict.FuzzyDict()
        files = ('qt.qch', 'qmake.qch', 'assistant.qch', 'designer.qch', 'linguist.qch')
        for file in files:
            self.dict.update(self._index(file))
            #for (key, value) in self._index(file):
            #    self.dict[key] = value

    def _index(self, file):
        dict = fuzzydict.FuzzyDict()
        db = sqlite3.connect(file)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM IndexTable, FileNameTable '
                       'WHERE IndexTable.FileId = FileNameTable.FileId')
        rows = cursor.fetchall()
        for row in rows:
            tmp = {}
            tmp['name'] = row[1]
            tmp['id'] = row[2]
            tmp['anchor'] = row[5]
            tmp['file'] = row[7]
            tmp['title'] = row[9]
            dict[tmp['name']] = tmp
            dict[tmp['id']] = tmp
            dict[tmp['file']] = tmp
        return dict
    
    def _query(self, file, query):
        db = sqlite3.connect(file)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM IndexTable, FileNameTable '
                       'WHERE IndexTable.FileId = FileNameTable.FileId AND '
                       '(IndexTable.Name LIKE ? OR IndexTable.Identifier LIKE ?)',
                       (query, query));
        rows = cursor.fetchall()
        replies = list()
        if len(rows) > 3:
            replies.append('Too many matches for: \'%s\'' % query)
        elif len(rows) > 0:
            for row in rows:
                url = self.registryValue('doc-url')
                reply = '%s - %s/%s' % (row[9], url, row[7])
                if row[5] != None:
                    reply = '%s#%s' % (reply, row[5])
                replies.append(reply)
        return replies
    
    def rtfm(self, irc, msg, args, query):
        """ <keyword(s)>

        Searches the Qt documentation for <keyword(s)> and returns the
        corresponding online documentation URL if matched.
        """

        if query == None:
            query = 'Qt Reference Documentation (Full Framework Edition)'
        #query = query.replace('*', '%')
        #query = query.replace('?', '_')

        #replies = list()
        #files = ('qt.qch', 'qmake.qch', 'assistant.qch', 'designer.qch', 'linguist.qch')
        #for file in files:
        #    replies = self._query(file, query)
        #    if len(replies) > 0:
        #        break
        
        if query.lower().startswith('qxt'):
            return irc.reply('Sorry, Qxt is not supported at the moment.')
        
        try:
            matched, key, item, ratio = self.dict._search(query)
        except:
            matched = False

        if not matched:
            return irc.reply('No matches for: \'%s\'' % query)

        url = self.registryValue('doc-url')
        reply = '%s - %s/%s' % (item['title'], url, item['file'])
        if item['anchor'] != None:
            reply = '%s - %s - %s/%s#%s' % (item['title'], item['id'], url, item['file'], item['anchor'])
        irc.reply(reply)

    rtfm = wrap(rtfm, [additional('text')])

Class = Rtfm2

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
