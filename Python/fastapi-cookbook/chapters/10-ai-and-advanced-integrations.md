# Chapter 10 — AI and Advanced Integrations

> **Projects:** `chef_ai`, `ecotech_RAG`, `graphql`, `grpc_gateway`

---

## 🎯 What This Chapter Covers

Integrating LLM APIs (Cohere) for conversational AI, building a RAG (Retrieval-Augmented Generation) system with LangChain and Chroma vector store, adding a GraphQL interface with Strawberry, and building a gRPC gateway that lets HTTP clients talk to gRPC services.

---

## 🤖 Chef AI — Stateful Conversational Chatbot

The chef chatbot maintains conversation history across messages. The key challenge: HTTP is stateless, but LLMs need context. The solution: store conversation history in `request.state`, which FastAPI initializes from the `lifespan` context.

```python
# chef_ai/main.py
from contextlib import asynccontextmanager
from typing import Annotated
import cohere
from fastapi import Body, FastAPI, Request
from pydantic import BaseModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Yield a dict — anything in it becomes request.state attributes.
    Here we initialize an empty conversation history list.
    """
    yield {"messages": []}   # shared mutable state for the app lifetime

app = FastAPI(title="Chef AI Chatbot", lifespan=lifespan)

# chef_ai/handlers.py
async def generate_chat_completion(
    query: str,
    history: list,              # previous messages in this conversation
) -> str:
    """
    Call Cohere's chat API with the full conversation history.
    The history lets the model remember previous turns.
    """
    co = cohere.AsyncClient()   # uses COHERE_API_KEY from environment

    response = await co.chat(
        message=query,
        chat_history=history,   # pass ALL previous messages
        model="command-r",
        preamble=(
            "You are a helpful chef assistant. You ONLY answer questions about "
            "cooking, recipes, ingredients, and kitchen techniques. For any other "
            "topic, politely decline and redirect to food-related questions."
        ),
    )

    # Update history with this exchange
    history.append({"role": "USER", "message": query})
    history.append({"role": "CHATBOT", "message": response.text})

    return response.text

# Endpoints
@app.post("/chat")
async def chat(
    request: Request,
    query: Annotated[str, Body(min_length=1, example="How do I make pasta carbonara?")],
) -> str:
    """
    Send a message to the chef.
    request.state.messages persists the conversation history across calls.
    """
    return await generate_chat_completion(query, request.state.messages)

@app.get("/history")
def get_history(request: Request) -> list:
    """Return the full conversation so far."""
    return request.state.messages

@app.post("/restart")
def restart_conversation(request: Request):
    """Clear conversation history — start fresh."""
    request.state.messages.clear()
    return {"message": "Conversation cleared"}
```

---

## 📚 Ecotech RAG — Retrieval-Augmented Generation

RAG solves a core LLM problem: LLMs don't know about YOUR documents (company policies, product manuals, recent research). RAG fixes this by:
1. Splitting your documents into chunks and storing them as vector embeddings
2. When a question arrives, finding the most relevant chunks (semantic search)
3. Injecting those chunks into the LLM prompt as context
4. The LLM answers based on YOUR documents, not its training data

```
User question: "What's our return policy for electronics?"
    ↓
Embed the question → search vector DB for similar chunks
    ↓
Found: [chunk from returns_policy.pdf page 3]
    ↓
Prompt: "Answer based only on this context:\n{chunk}\n\nQuestion: {question}"
    ↓
LLM response: "Electronics can be returned within 30 days with original packaging..."
```

```python
# ecotech_rag/main.py
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Body, FastAPI, HTTPException, Request, UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pathlib import Path

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

async def load_existing_documents(db: Chroma):
    """Load any documents that were saved in previous sessions."""
    for doc_path in DOCS_DIR.glob("*.txt"):
        text = doc_path.read_text()
        doc = Document(page_content=text, metadata={"source": doc_path.name})
        await db.aadd_documents([doc])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the vector store with Cohere embeddings
    # Chroma stores embeddings in-memory (or on disk) — no separate DB needed
    db = Chroma(embedding_function=CohereEmbeddings(model="embed-english-v3.0"))
    await load_existing_documents(db)
    yield {"db": db}   # available as request.state.db

app = FastAPI(title="Ecotech AI Assistant", lifespan=lifespan)

# ecotech_rag/retrieval.py
def get_relevant_context(question: str, db: Chroma, k: int = 4) -> str:
    """
    Find the k most relevant document chunks for the question.
    Returns them as a single string to inject into the prompt.
    """
    # similarity_search uses cosine similarity on embeddings
    relevant_docs = db.similarity_search(question, k=k)
    context_parts = []
    for i, doc in enumerate(relevant_docs, 1):
        context_parts.append(f"[Source {i}: {doc.metadata.get('source', 'unknown')}]")
        context_parts.append(doc.page_content)
    return "\n\n".join(context_parts)

# ecotech_rag/model.py
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("""
You are an assistant for Ecotech company. Answer questions using ONLY the context below.
If the answer is not in the context, say "I don't have that information in my documents."
Do not make up information.

Context:
{context}

Question: {question}

Answer:
""")

llm = ChatCohere(model="command-r", temperature=0)
chain = prompt | llm | StrOutputParser()

# Endpoints
@app.post("/ask")
async def ask_question(
    request: Request,
    question: Annotated[str, Body(min_length=5)],
) -> str:
    """Answer a question using documents in the vector store."""
    db = request.state.db
    context = get_relevant_context(question, db)

    if not context:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found. Upload documents first.",
        )

    return await chain.ainvoke({"question": question, "context": context})

@app.post("/documents", status_code=201)
async def upload_document(request: Request, file: UploadFile):
    """
    Upload a text document to the knowledge base.
    The document is split into chunks and stored as embeddings.
    """
    if not file.content_type == "text/plain":
        raise HTTPException(status_code=400, detail="Only .txt files accepted")

    content = (await file.read()).decode("utf-8")

    # Split into chunks for better retrieval granularity
    # chunk_size: tokens per chunk (larger = more context, less precision)
    # chunk_overlap: overlap between chunks (prevents splitting important sentences)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.create_documents(
        texts=[content],
        metadatas=[{"source": file.filename}],
    )

    # Add to vector store (embeddings computed here)
    db = request.state.db
    await db.aadd_documents(chunks)

    # Save to disk for persistence across restarts
    (DOCS_DIR / file.filename).write_text(content)

    return {
        "filename": file.filename,
        "chunks_created": len(chunks),
        "message": f"Document indexed in {len(chunks)} chunks",
    }

@app.delete("/documents/{filename}")
async def delete_document(filename: str, request: Request):
    """Remove a document from the knowledge base."""
    file_path = DOCS_DIR / Path(filename).name   # prevent path traversal
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    file_path.unlink()
    # Note: removing from Chroma requires knowing the document IDs — implementation varies
    return {"message": f"Deleted {filename}"}
```

