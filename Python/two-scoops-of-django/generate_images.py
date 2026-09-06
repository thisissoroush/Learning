#!/usr/bin/env python3
"""
Generate architecture diagrams for Two Scoops of Django 3.x.
Run: python3 generate_images.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'blue': '#2196F3', 'darkblue': '#1565C0', 'green': '#4CAF50',
    'orange': '#FF9800', 'purple': '#9C27B0', 'red': '#F44336',
    'teal': '#009688', 'gray': '#9E9E9E', 'amber': '#FFC107',
    'bg': '#F8F9FA', 'text': '#212121', 'cyan': '#00BCD4',
    'indigo': '#3F51B5',
}

def save(fig, name):
    fig.savefig(os.path.join(OUTPUT_DIR, name), dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close(fig)
    print(f"  ✓ {name}")

def box(ax, x, y, w, h, label, color, fontsize=9, text_color='white'):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.2",
        facecolor=color, edgecolor='white', linewidth=1.5, zorder=3))
    ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight='bold', zorder=4)

def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color='#424242', lw=1.5), zorder=2)
    if label:
        ax.text((x1+x2)/2+0.1, (y1+y2)/2, label, fontsize=7, color='#424242')


def settings_diagram():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 5: Split Settings for Multiple Environments', fontsize=13, fontweight='bold')
    box(ax, 6, 6.3, 8, 0.7, 'config/settings/', COLORS['darkblue'])
    box(ax, 2.5, 4.8, 3, 0.9, 'base.py\n(shared by all)', COLORS['teal'])
    box(ax, 6, 4.8, 3, 0.9, 'local.py\n(development)', COLORS['green'])
    box(ax, 9.5, 4.8, 3, 0.9, 'production.py\n(live site)', COLORS['red'])
    arrow(ax, 6, 5.95, 2.5, 5.25); arrow(ax, 6, 5.95, 6, 5.25); arrow(ax, 6, 5.95, 9.5, 5.25)
    for i, n in enumerate(['INSTALLED_APPS', 'AUTH_USER_MODEL', 'DATABASES', 'TEMPLATES']):
        ax.text(0.5, 3.9 - i*0.45, f'• {n}', fontsize=8, color=COLORS['teal'])
    for i, n in enumerate(['DEBUG = True', 'debug_toolbar', 'EMAIL = console']):
        ax.text(4.5, 3.9 - i*0.45, f'• {n}', fontsize=8, color=COLORS['green'])
    for i, n in enumerate(['DEBUG = False', 'SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE']):
        ax.text(8, 3.9 - i*0.45, f'• {n}', fontsize=8, color=COLORS['red'])
    box(ax, 2.5, 1.5, 3, 0.7, 'requirements/local.txt\n-r base.txt + dev tools', COLORS['green'])
    box(ax, 6, 1.5, 3, 0.7, 'requirements/base.txt\nDjango, psycopg2', COLORS['teal'])
    box(ax, 9.5, 1.5, 3, 0.7, 'requirements/production.txt\n-r base.txt + gunicorn', COLORS['red'])
    ax.text(6, 0.5, 'All settings in VCS  |  No local_settings.py  |  Secrets in env vars',
            ha='center', fontsize=9, color=COLORS['text'], fontweight='bold')
    save(fig, '05-settings.png')

def architecture_diagram():
    fig, ax = plt.subplots(figsize=(13, 8), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis('off')
    ax.set_title('Two Scoops: Fat Models, Thin Views, Stupid Templates', fontsize=13, fontweight='bold')
    box(ax, 6.5, 7.3, 5, 0.7, 'HTTP Request', COLORS['blue'])
    box(ax, 6.5, 6.2, 5, 0.7, 'URLconf (namespace="app")', COLORS['indigo'])
    box(ax, 6.5, 5.1, 5, 0.9, 'Thin View (HTTP concerns only)', COLORS['orange'])
    box(ax, 2, 3.5, 3.5, 1.2, 'Stupid Template\nOnly HTML, no logic', COLORS['cyan'])
    box(ax, 6.5, 3.5, 3.5, 1.2, 'Fat Model\nValidation + Business Logic\nCustom Managers', COLORS['green'])
    box(ax, 10.5, 3.5, 2.5, 1.2, 'Utility Module\nShared Logic', COLORS['teal'])
    box(ax, 6.5, 1.8, 3.5, 0.7, 'PostgreSQL', COLORS['darkblue'])
    arrow(ax, 6.5, 6.95, 6.5, 6.55); arrow(ax, 6.5, 5.85, 6.5, 5.55)
    arrow(ax, 5.5, 4.75, 2, 4.1); arrow(ax, 6.5, 4.75, 6.5, 4.1); arrow(ax, 7.5, 4.75, 10.5, 4.1)
    arrow(ax, 6.5, 2.9, 6.5, 2.5)
    save(fig, 'architecture.png')

def forms_diagram():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 12: Five Common Django Form Patterns', fontsize=13, fontweight='bold')
    for x, y, label, color in [
        (1.8, 5.8, 'Pattern 1\nSimple ModelForm', COLORS['blue']),
        (5.5, 5.8, 'Pattern 2\nCustom Validators', COLORS['green']),
        (9.2, 5.8, 'Pattern 3\nOverriding clean()', COLORS['orange']),
        (3, 3.2, 'Pattern 4\n2 Forms, 1 Model', COLORS['purple']),
        (8, 3.2, 'Pattern 5\nSearch Mixin', COLORS['teal'])]:
        box(ax, x, y, 3, 1.2, label, color)
    for i, n in enumerate(['Pattern 1: ModelForm — covers 90% of use cases',
                           'Pattern 2: field.validators.append(fn) — reusable validation',
                           'Pattern 3: clean_field() for one, clean() for cross-field',
                           'Pattern 4: Different form classes for different roles/views',
                           'Pattern 5: TitleSearchMixin reusable across ListViews',
                           'ALWAYS: {% csrf_token %} on every POST form!']):
        ax.text(0.3, 1.8 - i*0.42, f'• {n}', fontsize=8.5, color=COLORS['text'])
    save(fig, '12-forms.png')

def rest_api_diagram():
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=COLORS['bg'])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis('off')
    ax.set_title('Chapter 17: DRF ViewSet + Router Architecture', fontsize=13, fontweight='bold')
    box(ax, 1.5, 6.2, 2, 0.7, 'Client\n(Mobile/SPA)', COLORS['blue'])
    box(ax, 5, 6.2, 2.5, 0.7, 'Router URL\n/api/flavors/', COLORS['indigo'])
    box(ax, 9, 6.2, 3, 0.7, 'FlavorViewSet\n(ModelViewSet)', COLORS['green'])
    box(ax, 2, 4.5, 2, 0.7, 'Serializer\n(JSON ↔ Model)', COLORS['teal'])
    box(ax, 6, 4.5, 2.5, 0.7, 'Authentication\n(Token/JWT)', COLORS['orange'])
    box(ax, 10, 4.5, 2.5, 0.7, 'Permissions\n(IsAuthenticated)', COLORS['red'])
    box(ax, 6, 2.8, 2.5, 0.7, 'PostgreSQL', COLORS['darkblue'])
    arrow(ax, 2.5, 6.2, 3.8, 6.2); arrow(ax, 6.3, 6.2, 7.5, 6.2)
    arrow(ax, 9, 5.85, 2, 5.15); arrow(ax, 9, 5.85, 6, 5.15); arrow(ax, 9, 5.85, 10, 5.15)
    arrow(ax, 2, 4.15, 2, 3.45)
    for i, n in enumerate(['GET /api/flavors/      → list()    → 200',
                           'POST /api/flavors/     → create()  → 201',
                           'GET /api/flavors/1/    → retrieve()→ 200',
                           'PUT /api/flavors/1/    → update()  → 200',
                           'DELETE /api/flavors/1/ → destroy() → 204',
                           'perform_create(): set creator=request.user']):
        ax.text(3.5, 2.0 - i*0.38, n, fontsize=8.5, color=COLORS['text'])
    save(fig, '17-rest-api.png')

if __name__ == "__main__":
    print(f"Generating images in: {OUTPUT_DIR}")
    settings_diagram(); architecture_diagram(); forms_diagram(); rest_api_diagram()
    print(f"\n✅ All 4 images generated successfully!")
