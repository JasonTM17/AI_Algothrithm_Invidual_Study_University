# Deploy Web and Release Desktop EXE

This document explains how to publish the Stage 3 showcase app and build a desktop `.exe` release.

## 1. Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run stage3_search_showcase_app.py
```

Open:

```text
http://localhost:8501
```

## 2. Deploy to Streamlit Community Cloud

Recommended entry point:

```text
stage3_search_showcase_app.py
```

Suggested settings:

```text
Repository: JasonTM17/AI_Algothrithm_Invidual_Study_University
Branch: main
Main file path: stage3_search_showcase_app.py
Python dependencies: requirements.txt
```

General flow:

1. Push the merged project to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Select the branch and set the main file path to `stage3_search_showcase_app.py`.
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
python -m streamlit run stage3_search_showcase_app.py --server.address=0.0.0.0 --server.port=$PORT
```

## 5. Build desktop EXE locally

On Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
.\build_desktop_exe.ps1 -Python python -Name 8PuzzleSearchLab
.\dist\8PuzzleSearchLab.exe
```

## 6. Build desktop EXE with GitHub Actions

The repository includes:

```text
.github/workflows/release-desktop.yml
```

Manual run:

1. Go to GitHub Actions.
2. Select `Build Desktop EXE`.
3. Click `Run workflow`.
4. Download artifact `8PuzzleSearchLab-windows`.

Tag-based release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

When a tag starting with `v` is pushed, the workflow builds `dist/8PuzzleSearchLab.exe` and attaches it to a GitHub Release.

Official GitHub Actions Python workflow documentation: https://docs.github.com/en/actions/tutorials/build-and-test-code/python

Official artifact download documentation: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts
