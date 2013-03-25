#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from subprocess import call

#1 #n alberi 
#11222
#13232
#13332
#45322
#45555

tab = {}

SAT_FNAME = 'alberi.problem.minisat'
OUT_FNAME = 'alberi.solution.minisat'

def main():
    ntrees,surfaces,aa = readinput()
    assert ntrees==1,'Only one tree game is supported'

    r = range(1,len(aa)+1)
    #Add the tree layer
    initlookup(r,aa) # r * r * (aa+1)
    closures = albericons(r,aa)

    #print '/',surfaces

    #define the input in closure form
    inputclosures = []
    for i,l in enumerate(surfaces):
        for j,area in enumerate(l):
            #print i+1,j+1,area
            for a in aa:
                if area==a:
                    inputclosures.append( lookup(i+1,j+1,a) )
                else:
                    inputclosures.append( -lookup(i+1,j+1,a) )
                #print i+1,j+1,a,
                #print inputclosures[-1]
                    

    #print len(closures)
    #print closures
    
    fo = file(SAT_FNAME,'w')
    
    fo.write('c alberi.py © 2013 the9ull^\n')
    lenr = len(r)
    #print r
    #print surfaces
    #print lenr**2 + 2* lenr**3
    fo.write('p cnf %d %d\n' % (lenr**2 + 2* lenr**3,len(closures)+len(inputclosures)))
    fo.write('c Sudoku constraints\n')
    for closure in closures:
        fo.write(' '.join(map(str,closure)) + ' 0\n')

    fo.write('c Input constraints\n')
    for x in inputclosures:
        fo.write('%d 0\n' % x)

    # reverse lookup
    fo.write('\n\nc Variable lookup\n\n')
    rev = {}
    for k,v in tab.iteritems():
        rev[v] = k
        #print k,v, rev[v],v
    newline = 0
    for k in sorted(rev.keys()):
        v = rev[k]
        #print k,v
        if newline==0:
            fo.write('c ')
        if len(v)==2:
            s = ''
        else:
            if len(v)==3:
                s = ' a=%s' % v[2]
            else:
                if len(v)==4 and v[3]=='a':
                    s = ' a=%s ij&ija' % v[2]
                else:
                    assert 0,'Tab error'

        fo.write('%d [row=%d col=%d%s]' % (k,v[0],v[1],s))
        if newline==2:
            fo.write('\n')
        else:
            fo.write('    ')
        newline = ((newline+1) % 3)
    fo.close()

    # Call (Mini)sat solver

    if call(['which','minisat']) == 0:
        minisat = 'minisat'
    elif call(['which','minisat2']) == 0:
        minisat = 'minisat2'
    else:
        print 'Minisat missed!'
        return

    ret = call([minisat,'-verb=0',SAT_FNAME,OUT_FNAME])

    if ret == 10:
        #SAT
        lines = file(OUT_FNAME).readlines()
        
        assert lines[0]=='SAT\n'

        truevars = set(filter(lambda x: x>0,map(int,lines[1].split())))
        for i in r:
            s = []
            for j in r:
                if lookup(i,j) in truevars:
                        #s.append('+')
                    s.append(treeSign(surfaces[i-1][j-1]))
                else:
                    s.append(surfaces[i-1][j-1])
            print ''.join(s)
            
    elif ret == 20:
        #UNSAT
        print 'Did you give me a valid input?'
    else:
        print 'Minisat ERROR'
        return

def treeSign(c):
    if c>='a' and c<='z':
        return chr(ord(c)-ord('a')+ord('A'))
    if c>='A' and c<='Z':
        return chr(ord(c)-ord('A')+ord('a'))
    if c>='1' and c<='9':
        return chr(ord(c)-ord('1')+ord('a'))
    return '+'
    

def readinput():
    data = [tuple(x.split('#')[0].strip(' \n')) for x in sys.stdin.readlines()]
    assert len(data)>0
    n = int(data[0][0])
    data = data[1:]
    aa = set()
    for l in data:
        aa.update(set(l))

    #check: square matrix
    assert len(aa)==len(data),'Check the input'
    for l in data:
        assert len(l)==len(data)
    return n,data,sorted(list(aa))
    

def initlookup(r,aa):
    '''
    Create hash table to resolve the associated variable.
    i,j,a → #n
    '''
    count = 1
    for i in r:
        for j in r:
            tab[(i,j)] = count
            count+=1
            for a in aa:
                tab[(i,j,a)] = count
                count+=1
                tab[(i,j,a,'a')] = count
                count+=1
                

    #print tab

lookup = lambda *args :tab[tuple(args)]
    
rsub = lambda r,i: [x for x in r if x!=i]
    
def albericons(r,aa):
    '''
    closures format:
      (x1 | ¬x2 | x3) &
      (¬x1 | x2 | x3)
    becomes:
      1 -2 3
      -1 2 3
    becomes:
      o = [(1,-2,3),
           (-1,2,3)]
    '''
    o = []
    add = lambda *args: o.append(tuple(args))

    for i in r:
        # At most one tree for each row
        for j in r:
            ij = lookup(i,j)
            for jj in r:
                if j!=jj:
                    add(-ij,-lookup(i,jj))

            # Trees can't be too near (checks only diagonals)
            # NB: with ntree==2 → we must check also horizontal and vertical
            if i-1 in r and j-1 in r:
                add(-ij,-lookup(i-1,j-1))
            if i-1 in r and j+1 in r:
                add(-ij,-lookup(i-1,j+1))
            if i+1 in r and j+1 in r:
                add(-ij,-lookup(i+1,j+1))
            if i+1 in r and j-1 in r:
                add(-ij,-lookup(i+1,j-1))



        # At least one tree for each row
        add(*[lookup(i,x) for x in r])

    for j in r:
        # At most one tree for each column
        for i in r:
            ij = lookup(i,j)
            for ii in r:
                if i!=ii:
                    add(-ij,-lookup(ii,j))
        # At least one tree for each column
        add(*[lookup(x,j,) for x in r])

    # One tree for each area
    for a in aa:
        # At least one tree for each area

        #  Formula:
        ## h <-> 1 & 2
        ## (-h | 1) & (-h | 2) & (h | -1 | -2)
        # |(ija & ij) → |(ijaa)

        atleast = []
        for i in r:
            for j in r:
                ijaa = lookup(i,j,a,'a')
                ija = lookup(i,j,a)
                ij = lookup(i,j)

                atleast.append(ijaa)
                # Definition of ijaa variables
                add(-ijaa,ija)
                add(-ijaa,ij)
                add(ijaa,-ija,-ij)

                # At most one tree for each area
                for ii in r:
                    for jj in r:
                        if i!=ii and j!=jj:
                            add(-ijaa,-lookup(ii,jj,a,'a'))
        # At least one ijaa variable must be true for each area
        add(*atleast)
        

    return o

if __name__=="__main__":
    main()
