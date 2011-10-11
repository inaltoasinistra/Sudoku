#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from subprocess import call

#
#   00 .. 08
#   10 .. 18
#      ..          x 1..9
#   80 .. 88
#

tab = {}

r = range(1,10)

SAT_FNAME = 'proble.minisat'
OUT_FNAME = 'solution.minisat'

def main():

    initlookup()
    closures = sudokucons()

    sudoku = readinput()

    #print sudoku

    singleclosures = []
    for i in r:
        for j in r:
            #print i,j,sudoku[i-1][j-1]
            if sudoku[i-1][j-1] != ' ':
                singleclosures.append( lookup(i,j,int(sudoku[i-1][j-1])) )

    #print len(closures)
    #print closures
    
    fo = file(SAT_FNAME,'w')
    
    fo.write('c sudoku.py © 2011 the9ull^\n')
    fo.write('p cnf %d %d\n' % (9**3,len(closures)+len(singleclosures)))
    fo.write('c Sudoku constraints\n')
    for x,y in closures:
        fo.write('%d %d 0\n' % (x,y))

    fo.write('c Input constraints\n')
    for x in singleclosures:
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
        fo.write('%d [row=%d col=%d value=%d]' % (k,v[0],v[1],v[2]))
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
        if lines[0].strip() != 'SAT':
            print 'Check %s file please' % OUT_FNAME
            return

        # Prepare void matrix
        sol = []
        for i in r:
            sol.append([])
            for j in r:
                sol[-1].append(' ')

        # Elabote solution
        for n in [int(x) for x in lines[1].strip().split() if int(x)>0]:
            (i,j,v) = rev[n]
            sol[i-1][j-1] = str(v)
            print i,j,v

        # Print sol matrix
        for i in r:
            line = []
            for j in r:
                line.append(sol[i-1][j-1])
            print ''.join(line)
            
    elif ret == 20:
        #UNSAT
        print 'Did you give me a valid input?'
    else:
        print 'Minisat ERROR'
        return

def readinput():
    data = [tuple(x.strip('\n')) for x in sys.stdin.readlines()]
    assert len([x for x in data if len(x)==9]) == 9
    return data
    

def initlookup():
    count = 1
    for i in r:
        for j in r:
            for k in r:
                tab[(i,j,k)] = count
                count+=1

    #print tab

lookup = lambda i,j,k :tab[(i,j,k)]
    
rsub = lambda r,i: [x for x in r if x!=i]
    

def sudokucons():

    o = []
    add = lambda x,y: o.append((x,y))

    for i in r:
        for j in r:
            for v in r:

                
                # (ij,v) -> there are no other var with the same value v on
                #             1. same line
                #             2. same col
                #             3. same square

                #print lookup(i,j,v),'(%d %d %d) ->'%(i,j,v)

                cell = -lookup(i,j,v)

                #lines
                #print 'lines',
                for jj in rsub(r,j):
                    #print -lookup(i,jj,v), '(%d %d %d)'%(i,jj,v)
                    add(cell,-lookup(i,jj,v))

                #cols
                #print 'cols',
                for ii in rsub(r,i):
                    #print -lookup(ii,j,v), '(%d %d %d)'%(ii,j,v)
                    add(cell,-lookup(ii,j,v))

                #squares
                #print 'squares',
                if i>=1 and i<=3: ir = rsub(range(1,4),i)
                elif i>=4 and i<=6: ir = rsub(range(4,7),i)
                elif i>=7 and i<=9: ir = rsub(range(7,10),i)
                else: assert 0
                assert len(ir)==2,ir

                if j>=1 and j<=3: jr = rsub(range(1,4),j)
                elif j>=4 and j<=6: jr = rsub(range(4,7),j)
                elif j>=7 and j<=9: jr = rsub(range(7,10),j)
                else: assert 0
                assert len(jr)==2,jr
                
                for ii in ir:
                    for jj in jr:
                        #print -lookup(ii,jj,v), '(%d %d %d)'%(ii,jj,v)
                        add(cell,-lookup(ii,jj,v))

                #one value
                #print 'one value',
                for vv in rsub(r,v):
                    #print -lookup(i,j,vv), '(%d %d %d)'%(i,j,vv)
                    add(cell,-lookup(i,j,vv))

    return o

if __name__=="__main__":
    main()
