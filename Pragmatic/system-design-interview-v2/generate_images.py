#!/usr/bin/env python3
"""Generate architecture diagram images for System Design Interview Vol. 2"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

OUT = "/home/soroush/Projects/Learning/Pragmatic/system-design-interview-v2/images"
os.makedirs(OUT, exist_ok=True)

BG = "#1E1E2E"
C1 = "#4A90D9"   # blue
C2 = "#50C878"   # green
C3 = "#E67E22"   # orange
C4 = "#9B59B6"   # purple
C5 = "#E74C3C"   # red
C6 = "#1ABC9C"   # teal
C7 = "#F39C12"   # yellow
DB = "#2C3E50"   # dark box


def box(ax, x, y, w, h, label, color=C1, fontsize=9):
    p = FancyBboxPatch((x - w/2, y - h/2), w, h,
                       boxstyle="round,pad=0.05",
                       linewidth=1.5, edgecolor="white",
                       facecolor=color, alpha=0.92, zorder=3)
    ax.add_patch(p)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4, multialignment="center")


def arr(ax, x1, y1, x2, y2, color="#AAAAAA"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=2)


def save(fig, name):
    path = f"{OUT}/{name}"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ {name}")


# ─── 1. Geohash Grid ────────────────────────────────────────────────────────
def img_01_geohash():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Geohash: Encoding Earth into a Grid", color="white", fontsize=13, fontweight="bold")

    ax = axes[0]
    ax.set_facecolor(BG)
    ax.set_xlim(0, 8); ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.set_title("Geohash Grid (precision 3)", color="#AAAAAA", fontsize=10)
    tile_colors = ["#2A3A5A", "#1E4D6B", "#2C5F7A", "#3A7CA5"]
    for i in range(8):
        for j in range(8):
            ax.add_patch(plt.Rectangle((i, j), 1, 1, color=tile_colors[(i+j) % 4], lw=0.3, ec="#555"))
    ax.add_patch(plt.Rectangle((3, 4), 1, 1, color=C3, lw=2, ec="white", alpha=0.9))
    ax.text(3.5, 4.5, "9q8yy", color="white", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(4, -0.6, "Longitude →", color="#888", fontsize=8, ha="center")
    ax.text(-0.6, 4, "Latitude →", color="#888", fontsize=8, ha="center", rotation=90)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for sp in ax.spines.values():
        sp.set_edgecolor("#444")

    ax2 = axes[1]
    ax2.set_facecolor(BG)
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 9)
    ax2.axis("off")
    ax2.set_title("Geohash Precision Levels", color="#AAAAAA", fontsize=10)
    rows = [
        ("1", "±2500 km", "5000×5000 km", C1),
        ("2", "±630 km",  "1250×625 km",  C2),
        ("3", "±78 km",   "156×156 km",   C3),
        ("4", "±20 km",   "39×20 km",     C4),
        ("5", "±2.4 km",  "4.9×4.9 km",   C6),
        ("6", "±610 m",   "1.2×0.6 km",   C5),
        ("7", "±76 m",    "153×153 m",    C7),
    ]
    ax2.text(5, 8.6, "  Precision     Error          Cell Size", color="#BBBBBB",
             ha="center", fontsize=9, fontweight="bold", fontfamily="monospace")
    for i, (prec, err, size, c) in enumerate(rows):
        y = 7.6 - i * 1.0
        ax2.add_patch(plt.Rectangle((0.3, y-0.38), 9.4, 0.72, color=c, alpha=0.18, lw=0))
        ax2.text(1.3, y, prec,  color=c,       ha="center", fontsize=11, fontweight="bold")
        ax2.text(4.2, y, err,   color="white",  ha="center", fontsize=9)
        ax2.text(7.8, y, size,  color="#BBBBBB", ha="center", fontsize=8)

    fig.tight_layout(pad=1.2)
    save(fig, "01-geohash-grid.png")


# ─── 2. QuadTree ────────────────────────────────────────────────────────────
def img_01_quadtree():
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 11); ax.set_ylim(0, 6.5)
    ax.set_title("QuadTree Spatial Partitioning\n(subdivide cell when business count > threshold)",
                 color="white", fontsize=12, fontweight="bold")

    box(ax, 5.5, 5.8, 2.2, 0.65, "Root (World)", C1)
    for xp, lbl in [(1.5, "NW"), (4.2, "NE"), (6.8, "SW"), (9.5, "SE")]:
        box(ax, xp, 4.4, 1.6, 0.55, lbl, C2, fontsize=9)
        arr(ax, 5.5, 5.47, xp, 4.67)

    # subdivide NE
    for xp, lbl in [(3.0, "NE-NW"), (4.0, "NE-NE"), (5.0, "NE-SW"), (6.0, "NE-SE")]:
        box(ax, xp, 2.9, 0.9, 0.5, lbl, C3, fontsize=7)
        arr(ax, 4.2, 4.12, xp, 3.15)

    for xp, n in [(3.0, 3), (4.0, 120), (5.0, 7), (6.0, 2)]:
        c = C5 if n > 100 else DB
        lbl = f"leaf\nn={n}"
        if n > 100:
            lbl = f"SPLIT!\nn={n}"
        box(ax, xp, 1.6, 0.9, 0.5, lbl, c, fontsize=7)
        arr(ax, xp, 2.65, xp, 1.85)

    ax.text(8.5, 2.5,
            "If n > max_biz:\n  split into 4 children\n  recurse\nElse:\n  leaf node",
            color="#CCCCCC", fontsize=8.5, va="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="#252540", edgecolor="#555", alpha=0.9))
    save(fig, "01-quadtree.png")


# ─── 3. Proximity Service Architecture ──────────────────────────────────────
def img_01_proximity_arch():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.5)
    ax.set_title("Proximity Service — High-Level Architecture", color="white", fontsize=12, fontweight="bold")

    box(ax, 1.2, 3.5, 1.8, 0.7, "Mobile\nClient", C6)
    box(ax, 3.8, 3.5, 1.8, 0.7, "Load\nBalancer", C7)
    box(ax, 6.5, 5.0, 2.0, 0.7, "Location\nService", C1)
    box(ax, 6.5, 2.0, 2.0, 0.7, "Business\nService", C2)
    box(ax, 10.0, 5.0, 2.0, 0.7, "Redis\n(Geohash)", C5)
    box(ax, 10.0, 3.2, 2.0, 0.7, "Business\nDB (read)", DB)
    box(ax, 10.0, 1.4, 2.0, 0.7, "Business\nDB (write)", DB)

    arr(ax, 2.1, 3.5, 2.9, 3.5)
    arr(ax, 4.7, 3.8, 5.5, 5.0)
    arr(ax, 4.7, 3.2, 5.5, 2.0)
    arr(ax, 7.5, 5.0, 9.0, 5.0)
    arr(ax, 7.5, 2.3, 9.0, 3.2)
    arr(ax, 7.5, 1.7, 9.0, 1.4)

    ax.text(1.5, 5.8, "Search flow:", color=C1, fontsize=9, fontweight="bold")
    ax.text(1.5, 5.3,
            "① Client sends (lat, lng, radius)\n"
            "② LB routes to Location Service\n"
            "③ Location Service queries Redis Geohash index\n"
            "④ Returns business IDs → fetch details from Business Service",
            color="#BBBBBB", fontsize=8.5)
    save(fig, "01-proximity-service-arch.png")


# ─── 4. Nearby Friends ──────────────────────────────────────────────────────
def img_02_nearby_friends():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 13); ax.set_ylim(0, 6)
    ax.set_title("Nearby Friends — Real-time Location Broadcasting", color="white", fontsize=12, fontweight="bold")

    box(ax, 1.2, 3.0, 1.8, 0.65, "User A\n(moving)", C6)
    box(ax, 4.0, 3.0, 1.9, 0.65, "WebSocket\nHandler", C1)
    box(ax, 7.0, 4.5, 2.2, 0.65, "Redis\nPub/Sub", C5)
    box(ax, 7.0, 1.5, 2.2, 0.65, "Location\nHistory DB", DB)
    box(ax, 10.2, 3.0, 2.0, 0.65, "WebSocket\nHandler 2", C2)
    box(ax, 12.3, 3.0, 1.5, 0.65, "User B\n(friend)", C7)

    arr(ax, 2.1, 3.0, 3.05, 3.0)
    arr(ax, 4.95, 3.35, 5.9, 4.5)
    arr(ax, 4.95, 2.65, 5.9, 1.5)
    arr(ax, 8.1, 4.2, 9.2, 3.35)
    arr(ax, 11.2, 3.0, 11.55, 3.0)

    ax.text(2.6, 3.15, "location\nupdate", color="#AAAAAA", fontsize=7, ha="center")
    ax.text(5.3, 4.1, "publish\nchannel", color="#AAAAAA", fontsize=7, ha="center")
    ax.text(5.3, 1.9, "persist", color="#AAAAAA", fontsize=7, ha="center")
    ax.text(8.8, 4.0, "subscribe\n& push", color="#AAAAAA", fontsize=7, ha="center")

    ax.text(6.5, 0.4,
            "Each WebSocket server subscribes to friends' Redis channels  "
            "→  when A moves, all of A's friends on any server get notified",
            color="#AAAAAA", fontsize=8, ha="center")
    save(fig, "02-nearby-friends-arch.png")


# ─── 5. Google Maps Tile System ─────────────────────────────────────────────
def img_03_google_maps():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Google Maps — Tile System & Navigation Pipeline", color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 8); ax.set_ylim(0, 9)
    ax.set_title("Map Tile Pyramid (Zoom Levels)", color="#AAAAAA", fontsize=10)

    levels = [
        (8.2, "Zoom 0", "1 tile  (whole world)", C1),
        (7.0, "Zoom 1", "4 tiles",               C2),
        (5.8, "Zoom 2", "16 tiles",              C3),
        (4.6, "Zoom 5", "1,024 tiles",           C4),
        (3.4, "Zoom 10","1M tiles",              C5),
        (2.2, "Zoom 15","1B tiles",              C6),
        (1.0, "Zoom 21","4T tiles (street-level)",C7),
    ]
    for y, zoom, tiles, c in levels:
        w = 3.0 + (8.2 - y) * 0.4
        box(ax, 4, y, w, 0.65, f"{zoom}: {tiles}", c, fontsize=8)

    ax.text(4, 0.2, "Each tile = 256×256 px PNG  ·  Served from CDN",
            color="#AAAAAA", fontsize=8, ha="center")

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 8)
    ax2.set_title("Navigation & ETA Pipeline", color="#AAAAAA", fontsize=10)

    for x, y, lbl, c in [
        (3.5, 7.2, "Mobile Client", C6),
        (3.5, 5.8, "Navigation Service", C1),
        (1.5, 4.2, "Map Tile CDN", C7),
        (5.5, 4.2, "Route Service\n(Dijkstra/A*)", C2),
        (5.5, 2.7, "Graph DB\n(road network)", DB),
        (3.5, 2.7, "ETA ML Model", C4),
    ]:
        box(ax2, x, y, 2.4, 0.7, lbl, c, fontsize=9)

    arr(ax2, 3.5, 6.85, 3.5, 6.15)
    arr(ax2, 2.6, 5.45, 1.5, 4.55)
    arr(ax2, 4.4, 5.45, 5.5, 4.55)
    arr(ax2, 5.5, 3.85, 5.5, 3.05)
    arr(ax2, 4.7, 2.7, 4.7, 2.7)
    arr(ax2, 4.35, 5.45, 3.5, 3.05)

    fig.tight_layout(pad=1.2)
    save(fig, "03-google-maps-tiles.png")


# ─── 6. Distributed Message Queue ───────────────────────────────────────────
def img_04_message_queue():
    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.set_title("Distributed Message Queue — Partition & Replication (Kafka-style)",
                 color="white", fontsize=12, fontweight="bold")

    for i, lbl in enumerate(["Producer 1", "Producer 2", "Producer 3"]):
        box(ax, 1.2, 5.8 - i*1.6, 1.8, 0.6, lbl, C6, fontsize=8)
        arr(ax, 2.1, 5.8 - i*1.6, 3.0, 5.8 - i*1.6)

    # broker outline
    ax.add_patch(FancyBboxPatch((2.8, 0.8), 6.5, 5.5,
                                boxstyle="round,pad=0.1",
                                facecolor="#141424", edgecolor=C1, lw=2, alpha=0.8))
    ax.text(6.05, 6.55, "Broker Cluster", color=C1, ha="center", fontsize=10, fontweight="bold")

    for i, (lbl, yp) in enumerate([
        ("Partition 0  (Leader)", 5.5),
        ("Partition 1  (Leader)", 4.0),
        ("Partition 2  (Leader)", 2.5),
    ]):
        box(ax, 5.5, yp, 3.8, 0.65, lbl, C2, fontsize=8)
        box(ax, 8.0, yp - 0.55, 1.8, 0.4, "Follower (replica)", C4, fontsize=7)
        arr(ax, 7.0, yp - 0.05, 7.1, yp - 0.35, color="#9B59B6")

    for i, lbl in enumerate(["Consumer\nGroup A", "Consumer\nGroup B"]):
        box(ax, 11.5, 5.0 - i*2.5, 1.8, 0.65, lbl, C3, fontsize=8)
        arr(ax, 9.5, 5.5 - i*0.8, 10.6, 5.0 - i*2.5)

    ax.text(1.0, 0.35,
            "Key concepts:  offset per consumer  ·  retention period  ·  "
            "replication factor ≥ 3  ·  partition key for ordering",
            color="#AAAAAA", fontsize=8)
    save(fig, "04-message-queue-partitions.png")


# ─── 7. Metrics Monitoring ──────────────────────────────────────────────────
def img_05_metrics():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 13); ax.set_ylim(0, 6.5)
    ax.set_title("Metrics Monitoring & Alerting — Data Pipeline",
                 color="white", fontsize=12, fontweight="bold")

    for x, y, lbl, c in [
        (1.2, 3.0, "Servers\nApps\nK8s pods", C6),
        (3.8, 3.0, "Metrics\nCollector", C1),
        (6.5, 5.0, "Kafka\n(buffer)", C7),
        (6.5, 3.0, "Time-Series\nDB (Prometheus\n/ InfluxDB)", C2),
        (9.5, 3.0, "Query\nService", C3),
        (11.8, 4.2, "Alerting\nSystem", C5),
        (11.8, 1.8, "Grafana\nDashboard", C4),
    ]:
        box(ax, x, y, 2.0, 0.8, lbl, c, fontsize=8)

    arr(ax, 2.2, 3.0, 2.8, 3.0)
    arr(ax, 4.8, 3.4, 5.5, 5.0)
    arr(ax, 4.8, 3.0, 5.5, 3.0)
    arr(ax, 7.5, 5.0, 7.5, 3.4)
    arr(ax, 7.5, 3.0, 8.5, 3.0)
    arr(ax, 10.5, 3.3, 10.8, 4.2)
    arr(ax, 10.5, 2.7, 10.8, 1.8)

    ax.text(6.5, 0.4,
            "Pull model: collector scrapes /metrics endpoints every N seconds  |  "
            "Push model: agents push to collector\n"
            "TSDB row: (metric_name, labels, timestamp, float_value)  ·  Downsampling old data to save space",
            color="#AAAAAA", fontsize=8, ha="center")
    save(fig, "05-metrics-pipeline.png")


# ─── 8. Lambda Architecture ─────────────────────────────────────────────────
def img_06_lambda():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 12); ax.set_ylim(0, 7.5)
    ax.set_title("Ad Click Event Aggregation — Lambda Architecture",
                 color="white", fontsize=12, fontweight="bold")

    box(ax, 2.0, 6.8, 2.2, 0.65, "Click Events\n(stream)", C6)
    box(ax, 6.0, 6.8, 2.2, 0.65, "Message Queue\n(Kafka)", C7)
    arr(ax, 3.1, 6.8, 4.9, 6.8)
    ax.text(4.0, 7.05, "ingest", color="#AAAAAA", fontsize=7.5, ha="center")

    arr(ax, 5.0, 6.5, 3.0, 4.8)
    arr(ax, 7.0, 6.5, 9.0, 4.8)

    # Speed layer
    ax.add_patch(FancyBboxPatch((1.2, 3.0), 3.7, 2.1, boxstyle="round,pad=0.1",
                                facecolor="#1A1A2E", edgecolor=C5, lw=1.5, alpha=0.7))
    ax.text(3.05, 5.3, "⚡ Speed Layer", color=C5, ha="center", fontsize=9, fontweight="bold")
    box(ax, 3.05, 4.55, 3.0, 0.6, "Flink / Storm\n(streaming)", C5, fontsize=8)
    box(ax, 3.05, 3.3,  3.0, 0.6, "Real-time View\n(Redis / Druid)", C5, fontsize=8)
    arr(ax, 3.05, 4.25, 3.05, 3.6)

    # Batch layer
    ax.add_patch(FancyBboxPatch((7.1, 3.0), 3.7, 2.1, boxstyle="round,pad=0.1",
                                facecolor="#1A1A2E", edgecolor=C2, lw=1.5, alpha=0.7))
    ax.text(8.95, 5.3, "📦 Batch Layer", color=C2, ha="center", fontsize=9, fontweight="bold")
    box(ax, 8.95, 4.55, 3.0, 0.6, "Spark / Hadoop\n(batch jobs)", C2, fontsize=8)
    box(ax, 8.95, 3.3,  3.0, 0.6, "Batch View\n(S3 + Hive)", C2, fontsize=8)
    arr(ax, 8.95, 4.25, 8.95, 3.6)

    box(ax, 6.0, 1.5, 3.0, 0.7, "Serving Layer\n(merges both views)", C1)
    arr(ax, 3.05, 3.0, 5.0, 1.85)
    arr(ax, 8.95, 3.0, 7.0, 1.85)

    ax.text(6.0, 0.4,
            "Lambda = Speed (low latency, approximate) + Batch (accurate, higher latency) + Serving (unified API)",
            color="#AAAAAA", fontsize=8, ha="center")
    save(fig, "06-lambda-architecture.png")


# ─── 9. Hotel Reservation ───────────────────────────────────────────────────
def img_07_hotel():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Hotel Reservation System — Concurrency, Idempotency & Consistency",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 7); ax.set_ylim(0, 7)
    ax.set_title("Service Architecture", color="#AAAAAA", fontsize=10)
    for x, y, lbl, c in [
        (3.5, 6.5, "User Client", C6),
        (3.5, 5.2, "API Gateway", C7),
        (1.5, 3.8, "Hotel\nService", C1),
        (5.5, 3.8, "Reservation\nService", C2),
        (1.5, 2.3, "Inventory\nDB", DB),
        (5.5, 2.3, "Reservation\nDB", DB),
        (3.5, 0.8, "Redis Cache\n(room counts)", C5),
    ]:
        box(ax, x, y, 2.2, 0.65, lbl, c, fontsize=9)
    arr(ax, 3.5, 6.17, 3.5, 5.52)
    arr(ax, 2.6, 4.87, 1.5, 4.12)
    arr(ax, 4.4, 4.87, 5.5, 4.12)
    arr(ax, 1.5, 3.47, 1.5, 2.62)
    arr(ax, 5.5, 3.47, 5.5, 2.62)
    arr(ax, 2.5, 2.3, 3.5, 1.12)
    arr(ax, 4.5, 2.3, 3.5, 1.12)

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 7)
    ax2.set_title("Concurrency Problem & Solutions", color="#AAAAAA", fontsize=10)
    problems = [
        ("❌ Race Condition",
         "Two users book last room simultaneously\n→ both succeed → overbooking!", C5),
        ("✅ Optimistic Locking",
         "UPDATE rooms SET count=count-1\n  WHERE count > 0 AND version=N\nCheck rows affected=1", C2),
        ("✅ Idempotency Key",
         "Client sends unique reservation_id\nServer checks: already processed?\n→ return cached result", C1),
        ("✅ Database Constraints",
         "CHECK (reserved_count <= total_count)\nFails loudly instead of silently\novercommitting", C3),
    ]
    y = 6.5
    for title, detail, c in problems:
        ax2.add_patch(plt.Rectangle((0.2, y-0.7), 6.6, 1.05, color=c, alpha=0.15, lw=0))
        ax2.text(0.5, y - 0.05, title, color=c, fontsize=9, fontweight="bold")
        ax2.text(0.5, y - 0.5, detail, color="#CCCCCC", fontsize=7.5, fontfamily="monospace")
        y -= 1.55

    fig.tight_layout(pad=1.2)
    save(fig, "07-hotel-reservation.png")


# ─── 10. Email Service ──────────────────────────────────────────────────────
def img_08_email():
    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.set_title("Distributed Email Service — Architecture",
                 color="white", fontsize=12, fontweight="bold")

    for x, y, lbl, c in [
        (1.2,  4.5, "Email\nClient", C6),
        (3.8,  6.0, "HTTPS\nWeb Servers", C1),
        (3.8,  4.5, "WebSocket\n(real-time)", C2),
        (3.8,  3.0, "SMTP\nGateway", C3),
        (7.0,  4.5, "Message\nQueue", C7),
        (10.0, 5.5, "Mail\nProcessing\nWorkers", C4),
        (10.0, 3.5, "Blob Store\n(attachments)", DB),
        (12.2, 4.5, "Metadata\nDB\n(Cassandra)", DB),
    ]:
        box(ax, x, y, 2.0, 0.8, lbl, c, fontsize=8)

    arr(ax, 2.2, 4.8, 2.8, 6.0)
    arr(ax, 2.2, 4.5, 2.8, 4.5)
    arr(ax, 2.2, 4.2, 2.8, 3.0)
    arr(ax, 4.8, 6.0, 6.0, 4.8)
    arr(ax, 4.8, 4.5, 6.0, 4.5)
    arr(ax, 4.8, 3.0, 6.0, 4.2)
    arr(ax, 8.0, 5.0, 9.0, 5.5)
    arr(ax, 8.0, 4.0, 9.0, 3.5)
    arr(ax, 11.0, 4.5, 11.2, 4.5)

    ax.text(6.5, 0.5,
            "IMAP/POP3 for email retrieval  ·  Cassandra: fast user-mailbox queries (partition by user_id)  "
            "·  Attachments in blob store  ·  Queue decouples ingestion from processing",
            color="#AAAAAA", fontsize=8, ha="center")
    save(fig, "08-distributed-email.png")


# ─── 11. Object Storage ─────────────────────────────────────────────────────
def img_09_object_storage():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor(BG)
    fig.suptitle("S3-like Object Storage — Architecture & Data Durability",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 7); ax.set_ylim(0, 7)
    ax.set_title("Service Architecture", color="#AAAAAA", fontsize=10)
    for x, y, lbl, c in [
        (3.5, 6.5, "Client", C6),
        (3.5, 5.2, "Load Balancer", C7),
        (3.5, 3.9, "API Service", C1),
        (1.5, 2.5, "Metadata\nService", C2),
        (5.5, 2.5, "Data Store\nService", C3),
        (1.5, 1.0, "Metadata DB\n(SQL)", DB),
        (5.5, 1.0, "Data Nodes\n(6+3 EC)", C4),
    ]:
        box(ax, x, y, 2.4, 0.65, lbl, c, fontsize=9)
    arr(ax, 3.5, 6.17, 3.5, 5.52)
    arr(ax, 3.5, 4.87, 3.5, 4.22)
    arr(ax, 2.4, 3.57, 1.5, 2.82)
    arr(ax, 4.6, 3.57, 5.5, 2.82)
    arr(ax, 1.5, 2.17, 1.5, 1.32)
    arr(ax, 5.5, 2.17, 5.5, 1.32)

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 7)
    ax2.set_title("Erasure Coding vs Replication", color="#AAAAAA", fontsize=10)

    ax2.text(3.5, 6.6, "3× Replication (simple):", color=C1, ha="center", fontsize=9, fontweight="bold")
    for i, (lbl, c) in enumerate([("Data", C1), ("Copy 1", C2), ("Copy 2", C3)]):
        box(ax2, 1.2 + i*2, 5.8, 1.6, 0.55, lbl, c, fontsize=8)
    ax2.text(3.5, 5.35, "Storage overhead: 3× = 200% extra\nSurvives: 2 node failures", color="#BBBBBB", ha="center", fontsize=8)

    ax2.text(3.5, 4.7, "Erasure Coding 6+3 (efficient):", color=C4, ha="center", fontsize=9, fontweight="bold")
    colors_ec = [C1]*6 + [C5]*3
    labels_ec = [f"D{i}" for i in range(6)] + [f"P{i}" for i in range(3)]
    for i, (lbl, c) in enumerate(zip(labels_ec, colors_ec)):
        col = i % 5
        row = i // 5
        box(ax2, 0.8 + col*1.3, 4.1 - row*0.8, 1.1, 0.55, lbl, c, fontsize=8)
    ax2.text(3.5, 2.5, "Storage overhead: 1.5× = 50% extra\nSurvives: 3 node failures\nTrade-off: more CPU for encode/decode", color="#BBBBBB", ha="center", fontsize=8)

    fig.tight_layout(pad=1.2)
    save(fig, "09-object-storage.png")


# ─── 12. Leaderboard ────────────────────────────────────────────────────────
def img_10_leaderboard():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Real-time Gaming Leaderboard — Redis Sorted Set",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 6); ax.set_ylim(0, 8)
    ax.set_title("Redis ZSET Data Structure", color="#AAAAAA", fontsize=10)
    ax.text(0.5, 7.7, "Rank", color="#888", fontsize=8.5, fontweight="bold")
    ax.text(1.8, 7.7, "Player", color="#888", fontsize=8.5, fontweight="bold")
    ax.text(5.2, 7.7, "Score", color="#888", fontsize=8.5, fontweight="bold", ha="right")
    ax.axhline(7.5, color="#444", lw=0.8, xmin=0.05, xmax=0.95)
    players = [
        (1, "🥇 alice",  9820, C7),
        (2, "🥈 bob",    8750, "#C0C0C0"),
        (3, "🥉 carol",  7640, "#CD7F32"),
        (4, "    dave",  6200, C1),
        (5, "    eve",   4910, C2),
        (6, "    frank", 3100, C3),
    ]
    for rank, name, score, c in players:
        y = 6.8 - (rank-1) * 1.05
        ax.add_patch(plt.Rectangle((0.15, y-0.38), 5.7, 0.72, color=c, alpha=0.12, lw=0))
        ax.text(0.5, y, f"#{rank}", color=c, fontsize=10, fontweight="bold", va="center")
        ax.text(1.6, y, name, color="white", fontsize=9, va="center")
        ax.text(5.5, y, f"{score:,}", color="#BBBBBB", fontsize=9, va="center", ha="right")

    ax.text(3.0, 0.35,
            "ZADD leaderboard 9820 alice\n"
            "ZREVRANK leaderboard alice  → 0\n"
            "ZREVRANGE leaderboard 0 9  → top 10",
            color="#AAAAAA", fontsize=7.5, ha="center", fontfamily="monospace")

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 7)
    ax2.set_title("Leaderboard Service Architecture", color="#AAAAAA", fontsize=10)
    for x, y, lbl, c in [
        (3.5, 6.5, "Game Server", C6),
        (3.5, 5.2, "Score Service", C1),
        (1.5, 3.8, "Redis ZSET\n(top-N cache)", C5),
        (5.5, 3.8, "MySQL\n(all scores)", DB),
        (3.5, 2.4, "Leaderboard API", C2),
        (3.5, 1.0, "Client / CDN", C7),
    ]:
        box(ax2, x, y, 2.4, 0.65, lbl, c, fontsize=9)
    arr(ax2, 3.5, 6.17, 3.5, 5.52)
    arr(ax2, 2.6, 4.87, 1.5, 4.12)
    arr(ax2, 4.4, 4.87, 5.5, 4.12)
    arr(ax2, 1.5, 3.47, 3.5, 2.72)
    arr(ax2, 5.5, 3.47, 3.5, 2.72)
    arr(ax2, 3.5, 2.07, 3.5, 1.32)

    fig.tight_layout(pad=1.2)
    save(fig, "10-leaderboard.png")


# ─── 13. Payment System ─────────────────────────────────────────────────────
def img_11_payment():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Payment System — PSP Integration, Idempotency & Reconciliation",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 7); ax.set_ylim(0, 8)
    ax.set_title("Payment Flow", color="#AAAAAA", fontsize=10)
    for x, y, lbl, c in [
        (3.5, 7.5, "User", C6),
        (3.5, 6.2, "Payment Service", C1),
        (3.5, 4.9, "Payment Executor", C2),
        (3.5, 3.6, "PSP  (Stripe/Adyen)", C3),
        (3.5, 2.3, "Ledger Service", C4),
        (3.5, 1.0, "Reconciliation\nService", C7),
    ]:
        box(ax, x, y, 2.6, 0.65, lbl, c, fontsize=9)
    for y1, y2 in [(7.17,6.52),(6.52-0.65,4.87+0.33),(4.87-0.33,3.6+0.33),(3.6-0.33,2.3+0.33),(2.3-0.33,1.33)]:
        arr(ax, 3.5, y1, 3.5, y2)

    ax.text(0.3, 0.1,
            "Idempotency key prevents double-charge on retry",
            color=C5, fontsize=8)

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 8)
    ax2.set_title("Exactly-Once Payment Pattern", color="#AAAAAA", fontsize=10)
    steps = [
        ("① Client sends payment + idempotency_key", C6),
        ("② Server checks: key seen before?", C7),
        ("   YES → return cached result (no charge)", C3),
        ("   NO  → process payment", C2),
        ("③ Store result with idempotency_key", C1),
        ("④ Return result to client", C6),
        ("⑤ Nightly reconciliation:\n   Internal ledger  ↔  Bank statement", C4),
    ]
    y = 7.5
    for txt, c in steps:
        ax2.add_patch(plt.Rectangle((0.2, y-0.5), 6.6, 0.65, color=c, alpha=0.15, lw=0))
        ax2.text(0.5, y - 0.17, txt, color="white", fontsize=8.5, va="center")
        y -= 0.9

    fig.tight_layout(pad=1.2)
    save(fig, "11-payment-system.png")


# ─── 14. Digital Wallet ─────────────────────────────────────────────────────
def img_12_wallet():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Digital Wallet — Double-Entry Bookkeeping & Event Sourcing",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 7); ax.set_ylim(0, 8)
    ax.set_title("Double-Entry Bookkeeping", color="#AAAAAA", fontsize=10)

    # header
    for x, h in [(1.0,"Account"),(2.8,"Debit"),(4.5,"Credit"),(6.2,"Balance")]:
        ax.text(x, 7.6, h, color=C1, fontsize=9, fontweight="bold", ha="center")
    ax.axhline(7.35, color="#555", lw=0.8, xmin=0.03, xmax=0.97)

    rows = [
        ("Alice",    "$100",  "",      "$900",    C5),
        ("Bob",      "",      "$100",  "$1,100",  C2),
    ]
    for i, (acc, deb, cre, bal, c) in enumerate(rows):
        y = 6.5 - i * 1.3
        ax.add_patch(plt.Rectangle((0.1, y-0.45), 6.8, 0.9, color=c, alpha=0.12, lw=0))
        for x, val, cc in [(1.0,acc,C1),(2.8,deb,C5),(4.5,cre,C2),(6.2,bal,C7)]:
            ax.text(x, y, val, color=cc, fontsize=9, ha="center", va="center", fontweight="bold")

    ax.axhline(4.6, color="#555", lw=1, xmin=0.03, xmax=0.97)
    ax.text(1.0, 4.1, "Net Δ", color=C7, fontsize=9, ha="center", fontweight="bold")
    ax.text(2.8, 4.1, "$100", color=C5, fontsize=9, ha="center")
    ax.text(4.5, 4.1, "$100", color=C2, fontsize=9, ha="center")
    ax.text(6.2, 4.1, "✓ zero", color=C2, fontsize=9, ha="center", fontweight="bold")

    ax.text(3.5, 3.2,
            "Rule: Every transaction\ndebits ≥1 account\n& credits ≥1 account.\n\nSum(debits) = Sum(credits)\n→ books always balance.",
            color="#BBBBBB", fontsize=9, ha="center", va="top",
            bbox=dict(boxstyle="round", facecolor="#252540", edgecolor="#555", alpha=0.8))

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 8)
    ax2.set_title("Event Sourcing: Wallet State from Events", color="#AAAAAA", fontsize=10)
    events = [
        ("TransferInitiated",  "amount=$100, from=Alice, to=Bob", C1),
        ("BalanceDebited",     "account=Alice, delta=-100",       C5),
        ("BalanceCredited",    "account=Bob,   delta=+100",       C2),
        ("TransferCompleted",  "txn_id=4421, status=SUCCESS",     C3),
    ]
    for i, (ev, detail, c) in enumerate(events):
        y = 7.0 - i * 1.5
        box(ax2, 3.5, y, 6.2, 0.75, f"{ev}\n{detail}", c, fontsize=8)
        if i < 3:
            arr(ax2, 3.5, y - 0.38, 3.5, y - 0.75)

    ax2.text(3.5, 1.2,
             "Current balance = replay all events\n"
             "Any point-in-time query = replay up to that timestamp",
             color="#AAAAAA", fontsize=8.5, ha="center")

    fig.tight_layout(pad=1.2)
    save(fig, "12-digital-wallet.png")


# ─── 15. Stock Exchange ─────────────────────────────────────────────────────
def img_13_stock_exchange():
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Stock Exchange — Order Book & Matching Engine",
                 color="white", fontsize=12, fontweight="bold")

    ax = axes[0]; ax.set_facecolor(BG); ax.axis("off")
    ax.set_xlim(0, 6); ax.set_ylim(0, 8.5)
    ax.set_title("Order Book: AAPL", color="#AAAAAA", fontsize=10)
    ax.text(1.4, 8.0, "BID (Buy Orders)", color=C2, ha="center", fontsize=9, fontweight="bold")
    ax.text(4.6, 8.0, "ASK (Sell Orders)", color=C5, ha="center", fontsize=9, fontweight="bold")
    ax.axhline(7.75, color="#555", lw=0.8, xmin=0.03, xmax=0.97)
    ax.axvline(3.0, color="#555", lw=1, ymin=0.05, ymax=0.9)

    bids = [(185.10, 500), (185.05, 1200), (185.00, 800), (184.95, 2000), (184.90, 1500)]
    asks = [(185.15, 300), (185.20, 900), (185.25, 1500), (185.30, 600), (185.35, 2200)]
    for i, (price, qty) in enumerate(bids):
        y = 7.1 - i * 1.15
        bar_w = qty / 2500 * 2.5
        ax.add_patch(plt.Rectangle((3.0 - bar_w, y - 0.38), bar_w, 0.72, color=C2, alpha=0.25))
        ax.text(2.85, y, f"${price:.2f}", color=C2, fontsize=9, ha="right", va="center", fontweight="bold")
        ax.text(1.0, y, f"{qty:,}", color="#BBBBBB", fontsize=8, ha="center", va="center")
    for i, (price, qty) in enumerate(asks):
        y = 7.1 - i * 1.15
        bar_w = qty / 2500 * 2.5
        ax.add_patch(plt.Rectangle((3.0, y - 0.38), bar_w, 0.72, color=C5, alpha=0.25))
        ax.text(3.15, y, f"${price:.2f}", color=C5, fontsize=9, ha="left", va="center", fontweight="bold")
        ax.text(5.0, y, f"{qty:,}", color="#BBBBBB", fontsize=8, ha="center", va="center")

    ax.text(3.0, 0.5, "Spread: $0.05  ·  Best bid: $185.10  ·  Best ask: $185.15",
            color="#AAAAAA", fontsize=8, ha="center")

    ax2 = axes[1]; ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 7); ax2.set_ylim(0, 8)
    ax2.set_title("Exchange Architecture", color="#AAAAAA", fontsize=10)
    for x, y, lbl, c in [
        (3.5, 7.4, "Broker / Client App", C6),
        (3.5, 6.1, "Gateway", C7),
        (3.5, 4.8, "Sequencer\n(FIFO order queue)", C1),
        (3.5, 3.5, "Matching Engine\n(single-threaded)", C2),
        (1.4, 2.1, "Order Book\n(in-memory)", C3),
        (5.6, 2.1, "Market Data\nPublisher", C4),
        (5.6, 0.8, "Market Feed\n(subscribers)", DB),
        (1.4, 0.8, "Order Store\n(audit log)", DB),
    ]:
        box(ax2, x, y, 2.5, 0.7, lbl, c, fontsize=9)
    arr(ax2, 3.5, 7.05, 3.5, 6.45)
    arr(ax2, 3.5, 5.75, 3.5, 5.15)
    arr(ax2, 3.5, 4.45, 3.5, 3.85)
    arr(ax2, 2.3, 3.15, 1.4, 2.45)
    arr(ax2, 4.7, 3.15, 5.6, 2.45)
    arr(ax2, 5.6, 1.75, 5.6, 1.15)
    arr(ax2, 1.4, 1.75, 1.4, 1.15)

    ax2.text(3.5, 0.2, "Latency: microseconds  ·  Sequencer ensures total ordering  ·  No locks in matching engine",
             color="#AAAAAA", fontsize=7.5, ha="center")

    fig.tight_layout(pad=1.2)
    save(fig, "13-stock-exchange.png")


# ─── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating images → {OUT}")
    img_01_geohash()
    img_01_quadtree()
    img_01_proximity_arch()
    img_02_nearby_friends()
    img_03_google_maps()
    img_04_message_queue()
    img_05_metrics()
    img_06_lambda()
    img_07_hotel()
    img_08_email()
    img_09_object_storage()
    img_10_leaderboard()
    img_11_payment()
    img_12_wallet()
    img_13_stock_exchange()
    print(f"\nDone! {len(os.listdir(OUT))} images saved.")
