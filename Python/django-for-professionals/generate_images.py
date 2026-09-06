#!/usr/bin/env python3
"""
Generate architecture diagrams for Django for Professionals chapters.
Run: python3 generate_images.py
Requires: pip install matplotlib
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'blue': '#2196F3', 'lightblue': '#BBDEFB', 'darkblue': '#1565C0',
    'green': '#4CAF50', 'orange': '#FF9800', 'purple': '#9C27B0',
    'red': '#F44336', 'teal': '#009688', 'gray': '#9E9E9E',
    'amber': '#FFC107', 'bg': '#F8F9FA', 'text': '#212121',
}

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close(fig)
    print(f"  ✓ {name}")

def box(ax, x, y, w, h, label, color, fontsize=9, text_color='white'):
    fancy = FancyBboxPatch((x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.2", facecolor=color, edgecolor='white', linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight='bold', zorder=4)

def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color='#424242', lw=1.5), zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my, label, ha='center', va='center', fontsize=7,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9))

def ch02_docker():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 2: Docker Containers vs Virtual Machines', fontsize=13, fontweight='bold')
    ax = axes[0]; ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Virtual Machines (Heavy)', fontsize=10, color=COLORS['red'])
    box(ax, 5, 9, 7, 0.7, 'Physical Server', COLORS['darkblue'])
    box(ax, 5, 7.9, 7, 0.7, 'Hypervisor', COLORS['blue'])
    box(ax, 2, 6.3, 2.5, 1.2, 'VM 1\nGuest OS 700MB+', COLORS['red'])
    box(ax, 5, 6.3, 2.5, 1.2, 'VM 2\nGuest OS 700MB+', COLORS['red'])
    box(ax, 8, 6.3, 2.5, 1.2, 'VM 3\nGuest OS 700MB+', COLORS['red'])
    box(ax, 2, 4.8, 2.5, 0.7, 'App A', COLORS['orange'])
    box(ax, 5, 4.8, 2.5, 0.7, 'App B', COLORS['orange'])
    box(ax, 8, 4.8, 2.5, 0.7, 'App C', COLORS['orange'])
    ax.text(5, 3.2, 'Each VM = full OS copy (700MB+)\nSlow start, high memory', ha='center', fontsize=9, color=COLORS['red'])
    ax = axes[1]; ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
    ax.set_title('Docker Containers (Lightweight)', fontsize=10, color=COLORS['green'])
    box(ax, 5, 9, 7, 0.7, 'Physical Server', COLORS['darkblue'])
    box(ax, 5, 7.9, 7, 0.7, 'Host OS + Docker Engine', COLORS['teal'])
    box(ax, 2, 6.7, 2.5, 0.9, 'Container 1\nDjango', COLORS['green'])
    box(ax, 5, 6.7, 2.5, 0.9, 'Container 2\nPostgreSQL', COLORS['blue'])
    box(ax, 8, 6.7, 2.5, 0.9, 'Container 3\nRedis', COLORS['purple'])
    box(ax, 5, 5.4, 7, 0.7, 'Shared Linux Kernel', COLORS['gray'])
    ax.text(5, 3.8, 'Shared OS, start in ms, megabytes', ha='center', fontsize=9, color=COLORS['green'])
    for i, n in enumerate(['Dockerfile = image blueprint', 'docker-compose.yml = orchestrate services',
                           'Volumes = live code sync']):
        ax.text(0.5, 2.8 - i*0.55, f'• {n}', fontsize=8, color=COLORS['text'])
    save(fig, '02-docker.png')

def ch03_postgresql():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 3: PostgreSQL in Docker Compose', fontsize=13, fontweight='bold')
    box(ax, 1.5, 6.3, 2, 0.7, 'Developer\n:8000', COLORS['blue'])
    box(ax, 5, 6.3, 2.5, 0.7, 'web service\nDjango', COLORS['green'])
    box(ax, 9.5, 6.3, 2.5, 0.7, 'db service\nPostgreSQL', COLORS['orange'])
    box(ax, 5, 4.8, 2.5, 0.7, '.:/code\n(volume)', COLORS['teal'])
    box(ax, 9.5, 4.8, 2.5, 0.7, 'postgres_data\n(named volume)', COLORS['purple'])
    arrow(ax, 2.5, 6.3, 3.8, 6.3, label='port 8000')
    arrow(ax, 6.3, 6.3, 8.3, 6.3, label='HOST="db"')
    arrow(ax, 5, 5.95, 5, 5.15); arrow(ax, 9.5, 5.95, 9.5, 5.15)
    for i, n in enumerate(['HOST: "db" not "localhost" — service name is the hostname',
                           'Named volume: data survives docker-compose down',
                           'depends_on: db — Django waits for PostgreSQL to start',
                           'psycopg2-binary required in requirements.txt',
                           'Never SQLite in production — behavior differences cause bugs']):
        ax.text(0.3, 3.8 - i*0.6, f'• {n}', fontsize=9, color=COLORS['text'])
    save(fig, '03-postgresql.png')


def ch07_static():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORS['bg'])
    fig.suptitle('Chapter 7: Static Files — Dev vs Production', fontsize=13, fontweight='bold')
    for ax, title, bcolor, notes in [
        (axes[0], 'Development (DEBUG=True)', COLORS['blue'],
         ['Django runserver serves static directly', 'STATICFILES_DIRS = [BASE_DIR/"static"]', 'Fine locally, too slow for production']),
        (axes[1], 'Production (DEBUG=False)', COLORS['green'],
         ['WhiteNoise serves compressed files', 'python manage.py collectstatic', 'STATICFILES_STORAGE = CompressedManifest...'])]:
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
        ax.set_title(title, fontsize=10, color=bcolor)
        box(ax, 5, 9, 5, 0.7, 'Browser', COLORS['blue'])
        box(ax, 5, 7.5, 5, 0.7, 'Django runserver' if bcolor==COLORS['blue'] else 'WhiteNoise + Gunicorn', bcolor)
        box(ax, 2.5, 5.8, 3, 0.7, 'HTML', COLORS['teal'])
        box(ax, 7.5, 5.8, 3, 0.7, 'CSS/JS/Images', COLORS['orange'])
        arrow(ax, 5, 8.65, 5, 7.85); arrow(ax, 5, 7.15, 2.5, 6.15); arrow(ax, 5, 7.15, 7.5, 6.15)
        for i, n in enumerate(notes):
            ax.text(0.3, 4.5 - i*0.7, f'• {n}', fontsize=8, color=COLORS['text'])
    save(fig, '07-static-assets.png')

def ch18_deployment():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 18: Production Deployment on Heroku', fontsize=13, fontweight='bold')
    box(ax, 1.5, 5.5, 2, 0.7, 'Browser\n(HTTPS)', COLORS['blue'])
    box(ax, 4.5, 5.5, 2, 0.7, 'Heroku\nLoad Balancer', COLORS['purple'])
    box(ax, 7.5, 5.5, 2.5, 0.7, 'Gunicorn\n(4 workers)', COLORS['green'])
    box(ax, 11, 5.5, 2, 0.7, 'Django App\nDEBUG=False', COLORS['teal'])
    box(ax, 4.5, 3.8, 2, 0.7, 'WhiteNoise\n(static files)', COLORS['orange'])
    box(ax, 7.5, 3.8, 2.5, 0.7, 'PostgreSQL\n(Heroku addon)', COLORS['red'])
    box(ax, 11, 3.8, 2, 0.7, 'S3\n(media files)', COLORS['amber'], text_color=COLORS['text'])
    arrow(ax, 2.5, 5.5, 3.5, 5.5, label='TLS')
    arrow(ax, 5.5, 5.5, 6.3, 5.5); arrow(ax, 8.8, 5.5, 9.9, 5.5)
    arrow(ax, 4.5, 5.15, 4.5, 4.45); arrow(ax, 7.5, 5.15, 7.5, 4.45); arrow(ax, 11, 5.15, 11, 4.45)
    for i, n in enumerate(['Procfile: web: gunicorn django_project.wsgi --log-file -',
                           'ALLOWED_HOSTS = [".herokuapp.com"] — required in production',
                           'DATABASE_URL set automatically by Heroku PostgreSQL addon',
                           'python manage.py collectstatic before each deploy',
                           'heroku config:set DJANGO_SECRET_KEY=... for env vars',
                           'python manage.py check --deploy — fix all warnings!']):
        ax.text(0.3, 2.8 - i*0.46, f'• {n}', fontsize=8.5, color=COLORS['text'])
    save(fig, '18-deployment.png')

if __name__ == "__main__":
    print(f"Generating images in: {OUTPUT_DIR}")
    ch02_docker(); ch03_postgresql(); ch07_static(); ch18_deployment()
    print(f"\n✅ All 4 images generated successfully!")
