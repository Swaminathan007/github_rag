"""
pyreactssr/errors.py

Renders a styled in-browser error overlay when esbuild compilation fails,
mimicking Vite / CRA dev-mode behaviour.
"""


def render_error_page(error_message: str, component_path: str = "") -> str:
    """Return a full HTML page that displays the build error nicely."""
    safe_msg = (
        error_message.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    safe_path = component_path.replace("&", "&amp;").replace("<", "&lt;")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Build Error — py-react-ssr</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #0d0d0d;
      font-family: 'Menlo', 'Consolas', 'Monaco', monospace;
      padding: 32px 16px;
    }}
    .overlay {{
      background: #1a1a1a;
      border: 1px solid #ef4444;
      border-radius: 12px;
      padding: 32px 40px;
      max-width: 860px;
      width: 100%;
      box-shadow: 0 0 40px rgba(239, 68, 68, 0.15);
    }}
    .badge {{
      display: inline-block;
      background: #ef4444;
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 3px 10px;
      border-radius: 4px;
      margin-bottom: 16px;
    }}
    h1 {{
      color: #fca5a5;
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 8px;
    }}
    .file {{
      color: #6b7280;
      font-size: 13px;
      margin-bottom: 24px;
    }}
    pre {{
      background: #111;
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      padding: 20px 24px;
      color: #f87171;
      font-size: 13px;
      line-height: 1.7;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .hint {{
      margin-top: 20px;
      color: #4b5563;
      font-size: 12px;
    }}
    .hint span {{ color: #6b7280; }}
  </style>
</head>
<body>
  <div class="overlay">
    <div class="badge">Build Error</div>
    <h1>esbuild compilation failed</h1>
    <p class="file">↳ {safe_path}</p>
    <pre>{safe_msg}</pre>
    <p class="hint">Fix the error above and <span>refresh the page</span>.</p>
  </div>
</body>
</html>"""
