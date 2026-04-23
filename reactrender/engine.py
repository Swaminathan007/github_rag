import json
import os
import subprocess
import tempfile
import hashlib
import threading
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from .config import Config
from .errors import render_error_page


@dataclass
class RenderConfig:
    file: str
    """Relative path to the React component inside frontend_dir. E.g. 'pages/Home.tsx'"""

    title: str = ""
    """HTML <title> for the page."""

    props: Optional[dict[str, Any]] = None
    """Props dict passed to the root React component."""

    meta_tags: dict[str, str] = field(default_factory=dict)
    """Key/value pairs rendered as <meta name="key" content="value"> tags."""

    lang: str = "en"
    """HTML lang attribute."""


class ReactSSR:
    """
    Python + FastAPI equivalent of go-react-ssr.

    Bundles React components on-demand with esbuild and returns full HTML pages.
    Props are serialised as JSON and injected into the bundle at request time.

    Usage:
        engine = ReactSSR(Config(frontend_dir="./frontend/src"))
        html = engine.render(RenderConfig(
            file="pages/Home.tsx",
            title="Home",
            props={"name": "World"},
        ))

    Hot reload (dev mode):
        engine.start_watcher()   # call once after creating the engine
    """

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._cache: dict[str, str] = {}
        self._lock = threading.Lock()
        self._esbuild_path = self._find_esbuild()
        self._watcher = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, render_config: RenderConfig) -> str:
        """
        Compile the React component and return a complete HTML page string.

        Dev mode  (production=False): rebuilt on every request; build errors
                  are shown as a styled overlay in the browser.
        Prod mode (production=True):  bundles are cached in-memory and
                  minified. Use start_watcher() to auto-invalidate on change.
        """
        try:
            component_path = self._resolve_component(render_config.file)
        except FileNotFoundError as exc:
            if self.config.production:
                raise
            return render_error_page(str(exc), render_config.file)

        cache_key = self._cache_key(component_path, render_config.props)

        if self.config.production and cache_key in self._cache:
            cached = json.loads(self._cache[cache_key])
            bundle_js, css = cached["js"], cached["css"]
        else:
            try:
                bundle_js, css = self._build(component_path, render_config.props)
            except RuntimeError as exc:
                if self.config.production:
                    raise
                return render_error_page(str(exc), component_path)

            if self.config.production:
                with self._lock:
                    self._cache[cache_key] = json.dumps({"js": bundle_js, "css": css})

        return self._wrap_html(bundle_js, css, render_config)

    def render_response(self, render_config: RenderConfig):
        """
        Convenience wrapper — returns a FastAPI HTMLResponse directly.

        Example:
            @app.get("/")
            async def index():
                return engine.render_response(RenderConfig(file="pages/Home.tsx"))
        """
        from fastapi.responses import HTMLResponse
        return HTMLResponse(self.render(render_config))

    def start_watcher(self):
        """
        Start a background thread that watches frontend_dir for file changes
        and clears cached bundles automatically (useful in production with
        long-lived processes). In plain dev mode (uvicorn --reload) this is
        optional since bundles are rebuilt on every request anyway.
        """
        from .watcher import FrontendWatcher

        def _on_change(changed_path: str):
            with self._lock:
                self._cache.clear()

        self._watcher = FrontendWatcher(
            watch_dir=self.config.frontend_dir,
            on_change=_on_change,
        )
        self._watcher.start()

    def stop_watcher(self):
        """Stop the file watcher if running."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None

    def clear_cache(self):
        """Manually clear all cached bundles."""
        with self._lock:
            self._cache.clear()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self, component_path: str, props: Optional[dict]) -> tuple[str, str]:
        """
        Write a tiny JSX entrypoint that imports the user component,
        invoke esbuild to bundle it into a single IIFE, and return
        (js_bundle, css_bundle).
        """
        props_json = json.dumps(props or {})

        entry_src = f"""
import React from 'react';
import {{ createRoot }} from 'react-dom/client';
import {{ Theme }} from '@radix-ui/themes';
import Component from '{component_path}';
import '@radix-ui/themes/styles.css';

const props = {props_json};

