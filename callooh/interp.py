#!/usr/bin/python
# -*- coding: us-ascii -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import collections

sys.recursionlimit = 1000

class WL(object):
    def __init__(self):
        self.symbols = collections.defaultdict(list)
        self.stack = []
        self.scopes = [[]]
        self.dispatchdi = {'declare': self.declare,
                           'assign': self.assign,
                           'call': self.call,
                           'length': self.length,
                           'index': self.index,
                           'catenate': self.catenate,
                           'append': self.append,
                           'if': self.if_,
                           'munch': self.munch,
                           '+': self.add,
                           '-': self.sub,
                           '*': self.mul,
                           '/': self.div,
                           '%': self.mod,
                           '>': self.gt,
                           '<': self.lt,
                           '==': self.eq,
                           'end': self.end,
                           'begin': self.begin,
                          }
    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()

    def read(self, token):
        if '--debug' in sys.argv:
            print(self.stack)
        if token[0] == token[-1] == "'":
            self.push(token.strip("'"))
        elif token[0] == '{' and token[-1] == '}':
            self.push(token[2:-2])
        elif token.isdigit():
            self.push(int(token))
        elif token == '[]':
            self.push([])
        elif token in self.dispatchdi:
            self.dispatchdi[token]()
        else:
            self.push(self.symbols[token][-1])

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
        print('MOD', fst, snd)
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
            if wordlet == '*/':
                comment = False
                continue
            if wordlet == '/*':
                comment = True
                continue
            if comment:
                continue
            if wordlet == '{':
                tokbuf.append(wordlet)
                if curlycount == 0:
                    tokbuf.append('begin')
                curlycount += 1
                continue
            if wordlet == '}':
                curlycount -= 1
                if curlycount == 0:
                    tokbuf.append('end')
                    tokbuf.append(wordlet)
                    tokens.append(' '.join(tokbuf))
                    tokbuf = []
                else:
                    tokbuf.append(wordlet)
                continue
            if curlycount:
                tokbuf.append(wordlet)
                continue
            tokens.append(wordlet)
        return tokens

    def eval(self, block):
        for token in self.tokenize(block):
            self.read(token)

sampcode = """
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
    wl = WL()
    #print('\n'.join(wl.tokenize(sampcode)))
    wl.eval(sampcode)
    #wl.eval(sys.stdin.read())
    for st in wl.stack:
        print(''.join([ chr(96 + c) for c in st ]), end=' ')
    print()
    print('JABBERWOCK', wl.symbols['jabberwock'])
    return 0

if __name__ == '__main__':
    sys.exit(main())
