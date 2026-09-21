# Chapter 7 — Advanced Data Storage

> **Project:** `streaming_platform`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter07)

---

## 🎯 What This Chapter Covers

MongoDB with Motor (async), Elasticsearch for full-text search, Redis caching with `fastapi-cache`, MongoDB indexing, and combining multiple data stores in one app.

---

## 🏗️ Multi-Store App Startup

```python
from asyncio import gather
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ping all three stores concurrently
    await gather(
        ping_mongo_db_server(),
        ping_elasticsearch_server(),
        ping_redis_server(),
    )

    # Create MongoDB indexes on startup
    db = mongo_database()
    await db.songs.drop_indexes()
    await db.songs.create_index({"album.release_year": -1})   # sort index
    await db.songs.create_index({"artist": "text"})           # full-text search index

    # Initialize Redis cache
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    yield
```

---

## 🍃 Async MongoDB with Motor

```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.encoders import ENCODERS_BY_TYPE

# Register ObjectId serializer globally
ENCODERS_BY_TYPE[ObjectId] = str

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["streaming"]

async def mongo_database():
    yield db

@app.post("/song")
async def add_song(
    song: dict = Body(example={"title": "My Song", "artist": "My Artist", "genre": "Rock"}),
    mongo_db=Depends(mongo_database),
):
    await mongo_db.songs.insert_one(song)
    return {"message": "Song added successfully", "id": song.get("_id")}

@app.get("/song/{song_id}")
async def get_song(song_id: str, db=Depends(mongo_database)):
    song = await db.songs.find_one(
        {"_id": ObjectId(song_id) if ObjectId.is_valid(song_id) else None}
    )
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    song.pop("album", None)   # don't expose nested album data
    return song

@app.put("/song/{song_id}")
async def update_song(song_id: str, updated_song: dict, db=Depends(mongo_database)):
    result = await db.songs.update_one(
        {"_id": ObjectId(song_id) if ObjectId.is_valid(song_id) else None},
        {"$set": updated_song},
    )
    if result.modified_count == 1:
        return {"message": "Song updated successfully"}
    raise HTTPException(status_code=404, detail="Song not found")
```

---

## 🔍 MongoDB Indexes for Performance

```python
# Sort index — fast queries by release year
await db.songs.create_index({"album.release_year": -1})

# Text index — full-text search on artist field
await db.songs.create_index({"artist": "text"})

@app.get("/songs/year")
async def get_songs_by_released_year(year: int, db=Depends(mongo_database)):
    query = db.songs.find({"album.release_year": year})

    # Log which index was used
    explained_query = await query.explain()
    logger.info(
        "Index used: %s",
        explained_query.get("queryPlanner", {})
            .get("winningPlan", {})
            .get("inputStage", {})
            .get("indexName", "No index used"),
    )
    return await query.to_list(None)

@app.get("/songs/artist")
async def get_songs_by_artist(artist: str, db=Depends(mongo_database)):
    # Uses text index
    query = db.songs.find({"$text": {"$search": artist}})
    return await query.to_list(None)
```

---

## 🎵 Playlists with Embedded References

```python
from pydantic import BaseModel

class Playlist(BaseModel):
    name: str
    songs: list[str] = []   # list of song ObjectId strings

@app.post("/playlist")
async def create_playlist(
    playlist: Playlist = Body(example={"name": "My Playlist", "songs": ["song_id"]}),
    db=Depends(mongo_database),
):
    result = await db.playlists.insert_one(playlist.model_dump())
    return {"message": "Playlist created successfully", "id": str(result.inserted_id)}

@app.get("/playlist/{playlist_id}")
async def get_playlist(playlist_id: str, db=Depends(mongo_database)):
    playlist = await db.playlists.find_one(
        {"_id": ObjectId(playlist_id) if ObjectId.is_valid(playlist_id) else None}
    )
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Resolve song references — like a JOIN in SQL
    songs = await db.songs.find(
        {"_id": {"$in": [ObjectId(sid) for sid in playlist["songs"]]}}
    ).to_list(None)

    return {"name": playlist["name"], "songs": songs}
```

---

## ⚡ Redis Caching with fastapi-cache

```python
from fastapi_cache.decorator import cache

# Cache the response for 60 seconds
@app.get("/songs/popular")
@cache(expire=60)
async def get_popular_songs(db=Depends(mongo_database)):
    return await db.songs.find().sort("plays", -1).limit(10).to_list(None)

# Cache with custom key builder
from fastapi_cache import FastAPICache

def my_key_builder(func, namespace, request, response, *args, **kwargs):
    return f"{namespace}:{request.url.path}:{request.query_params}"

@app.get("/songs/by-genre/{genre}")
@cache(expire=300, key_builder=my_key_builder)
async def get_by_genre(genre: str, db=Depends(mongo_database)):
    return await db.songs.find({"genre": genre}).to_list(None)
```

---

## 🔑 Key Takeaways

- `ENCODERS_BY_TYPE[ObjectId] = str` — register globally so `ObjectId` serializes to string automatically
- `await gather(ping_mongo(), ping_elastic(), ping_redis())` — check all stores in parallel on startup
- Create MongoDB indexes in `lifespan`, not per-request — indexes are created once
- `query.explain()` reveals which index MongoDB used — invaluable for query optimization
- `{"$text": {"$search": artist}}` uses the text index for full-text search
- `@cache(expire=60)` from `fastapi-cache` caches the full response in Redis with one decorator
- Resolve references manually in MongoDB (`$in` query) — there's no JOIN; design accordingly
