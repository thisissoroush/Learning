#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'blue': '#2196F3', 'green': '#4CAF50', 'orange': '#FF9800',
    'purple': '#9C27B0', 'red': '#F44336', 'teal': '#009688',
    'darkblue': '#1565C0', 'darkgreen': '#2E7D32', 'lightgreen': '#C8E6C9',
    'bg': '#F8F9FA', 'text': '#212121',
}

def save(fig, name):
    plt.savefig(os.path.join(OUTPUT_DIR, name), dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close(fig)
    print(f"  ✓ {name}")

def box(ax, x, y, w, h, label, color, fontsize=9, text_color='white'):
    fancy = FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1", facecolor=color, edgecolor='white', linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight='bold', zorder=4)

def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color='#424242', lw=2), zorder=2)

def gen_all():
    for name in ['00-architecture-overview', '01-domain-model', '02-repository-pattern',
                 '04-service-layer', '06-unit-of-work', '07-aggregates', 
                 '08-events-message-bus', '11-event-driven-microservices', '12-cqrs']:
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=COLORS['bg'])
        ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')
        ax.text(6, 3.5, f"{name}", ha='center', fontsize=14, weight='bold')
        save(fig, f"{name}.png")

if __name__ == "__main__":
    print(f"Generating images in: {OUTPUT_DIR}")
    gen_all()
    print(f"\n✅ All 9 images generated!")
