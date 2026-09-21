# Chapter 10 — AI and Advanced Integrations

> **Projects:** `chef_ai`, `ecotech_RAG`, `ai_doctor`, `graphql`, `grpc_gateway`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter10)

---

## 🎯 What This Chapter Covers

Integrating AI/LLM APIs (Cohere), RAG with LangChain + Chroma vector store, GraphQL with Strawberry, and a gRPC gateway pattern.

---

## 🤖 Chef AI — Conversational Chatbot (Cohere)

```python
from contextlib import asynccontextmanager
from fastapi import Body, FastAPI, Request
from cohere import ChatMessage

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield {"messages": []}    # conversation history stored in app state

app = FastAPI(title="Chef Cuisine Chatbot App", lifespan=lifespan)

@app.post("/query")
async def query_chat_bot(
    request: Request,
    query: Annotated[str, Body(min_length=1)],
) -> str:
    answer = await generate_chat_completion(query, request.state.messages)
    return answer

@app.get("/messages")
def get_conversation_history(request: Request) -> MessagesResponse:
    return MessagesResponse.from_chat_messages(messages=request.state.messages)

@app.post("/restart-conversation")
def restart_conversation(request: Request):
    request.state.messages = []
    return {"message": "Conversation restarted"}
```

```python
# handlers.py — Cohere API call
import cohere

async def generate_chat_completion(
    query: str,
    messages: list[ChatMessage],
) -> str:
    co = cohere.AsyncClient()
    response = await co.chat(
        message=query,
        chat_history=messages,
        model="command-r",
        preamble="You are a helpful chef assistant who only answers questions about cooking.",
    )
    # Store conversation history
    messages.append(ChatMessage(role="USER", message=query))
    messages.append(ChatMessage(role="CHATBOT", message=response.text))
    return response.text
```

**Key pattern:** Conversation history stored in `request.state` (lifespan-initialized) — no DB needed for simple chatbots.

---

## 📚 Ecotech RAG — Retrieval Augmented Generation

```python
from contextlib import asynccontextmanager
from fastapi import Body, FastAPI, HTTPException, Request, UploadFile
from langchain.text_splitter import CharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Chroma(embedding_function=CohereEmbeddings())
    await load_documents(db)     # pre-load docs into vector store
    yield {"db": db}             # make vector store available via request.state

app = FastAPI(title="Ecotech AI Assistant", lifespan=lifespan)

@app.post("/message")
async def query_assistant(
    request: Request,
    question: Annotated[str, Body()],
) -> str:
    context = get_context(question, request.state.db)   # retrieve relevant chunks
    response = await chain.ainvoke({
        "question": question,
        "context": context,
    })
    return response

@app.post("/add_document")
async def add_document(request: Request, file: UploadFile):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="File must be a text file")

    content = file.file.read().decode()
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    chunks = text_splitter.split_documents([Document(content)])
    await request.state.db.aadd_documents(chunks)

    # Persist file
    with open(f"docs/{file.filename}", "w") as buffer:
        buffer.write(content)

    return {"filename": file.filename}
```

```python
# model.py — LangChain chain
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the following context:
{context}

Question: {question}
""")

llm = ChatCohere(model="command-r")
chain = prompt | llm | StrOutputParser()
```

**RAG flow:**
```
User question
    → embed question (CohereEmbeddings)
    → vector similarity search in Chroma
    → retrieve top-K relevant document chunks (context)
    → LLM prompt: "Answer based only on context: {context}\nQuestion: {question}"
    → streamed/awaited response
```

---

## 🍓 GraphQL with Strawberry

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

@strawberry.type
class Song:
    id: int
    title: str
    artist: str
    genre: str

@strawberry.type
class Query:
    @strawberry.field
    def songs(self) -> list[Song]:
        return get_all_songs_from_db()

    @strawberry.field
    def song(self, id: int) -> Song | None:
        return get_song_by_id(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_song(self, title: str, artist: str, genre: str) -> Song:
        return create_song(title, artist, genre)

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

**Why GraphQL over REST?**
- Client requests exactly the fields it needs — no over/under-fetching
- Single endpoint (`/graphql`) instead of many REST routes
- Introspection — clients can discover the schema automatically
- Better for complex nested data (playlists → songs → artists)

---

## 🔗 gRPC Gateway

```proto
// grpcserver.proto
syntax = "proto3";

service GrpcServer {
    rpc GetServerResponse(Message) returns (MessageResponse) {}
}

message Message {
    string message = 1;
}

message MessageResponse {
    string message = 1;
    bool received = 2;
}
```

```python
# FastAPI acts as HTTP gateway → forwards to gRPC server
from fastapi import FastAPI
import grpc
import grpcserver_pb2, grpcserver_pb2_grpc

app = FastAPI()

@app.post("/grpc-call")
async def call_grpc_service(message: str):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = grpcserver_pb2_grpc.GrpcServerStub(channel)
        response = await stub.GetServerResponse(
            grpcserver_pb2.Message(message=message)
        )
    return {"message": response.message, "received": response.received}
```

---

## 🔑 Key Takeaways

- `request.state` from `lifespan` yield is the clean way to share app-level resources (vector DB, LLM client, connection pools)
- RAG = embed query → vector search → inject context → LLM — LangChain chains make this composable
- `CharacterTextSplitter(chunk_size=100, chunk_overlap=0)` chunks documents for embedding
- Strawberry GraphQL integrates with FastAPI via `GraphQLRouter` — one line to mount
- gRPC gateway: FastAPI handles HTTP, proxies to gRPC service — best of both worlds
- `chain = prompt | llm | StrOutputParser()` — LangChain pipe syntax composes processing steps
