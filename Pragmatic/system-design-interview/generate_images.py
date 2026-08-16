#!/usr/bin/env python3
"""
Generate architecture diagrams for System Design Interview (Vol. 1, 2nd Edition) chapters.
Run: python3 generate_images.py
Requires: pip install matplotlib numpy
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'blue': '#2196F3', 'lightblue': '#BBDEFB', 'darkblue': '#1565C0',
    'green': '#4CAF50', 'lightgreen': '#C8E6C9',
    'orange': '#FF9800', 'lightorange': '#FFE0B2',
    'purple': '#9C27B0', 'lightpurple': '#E1BEE7',
    'red': '#F44336', 'lightred': '#FFCDD2',
    'teal': '#009688', 'lightteal': '#B2DFDB',
    'bg': '#F8F9FA', 'text': '#212121', 'border': '#424242',
    'gray': '#9E9E9E', 'lightgray': '#F5F5F5',
    'amber': '#FFC107',
}

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close(fig)
    print(f"  ✓ {name}")

def box(ax, x, y, w, h, label, color, fontsize=9, text_color='white', radius=0.3):
    fancy = FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad={radius}", facecolor=color, edgecolor='white', linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight='bold', zorder=4, wrap=True)

def arrow(ax, x1, y1, x2, y2, color='#424242', label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my, label, ha='center', va='center', fontsize=7, color=color,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.9))

# ─── Chapter 1: Scale From Zero ──────────────────────────────────────────────
def ch01_scale():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 1: Scale From Zero to Millions of Users', fontsize=13, fontweight='bold', color=COLORS['text'])

    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Single Server Setup', fontsize=10, color=COLORS['text'])
    box(ax, 5, 8.5, 3, 0.9, '👤 Users', COLORS['blue'])
    box(ax, 5, 6.5, 3, 0.9, '🌐 DNS', COLORS['teal'])
    box(ax, 5, 4.5, 3, 0.9, '🖥 Web Server\n(App + DB)', COLORS['orange'])
    arrow(ax, 5, 8.0, 5, 7.0, label='query')
    arrow(ax, 5, 6.0, 5, 5.0, label='IP')

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Multi-tier + CDN + Cache', fontsize=10, color=COLORS['text'])
    box(ax, 5, 9.3, 4, 0.8, '👤 Users', COLORS['blue'])
    box(ax, 2, 7.8, 2.5, 0.8, '📦 CDN', COLORS['green'])
    box(ax, 7, 7.8, 2.5, 0.8, '⚖ Load Balancer', COLORS['orange'])
    box(ax, 5.5, 6.2, 2, 0.8, '🖥 App Server 1', COLORS['purple'])
    box(ax, 8.5, 6.2, 2, 0.8, '🖥 App Server 2', COLORS['purple'])
    box(ax, 4, 4.5, 2, 0.8, '⚡ Cache\n(Redis)', COLORS['teal'])
    box(ax, 7, 4.5, 2, 0.8, '🗄 DB\n(Primary)', COLORS['red'])
    box(ax, 9, 4.5, 1.5, 0.8, '🗄 DB Replica', COLORS['lightred'], text_color=COLORS['text'])
    arrow(ax, 5, 9.0, 2, 8.2); arrow(ax, 5, 9.0, 7, 8.2)
    arrow(ax, 7, 7.4, 5.5, 6.6); arrow(ax, 7, 7.4, 8.5, 6.6)
    arrow(ax, 5.5, 5.8, 4, 4.9); arrow(ax, 5.5, 5.8, 7, 4.9)
    arrow(ax, 7, 4.5, 9, 4.5, label='replicate')

    save(fig, '01-scale-from-zero.png')

# ─── Chapter 2: Estimation ───────────────────────────────────────────────────
def ch02_estimation():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Chapter 2: Back-of-Envelope Estimation Cheat Sheet', fontsize=13, fontweight='bold', color=COLORS['text'])

    data = [
        ('⚡ Powers of 2', '#1565C0', [
            '2^10 = 1KB (Kilobyte)',
            '2^20 = 1MB (Megabyte)',
            '2^30 = 1GB (Gigabyte)',
            '2^40 = 1TB (Terabyte)',
            '2^50 = 1PB (Petabyte)',
        ]),
        ('⏱ Latency Numbers', '#2E7D32', [
            'L1 cache: 1 nanosecond',
            'Main memory: 100 ns',
            'SSD: 150μs',
            'Network round trip (DC): 500μs',
            'Disk seek: 10ms',
        ]),
        ('📊 Availability', '#E65100', [
            '99%: 3.65 days down/year',
            '99.9%: 8.77 hours down/year',
            '99.99%: 52.6 min down/year',
            '99.999%: 5.26 min down/year',
            '11 nines: ~0 seconds',
        ]),
    ]

    for i, (title, color, items) in enumerate(data):
        x_start = 0.5 + i * 3.8
        fancy = FancyBboxPatch((x_start, 1.0), 3.3, 6.0,
            boxstyle="round,pad=0.2", facecolor=color+'20', edgecolor=color, linewidth=2)
        ax.add_patch(fancy)
        ax.text(x_start + 1.65, 6.7, title, ha='center', fontsize=10, fontweight='bold', color=color)
        for j, item in enumerate(items):
            ax.text(x_start + 0.2, 5.9 - j * 1.0, f'• {item}', fontsize=8.5, color=COLORS['text'])

    save(fig, '02-estimation-cheatsheet.png')

# ─── Chapter 3: Interview Framework ──────────────────────────────────────────
def ch03_framework():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Chapter 3: 4-Step System Design Interview Framework', fontsize=13, fontweight='bold', color=COLORS['text'])

    steps = [
        (1.5, 6, '① UNDERSTAND\nthe Problem\n(3-10 min)', COLORS['blue'],
         ['What features to build?', 'Read/write ratio?', 'Mobile or web?', 'How many users?', 'SQL or NoSQL?']),
        (4.5, 6, '② PROPOSE\nHigh-Level Design\n(10-15 min)', COLORS['green'],
         ['Draw box diagram', 'API endpoints', 'Back-of-envelope math', 'Propose data model', 'Discuss with interviewer']),
        (7.5, 6, '③ DEEP DIVE\ninto Design\n(10-25 min)', COLORS['orange'],
         ['Focus on bottlenecks', 'Scale components', 'DB schema detail', 'Algorithm detail', 'Handle failures']),
        (10.5, 6, '④ WRAP UP\n& Discuss\n(3-5 min)', COLORS['purple'],
         ['Recap the design', 'Identify trade-offs', 'Monitor & alerts', 'Error handling', 'Future improvements']),
    ]

    for i, (x, y, label, color, bullets) in enumerate(steps):
        box(ax, x, y, 2.5, 1.6, label, color, fontsize=9)
        for j, b in enumerate(bullets):
            ax.text(x, 4.3 - j * 0.55, f'• {b}', ha='center', fontsize=7.5, color=COLORS['text'])
        if i < 3:
            arrow(ax, x + 1.3, y, x + 2.2, y, label='then')

    ax.text(6, 0.8, '"Never jump straight to a solution — understand the problem first."',
            ha='center', fontsize=10, style='italic', color=COLORS['gray'])

    save(fig, '03-interview-framework.png')

# ─── Chapter 4: Rate Limiter ─────────────────────────────────────────────────
def ch04_rate_limiter():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 4: Rate Limiter — Algorithms & Architecture', fontsize=13, fontweight='bold', color=COLORS['text'])

    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Token Bucket Algorithm', fontsize=10, color=COLORS['text'])
    fancy = FancyBboxPatch((2, 3), 6, 5, boxstyle="round,pad=0.3",
        facecolor=COLORS['lightblue'], edgecolor=COLORS['blue'], linewidth=2)
    ax.add_patch(fancy)
    ax.text(5, 7.5, '🪣 Token Bucket', ha='center', fontsize=11, fontweight='bold', color=COLORS['darkblue'])
    for i in range(4):
        ax.text(3.5 + i * 0.8, 6.5, '🔵', ha='center', fontsize=14)
    ax.text(5, 5.8, 'capacity=10, rate=2/sec', ha='center', fontsize=8, color=COLORS['gray'])
    ax.text(5, 5.2, 'Tokens refilled at fixed rate', ha='center', fontsize=8.5, color=COLORS['text'])
    ax.text(5, 4.6, 'Request uses 1 token', ha='center', fontsize=8.5, color=COLORS['text'])
    ax.text(5, 4.0, 'No token → reject request (429)', ha='center', fontsize=8.5, color=COLORS['red'])
    box(ax, 2, 1.5, 2, 0.8, '✅ Allow', COLORS['green'])
    box(ax, 8, 1.5, 2, 0.8, '❌ Reject (429)', COLORS['red'])
    arrow(ax, 5, 3.0, 3, 1.9, label='token?')
    arrow(ax, 5, 3.0, 7, 1.9, label='no token')

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Rate Limiter Architecture', fontsize=10, color=COLORS['text'])
    box(ax, 5, 9.0, 4, 0.8, '🌐 Client Request', COLORS['blue'])
    box(ax, 5, 7.2, 4, 0.8, '🚦 Rate Limiter\nMiddleware', COLORS['orange'])
    box(ax, 3, 5.4, 2.5, 0.8, '⚡ Redis\n(counters)', COLORS['red'])
    box(ax, 7, 5.4, 2.5, 0.8, '📋 Rules\n(config)', COLORS['purple'])
    box(ax, 5, 3.5, 4, 0.8, '🖥 API Server', COLORS['green'])
    box(ax, 5, 1.8, 4, 0.8, '🗄 Database', COLORS['teal'])
    arrow(ax, 5, 8.6, 5, 7.6)
    arrow(ax, 5, 6.8, 3, 5.8, label='check count')
    arrow(ax, 5, 6.8, 7, 5.8, label='get rule')
    arrow(ax, 5, 6.8, 5, 3.9, label='allowed')
    arrow(ax, 5, 3.1, 5, 2.2)

    save(fig, '04-rate-limiter.png')

# ─── Chapter 5: Consistent Hashing ──────────────────────────────────────────
def ch05_consistent_hashing():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 5: Consistent Hashing — Ring Topology', fontsize=13, fontweight='bold', color=COLORS['text'])

    ax = axes[0]
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Hash Ring (4 Servers)', fontsize=10, color=COLORS['text'])
    circle = plt.Circle((0, 0), 1.2, fill=False, color=COLORS['blue'], linewidth=3)
    ax.add_patch(circle)
    servers = [('Server A', 0), ('Server B', 90), ('Server C', 180), ('Server D', 270)]
    keys = [('Key 1', 30), ('Key 2', 120), ('Key 3', 210), ('Key 4', 315)]
    colors_s = [COLORS['red'], COLORS['green'], COLORS['orange'], COLORS['purple']]
    for (name, angle), color in zip(servers, colors_s):
        rad = np.radians(angle)
        ax.plot(1.2*np.cos(rad), 1.2*np.sin(rad), 'o', ms=14, color=color)
        ax.text(1.35*np.cos(rad), 1.35*np.sin(rad), name, ha='center', va='center', fontsize=8, fontweight='bold', color=color)
    for (name, angle) in keys:
        rad = np.radians(angle)
        ax.plot(1.2*np.cos(rad), 1.2*np.sin(rad), '^', ms=8, color=COLORS['teal'])
        ax.text(1.0*np.cos(rad), 1.0*np.sin(rad), name, ha='center', va='center', fontsize=7.5, color=COLORS['teal'])

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Virtual Nodes', fontsize=10, color=COLORS['text'])
    fancy = FancyBboxPatch((0.5, 1), 9, 8.2, boxstyle="round,pad=0.3",
        facecolor=COLORS['lightgray'], edgecolor=COLORS['gray'], linewidth=1)
    ax.add_patch(fancy)
    rows = [
        ('Regular (3 servers)', ['S1', 'S3', 'S2', 'S1', 'S2', 'S3'], ['', '', 'empty', 'S1-heavy', '', '']),
        ('Virtual Nodes (3 servers\n× 3 virtual = 9 nodes)',
         ['S1-1','S2-1','S3-1','S1-2','S2-2','S3-2','S1-3','S2-3','S3-3'], []),
    ]
    colors_srv = {'S1':'#F44336','S2':'#4CAF50','S3':'#2196F3',
                  'S1-1':'#F44336','S1-2':'#F44336','S1-3':'#F44336',
                  'S2-1':'#4CAF50','S2-2':'#4CAF50','S2-3':'#4CAF50',
                  'S3-1':'#2196F3','S3-2':'#2196F3','S3-3':'#2196F3', '':'#9E9E9E', 'empty':'#9E9E9E', 'S1-heavy':'#9E9E9E'}
    ax.text(5, 8.8, 'Problem: Uneven distribution without virtual nodes', ha='center', fontsize=9, color=COLORS['red'])
    for j, label in enumerate(['S1','S3','S2']):
        x = 2 + j*1.5
        c = {'S1': COLORS['red'], 'S2': COLORS['green'], 'S3': COLORS['blue']}[label]
        ax.add_patch(FancyBboxPatch((x-0.5, 7.2), 1, 0.7, boxstyle="round,pad=0.1", facecolor=c))
        ax.text(x, 7.55, label, ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    ax.text(5, 6.8, 'vs. Virtual Nodes: each server has multiple positions on ring', ha='center', fontsize=9, color=COLORS['green'])
    ax.text(5, 6.2, '→ More uniform distribution, easy to add/remove servers', ha='center', fontsize=9, color=COLORS['text'])
    ax.text(5, 5.5, 'Adding Server E: only keys between E\'s position and previous', ha='center', fontsize=8.5, color=COLORS['text'])
    ax.text(5, 4.9, 'server move to E. All other keys unaffected.', ha='center', fontsize=8.5, color=COLORS['text'])
    ax.text(5, 4.1, 'Used by: Amazon Dynamo, Apache Cassandra, Riak', ha='center', fontsize=9, color=COLORS['blue'], fontweight='bold')

    save(fig, '05-consistent-hashing.png')

# ─── Chapter 6: Key-Value Store ──────────────────────────────────────────────
def ch06_kv_store():
    fig, ax = plt.subplots(figsize=(13, 8), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Chapter 6: Key-Value Store — Write Path (LSM Tree)', fontsize=13, fontweight='bold', color=COLORS['text'])

    box(ax, 2, 7, 2.5, 0.9, '📝 Write Request\nput(k, v)', COLORS['blue'])
    box(ax, 2, 5.5, 2.5, 0.9, '📋 WAL\n(Write-Ahead Log)', COLORS['green'])
    box(ax, 2, 4, 2.5, 0.9, '🧠 MemTable\n(in-memory, sorted)', COLORS['orange'])
    box(ax, 2, 2.5, 2.5, 0.9, '📂 SSTable\n(immutable on disk)', COLORS['purple'])
    box(ax, 6, 2.5, 2.5, 0.9, '📂 SSTable\nLevel 1', COLORS['purple'])
    box(ax, 10, 2.5, 2.5, 0.9, '📂 SSTable\nLevel 2 (bigger)', COLORS['darkblue'])
    box(ax, 2, 1, 2.5, 0.9, '💾 Bloom Filter\n(fast miss detection)', COLORS['teal'])

    arrow(ax, 2, 6.55, 2, 5.95, label='1. persist')
    arrow(ax, 2, 5.05, 2, 4.45, label='2. write')
    arrow(ax, 2, 3.55, 2, 2.95, label='3. flush when full')
    arrow(ax, 3.3, 2.5, 4.8, 2.5, label='4. compact')
    arrow(ax, 7.3, 2.5, 8.8, 2.5, label='5. compact')

    ax.text(7.5, 5.5, 'READ PATH:', fontsize=11, fontweight='bold', color=COLORS['text'])
    read_steps = [
        '1. Check MemTable (fastest)',
        '2. Check Bloom Filter → skip SSTable if key absent',
        '3. Check SSTable Level 0 → 1 → 2 (oldest data)',
        '',
        'Bloom Filter: probabilistic structure',
        '  - "Key NOT here" = 100% certain → skip file',
        '  - "Key here" = might be here → check file',
        '',
        'Compaction: merges SSTables, removes deleted keys',
        '  - Keeps data sorted for O(log N) binary search',
    ]
    for i, step in enumerate(read_steps):
        ax.text(7.5, 4.9 - i * 0.45, step, fontsize=8.5, color=COLORS['text'])

    save(fig, '06-key-value-store.png')

# ─── Chapter 7: Unique ID Generator ─────────────────────────────────────────
def ch07_unique_id():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 7: Unique ID Generator — Twitter Snowflake', fontsize=13, fontweight='bold', color=COLORS['text'])

    # 64-bit layout
    segments = [
        (0.3, 1, '0\n(sign bit)', COLORS['gray'], '1 bit'),
        (1.3, 5, 'Timestamp\n(ms since epoch)', COLORS['blue'], '41 bits'),
        (6.8, 2, 'Datacenter\nID', COLORS['green'], '5 bits'),
        (8.8, 2, 'Machine\nID', COLORS['orange'], '5 bits'),
        (10.8, 2, 'Sequence\nNumber', COLORS['purple'], '12 bits'),
    ]

    ax.text(6.5, 6.5, '64-bit Snowflake ID Layout', ha='center', fontsize=11, fontweight='bold', color=COLORS['text'])
    y_box = 5.2
    x = 0
    widths = [1, 5, 2, 2, 2]
    for i, (_, w, label, color, bits) in enumerate(segments):
        fancy = FancyBboxPatch((x + 0.1, y_box - 0.5), w - 0.2, 1.0,
            boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(fancy)
        ax.text(x + w/2, y_box, label, ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        ax.text(x + w/2, y_box - 0.8, bits, ha='center', fontsize=8, color=color)
        x += w

    props_x = 0.5
    props = [
        ('41-bit Timestamp', '2^41 ms ≈ 69 years from epoch', COLORS['blue']),
        ('5-bit Datacenter ID', '2^5 = 32 datacenters supported', COLORS['green']),
        ('5-bit Machine ID', '2^5 = 32 machines per datacenter', COLORS['orange']),
        ('12-bit Sequence', '2^12 = 4096 IDs per machine per millisecond', COLORS['purple']),
    ]
    ax.text(0.5, 3.8, 'Properties:', fontsize=10, fontweight='bold', color=COLORS['text'])
    for i, (title, desc, color) in enumerate(props):
        ax.add_patch(FancyBboxPatch((props_x, 3.0 - i * 0.7), 12, 0.55,
            boxstyle="round,pad=0.1", facecolor=color+'25', edgecolor=color, linewidth=1.5))
        ax.text(props_x + 0.2, 3.3 - i * 0.7, f'• {title}: {desc}', fontsize=9, color=COLORS['text'])

    ax.text(6.5, 0.4, 'Total throughput: 32 DC × 32 machines × 4096/ms = 4,194,304 unique IDs/ms',
            ha='center', fontsize=9.5, fontweight='bold', color=COLORS['darkblue'])

    save(fig, '07-unique-id-generator.png')

# ─── Chapter 8: URL Shortener ────────────────────────────────────────────────
def ch08_url_shortener():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 8: URL Shortener — Encode/Decode Design', fontsize=13, fontweight='bold', color=COLORS['text'])

    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('URL Shortening Flow', fontsize=10, color=COLORS['text'])
    box(ax, 5, 9, 4, 0.8, '👤 User: POST /api/v1/data\n{"longUrl": "https://very.long..."}', COLORS['blue'], fontsize=8)
    box(ax, 5, 7.3, 4, 0.8, '🖥 API Server', COLORS['green'])
    box(ax, 2, 5.5, 3, 0.8, '🔢 ID Generator\n(unique ID)', COLORS['orange'])
    box(ax, 8, 5.5, 3, 0.8, '🔤 Base62 Encoder\n[a-zA-Z0-9]', COLORS['purple'])
    box(ax, 5, 3.8, 4, 0.8, '🗄 Database\n(id, shortURL, longURL)', COLORS['teal'])
    box(ax, 5, 2.1, 4, 0.8, '📤 Return: https://tinyurl.com/Y7keocwj', COLORS['green'], fontsize=8)
    arrow(ax, 5, 8.6, 5, 7.7)
    arrow(ax, 5, 6.9, 2, 5.9, label='get ID')
    arrow(ax, 2, 5.1, 4, 4.2, label='ID=123456')
    arrow(ax, 4, 4.2, 6, 5.1, label='encode')
    arrow(ax, 5, 3.4, 5, 2.5, label='store + return')

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Redirection Flow (301 vs 302)', fontsize=10, color=COLORS['text'])
    box(ax, 5, 9, 4, 0.8, '👤 Browser: GET tinyurl.com/abc', COLORS['blue'])
    box(ax, 5, 7.2, 4, 0.8, '🖥 Load Balancer\n+ Web Server', COLORS['green'])
    box(ax, 2, 5.4, 3, 0.8, '⚡ Cache\n(shortURL→longURL)', COLORS['orange'])
    box(ax, 8, 5.4, 3, 0.8, '🗄 Database', COLORS['purple'])
    box(ax, 5, 3.6, 4, 0.8, '↩ 301/302 Redirect\nLocation: longURL', COLORS['teal'])
    arrow(ax, 5, 8.6, 5, 7.6)
    arrow(ax, 5, 6.8, 2, 5.8, label='cache hit?')
    arrow(ax, 2, 5.0, 4.3, 4.0, label='found')
    arrow(ax, 3, 5.4, 7, 5.4, label='miss→DB')
    arrow(ax, 8, 5.0, 6.5, 4.0)

    y = 2.2
    ax.text(1, y, '301 Permanent:', fontsize=9, fontweight='bold', color=COLORS['red'])
    ax.text(1, y-0.5, '• Browser caches redirect', fontsize=8.5, color=COLORS['text'])
    ax.text(1, y-1.0, '• Less load on servers', fontsize=8.5, color=COLORS['text'])
    ax.text(1, y-1.5, '• Analytics harder (browser bypasses)', fontsize=8.5, color=COLORS['text'])
    ax.text(6, y, '302 Temporary:', fontsize=9, fontweight='bold', color=COLORS['green'])
    ax.text(6, y-0.5, '• Always hits your server', fontsize=8.5, color=COLORS['text'])
    ax.text(6, y-1.0, '• Better for analytics', fontsize=8.5, color=COLORS['text'])
    ax.text(6, y-1.5, '• More load on server', fontsize=8.5, color=COLORS['text'])

    save(fig, '08-url-shortener.png')

# ─── Chapters 9-16 quick diagrams ────────────────────────────────────────────
def ch09_web_crawler():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 9: Web Crawler Architecture', fontsize=13, fontweight='bold', color=COLORS['text'])
    box(ax, 1.5, 6, 2, 0.8, '🌱 Seed URLs', COLORS['green'])
    box(ax, 1.5, 4.5, 2, 0.8, '📋 URL Frontier\n(priority queue)', COLORS['blue'])
    box(ax, 4.5, 4.5, 2, 0.8, '📥 HTML\nDownloader', COLORS['orange'])
    box(ax, 4.5, 6, 2, 0.8, '🤖 DNS\nResolver', COLORS['teal'])
    box(ax, 7.5, 4.5, 2, 0.8, '🧠 Content\nParser', COLORS['purple'])
    box(ax, 7.5, 6, 2, 0.8, '✅ Seen?\nBloom Filter', COLORS['red'])
    box(ax, 10.5, 4.5, 2, 0.8, '🔗 URL\nExtractor', COLORS['green'])
    box(ax, 10.5, 6, 2, 0.8, '🗄 Content\nStore', COLORS['darkblue'])
    arrow(ax, 1.5, 5.6, 1.5, 4.9)
    arrow(ax, 2.5, 4.5, 3.5, 4.5)
    arrow(ax, 4.5, 5.6, 4.5, 4.9, label='resolve')
    arrow(ax, 5.5, 4.5, 6.5, 4.5)
    arrow(ax, 7.5, 5.6, 7.5, 4.9, label='check')
    arrow(ax, 8.5, 4.5, 9.5, 4.5)
    arrow(ax, 10.5, 5.6, 10.5, 4.9, label='save')
    arrow(ax, 10.5, 4.1, 1.5, 4.1, label='new URLs → back to frontier')
    notes = ['Politeness: one request per domain at a time (robots.txt)', 
             'BFS traversal from seed URLs', 'Bloom Filter: O(1) seen-URL check',
             'Priority: high-PageRank URLs first', 'Distributed: many downloader workers']
    for i, n in enumerate(notes):
        ax.text(0.5, 2.5 - i * 0.55, f'• {n}', fontsize=9, color=COLORS['text'])
    save(fig, '09-web-crawler.png')

def ch10_notification():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 10: Notification System — Multi-channel Fan-out', fontsize=13, fontweight='bold', color=COLORS['text'])
    box(ax, 1.5, 6.2, 2, 0.8, '🔔 Notification\nService', COLORS['blue'])
    box(ax, 1.5, 4.5, 2, 0.8, '💬 Message Queue\n(Kafka)', COLORS['orange'])
    channels = [('📱 iOS\n(APNs)', 4.5, 6.2, COLORS['darkblue']),
                ('🤖 Android\n(FCM)', 6.5, 6.2, COLORS['green']),
                ('📧 Email\n(Sendgrid)', 8.5, 6.2, COLORS['purple']),
                ('💬 SMS\n(Twilio)', 10.5, 6.2, COLORS['teal'])]
    for label, x, y, c in channels:
        box(ax, x, y, 1.8, 0.8, label, c, fontsize=8)
        arrow(ax, 2.5, 4.5, x, 5.8)
    arrow(ax, 1.5, 5.8, 1.5, 4.9)
    notes = ['Notification Service: creates/updates/manages notifications',
             'Kafka decouples producers from consumers (retry on failure)',
             'APNs = Apple Push Notification Service (iOS)',
             'FCM = Firebase Cloud Messaging (Android)',
             'Worker per channel: independently scalable',
             'Retry with exponential backoff for failed deliveries',
             'Deduplication: prevent duplicate notifications']
    for i, n in enumerate(notes):
        ax.text(0.3, 3.2 - i * 0.52, f'• {n}', fontsize=9, color=COLORS['text'])
    save(fig, '10-notification-system.png')

def ch11_news_feed():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 11: News Feed — Push vs. Pull', fontsize=13, fontweight='bold', color=COLORS['text'])
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Fan-out on Write (Push Model)', fontsize=10, color=COLORS['text'])
    box(ax, 5, 7.3, 3, 0.7, '✍️ User publishes post', COLORS['blue'])
    box(ax, 5, 6.0, 3, 0.7, '📬 Feed Service', COLORS['orange'])
    for i, (x, label) in enumerate([(2,'Friend A'), (5,'Friend B'), (8,'Friend C')]):
        box(ax, x, 4.5, 2, 0.7, f'📥 {label}\nFeed Cache', COLORS['green'])
        arrow(ax, 5, 5.65, x, 4.85, label='push')
    ax.text(5, 2.5, '✅ Read is fast (pre-built feed)\n❌ Celebrity problem (millions of writes)', ha='center', fontsize=9, color=COLORS['text'])

    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Fan-out on Read (Pull Model)', fontsize=10, color=COLORS['text'])
    box(ax, 5, 7.3, 3, 0.7, '👀 User loads feed', COLORS['blue'])
    box(ax, 5, 6.0, 3, 0.7, '📰 Feed Aggregator', COLORS['orange'])
    for i, (x, label) in enumerate([(2,'Followee A'), (5,'Followee B'), (8,'Followee C')]):
        box(ax, x, 4.5, 2, 0.7, f'🗄 {label}\nPosts', COLORS['purple'])
        arrow(ax, x, 4.85, 5, 5.65, label='fetch')
    ax.text(5, 2.5, '✅ No wasted writes for celebrities\n❌ Slow feed load (many DB queries)', ha='center', fontsize=9, color=COLORS['text'])
    ax.text(5, 1.5, '★ HYBRID: Push for regular users, Pull for celebrities', ha='center', fontsize=10, fontweight='bold', color=COLORS['darkblue'])
    save(fig, '11-news-feed.png')

def ch12_chat():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 12: Chat System — WebSocket & Storage Design', fontsize=13, fontweight='bold', color=COLORS['text'])
    box(ax, 1.5, 6.2, 2, 0.8, '📱 Client A', COLORS['blue'])
    box(ax, 11.5, 6.2, 2, 0.8, '📱 Client B', COLORS['blue'])
    box(ax, 4.5, 6.2, 2, 0.8, '🔌 Chat Server 1\n(WebSocket)', COLORS['green'])
    box(ax, 8.5, 6.2, 2, 0.8, '🔌 Chat Server 2\n(WebSocket)', COLORS['green'])
    box(ax, 6.5, 4.5, 2, 0.8, '⚡ Redis\nPub/Sub', COLORS['red'])
    box(ax, 2.5, 3.0, 3, 0.8, '🧭 Presence\nServer', COLORS['orange'])
    box(ax, 6.5, 3.0, 2.5, 0.8, '🗄 Message DB\n(Cassandra)', COLORS['purple'])
    box(ax, 10.5, 3.0, 2.5, 0.8, '🆔 ID Generator\n(Snowflake)', COLORS['teal'])
    arrow(ax, 2.5, 6.2, 3.5, 6.2, label='WS')
    arrow(ax, 5.5, 6.2, 7.5, 6.2, label='pub/sub')
    arrow(ax, 9.5, 6.2, 10.5, 6.2, label='WS')
    arrow(ax, 4.5, 5.8, 5.5, 4.9, label='store')
    arrow(ax, 8.5, 5.8, 7.5, 4.9)
    notes = ['WebSocket: bidirectional, persistent, low-latency', 
             'Cassandra: write-heavy, no message update/delete in flight',
             'Message ID: must be sortable (Snowflake gives time-ordered IDs)',
             'Presence: heartbeat every 5s, mark offline after 30s no heartbeat',
             'Group chat: each member\'s inbox gets a copy of the message']
    for i, n in enumerate(notes):
        ax.text(0.3, 2.2 - i * 0.5, f'• {n}', fontsize=8.5, color=COLORS['text'])
    save(fig, '12-chat-system.png')

def ch13_autocomplete():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 13: Search Autocomplete — Trie Data Structure', fontsize=13, fontweight='bold', color=COLORS['text'])
    # Trie diagram
    trie_nodes = {
        'root': (3, 6.5),
        'a': (1.5, 5.5), 'b': (3, 5.5), 'c': (4.5, 5.5),
        'ad': (1, 4.5), 'al': (2, 4.5),
        'ado': (0.5, 3.5), 'ads': (1.5, 3.5),
        'aln': (2, 3.5),
    }
    labels = {'root': 'root', 'a': 'a', 'b': 'b', 'c': 'c',
              'ad': 'd', 'al': 'l', 'ado': 'o', 'ads': 's', 'aln': 'n'}
    is_word = {'ads', 'ado', 'aln'}
    for node, (x, y) in trie_nodes.items():
        c = COLORS['red'] if node in is_word else COLORS['lightblue']
        tc = 'white' if node in is_word else COLORS['darkblue']
        circle = plt.Circle((x, y), 0.25, facecolor=c, edgecolor=COLORS['blue'], linewidth=1.5, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, labels[node], ha='center', va='center', fontsize=8, fontweight='bold', color=tc, zorder=4)
    edges = [('root','a'),('root','b'),('root','c'),('a','ad'),('a','al'),('ad','ado'),('ad','ads'),('al','aln')]
    for p, c in edges:
        px, py = trie_nodes[p]; cx, cy = trie_nodes[c]
        ax.plot([px, cx], [py - 0.25, cy + 0.25], 'b-', lw=1.5, zorder=2)

    ax.text(6.5, 6.5, 'Architecture:', fontsize=11, fontweight='bold', color=COLORS['text'])
    box(ax, 9, 6, 2.5, 0.7, '🌐 Client\n(AJAX, debounced)', COLORS['blue'], fontsize=8)
    box(ax, 9, 4.8, 2.5, 0.7, '⚡ Load Balancer', COLORS['green'], fontsize=8)
    box(ax, 7.5, 3.6, 2, 0.7, '🔍 Query\nService', COLORS['orange'], fontsize=8)
    box(ax, 10.5, 3.6, 2, 0.7, '🔄 Trie\nBuilder', COLORS['purple'], fontsize=8)
    box(ax, 9, 2.4, 2.5, 0.7, '🗄 Trie DB\n(Redis/Cassandra)', COLORS['teal'], fontsize=8)
    box(ax, 9, 1.2, 2.5, 0.7, '📊 Log Aggregator\n(builds from queries)', COLORS['red'], fontsize=8)
    arrow(ax, 9, 5.65, 9, 5.15); arrow(ax, 9, 4.45, 7.5, 3.95)
    arrow(ax, 9, 4.45, 10.5, 3.95); arrow(ax, 9, 2.05, 9, 1.55)
    notes = ['• Trie: prefix tree for fast O(p+n) top-k retrieval',
             '• Top suggestions cached at each trie node',
             '• Trie rebuilt offline from query logs (weekly)',
             '• AJAX with 300ms debounce (don\'t query on every keystroke)']
    for i, n in enumerate(notes):
        ax.text(6, 2.5 - i * 0.5, n, fontsize=8.5, color=COLORS['text'])
    save(fig, '13-search-autocomplete.png')

def ch14_youtube():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 14: YouTube — Video Upload & Streaming Pipeline', fontsize=13, fontweight='bold', color=COLORS['text'])
    box(ax, 1.5, 6.5, 2, 0.8, '📱 Client\n(Upload)', COLORS['blue'])
    box(ax, 4.5, 6.5, 2, 0.8, '🌐 API\nServers', COLORS['green'])
    box(ax, 7.5, 6.5, 2, 0.8, '📦 Raw\nStorage\n(S3)', COLORS['orange'])
    box(ax, 10.5, 6.5, 2, 0.8, '🔄 Transcoding\nServers', COLORS['purple'])
    box(ax, 7.5, 4.7, 2, 0.8, '📂 Transcoded\nStorage\n(S3)', COLORS['teal'])
    box(ax, 10.5, 4.7, 2, 0.8, '🌍 CDN', COLORS['red'])
    box(ax, 4.5, 4.7, 2, 0.8, '🗄 Metadata\nDB', COLORS['darkblue'])
    box(ax, 1.5, 4.7, 2, 0.8, '📱 Client\n(Watch)', COLORS['blue'])
    arrow(ax, 2.5, 6.5, 3.5, 6.5); arrow(ax, 5.5, 6.5, 6.5, 6.5)
    arrow(ax, 8.5, 6.5, 9.5, 6.5)
    arrow(ax, 10.5, 6.1, 10.5, 5.1, label='output')
    arrow(ax, 9.5, 4.7, 8.5, 4.7)
    arrow(ax, 9.5, 4.7, 10.5, 4.7)
    arrow(ax, 10.5, 4.7, 11.5, 4.7)
    arrow(ax, 2.5, 4.7, 3.5, 4.7)
    arrow(ax, 11.5, 4.7, 12, 4.7)
    notes = ['Transcoding: 1 video → multiple resolutions (360p, 720p, 1080p, 4K)',
             'DAG Pipeline: each processing step is a DAG node (audio, video, thumbnail)',
             'CDN serves video chunks: adaptive bitrate streaming (HLS, DASH)',
             'Metadata DB: video title, description, views, likes (MySQL/Cassandra)',
             'Blob Storage: raw + transcoded videos (petabytes scale)']
    for i, n in enumerate(notes):
        ax.text(0.3, 3.2 - i * 0.55, f'• {n}', fontsize=9, color=COLORS['text'])
    save(fig, '14-youtube.png')

def ch15_google_drive():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 15: Google Drive — Sync & Block Storage', fontsize=13, fontweight='bold', color=COLORS['text'])
    box(ax, 1.5, 6.3, 2, 0.8, '💻 Client A\n(Desktop App)', COLORS['blue'])
    box(ax, 1.5, 4.5, 2, 0.8, '📱 Client B\n(Mobile)', COLORS['blue'])
    box(ax, 4.5, 5.4, 2, 0.8, '⚖ Load\nBalancer', COLORS['green'])
    box(ax, 7.5, 6.5, 2, 0.8, '🔔 Notification\nService', COLORS['orange'])
    box(ax, 7.5, 5.2, 2, 0.8, '📤 Upload\nService', COLORS['purple'])
    box(ax, 7.5, 3.9, 2, 0.8, '🧩 Block\nStorage (S3)', COLORS['teal'])
    box(ax, 10.5, 5.2, 2, 0.8, '🗄 Metadata\nDB', COLORS['red'])
    box(ax, 10.5, 3.9, 2, 0.8, '📋 Sync Queue\n(Kafka)', COLORS['darkblue'])
    arrow(ax, 2.5, 6.3, 3.5, 5.7); arrow(ax, 2.5, 4.5, 3.5, 5.1)
    arrow(ax, 5.5, 5.4, 6.5, 5.7); arrow(ax, 5.5, 5.4, 6.5, 5.1)
    arrow(ax, 8.5, 5.2, 9.5, 5.2); arrow(ax, 8.5, 3.9, 9.5, 3.9)
    arrow(ax, 10.5, 4.7, 10.5, 4.3)
    notes = ['Block-level sync: only upload changed BLOCKS of a file (delta sync)',
             '• 4MB file changed 1KB → only upload the 4KB block containing change',
             'Notification Service: long-polling or WebSocket for sync events',
             'Conflict resolution: last-write-wins or present both versions',
             'Metadata DB: file tree, versions, owner, shared-with (MySQL)',
             'Deduplication: SHA-256 hash → same content stored once (like S3)']
    for i, n in enumerate(notes):
        ax.text(0.3, 2.8 - i * 0.52, f'{"" if n.startswith("•") else "• "}{n}', fontsize=8.5, color=COLORS['text'])
    save(fig, '15-google-drive.png')

# ─── Run All ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating images in: {OUTPUT_DIR}")
    ch01_scale()
    ch02_estimation()
    ch03_framework()
    ch04_rate_limiter()
    ch05_consistent_hashing()
    ch06_kv_store()
    ch07_unique_id()
    ch08_url_shortener()
    ch09_web_crawler()
    ch10_notification()
    ch11_news_feed()
    ch12_chat()
    ch13_autocomplete()
    ch14_youtube()
    ch15_google_drive()
    print(f"\n✅ All 15 images generated successfully!")
