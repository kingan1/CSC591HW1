import functools
import math
import random

from options import options
from utils import cliffsDelta


def erf(x):
    a1 =  0.254829592
    a2 = -0.284496736
    a3 =  1.421413741
    a4 = -1.453152027
    a5 =  1.061405429
    p  =  0.3275911

    sign = 1

    if x < 0:
        sign = -1

    x = abs(x)
    t = 1 / (1 + (p * x))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    
    return sign * y

def RX(t,s) :
    t = sorted(t)
    return {"name":s or "", 
            "rank":0, 
            "n":len(t), 
            "show":"", 
            "has":t} 

def mid(t):
    t= t.get("has", t)
    n = len(t)//2
    return (t[n] +t[n+1])/2 if len(t)%2==0 else t[n+1]

def div(t):
    t= t.get("has", t)
    return (t[ len(t)*9//10 ] - t[ len(t)*1//10 ])/2.56


def delta(i, other):
    e, y, z = 1E-32, i, other
    return abs(y.mu - z.mu) / ((e + y.sd ^ 2 / y.n + z.sd ^ 2 / z.n) ^ .5)

def merge(rx1,rx2) :
    rx3 = RX([], rx1['name'])
    for _,t in enumerate([rx1['has'],rx2['has']]):
        for _,x in enumerate(t): 
            rx3['has'].append(x)
    rx3['has'] = sorted(rx3['has'])
    rx3['n'] = len(rx3['has'])
    return rx3

def samples(t,n=0):
    u= []
    n = n or len(t)
    for i in range(n): 
        u.append(t[random.randrange(len(t))]) 
    return u

def gaussian(mu,sd): #  #--> n; return a sample from a Gaussian with mean `mu` and sd `sd`
    mu,sd = mu or 0, sd or 1
    sq,pi,log,cos,r = math.sqrt,math.pi,math.log,math.cos,random.random
    return  mu + sd * sq(-2*log(r())) * cos(2*pi*r())


class ScottKnott:
    def __init__(self, rxs):
        self.rxs = rxs

        self.cohen = None

    def run(self):
        sorted(self.rxs, key=functools.cmp_to_key(lambda x, y: mid(x) - mid(y)))
        self.cohen = div(self.merges(0, len(self.rxs - 1))) * options["cohen"]

        self.recurse(0, len(self.rxs) - 1, 1)

    def merges(self, i, j):
        out = RX({}, self.rxs[i].name)

        for k in range(i, j + 1):
            out = merge(out, self.rxs[j])

        return out

    def same(self, lo, cut, hi):
        l = self.merges(lo, cut)
        r = self.merges(cut + 1, hi)

        return cliffsDelta(l["has"], r["has"]) and bootstrap(l["has"], r["has"])

    def recurse(self, lo, hi, rank):
        cut = None
        b4 = self.merges(lo, hi)
        best = 0

        for j in range(lo, hi + 1):
            if j < hi:
                l = self.merges(lo, j)
                r = self.merges(j + 1, hi)

                now = (l["n"] * (mid(l) - mid(b4)) ^ 2 + r["n"] * (mid(r) - mid(b4)) ^ 2) / (l["n"] + r["n"])

                if now > best:
                    if abs(mid(l) - mid(r)) >= self.cohen:
                        cut, best = j, now

        if cut and not self.same(lo, cut, hi):
            rank = self.recurse(lo, cut, rank) + 1
            rank = self.recurse(cut + 1, hi, rank)
        else:
            for i in range(lo, hi + 1):
                self.rxs[i]["rank"] = rank

        return rank
