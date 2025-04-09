# h2s


## Quiz Generator
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

## Documents Generator

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


## Scheduling

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


## Uploading to Vector DB
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
