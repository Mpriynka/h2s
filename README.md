# 🧠 RAG-Powered Teaching Assistant

This system is designed to assist educators using a Retrieval-Augmented Generation (RAG) pipeline. Teachers can upload books and documents which are stored in a vector database. These resources can then be used to generate quizzes, schedule sessions, and provide document-based assistance.

---

## 🔧 Features Overview

| Feature              | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| **Document Upload**   | Teachers upload materials which are parsed and saved to a vector database. |
| **Quiz Generator**    | Generates intelligent quizzes based on uploaded content.                   |
| **Document Generator**| Allows generating summaries or notes from uploaded files.                  |
| **Scheduling**        | Manages teacher-student sessions and activity timelines.                   |

---

## 🚀 Project Setup & Commands


### Quiz Generator
Terminal 1:
```
cd projects/rag_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```
Terminal 2:
```
cd projects/quiz_generator
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Terminal 3:
```
cd projects/quiz_generator
streamlit run frontend/app.py
```

### Documents Generator

```
cd documents_generator
```
Terminal 1:
```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Terminal 2:
```
streamlit run streamlit_app.py
```


### Scheduling

```
cd scheduling
```
Terminal 1:
```
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```
Terminal 2:
```
streamlit run main.py
```


### Uploading to Vector DB
```
cd rag_backend
```
Terminal 1:
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Terminal 2:
```
streamlit run ui/app.py
```
