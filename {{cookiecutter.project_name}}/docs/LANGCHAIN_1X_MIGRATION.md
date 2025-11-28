# LangChain 1.x Migration Guide

**Date:** November 2025
**Status:** ✅ Complete - Template upgraded to LangChain 1.1.0

This document describes the migration from LangChain 0.3.x to LangChain 1.x for the
Chatbot genAI cookiecutter template.

## 📋 Summary of Changes

### Dependency Upgrades

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| `langchain` | 0.3.27 | **1.1.0** | Major version upgrade |
| `langchain-core` | 0.3.80 | **1.1.0** | Core abstractions |
| `langchain-community` | 0.3.31 | **0.4.1** | No 1.x yet |
| `langchain-classic` | N/A | **1.0.0** | NEW - Legacy chains |
| `langgraph` | N/A | **1.0.4** | NEW - Modern agents |
| `langchain-aws` | 0.2.35 | **1.1.0** | AWS provider |
| `langchain-openai` | 0.2.14 | **0.3.34** | OpenAI provider |
| `langchain-google-vertexai` | 2.0.7 | **2.1.x** | Vertex AI provider |
| `pydantic` | 2.9 | **2.10** | Latest Pydantic 2.x |
| `fastapi` | 0.110.0 | **0.115.0** | Latest FastAPI |
| `uvicorn` | 0.29.0 | **0.32.0** | Latest Uvicorn |
| `python` | >=3.11, <3.12 | **>=3.11, <3.14** | Now supports 3.11-3.13 |

### Import Changes

#### 1. Legacy Chains → `langchain_classic`

**Before (0.3.x):**
```python
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
```

**After (1.x):**
```python
from langchain_classic.chains import LLMChain
from langchain_classic.chains.base import Chain
from langchain_classic.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_classic.chains.combine_documents.stuff import StuffDocumentsChain
```

#### 2. Core Components → `langchain_core`

**Before (0.3.x):**
```python
from langchain.schema import BaseMessage, AIMessage, HumanMessage
from langchain.callbacks.base import Callbacks
from langchain.embeddings.base import Embeddings
from langchain.prompts import PromptTemplate
```

**After (1.x):**
```python
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.callbacks import Callbacks
from langchain_core.embeddings import Embeddings
from langchain_core.prompts import PromptTemplate
```

#### 3. Callbacks → `langchain_classic`

**Before (0.3.x):**
```python
from langchain.callbacks import AsyncIteratorCallbackHandler
```

**After (1.x):**
```python
from langchain_classic.callbacks import AsyncIteratorCallbackHandler
```

## What was Changed in LangChain 1.x

### Old approach: LangChain Classic

LangChain 1.0 moved legacy chain patterns (`LLMChain`, `ConversationalRetrievalChain`, etc.) to a separate package called `langchain-classic` to:
- Keep the core `langchain` package focused on modern patterns
- Provide backward compatibility for existing code
- Encourage migration to modern LangGraph-based agents

### Modern Alternative: LangGraph

For new code, consider using **LangGraph** instead of legacy chains:

```python
from langgraph import StateGraph
from langchain_core.messages import HumanMessage

# Define state
class State(TypedDict):
    messages: list[BaseMessage]

# Create graph
graph = StateGraph(State)
# ... build modern agent workflow
```

## 📚 Resources

- [LangChain 1.0 Announcement](https://blog.langchain.com/langchain-langgraph-1dot0/)
- [LangChain Changelog](https://changelog.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Migration Guide (Official)](https://python.langchain.com/docs/versions/v0_2/)

---


**Migration completed:** November 2025
**Template version:** Updated for LangChain 1.1.0
**Maintained by:** CoE Solutions Team