---

## 🍓 GraphQL with Strawberry

GraphQL lets clients request exactly the fields they need. One endpoint serves many different query shapes.

```python
# graphql_app/schema.py
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from typing import Optional

# Define types with @strawberry.type decorator
@strawberry.type
class Song:
    id: int
    title: str
    artist: str
    genre: str
    year: int
    # duration is optional — some songs in the DB might not have it
    duration_seconds: Optional[int] = None

@strawberry.type
class Query:
    @strawberry.field
    def songs(
        self,
        genre: Optional[str] = None,
        limit: int = 20,
    ) -> list[Song]:
        """Fetch songs, optionally filtered by genre."""
        # In production: query from DB
        all_songs = get_songs_from_db(genre=genre, limit=limit)
        return all_songs

    @strawberry.field
    def song(self, id: int) -> Optional[Song]:
        """Fetch a single song by ID."""
        return get_song_by_id(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_song(
        self,
        title: str,
        artist: str,
        genre: str,
        year: int,
    ) -> Song:
        """Add a new song to the catalog."""
        return create_song_in_db(title, artist, genre, year)

# Mount the GraphQL router
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema, graphiql=True)   # graphiql = interactive browser IDE

app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")
```

```graphql
# Example GraphQL query — client gets exactly what it asks for
query {
  songs(genre: "rock", limit: 5) {
    title    # only these fields
    artist   # no genre, no id, no duration
  }
}

# Result:
# {"data": {"songs": [
#   {"title": "Hotel California", "artist": "Eagles"},
#   ...
# ]}}
```

---

## 🔗 gRPC Gateway — HTTP Frontend for gRPC Backend

Sometimes a backend service uses gRPC (fast binary protocol) but your clients want REST. A FastAPI gRPC gateway translates HTTP → gRPC.

```proto
// grpcserver.proto — defines the gRPC service
syntax = "proto3";

service DataService {
    rpc GetData(DataRequest) returns (DataResponse) {}
    rpc ProcessBatch(BatchRequest) returns (BatchResponse) {}
}

message DataRequest {
    string query = 1;
}

message DataResponse {
    string result = 1;
    bool success = 2;
    float confidence = 3;
}
```

```python
# gateway/main.py
import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# These are generated from the .proto file with: python -m grpc_tools.protoc ...
import grpcserver_pb2 as pb2
import grpcserver_pb2_grpc as pb2_grpc

app = FastAPI(title="gRPC Gateway")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    result: str
    success: bool
    confidence: float

GRPC_SERVER = "localhost:50051"

@app.post("/query", response_model=QueryResponse)
async def proxy_to_grpc(request: QueryRequest):
    """
    Accept an HTTP POST, forward it to the gRPC backend, return the result as JSON.
    HTTP clients don't need to know gRPC exists.
    """
    try:
        async with grpc.aio.insecure_channel(GRPC_SERVER) as channel:
            stub = pb2_grpc.DataServiceStub(channel)

            # Call the gRPC method — returns a protobuf message
            grpc_response = await stub.GetData(
                pb2.DataRequest(query=request.query),
                timeout=5.0,    # don't wait forever if gRPC server is slow
            )

        return QueryResponse(
            result=grpc_response.result,
            success=grpc_response.success,
            confidence=grpc_response.confidence,
        )

    except grpc.RpcError as e:
        # Map gRPC status codes to HTTP status codes
        code = e.code()
        if code == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail=e.details())
        elif code == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=e.details())
        elif code == grpc.StatusCode.DEADLINE_EXCEEDED:
            raise HTTPException(status_code=504, detail="gRPC server timed out")
        else:
            raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| `request.state` from `lifespan` | The only clean way to share app-level resources (vector DB, LLM client) across requests |
| Conversation history in `lifespan` state | HTTP is stateless — state must live somewhere; simple apps use memory, prod uses Redis |
| RAG = retrieval + injection + generation | LLMs answer from YOUR docs, not training data — chain is: embed → search → prompt → response |
| `RecursiveCharacterTextSplitter` | Splits text intelligently at paragraph/sentence/word boundaries — better retrieval |
| Strawberry `@strawberry.type` + `@strawberry.field` | Pure Python → GraphQL schema — no SDL files needed |
| `graphiql=True` | Interactive browser IDE at `/graphql` — great for dev/testing |
| `grpc.aio.insecure_channel` | Async gRPC client — matches FastAPI's async model |
| Map `grpc.StatusCode` → HTTP status | gRPC clients see grpc codes; HTTP clients need HTTP codes — always translate |
