# h2s

## Scheduling

```
cd scheduling
```

```
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

```
streamlit run main.py
```


## Quiz Generator

```
cd quiz_generator
```

```
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

```
streamlit run frontend/app.py
```

## Documents Generator

```
cd documents_generator
```

```
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

```
streamlit run streamlit_app.py
```