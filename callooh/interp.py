#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import collections
import os
import codecs

sys.recursionlimit = 1000

class WL(object):
    def __init__(self, flavour=u'callooh'):
        self.symbols = collections.defaultdict(list)
        self.stack = []
        self.scopes = [[]]
        if flavour == u'callooh':
            self.dispatchdi = {
                u'plead': self.import_,
                u'callay': self.declare,
                u'uff': self.assign,
                u'mome': self.call,
                u'frabjion': self.length,
                u'grend': self.index,
                u'whiffle': self.catenate,
                u'gimble': self.append,
                u'gyre': self.if_,
                u'munch': self.munch,
                u'{': u'«',
                u'}': u'»',
                u'[]': u'∅',
                u'oq': u'‹',
                u'cq': u'›',
                u'♠': self.add,
                u'♣': self.sub,
                u'♥': self.mul,
                u'♦': self.div,
                u'☋': self.gt,
                u'☊': self.lt,
                u'☁': self.mod,
                u'☺': self.eq,
                u'/*': u'☞',
                u'*/': u'☜',
                u'end': self.end,
                u'begin': self.begin
            }
            self.parseint = self.parseint14
            self.isnum = self.isnum14
        else:
            self.dispatchdi = {
                u'import': self.import_,
                u'declare': self.declare,
                u'assign': self.assign,
                u'call': self.call,
                u'length': self.length,
                u'index': self.index,
                u'catenate': self.catenate,
                u'append': self.append,
                u'if': self.if_,
                u'munch': self.munch,
                u'{': u'{',
                u'}': u'}',
                u'[]': u'[]',
                u'oq': u"'",
                u'cq': u"'",
                u'+': self.add,
                u'-': self.sub,
                u'*': self.mul,
                u'/': self.div,
                u'%': self.mod,
                u'>': self.gt,
                u'<': self.lt,
                u'==': self.eq,
                u'/*': u'/*',
                u'*/': u'*/',
                u'end': self.end,
                u'begin': self.begin
            }
            self.parseint = self.parseint10
            self.isnum = self.isnum10

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()

    def isnum10(self, token):
        return token.isdigit()

    def isnum14(self, token):
        return set(token) <= set(u'0A23456789TJQK')

    def parseint10(self, token):
        return int(token)

    def parseint14(self, token):
        lookup = {u'A': u'1', u'T': u'a', u'J': u'b', u'Q': u'c', u'K': u'd'}
        return int(u''.join([lookup[c] if c in lookup else c for c in token]),
                   14)

    def read(self, token):
        oq = self.dispatchdi[u'oq']
        cq = self.dispatchdi[u'cq']
        ocb = self.dispatchdi[u'{']
        ccb = self.dispatchdi[u'}']
        if u'--debug' in sys.argv:
            print(self.stack)
        if token[0] == oq and token[-1] == cq:
            self.push(token.strip(oq + cq))
        elif token[0] == ocb and token[-1] == ccb:
            self.push(token[2:-2])
        elif self.isnum(token):
            self.push(self.parseint(token))
        elif token == self.dispatchdi[u'[]']:
            self.push([])
        elif token in self.dispatchdi:
            self.dispatchdi[token]()
        else:
            try:
                self.push(self.symbols[token][-1])
            except IndexError as hell:
                print(token, self.symbols)
                raise hell

    def declare(self):
        sym = self.pop()
        self.symbols[sym].append(None)
        self.scopes[-1].append(sym)

    def assign(self):
        sym = self.stack.pop()
        val = self.stack.pop()
        #assert self.symbols[sym][-1] == None
        self.symbols[sym][-1] = val

    def call(self):
        self.eval(self.pop())

    def length(self):
        lgth = len(self.pop())
        self.push(lgth)

    def index(self):
        idx = self.pop()
        arr = self.pop()
        self.push(arr[idx])

    def catenate(self):
        snd = self.pop()
        fst = self.pop()
        self.push(fst + snd)

    def append(self):
        new = self.pop()
        arr = self.pop()
        arr.append(new)
        self.push(arr)

    def if_(self):
        test = self.pop()
        fal = self.pop()
        tru = self.pop()
        if test:
            self.eval(tru)
        else:
            self.eval(fal)

    def munch(self):
        lgth = self.pop()
        fst = self.pop()
        arr = self.pop()
        snd = fst + lgth
        self.push(arr[fst:snd])

    def add(self):
        snd = self.pop()
        fst = self.pop()
        val = fst + snd
        #assert val > 0
        self.push(val)

    def sub(self):
        snd = self.pop()
        fst = self.pop()
        val = fst - snd
        #assert val > 0
        self.push(val)

    def mul(self):
        snd = self.pop()
        fst = self.pop()
        val = fst * snd
        assert val > 0
        self.push(val)

    def div(self):
        snd = self.pop()
        fst = self.pop()
        val = fst / snd
        assert val > 0
        self.push(val)

    def mod(self):
        snd = self.pop()
        fst = self.pop()
        self.push(fst % snd)

    def gt(self):
        snd = self.pop()
        fst = self.pop()
        self.push(fst > snd)

    def lt(self):
        snd = self.pop()
        fst = self.pop()
        self.push(fst < snd)

    def eq(self):
        snd = self.pop()
        fst = self.pop()
        self.push(fst == snd)

    def end(self):
        for sym in self.scopes[-1]:
            self.symbols[sym].pop()
        self.scopes.pop()

    def begin(self):
        self.scopes.append([])

    def tokenize(self, block):
        wordlets = block.split()
        tokbuf = []
        curlycount = 0
        comment = False
        tokens = []
        for wordlet in wordlets:
            try:
                if wordlet == self.dispatchdi[u'*/']:
                    comment = False
                    continue
                if wordlet == self.dispatchdi[u'/*']:
                    comment = True
                    continue
                if comment:
                    continue
                if wordlet == self.dispatchdi[u'{']:
                    tokbuf.append(wordlet)
                    if curlycount == 0:
                        tokbuf.append(u'begin')
                    curlycount += 1
                    continue
                if wordlet == self.dispatchdi[u'}']:
                    curlycount -= 1
                    if curlycount == 0:
                        tokbuf.append(u'end')
                        tokbuf.append(wordlet)
                        tokens.append(u' '.join(tokbuf))
                        tokbuf = []
                    else:
                        tokbuf.append(wordlet)
                    continue
                if curlycount:
                    tokbuf.append(wordlet)
                    continue
                tokens.append(wordlet)
            except UnicodeWarning as hell:
                print(repr(wordlet))
                raise hell
        return tokens

    def eval(self, block):
        for token in self.tokenize(block):
            self.read(token)

    def import_(self):
        module = self.pop()
        if not os.path.exists(module):
            module += u'.wl'
        with codecs.getreader('utf-8')(open(module)) as modfile:
            self.eval(modfile.read())

