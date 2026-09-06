#!/usr/bin/env python3
"""
Generate diagrams for Cracking the Coding Interview, 6th Edition.
Run: python3 generate_images.py
Requires: pip install matplotlib numpy
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

C = {
    'blue': '#2196F3', 'lightblue': '#BBDEFB', 'darkblue': '#1565C0',
    'green': '#4CAF50', 'lightgreen': '#C8E6C9',
    'orange': '#FF9800', 'lightorange': '#FFE0B2',
    'purple': '#9C27B0', 'lightpurple': '#E1BEE7',
    'red': '#F44336', 'lightred': '#FFCDD2',
    'teal': '#009688', 'lightteal': '#B2DFDB',
    'bg': '#F8F9FA', 'text': '#212121',
    'gray': '#757575', 'lightgray': '#F5F5F5',
    'amber': '#FFC107', 'indigo': '#3F51B5',
}

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=C['bg'])
    plt.close(fig)
    print(f"  ✓ {name}")

def box(ax, x, y, w, h, label, color, fontsize=9, tc='white', r=0.2):
    p = FancyBboxPatch((x-w/2, y-h/2), w, h,
        boxstyle=f"round,pad={r}", facecolor=color, edgecolor='white',
        linewidth=1.5, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=tc, fontweight='bold', zorder=4, multialignment='center')

def arr(ax, x1, y1, x2, y2, color='#424242', label=''):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=2)
    if label:
        ax.text((x1+x2)/2+0.1,(y1+y2)/2, label, fontsize=7, color=color,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor=color, alpha=0.9))

# ── 01: Interview Process ────────────────────────────────────────────────────
def ch01():
    fig, ax = plt.subplots(figsize=(13, 4), facecolor=C['bg'])
    ax.set_xlim(0,13); ax.set_ylim(0,4); ax.axis('off')
    fig.suptitle('The Interview Process — Pipeline', fontsize=13, fontweight='bold', color=C['text'])
    stages = [(1.0,'📄\nResume\nScreen',C['blue']),(2.9,'📞\nPhone\nScreen',C['teal']),
              (4.8,'💻\nTake-Home\n(optional)',C['green']),(6.8,'🏢\nOnsite\nLoop',C['orange']),
              (8.8,'📋\nDebrief\n& Review',C['purple']),(10.8,'✅\nOffer /\nDecision',C['red'])]
    for x,label,color in stages:
        box(ax, x, 2.2, 1.65, 1.5, label, color, fontsize=8)
    for i in range(len(stages)-1):
        arr(ax, stages[i][0]+0.82, 2.2, stages[i+1][0]-0.82, 2.2)
    notes = ['HR Filter','1-2 Algo Qs','2-4hr Project','4-6 Rounds','Score Review','Result']
    for i,(x,_,_) in enumerate(stages):
        ax.text(x, 0.6, notes[i], ha='center', fontsize=7, color=C['gray'], style='italic')
    save(fig, '01-interview-process.png')

# ── 02: Company Comparison ───────────────────────────────────────────────────
def ch02():
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=C['bg'])
    ax.set_xlim(0,12); ax.set_ylim(0,6); ax.axis('off')
    fig.suptitle('Big 5 Company Hiring Styles', fontsize=13, fontweight='bold', color=C['text'])
    companies = ['Microsoft','Amazon','Google','Apple','Facebook']
    cols = [C['blue'],C['orange'],C['red'],C['gray'],C['indigo']]
    aspects = ['Algorithm','System\nDesign','Behavioral','Speed','Bar\nKeeper']
    ratings = [[3,2,3,3,3],[3,2,5,3,5],[5,4,2,1,4],[4,3,2,3,3],[4,4,3,5,2]]
    for ai, aspect in enumerate(aspects):
        ax.text(4.0+ai*1.6, 5.7, aspect, ha='center', fontsize=8,
                fontweight='bold', color=C['text'])
    for ci, (company, color, row) in enumerate(zip(companies, cols, ratings)):
        y = 4.8 - ci*0.9
        box(ax, 1.5, y, 2.4, 0.7, company, color, fontsize=9)
        for ai, val in enumerate(row):
            x = 4.0 + ai*1.6
            for s in range(5):
                sc = color if s < val else C['lightgray']
                ax.scatter(x + s*0.22 - 0.44, y, s=45, color=sc, zorder=3)
    save(fig, '02-company-comparison.png')

# ── 03: Big O ────────────────────────────────────────────────────────────────
def ch03():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=C['bg'])
    fig.suptitle('Big O Complexity Growth', fontsize=13, fontweight='bold', color=C['text'])
    n = np.linspace(1, 20, 300)
    curves = [
        (np.ones_like(n),        'O(1)',      C['green'],  '--'),
        (np.log2(n),             'O(log n)',  C['teal'],   '-'),
        (n,                      'O(n)',       C['blue'],   '-'),
        (n*np.log2(n),           'O(n log n)',C['orange'], '-'),
        (np.clip(n**2, 0, 400),  'O(n²)',     C['red'],    '-'),
        (np.clip(2**n/500*100,0,400),'O(2ⁿ)',C['purple'], '-'),
    ]
    for y, label, color, ls in curves:
        ax.plot(n, y, label=label, color=color, linewidth=2.5, linestyle=ls)
    ax.set_xlim(1,20); ax.set_ylim(0,410)
    ax.set_xlabel('n (input size)', fontsize=10); ax.set_ylabel('Operations', fontsize=10)
    ax.legend(fontsize=10, loc='upper left'); ax.set_facecolor(C['lightgray']); ax.grid(True, alpha=0.3)
    save(fig, '03-big-o-complexity.png')

# ── 04: Arrays & Strings ─────────────────────────────────────────────────────
def ch04():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor=C['bg'])
    fig.suptitle('Arrays & Strings — Core Patterns', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Hash Table O(1) Lookup', fontsize=10, color=C['text'])
    for i,(k,v) in enumerate([('key1','val1'),('key2','val2'),('key3','val3')]):
        y = 7.5 - i*1.8
        box(ax,2,y,2.5,1.0,k,C['blue'],fontsize=8)
        ax.text(5,y,'→',fontsize=14,ha='center',color=C['orange'],fontweight='bold')
        box(ax,7.5,y,2.5,1.0,v,C['green'],fontsize=8)
    ax.text(5,1.2,'hash(key) → bucket → value\nO(1) average',ha='center',
            fontsize=9,color=C['teal'],fontweight='bold')
    ax = axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Two Pointers', fontsize=10, color=C['text'])
    for i,v in enumerate([1,3,5,7,9,11,13]):
        box(ax, 0.7+i*1.2, 6.5, 1.0, 0.8, str(v), C['lightblue'], tc=C['text'], fontsize=9)
    ax.text(0.7,5.5,'L →',ha='center',fontsize=10,color=C['red'],fontweight='bold')
    ax.text(8.3,5.5,'← R',ha='center',fontsize=10,color=C['blue'],fontweight='bold')
    ax.text(5,3.0,'Move L right: sum too small\nMove R left: sum too large',
            ha='center',fontsize=8,color=C['text'],
            bbox=dict(boxstyle='round',facecolor=C['lightteal'],alpha=0.8))
    ax.text(5,1.5,'O(n) time, O(1) space',ha='center',fontsize=9,color=C['teal'],fontweight='bold')
    ax = axes[2]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Sliding Window', fontsize=10, color=C['text'])
    for i,ch in enumerate(list('ABCABCBB')):
        color = C['orange'] if 0<=i<=2 else C['lightblue']
        tc = 'white' if 0<=i<=2 else C['text']
        box(ax, 0.6+i*1.1, 6.5, 0.9, 0.8, ch, color, tc=tc, fontsize=9)
    ax.text(5,4.8,'Window [A,B,C] = length 3',ha='center',fontsize=8,color=C['orange'],fontweight='bold')
    ax.text(5,3.0,'Expand right, shrink left\non duplicate',ha='center',fontsize=8,
            color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightorange'],alpha=0.8))
    ax.text(5,1.5,'O(n) time, O(k) space',ha='center',fontsize=9,color=C['teal'],fontweight='bold')
    save(fig, '04-arrays-strings.png')

# ── 05-06: Linked Lists + Stacks/Queues ──────────────────────────────────────
def ch05():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=C['bg'])
    fig.suptitle('Linked Lists — Runner & Cycle Detection', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,8); ax.axis('off')
    ax.set_title('Runner Technique (Kth-to-Last)', fontsize=10, color=C['text'])
    for i,v in enumerate([1,2,3,4,5,6,7]):
        box(ax, 0.7+i*1.2, 5.5, 1.0, 0.8, str(v), C['blue'], fontsize=9)
        if i<6: arr(ax, 1.2+i*1.2, 5.5, 1.5+i*1.2, 5.5)
    ax.text(0.7,4.4,'↑ Slow',ha='center',fontsize=8,color=C['green'])
    ax.text(4.3,4.4,'↑ Fast (k=3 ahead)',ha='center',fontsize=8,color=C['red'])
    ax.text(4.5,2.5,'Fast hits null → Slow is kth-to-last',ha='center',fontsize=9,
            color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightblue'],alpha=0.8))
    ax = axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,8); ax.axis('off')
    ax.set_title("Floyd's Cycle Detection", fontsize=10, color=C['text'])
    for i,v in enumerate([1,2,3,4,5]):
        box(ax, 0.8+i*1.6, 5.5, 1.2, 0.8, str(v), C['blue'], fontsize=9)
        if i<4: arr(ax, 1.4+i*1.6, 5.5, 1.8+i*1.6, 5.5)
    ax.annotate('', xy=(7.2,4.3), xytext=(7.2,5.1),
        arrowprops=dict(arrowstyle='->', color=C['orange'], lw=2))
    ax.annotate('', xy=(2.4,4.3), xytext=(7.2,4.3),
        arrowprops=dict(arrowstyle='->', color=C['orange'], lw=2, connectionstyle='arc3,rad=0.3'))
    ax.text(4.5,2.5,'slow moves 1 step, fast moves 2\nIf they meet → CYCLE detected!',ha='center',
            fontsize=9,color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightorange'],alpha=0.8))
    save(fig, '05-linked-lists.png')

def ch06():
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), facecolor=C['bg'])
    fig.suptitle('Stacks & Queues', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.set_xlim(0,6); ax.set_ylim(0,8); ax.axis('off')
    ax.set_title('Stack (LIFO)', fontsize=10, color=C['text'])
    for i,v in enumerate([10,20,30]):
        box(ax,3,2.2+i*1.4,2.5,1.1,str(v),C['blue'] if i==2 else C['lightblue'],
            tc='white' if i==2 else C['text'])
    ax.text(3,6.5,'← TOP (push/pop here)',ha='center',fontsize=8,color=C['red'])
    ax = axes[1]; ax.set_xlim(0,9); ax.set_ylim(0,8); ax.axis('off')
    ax.set_title('Queue (FIFO)', fontsize=10, color=C['text'])
    for i,v in enumerate([10,20,30]):
        box(ax,1.5+i*2.3,4,2.0,1.1,str(v),C['green'] if i==0 else C['lightgreen'],
            tc='white' if i==0 else C['text'])
    ax.text(1.5,2.5,'FRONT\n(poll)',ha='center',fontsize=8,color=C['green'])
    ax.text(6.1,2.5,'BACK\n(offer)',ha='center',fontsize=8,color=C['blue'])
    ax = axes[2]; ax.set_xlim(0,8); ax.set_ylim(0,8); ax.axis('off')
    ax.set_title('MinStack Design', fontsize=10, color=C['text'])
    ax.text(2.5,7.3,'stack',ha='center',fontsize=9,fontweight='bold',color=C['blue'])
    ax.text(5.5,7.3,'minStack',ha='center',fontsize=9,fontweight='bold',color=C['orange'])
    for i,(v,m) in enumerate([(5,5),(3,3),(7,3),(2,2)]):
        y=6.2-i*1.2
        box(ax,2.5,y,2.5,0.9,str(v),C['blue'],fontsize=9)
        box(ax,5.5,y,2.5,0.9,str(m),C['orange'],fontsize=9)
    ax.text(4,1.2,'getMin() = minStack.peek() → O(1)',ha='center',fontsize=8,
            color=C['teal'],fontweight='bold')
    save(fig, '06-stacks-queues.png')

# ── 07: Trees & Graphs ───────────────────────────────────────────────────────
def ch07():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=C['bg'])
    fig.suptitle('Trees & Graphs — BST + BFS vs DFS', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,9); ax.axis('off')
    ax.set_title('Binary Search Tree', fontsize=10, color=C['text'])
    xs=[5,3,7,1.5,4.5,6,8.5]; ys=[8,6.2,6.2,4.4,4.4,4.4,4.4]; vals=[8,4,10,2,6,9,20]
    for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:
        ax.plot([xs[a],xs[b]],[ys[a]-0.42,ys[b]+0.42],color=C['gray'],lw=1.5)
    for x,y,v in zip(xs,ys,vals): box(ax,x,y,1.1,0.85,str(v),C['blue'],fontsize=10)
    ax.text(5,1.8,'In-order: 2,4,6,8,9,10,20 (always sorted!)',ha='center',fontsize=9,
            color=C['teal'],fontweight='bold',bbox=dict(boxstyle='round',facecolor=C['lightblue'],alpha=0.8))
    ax = axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,9); ax.axis('off')
    ax.set_title('BFS vs DFS', fontsize=10, color=C['text'])
    nxs=[5,3,7,2,4,6]; nys=[8,6.2,6.2,4.4,4.4,4.4]
    for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5)]:
        ax.plot([nxs[a],nxs[b]],[nys[a]-0.4,nys[b]+0.4],color=C['gray'],lw=1.5)
    for x,y,l in zip(nxs,nys,['A','B','C','D','E','F']):
        box(ax,x,y,1.1,0.8,l,C['indigo'],fontsize=11)
    ax.text(2,2.5,'🔵 BFS (Queue):\nA→B→C→D→E→F\nShortest path',ha='center',fontsize=8,
            color=C['blue'],bbox=dict(boxstyle='round',facecolor=C['lightblue'],alpha=0.9))
    ax.text(7.5,2.5,'🟢 DFS (Stack):\nA→B→D→E→C→F\nCycles + paths',ha='center',fontsize=8,
            color=C['green'],bbox=dict(boxstyle='round',facecolor=C['lightgreen'],alpha=0.9))
    save(fig, '07-trees-graphs.png')

# ── 08: Bit Manipulation ─────────────────────────────────────────────────────
def ch08():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=C['bg'])
    fig.suptitle('Bit Manipulation', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('AND, OR, XOR on 1100 & 1010', fontsize=10, color=C['text'])
    for i,(op,a,b,res,col) in enumerate([('AND (&)','1100','1010','1000',C['blue']),
            ('OR  (|)','1100','1010','1110',C['green']),('XOR (^)','1100','1010','0110',C['orange'])]):
        y=8.5-i*2.8; ax.text(0.3,y,op,fontsize=10,fontweight='bold',color=col)
        for j,bit in enumerate(a):
            box(ax,4+j,y,0.8,0.6,bit,C['blue'] if bit=='1' else C['lightblue'],tc='white' if bit=='1' else C['text'],fontsize=9)
        for j,bit in enumerate(b):
            box(ax,4+j,y-0.8,0.8,0.6,bit,C['green'] if bit=='1' else C['lightgreen'],tc='white' if bit=='1' else C['text'],fontsize=9)
        for j,bit in enumerate(res):
            box(ax,4+j,y-1.7,0.8,0.6,bit,col if bit=='1' else C['lightgray'],tc='white' if bit=='1' else C['text'],fontsize=9)
    ax = axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Key Bit Tricks', fontsize=10, color=C['text'])
    for i,(name,code,col) in enumerate([
            ("Check bit i:","(n >> i) & 1",C['blue']),("Set bit i:","n | (1 << i)",C['green']),
            ("Clear bit i:","n & ~(1 << i)",C['orange']),("Toggle bit i:","n ^ (1 << i)",C['purple']),
            ("Power of 2?","n & (n-1) == 0",C['red']),("XOR magic:","a ^ a = 0",C['teal'])]):
        y=9-i*1.4; ax.text(0.3,y,name,fontsize=9,fontweight='bold',color=col)
        ax.text(4.0,y,code,fontsize=9,color=C['text'],family='monospace',
                bbox=dict(boxstyle='round',facecolor=C['lightgray'],alpha=0.9))
    save(fig, '08-bit-manipulation.png')

# ── 09: Dynamic Programming ──────────────────────────────────────────────────
def ch09():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=C['bg'])
    fig.suptitle('Dynamic Programming — Memo vs Tabulation',
                 fontsize=13,fontweight='bold',color=C['text'])
    ax = axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Top-Down (Memoization) — fib(5)', fontsize=10, color=C['text'])
    nd=[(5,9,'fib(5)'),(3,7,'fib(4)'),(7,7,'fib(3)'),(2,5,'fib(3)'),(4.5,5,'fib(2)'),(6,5,'fib(2)'),(8,5,'fib(1)')]
    clrs=[C['blue'],C['blue'],C['orange'],C['orange'],C['orange'],C['lightblue'],C['lightblue']]
    for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:
        ax.plot([nd[a][0],nd[b][0]],[nd[a][1]-0.35,nd[b][1]+0.35],color=C['gray'],lw=1.5)
    for (x,y,label),cl in zip(nd,clrs): box(ax,x,y,1.8,0.7,label,cl,fontsize=8)
    ax.text(5,2.8,'🟠 fib(3) computed TWICE\nMemoize: O(2ⁿ) → O(n)',ha='center',fontsize=9,
            color=C['orange'],bbox=dict(boxstyle='round',facecolor=C['lightorange'],alpha=0.9))
    ax = axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Bottom-Up (Tabulation) — Fibonacci', fontsize=10, color=C['text'])
    for i,v in enumerate([0,1,1,2,3,5,8,13]):
        box(ax,0.8+i*1.05,6.5,0.9,0.8,str(v),C['blue'] if i<7 else C['green'],fontsize=9)
        ax.text(0.8+i*1.05,5.7,f'dp[{i}]',ha='center',fontsize=7,color=C['gray'])
    ax.text(5,4.2,'dp[i] = dp[i-1] + dp[i-2]',ha='center',fontsize=10,fontweight='bold',
            color=C['teal'],bbox=dict(boxstyle='round',facecolor=C['lightteal'],alpha=0.9))
    ax.text(5,1.5,'Time O(n) | Space O(n) or O(1) optimized',ha='center',fontsize=9,
            color=C['green'],fontweight='bold')
    save(fig, '09-dynamic-programming.png')

# ── 10: Sorting ──────────────────────────────────────────────────────────────
def ch10():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor=C['bg'])
    fig.suptitle('Sorting Algorithms', fontsize=13, fontweight='bold', color=C['text'])
    ax = axes[0]; ax.axis('off'); ax.set_title('Complexity', fontsize=10, color=C['text'])
    data=[['Algorithm','Avg','Worst','Space','Stable'],
          ['Bubble','O(n²)','O(n²)','O(1)','✅'],['Selection','O(n²)','O(n²)','O(1)','❌'],
          ['Insertion','O(n²)','O(n²)','O(1)','✅'],['Merge','O(n logn)','O(n logn)','O(n)','✅'],
          ['Quick','O(n logn)','O(n²)','O(logn)','❌'],['Heap','O(n logn)','O(n logn)','O(1)','❌'],
          ['Counting','O(n+k)','O(n+k)','O(k)','✅']]
    cc=[[C['lightblue']]*5]*4+[[C['lightgreen']]*5]*3
    t=ax.table(cellText=data,cellLoc='center',loc='center',cellColours=[[C['indigo']]*5]+cc)
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.2,1.6)
    ax=axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('QuickSort Partition', fontsize=10, color=C['text'])
    for i,v in enumerate([3,1,4,1,5,9,2,6]):
        box(ax,0.6+i*1.1,7.8,0.9,0.8,str(v),C['red'] if i==7 else C['blue'],fontsize=9)
    ax.text(5,6.5,'↓ after partition (pivot=6)',ha='center',fontsize=9,color=C['gray'])
    for i,v in enumerate([3,1,4,1,2,6,5,9]):
        box(ax,0.6+i*1.1,5.5,0.9,0.8,str(v),C['lightblue'] if i<5 else C['lightorange'],tc=C['text'],fontsize=9)
    ax.text(5,3.0,'Avg: O(n log n)  Worst: O(n²)\nUse random pivot to avoid worst case',
            ha='center',fontsize=9,color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightgray'],alpha=0.9))
    save(fig, '10-sorting-algorithms.png')

# ── 11: System Design ────────────────────────────────────────────────────────
def ch11():
    fig, ax = plt.subplots(figsize=(13,7), facecolor=C['bg'])
    ax.set_xlim(0,13); ax.set_ylim(0,7); ax.axis('off')
    fig.suptitle('System Design — Scalability Ladder', fontsize=13, fontweight='bold', color=C['text'])
    stages=[(1.2,5.5,'Single Server\n<1K',C['blue']),(3.9,5.5,'Separate DB\n<10K',C['teal']),
            (7.0,5.5,'LB + Replicas\n<1M',C['green']),(10.8,5.5,'Cache+CDN\nSharding\n<100M+',C['orange'])]
    for x,y,label,color in stages: box(ax,x,y,2.2,1.5,label,color,fontsize=8)
    for i in range(3): arr(ax,stages[i][0]+1.1,5.5,stages[i+1][0]-1.1,5.5)
    for x,y,label,color in [(3.9,3.0,'MySQL',C['purple']),(7.0,3.0,'Primary\n+Replicas',C['purple']),
                             (9.2,3.0,'Redis\nCache',C['red']),(11.8,3.0,'CDN',C['teal'])]:
        box(ax,x,y,1.8,1.0,label,color,fontsize=8)
    arr(ax,3.9,4.75,3.9,3.5); arr(ax,7.0,4.75,7.0,3.5)
    ax.annotate('',xy=(9.2,3.5),xytext=(10.8,4.75),arrowprops=dict(arrowstyle='->',color=C['gray'],lw=1.5))
    ax.annotate('',xy=(11.8,3.5),xytext=(10.8,4.75),arrowprops=dict(arrowstyle='->',color=C['gray'],lw=1.5))
    ax.text(6.5,1.2,'Cache 80%+ hits | Shard: hash(id) % N | CDN: static assets',
            ha='center',fontsize=9,color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightblue'],alpha=0.9))
    save(fig, '11-system-design.png')

# ── 12: Threads & Locks ──────────────────────────────────────────────────────
def ch12():
    fig, axes = plt.subplots(1, 2, figsize=(13,6), facecolor=C['bg'])
    fig.suptitle('Threads & Locks — Deadlock & Dining Philosophers',
                 fontsize=13,fontweight='bold',color=C['text'])
    ax=axes[0]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Deadlock — Circular Wait', fontsize=10, color=C['text'])
    box(ax,2.5,7.5,3.0,1.2,'🧵 Thread 1\nholds Lock A',C['blue'])
    box(ax,7.5,7.5,3.0,1.2,'🧵 Thread 2\nholds Lock B',C['orange'])
    ax.annotate('',xy=(6.0,7.5),xytext=(4.0,7.5),
        arrowprops=dict(arrowstyle='->',color=C['red'],lw=2.5,connectionstyle='arc3,rad=-0.4'))
    ax.text(5,8.6,'wants B →',ha='center',fontsize=8,color=C['red'])
    ax.annotate('',xy=(4.0,7.5),xytext=(6.0,7.5),
        arrowprops=dict(arrowstyle='->',color=C['red'],lw=2.5,connectionstyle='arc3,rad=0.4'))
    ax.text(5,6.5,'← wants A',ha='center',fontsize=8,color=C['red'])
    ax.text(5,4.5,'4 CONDITIONS:\n1. Mutual Exclusion\n2. Hold & Wait\n3. No Preemption\n4. Circular Wait',
            ha='center',fontsize=8,color=C['text'],bbox=dict(boxstyle='round',facecolor=C['lightred'],alpha=0.8))
    ax.text(5,1.5,'✅ FIX: Always acquire locks\nin the same consistent order!',ha='center',
            fontsize=9,fontweight='bold',color=C['green'],bbox=dict(boxstyle='round',facecolor=C['lightgreen'],alpha=0.9))
    ax=axes[1]; ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
    ax.set_title('Dining Philosophers', fontsize=10, color=C['text'])
    for i in range(5):
        angle=np.pi/2+i*2*np.pi/5
        px,py=5+3.0*np.cos(angle),5.5+3.0*np.sin(angle)
        box(ax,px,py,1.5,0.85,f'P{i+1}',C['blue'],fontsize=9)
        fangle=angle+np.pi/5; fx,fy=5+1.8*np.cos(fangle),5.5+1.8*np.sin(fangle)
        box(ax,fx,fy,0.8,0.8,f'F{i+1}',C['orange'],fontsize=8)
    ax.text(5,1.0,'FIX: Semaphore(4) → max 4 try simultaneously',
            ha='center',fontsize=9,fontweight='bold',color=C['green'],
            bbox=dict(boxstyle='round',facecolor=C['lightgreen'],alpha=0.9))
    save(fig, '12-threads-locks.png')

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Generating CTCI diagrams...")
    ch01(); ch02(); ch03(); ch04(); ch05(); ch06()
    ch07(); ch08(); ch09(); ch10(); ch11(); ch12()
    print(f"\n✅ All 12 diagrams saved to: {OUTPUT_DIR}")
