# Chapter 7 — Advanced Data Storage

> **Project:** `streaming_platform`

---

## 🎯 What This Chapter Covers

Using multiple databases in one app: async MongoDB with Motor for song/playlist storage, Elasticsearch for full-text search, Redis for response caching, and why each database is the right tool for a different problem.

---

## 🧠 The Right Database for the Right Job

The streaming platform uses three databases — not because complexity is good, but because each one excels at a different thing:

| Database | Used for | Why it's the right choice |
|----------|----------|--------------------------|
| **MongoDB** | Songs, playlists, user listening history | Flexible schema — songs have wildly different metadata (classical vs hip-hop) |
| **Elasticsearch** | Full-text artist/title search | Built for search — MongoDB text search is basic; ES handles fuzzy, ranked results |
| **Redis** | Caching popular song lists | In-memory key-value — returning cached lists is microseconds vs milliseconds |

---

## 🏗️ Multi-Database Startup

```python
# main.py
from asyncio import gather
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from db_connection import (
    get_mongo_client, get_es_client, get_redis_client,
    ping_mongo, ping_elasticsearch, ping_redis,
)
from database import mongo_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup: verify all three databases are reachable (in parallel),
    create indexes, and initialize the Redis cache.
    On shutdown: the async context manager handles cleanup automatically.
    """
    # Ping all three concurrently — fail fast if any is down
    await gather(
        ping_mongo(),
        ping_elasticsearch(),
        ping_redis(),
    )

    # Create MongoDB indexes — do this once at startup, not per request
    db = mongo_database()
    await db.songs.drop_indexes()     # reset in case they changed
    await db.songs.create_index(      # sort index: fast ORDER BY release_year
        [("album.release_year", -1)]  # -1 = descending
    )
    await db.songs.create_index(      # full-text search index on artist field
        [("artist", "text")]
    )

    # Initialize the Redis-backed response cache
    redis_client = get_redis_client()
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="streaming-cache:",    # all keys prefixed for namespacing
    )

    yield    # app runs here

app = FastAPI(lifespan=lifespan)
```

---

## 🍃 Async MongoDB with Motor

Motor is the async MongoDB driver. Unlike PyMongo (sync), Motor operations use `await` and don't block the event loop.

```python
# database.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends

_client: AsyncIOMotorClient | None = None

def get_mongo_client() -> AsyncIOMotorClient:
    """Singleton client — created once, reused for all requests."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient("mongodb://localhost:27017")
    return _client

def mongo_database() -> AsyncIOMotorDatabase:
    return get_mongo_client()["streaming"]

# Use as a FastAPI dependency
async def get_db(db = Depends(mongo_database)):
    return db
```

```python
# songs endpoints
from fastapi import FastAPI, Depends, HTTPException, Body
from bson import ObjectId
from fastapi.encoders import ENCODERS_BY_TYPE
from motor.motor_asyncio import AsyncIOMotorDatabase

# Register a serializer: ObjectId → str happens automatically in JSON responses
ENCODERS_BY_TYPE[ObjectId] = str

@app.post("/songs", status_code=201)
async def add_song(
    song: dict = Body(
        example={
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "album": {"name": "A Night at the Opera", "release_year": 1975},
            "duration_seconds": 354,
        }
    ),
    db: AsyncIOMotorDatabase = Depends(mongo_database),
):
    """
    Insert a song document. MongoDB will add _id automatically.
    We use dict instead of a Pydantic model because song schemas vary wildly.
    """
    result = await db.songs.insert_one(song)
    return {
        "id": str(result.inserted_id),
        "message": "Song added",
    }

@app.get("/songs/{song_id}")
async def get_song(
    song_id: str,
    db: AsyncIOMotorDatabase = Depends(mongo_database),
):
    # Always validate before converting — bad id raises InvalidId exception
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=400, detail="Invalid song ID format")

    song = await db.songs.find_one({"_id": ObjectId(song_id)})
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    # _id is an ObjectId — convert to string for JSON
    # The ENCODERS_BY_TYPE registration above handles this automatically
    return song

@app.get("/songs")
async def list_songs(
    db: AsyncIOMotorDatabase = Depends(mongo_database),
    limit: int = 20,
    skip: int = 0,
):
    # find() returns an AsyncCursor — iterate with async for or to_list()
    songs = await db.songs.find().skip(skip).limit(limit).to_list(None)
    return songs

@app.put("/songs/{song_id}")
async def update_song(
    song_id: str,
    updates: dict,
    db: AsyncIOMotorDatabase = Depends(mongo_database),
):
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=400, detail="Invalid song ID format")

    result = await db.songs.update_one(
        {"_id": ObjectId(song_id)},
        {"$set": updates},       # $set: only update specified fields
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": "Updated"}
```

---

## 🎵 Playlists — Embedding vs Referencing

