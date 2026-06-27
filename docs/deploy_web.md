# Deploy Web

This document explains how to publish the main Streamlit 8-Puzzle AI lab.

## 1. Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_eight_puzzle_app.py
```

Open:

```text
http://localhost:8501
```

## 2. Deploy to Streamlit Community Cloud

Recommended entry point:

```text
streamlit_eight_puzzle_app.py
```

Suggested settings:

```text
Repository: JasonTM17/AI_Algothrithm_Invidual_Study_University
Branch: main
Main file path: streamlit_eight_puzzle_app.py
Python dependencies: requirements.txt
```

General flow:

1. Push the merged project to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Select the branch and set the main file path to `streamlit_eight_puzzle_app.py`.
5. Deploy.

Official documentation: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## 3. Deploy with Docker

Build image:

```bash
docker build -t eight-puzzle-search-lab .
```

Run container:

```bash
docker run --rm -p 8501:8501 eight-puzzle-search-lab
```

Open:

```text
http://localhost:8501
```

## 4. Deploy with Render blueprint

The repository includes `render.yaml`.

Expected commands:

```bash
python -m pip install --upgrade pip && python -m pip install -r requirements.txt
python -m streamlit run streamlit_eight_puzzle_app.py --server.address=0.0.0.0 --server.port=$PORT
```
