from collections import Counter, defaultdict
import functools
import operator
import string
from typing import Callable

from lists import SEDEWORDLES as WORDLES
# from lists import WORDLES

INF = float('inf')


class Clue:
    __CLUE_STR_REQS = "cluestr must be `LLLLL CCCCC` | C∈{B,G,Y}, L∈[a-z]"

    @classmethod
    def ident(cls):
        res = cls("aaaaa BBBBB")
        res.includes['a'] = [0, INF]
        for s in res.possbyspot:
            s.add('a')
        return res

    def __init__(self, cluestr: str) -> None:
        if len(cluestr) != 11 or cluestr[5] != ' ':
            raise ValueError(self.__CLUE_STR_REQS)
        lets, cols = cluestr.split()
        if not all(map(str.islower, lets)) or not all(
                map(functools.partial(operator.contains, "BGY"), cols)):
            raise ValueError(self.__CLUE_STR_REQS)
        generalpos = set(string.ascii_lowercase)
        self.includes = {k: [0, INF] for k in string.ascii_lowercase}
        for k in set(lets):
            kcols = Counter(col for let, col in zip(lets, cols) if let == k)
            nks = sum(kcols.values())
            if 'B' in kcols:
                nincl = nks - kcols['B']
                self.includes[k] = [nincl, nincl]
                if 'Y' not in kcols:
                    generalpos.remove(k)
            else:
                self.includes[k] = [nks, INF]

        self.possbyspot = []
        for let, col in zip(lets, cols):
            if col == 'G':
                self.possbyspot.append({let})
            elif col == 'B':
                self.possbyspot.append(generalpos.copy())
            else:  # col == Y
                self.possbyspot.append(generalpos - {let})

        # print('created:')
        # for i, poss in enumerate(self.possbyspot):
        #     print(i, sorted(poss))
        # print('--')
        # for k, r in self.includes.items():
        #     print(k, r)

    def matches(self, ostr):
        octr = Counter(ostr)
        return (len(ostr) == 5 and all(map(str.islower, ostr))
                and all(let in plets
                        for let, plets in zip(ostr, self.possbyspot))
                and all(t[0] <= octr[k] <= t[1]
                        for k, t in self.includes.items()))

    def __iadd__(self, oclue: 'Clue'):
        if not isinstance(oclue, Clue):
            raise TypeError(
                f"unsupported operand type(s) for +=: 'Clue' and '{type(oclue)}'"
            )
        newincl = dict()
        for k in string.ascii_lowercase:
            slo, shi = self.includes[k]
            olo, ohi = oclue.includes[k]
            newlo = max(slo, olo)
            newhi = min(shi, ohi)
            if newhi < newlo:
                raise ValueError("Attempted merge of incompatible clues")
            newincl[k] = [newlo, newhi]

        newposs = [
            spos.intersection(opos)
            for spos, opos in zip(self.possbyspot, oclue.possbyspot)
        ]
        if not all(newposs):
            raise ValueError("Attempted merge of incompatible clues")

        self.includes = newincl
        self.possbyspot = newposs

        return self


FEIL = "---FEIL---"


def getclue(inputtoclueparam: Callable = None, firsttry=None, give_raw=False):
    if inputtoclueparam is None:
        inputtoclueparam = lambda s: s
    if firsttry is not None:
        try:
            if give_raw:
                return Clue(inputtoclueparam(firsttry)), firsttry
            else:
                return Clue(inputtoclueparam(firsttry))

        except:
            print(FEIL)
            pass
    fail = True
    while fail:
        try:
            user_input = input()
            clue = Clue(inputtoclueparam(user_input))
            fail = False
        except:
            print(FEIL)
            pass
    if give_raw:
        return clue, user_input
    else:
        return clue


def interact():
    print("Enter the clues already guessed, one line each.")
    print("Each line should first have the letters guessed,"
          " then the colors returned.")
    print("B: black (not included), "
          "G: Green (right letter, right place), "
          "Y: Yellow (right letter, wrong place)")
    print()
    print("To end clue entry, type a line containing just a `.`")
    print("To stop getting words, type a line containing just a `.`")
    print()
    print("Hint: power lucks admin")
    print("To repeat the same words you've already entered prior, enter `*`.")
    print("Then, just enter color codes on the next lines.")
    l = input()
    words = []
    while l != '.':
        if l == '*':
            clue = Clue.ident()
            for word in words:
                print(word, end=' ')
                clue += getclue(lambda cs: word + ' ' + cs)
        else:
            clue = getclue(firsttry=l)
            words.append(l.split()[0])
        while True:
            l = input()
            if l == '.':
                break
            newclue, l = getclue(firsttry=l, give_raw=True)
            clue += newclue
            words.append(l.split()[0])

        print('\nPossible Words:')

        for word in WORDLES:
            if clue.matches(word):
                print(word)
        print()

        l = input()


def genclue(guess, targ):
    res = ['B'] * 5
    uneqis = set()
    for i in range(5):
        if guess[i] == targ[i]:
            res[i] = 'G'
        else:
            uneqis.add(i)
    guesscnt = Counter(c for i, c in enumerate(guess) if i in uneqis)
    targcnt = Counter(c for i, c in enumerate(targ) if i in uneqis)
    for k, c in guesscnt.items():
        if k in targcnt:
            n = min(c, targcnt[k])
            for i in uneqis:
                if guess[i] == k:
                    res[i] = 'Y'
                    n -= 1
                    if not n:
                        break
    return ''.join(res)


def maxsingletest():
    guessbysinglecount = defaultdict(set)
    for guess in WORDLES:
        clues = Counter()
        for targ in WORDLES:
            clues[genclue(guess, targ)] += 1
        guessbysinglecount[sum(v for v in clues.values() if v == 1)].add(guess)
    c, words = sorted(guessbysinglecount.items(), reverse=True)[0]
    print(c)
    print(words)


def whatgivessingle(guess):
    guessbysinglecount = defaultdict(set)
    clues = Counter()
    for targ in WORDLES:
        clue = genclue(guess, targ)
        clues[clue] += 1
    singles = [c for c, v in clues.items() if v == 1]
    for clue in singles:
        print(sum(1 for c in clue if c == 'B'), clue)


if __name__ == "__main__":
    # whatgivessingle(input())
    # maxsingletest()
    interact()
"""
spilt
chant
brute
"""
