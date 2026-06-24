import base64
from typing import Optional


def get_sidebar_game_html(image_path: str, theme_vars: Optional[dict] = None) -> str:
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        img_data = f"data:image/png;base64,{encoded_string}"
    except OSError:
        img_data = ""

    # Build inline style from theme vars so the iframe inherits Streamlit's theme
    style_attrs = ""
    if theme_vars:
        style_attrs = "; ".join(f"{k}: {v}" for k, v in theme_vars.items())

    html_code = f"""
    <!DOCTYPE html>
    <html style="{style_attrs}">
    <head>
    <style>
        :root {{
            --game-bg: var(--background-color, #f7f5f2);
            --game-panel: var(--secondary-background-color, #faf8f5);
            --game-ink: var(--text-color, #1e1b18);
            --game-line: color-mix(in srgb, var(--text-color, #1e1b18) 14%, transparent);
            --game-accent: var(--primary-color, #0d9488);
            --game-accent-strong: var(--primary-color, #0f766e);
            --game-empty: color-mix(in srgb, var(--primary-color, #0d9488) 10%, transparent);
            --game-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
        }}
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: sans-serif;
            background: var(--game-bg);
            color: var(--game-ink);
            width: 100%;
        }}
        #puzzle-container {{
            position: relative;
            width: 100%;
            max-width: 600px;
            aspect-ratio: 1 / 1;
            background: var(--game-panel);
            border: 2px solid var(--game-line);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--game-shadow);
            margin-bottom: 20px;
        }}
        .tile {{
            position: absolute;
            width: 33.3333%;
            height: 33.3333%;
            background-image: url('{img_data}');
            background-size: 300% 300%;
            border: 1px solid var(--game-line);
            box-sizing: border-box;
            transition: top 0.2s, left 0.2s;
            cursor: pointer;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.32);
        }}
        .tile.empty {{
            background: var(--game-empty);
            border: 1px dashed var(--game-accent);
            box-shadow: none;
            cursor: default;
        }}
        #controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }}
        button {{
            background: var(--game-accent);
            color: var(--game-panel);
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }}
        button:hover {{
            background: var(--game-accent-strong);
        }}
        .game-title {{
            text-align: center;
            margin-bottom: 15px;
            font-size: 20px;
            font-weight: bold;
            color: var(--game-ink);
        }}
    </style>
    </head>
    <body>
        <div class="game-title">Chơi trực quan (Interactive)</div>
        <div id="puzzle-container"></div>
        <div id="controls">
            <button onclick="shuffle()">Trộn (Shuffle)</button>
        </div>

        <script>
            const container = document.getElementById('puzzle-container');
            let tiles = [];
            let emptyPos = 8;
            const size = 3;

            function init() {{
                for (let i = 0; i < 9; i++) {{
                    const tile = document.createElement('div');
                    tile.className = 'tile';
                    if (i === 8) {{
                        tile.classList.add('empty');
                        tile.style.backgroundImage = 'none';
                    }} else {{
                        const row = Math.floor(i / size);
                        const col = i % size;
                        tile.style.backgroundPosition = `${{col * 50}}% ${{row * 50}}%`;
                    }}
                    tile.onclick = () => move(i);
                    tiles.push({{ el: tile, currentPos: i, correctPos: i }});
                    container.appendChild(tile);
                }}
                render();
            }}

            function render() {{
                tiles.forEach(tile => {{
                    const row = Math.floor(tile.currentPos / size);
                    const col = tile.currentPos % size;
                    tile.el.style.top = `${{row * 33.3333}}%`;
                    tile.el.style.left = `${{col * 33.3333}}%`;
                }});
            }}

            function move(index) {{
                const tile = tiles[index];
                if (tile.currentPos === emptyPos) return;

                const tileRow = Math.floor(tile.currentPos / size);
                const tileCol = Math.floor(tile.currentPos % size);
                const emptyRow = Math.floor(emptyPos / size);
                const emptyCol = Math.floor(emptyPos % size);

                const isAdjacent = Math.abs(tileRow - emptyRow) + Math.abs(tileCol - emptyCol) === 1;

                if (isAdjacent) {{
                    const temp = tile.currentPos;
                    tile.currentPos = emptyPos;
                    tiles[8].currentPos = temp;
                    emptyPos = temp;
                    render();
                }}
            }}

            function shuffle() {{
                for (let i = 0; i < 150; i++) {{
                    const emptyRow = Math.floor(emptyPos / size);
                    const emptyCol = Math.floor(emptyPos % size);
                    const possibleMoves = [];
                    
                    tiles.forEach((tile, idx) => {{
                        if (idx === 8) return;
                        const r = Math.floor(tile.currentPos / size);
                        const c = tile.currentPos % size;
                        if (Math.abs(r - emptyRow) + Math.abs(c - emptyCol) === 1) {{
                            possibleMoves.push(idx);
                        }}
                    }});

                    if (possibleMoves.length > 0) {{
                        const randomMove = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
                        const tile = tiles[randomMove];
                        const temp = tile.currentPos;
                        tile.currentPos = emptyPos;
                        tiles[8].currentPos = temp;
                        emptyPos = temp;
                    }}
                }}
                render();
            }}

            init();
        </script>
    </body>
    </html>
    """
    return html_code