MongoDB supports two relationship patterns. Which you choose depends on access patterns:

```python
# EMBEDDED: store related data inside the document
# ✅ Fast reads (one query)
# ❌ Duplication when same data appears in many playlists
song_embedded = {
    "_id": ObjectId(),
    "title": "Hotel California",
    "artist": "Eagles",
    "duration": 391,
    # full song data repeated in every playlist that includes it
}

# REFERENCED: store song IDs, look up when needed
# ✅ No duplication
# ❌ Requires a second query to resolve song details
playlist_referenced = {
    "_id": ObjectId(),
    "name": "Classic Rock",
    "song_ids": [ObjectId("abc"), ObjectId("def")],  # just IDs
}

# Endpoint that resolves references (like a JOIN)
@app.get("/playlists/{playlist_id}")
async def get_playlist(
    playlist_id: str,
    db = Depends(mongo_database),
):
    if not ObjectId.is_valid(playlist_id):
        raise HTTPException(status_code=400, detail="Invalid playlist ID")

    playlist = await db.playlists.find_one({"_id": ObjectId(playlist_id)})
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Resolve song references in one query using $in
    song_ids = [ObjectId(sid) for sid in playlist.get("song_ids", [])]
    songs = await db.songs.find(
        {"_id": {"$in": song_ids}}
    ).to_list(None)

    return {
        "id": str(playlist["_id"]),
        "name": playlist["name"],
        "songs": songs,
        "song_count": len(songs),
    }
```

---

## 🔍 Using Indexes — Query Diagnostics

```python
# Endpoints that use the indexes we created at startup
@app.get("/songs/by-year/{year}")
async def songs_by_year(year: int, db = Depends(mongo_database)):
    # Uses the {"album.release_year": -1} index
    query = db.songs.find({"album.release_year": year})

    # Debugging: explain() tells you which index MongoDB used
    explained = await query.explain()
    winning_plan = (
        explained.get("queryPlanner", {})
        .get("winningPlan", {})
        .get("inputStage", {})
    )
    index_used = winning_plan.get("indexName", "COLLECTION SCAN — no index used!")

    songs = await query.to_list(None)
    return {
        "year": year,
        "count": len(songs),
        "index_used": index_used,   # useful for debugging performance
        "songs": songs,
    }

@app.get("/songs/search")
async def search_songs(artist: str, db = Depends(mongo_database)):
    # Uses the {"artist": "text"} index for full-text search
    # $text requires a text index to exist — created at startup
    songs = await db.songs.find(
        {"$text": {"$search": artist}}
    ).to_list(None)
    return songs
```

---

## ⚡ Redis Caching with fastapi-cache

Without caching: every request to "popular songs" hits MongoDB, sorts, and returns. With Redis: first call takes 50ms, subsequent calls take <1ms from cache.

```python
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

# Cache the response for 60 seconds
# Key is auto-generated from the function name + arguments
@app.get("/songs/popular")
@cache(expire=60)    # 60 seconds TTL
async def get_popular_songs(db = Depends(mongo_database)):
    """
    This result is cached in Redis for 60 seconds.
    All users get the same cached response during that window.
    """
    songs = await db.songs.find().sort("play_count", -1).limit(20).to_list(None)
    return songs

# Cache with custom key — include query params in the cache key
def song_cache_key(func, namespace, request, response, *args, **kwargs):
    """Custom key builder: cache per-genre separately."""
    genre = kwargs.get("genre", "all")
    return f"{namespace}:songs:genre:{genre}"

@app.get("/songs/genre/{genre}")
@cache(expire=300, key_builder=song_cache_key)
async def get_songs_by_genre(genre: str, db = Depends(mongo_database)):
    songs = await db.songs.find({"genre": genre}).limit(50).to_list(None)
    return songs

# Manually invalidate cache (e.g. when new songs are added)
@app.post("/songs/invalidate-cache")
async def invalidate_popular_cache():
    """Call this when songs are added/removed to clear stale cache."""
    backend = FastAPICache.get_backend()
    # Delete all keys matching the prefix
    await backend.clear(namespace="streaming-cache:")
    return {"message": "Cache cleared"}
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `ENCODERS_BY_TYPE[ObjectId] = str` | Registers globally — `ObjectId` serializes to string in ALL JSON responses |
| `await db.songs.find().to_list(None)` | Motor cursors are async — always `await` and call `to_list()` |
| `{"$set": updates}` in update_one | Only updates specified fields — without `$set`, the whole document is replaced |
| `{"$text": {"$search": artist}}` | Requires a text index — created at startup, not per-request |
| Index in startup `lifespan` | Idempotent and fast — creating an existing index is a no-op |
| `@cache(expire=60)` | TTL in seconds — cache expires automatically, no manual cleanup |
| `$in` for reference resolution | Fetch multiple documents by ID in one query — not N+1 queries |
