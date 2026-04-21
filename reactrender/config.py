from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    frontend_dir: str = "./frontend/src"
    """Directory containing your React component files."""

    asset_route: str = "/assets"
    """URL route prefix where bundled JS/CSS assets are served."""

    tailwind_css_path: Optional[str] = None
    """Optional path to a Tailwind/global CSS file to inject into every page."""

    production: bool = False
    """When True, bundles are minified and caching is enabled."""

    extensions: list = field(default_factory=lambda: [".tsx", ".ts", ".jsx", ".js"])
    """File extensions to resolve when no extension is given."""
