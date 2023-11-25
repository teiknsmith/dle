import operator as op
from collections import defaultdict as ddict
import functools as fntls
import itertools as ittls

OPS = {op.add, op.mul, op.sub, op.floordiv}



@fntls.cache
def poss(nums, r=0):
    res = ddict(set, {n: {(1, str(n))} for n in nums})
    if len(nums) < 2:
        return res
    for lsetis in ittls.chain.from_iterable(ittls.combinations(range(len(nums)), r) for r in range(1,(1+len(nums))//2+1)):
        lset = []
        rset = []
        for i in range(len(nums)):
            (lset if i in lsetis else rset).append(nums[i])
        lset, rset = map(tuple, [lset, rset])
        lposs = poss(lset, r+1)
        rposs = poss(rset, r+1)
        for a, b in ittls.product(lposs, rposs):
            acnt, astr = next(iter(lposs[a]))
            bcnt, bstr = next(iter(rposs[b]))
            res[a].add((acnt, astr))
            res[b].add((bcnt, bstr))
            res[a+b].add((acnt+bcnt, f'{astr} {bstr} +'))
            res[a*b].add((acnt+bcnt, f'{astr} {bstr} *'))
            if a > b:
                res[a-b].add((acnt+bcnt, f'{astr} {bstr} -'))
            elif b > a:
                res[b-a].add((acnt+bcnt, f'{bstr} {astr} -'))
            if b and not a%b:
                res[a//b].add((acnt+bcnt, f'{astr} {bstr} /'))
            if a and not b%a:
                res[b//a].add((acnt+bcnt, f'{bstr} {astr} /'))
    return res


if __name__ == '__main__':
    t = int(input("Enter the target value: "))
    vs = tuple(map(int, input("And the available nums: ").split()))
    print()
    print("Answer:", sorted(poss(vs)[t])[0][1])