sampcode = u"""
'slithy' declare
{ /* FIB */
  'k' declare
  'k' assign
    { k }
    { k 1 - slithy call k 2 - slithy call + }
  k 2 < if
} 'slithy' assign

'grabe' declare
{ /* GCD */
  'k' declare 'j' declare
  'j' assign 'k' assign
    { k }
    { j k j % grabe call }
  j 0 == if
} 'grabe' assign

'chortle' declare
{ /* LOOP */
  'tove' declare 'k' declare
  'k' assign 'tove' assign 
    { }
    { k 1 - tove call
      tove k 1 - chortle call }
  k 0 == if
} 'chortle' assign

'deficious' declare
'ovlet' declare
{ /* RAND */
  10001 ovlet * 12345 + 65536 % 'ovlet' assign
  ovlet
} 'deficious' assign

'burble' declare
{ /* SORT */
  'claws' declare
  'claws' assign
    { 'bandersnatch' declare 'port' declare 'starboard' declare
      [] 'port' assign
      [] 'starboard' assign
      claws 0 index 'bandersnatch' assign
        { 'k' declare 'j' declare
          'k' assign
          claws k 1 + index 'j' assign
            { starboard j append 'starboard' assign }
            { port j append 'port' assign }
          j bandersnatch > if
        }
        claws length 1 -
      chortle call
      port burble call bandersnatch append starboard burble call catenate
    }
    { claws }
  claws length 1 > if
} 'burble' assign

'muchness' declare
{ 'i' declare 'j' declare
  'i' assign
  0 'j' assign
  { 'k' declare 'k' assign
    i k index j + 'j' assign
  } i length chortle call
  j
} 'muchness' assign

'snack' declare
{ 'k' declare
  'k' assign
  jabberwock 0 k munch
  jabberwock k jabberwock length k - munch 'jabberwock' assign
} 'snack' assign

'tweedle' declare
{ 'stead' declare
  [] 'stead' assign
  { 'k' declare
    'k' assign
    stead jabberwock k index append 'stead' assign
  } jabberwock length chortle call
  stead 'jabberwock' assign
} 'tweedle' assign

'frolick' declare
{ 'stead' declare
  [] 'stead' assign
  { 'k' declare
    'k' assign
    stead jabberwock k index sword k index + 1 - 26 % 1 + append
    'stead' assign
  } jabberwock length chortle call
  stead 'jabberwock' assign
  tweedle call
} 'frolick' assign

'modge' declare
{ 'l' declare 'i' declare
  [] 'l' assign
  [] 'i' assign
  { 'k' declare
    'k' assign
    jabberwock k index
      { 'k' assign
        l k append 'l' assign
      }
      { 'k' assign
        i k append 'i' assign
      }
    k 2 % 0 == if
  } jabberwock length chortle call
  l 'jabberwock' assign tweedle call jabberwock
  i 'jabberwock' assign tweedle call jabberwock
  catenate 'jabberwock' assign
} 'modge' assign

'priot' declare
{ 'stead' declare
  [] 'stead' assign
  { 'k' declare 'j' declare
    'k' assign
    stead jabberwock k 1 + index jabberwock k index - 'j' assign
      { j 26 + }
      { j }
    j 1 < if
    append 'stead' assign
  } jabberwock length 1 - chortle call
  stead jabberwock 0 index append 'jabberwock' assign tweedle call
} 'priot' assign

'sword' declare
[] 233 append 4461 append 7992 append 9223 append 16764 append 21775 append
22004 append 22885 append 24890 append 31507 append 33518 append 39171 append
42416 append 48818 append 51953 append 52844 append 62326 append 63499 append
'sword' assign

/*
'jabberwock' declare
[] 2 append 16 append 20 append 9 append 24 append 7 append 7 append 3 append 23
append 25 append 
'jabberwock' assign

priot call
frolick call
*/

'jabberwock' declare
[] 8 slithy call 1 - append 6 slithy call append 5 slithy call append

3 append 25 append 126 198 grabe call append 16 append
[] 17 append 24 append 10 append 5 append 24 append 5 append
19 append burble call catenate
5 append 5 append 11 append 4 append 9 append 25 append 2 append
'jabberwock' assign

42 'ovlet' assign
'sword' declare
[] 'sword' assign
{ 'k' declare
  'k' assign
  sword deficious call append 'sword' assign
} 18 chortle call
sword burble call 'sword' assign

  {   { 
        3 snack call

        tweedle call
        frolick call
        6 snack call

        tweedle call
        modge call
        frolick call
        2 snack call

        tweedle call
        modge call
        priot call
        frolick call
        10 snack call
      }
      { [] 5 append 18 append 18 append 15 append 18 append }
    sword muchness call 556279 == if
  }
  { [] 5 append 18 append 18 append 15 append 18 append }
jabberwock muchness call 260 == if

"""

def main():
    sys.stdout = codecs.getwriter(u'utf-8')(sys.stdout)
    sys.stdin = codecs.getreader(u'utf-8')(sys.stdin)
    #print('\n'.join(wl.tokenize(sampcode)))
    if u'--demo' in sys.argv:
        wl = WL(flavour=u'english')
        wl.eval(sampcode)
    else:
        flavour = u'callooh'
        if u'--english' in sys.argv:
            flavour = u'english'
        wl = WL(flavour=flavour)
        wl.eval(sys.stdin.read())
    if u'--answer' in sys.argv or u'--demo' in sys.argv:
        for st in wl.stack:
            print(u''.join([ chr(96 + c) for c in st ]), end=u' ')
        print()
    return 0

if __name__ == '__main__':
    sys.exit(main())