const savedTheme = "dark";
const container = document.getElementById('__py_ssr_root__');
if (container) {{
    const root = createRoot(container);
    root.render(
        React.createElement(
            Theme,
            {{ appearance: savedTheme }},
            React.createElement(Component, props)
        )
    );
}}
"""
        with tempfile.NamedTemporaryFile(
            suffix=".jsx", delete=False, mode="w", dir=tempfile.gettempdir()
        ) as f:
            f.write(entry_src)
            entry_path = f.name

        with tempfile.NamedTemporaryFile(
            suffix=".js", delete=False, dir=tempfile.gettempdir()
        ) as out:
            out_path = out.name

        css_path = out_path.replace(".js", ".css")

        try:
            cmd = [
                self._esbuild_path,
                entry_path,
                f"--outfile={out_path}",
                "--bundle",
                "--format=iife",
                "--loader:.tsx=tsx",
                "--loader:.ts=ts",
                "--loader:.jsx=jsx",
                "--loader:.js=js",
                "--loader:.css=css",
                "--loader:.svg=dataurl",
                "--loader:.png=dataurl",
                "--loader:.jpg=dataurl",
                "--loader:.gif=dataurl",
                "--loader:.woff=dataurl",
                "--loader:.woff2=dataurl",
            ]

            if self.config.production:
                cmd += ["--minify", "--tree-shaking=true"]

            env = os.environ.copy()
            node_modules = self._find_node_modules()
            if node_modules:
                env["NODE_PATH"] = node_modules

            result = subprocess.run(
                cmd, capture_output=True, text=True, env=env,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"esbuild compilation error in '{component_path}':\n\n{result.stderr}"
                )

            with open(out_path) as f:
                js = f.read()

            css = ""
            if os.path.exists(css_path):
                with open(css_path) as f:
                    css = f.read()

        finally:
            _safe_remove(entry_path)
            _safe_remove(out_path)
            _safe_remove(css_path)

        return js, css

    # ------------------------------------------------------------------
    # HTML wrapping
    # ------------------------------------------------------------------

    def _wrap_html(self, js: str, css: str, rc: RenderConfig) -> str:
        meta_html = "\n".join(
            f'    <meta name="{k}" content="{v}">'
            for k, v in rc.meta_tags.items()
        )

        global_css = ""
        if self.config.tailwind_css_path:
            try:
                with open(self.config.tailwind_css_path) as f:
                    global_css = f"<style>{f.read()}</style>"
            except FileNotFoundError:
                pass

        inline_css = f"<style>{css}</style>" if css.strip() else ""

        return f"""<!DOCTYPE html>
<html lang="{rc.lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{rc.title}</title>
{meta_html}
{global_css}
{inline_css}
</head>
<body>
    <div id="__py_ssr_root__"></div>
    <script>{js}</script>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_component(self, file: str) -> str:
        """
        Resolve a component path to an absolute filesystem path.

        Accepts:
          - Relative + extension:  'pages/Home.tsx'
          - Relative, no ext:      'pages/Home'  → tries .tsx/.ts/.jsx/.js
          - Absolute:              '/abs/Comp.tsx'
        """
        if os.path.isabs(file):
            base = file
        else:
            base = os.path.join(self.config.frontend_dir, file)

        if any(base.endswith(ext) for ext in self.config.extensions):
            if not os.path.exists(base):
                raise FileNotFoundError(
                    f"Component not found: {base}\n"
                    f"(frontend_dir = '{self.config.frontend_dir}')"
                )
            return os.path.abspath(base)

        for ext in self.config.extensions:
            candidate = base + ext
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        raise FileNotFoundError(
            f"Could not resolve component '{file}'.\n"
            f"Looked in: '{self.config.frontend_dir}'\n"
            f"Tried extensions: {self.config.extensions}"
        )

    def _cache_key(self, path: str, props: Optional[dict]) -> str:
        try:
            mtime = str(os.path.getmtime(path))
        except OSError:
            mtime = "0"
        raw = f"{path}:{mtime}:{json.dumps(props or {}, sort_keys=True)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _find_esbuild(self) -> str:
        local = os.path.join(os.getcwd(), "node_modules", ".bin", "esbuild")
        if os.path.exists(local):
            return local
        import shutil
        found = shutil.which("esbuild")
        if found:
            return found
        raise RuntimeError(
            "esbuild binary not found.\n"
            "Run:  npm install esbuild\n"
            "or:   npm install -g esbuild"
        )

    def _find_node_modules(self) -> Optional[str]:
        cwd = Path(os.getcwd())
        for parent in [cwd, *cwd.parents]:
            nm = parent / "node_modules"
            if nm.is_dir():
                return str(nm)
        return None


def _safe_remove(path: str):
    try:
        if os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass
