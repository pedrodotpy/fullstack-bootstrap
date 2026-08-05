"""Shared helpers for building tiny template zip fixtures."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path


def write_zip(path: Path, files: dict[str, str], *, root_prefix: str | None = "project") -> Path:
    """Write a zip with optional single root directory prefix (GitHub-style)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for relative, content in sorted(files.items()):
            name = f"{root_prefix}/{relative}" if root_prefix else relative
            zf.writestr(name, content.encode("utf-8"))
    return path


def backend_fixture_files() -> dict[str, str]:
    return {
        "pyproject.toml": (
            '[project]\nname = "django-boilerplate"\nversion = "0.1.0"\n\n'
            "[tool.pytest.ini_options]\n"
            'DJANGO_SETTINGS_MODULE = "config.settings.test"\n'
        ),
        "manage.py": (
            "import os\n"
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")\n'
        ),
        "README.md": (
            "# Django Boilerplate\n\n"
            "Companion frontend: `../react-boilerplate`.\n"
            "Shared SPECS: `../SPECS/`.\n\n"
            "cp config/settings/local.py.example config/settings/local.py\n"
        ),
        "AGENTS.md": "# Agent guidelines (django-boilerplate)\n\nFollow `../SPECS/`.\n",
        "schema.yml": (
            "openapi: 3.0.3\ninfo:\n  title: Django Boilerplate API\n  version: 0.1.0\n"
        ),
        "uv.lock": 'name = "django-boilerplate"\nversion = "0.1.0"\n',
        ".env.example": "SECRET_KEY=change-me\nDEBUG=True\n",
        "config/__init__.py": "",
        "config/urls.py": 'ROOT = "ok"\n',
        "config/wsgi.py": (
            "import os\n"
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")\n'
        ),
        "config/asgi.py": (
            "import os\n"
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")\n'
        ),
        "config/settings/__init__.py": (
            '"""Django settings package. Use DJANGO_SETTINGS_MODULE=config.settings.local"""\n'
        ),
        "config/settings/base.py": (
            "from decouple import Csv, config\n\n"
            'SECRET_KEY = config("SECRET_KEY")\n'
            'ROOT_URLCONF = "config.urls"\n'
            'WSGI_APPLICATION = "config.wsgi.application"\n'
            "SPECTACULAR_SETTINGS = {\n"
            '    "TITLE": "Django Boilerplate API",\n'
            '    "DESCRIPTION": "Login-gated Django REST API with JWT and model-level permissions",\n'
            "}\n"
        ),
        "config/settings/local.py.example": "from .base import *  # noqa\n",
        "config/settings/local.py": "FROM_LOCAL = True\n",
        "config/settings/test.py": "from .base import *  # noqa\n",
        "apps/__init__.py": "",
        ".venv/ignored.txt": "should-skip\n",
        "db.sqlite3": "should-skip\n",
        ".env": "SECRET=should-skip\n",
    }


def frontend_fixture_files() -> dict[str, str]:
    return {
        "package.json": '{\n  "name": "react-boilerplate",\n  "private": true\n}\n',
        "README.md": (
            "# React Boilerplate\n\n"
            "Talking to `../django-boilerplate` over JWT.\n"
        ),
        "AGENTS.md": "# Agent guidelines (react-boilerplate)\n\nFollow `../SPECS/`.\n",
        ".env.example": (
            "VITE_API_BASE_URL=http://localhost:8000\n"
            "OPENAPI_SCHEMA_PATH=../django-boilerplate/schema.yml\n"
        ),
        "openapi-ts.config.ts": (
            'export default {\n  input: process.env.OPENAPI_SCHEMA_PATH || "../django-boilerplate/schema.yml",\n};\n'
        ),
        "index.html": "<!doctype html><html><head><title>App</title></head><body></body></html>\n",
        "src/shared/layout/AppShell.tsx": (
            "export function AppShell() {\n"
            "  return (\n"
            "    <div>\n"
            "      <header>\n"
            "        <a>\n"
            "              App\n"
            "        </a>\n"
            "      </header>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
        ),
        "src/features/auth/pages/LoginPage.tsx": (
            "export function LoginPage() {\n"
            "  return (\n"
            "    <div>\n"
            "      <h1>\n"
            "            App\n"
            "      </h1>\n"
            "    </div>\n"
            "  );\n"
            "}\n"
        ),
        "src/shared/api/sdk.gen.ts": "// generated — keep django-boilerplate string harmless\n",
        "node_modules/leftpad/index.js": "should-skip\n",
        "dist/index.html": "should-skip\n",
        ".env": "should-skip\n",
    }


def zip_bytes(files: dict[str, str], *, root_prefix: str | None = "project") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for relative, content in sorted(files.items()):
            name = f"{root_prefix}/{relative}" if root_prefix else relative
            zf.writestr(name, content.encode("utf-8"))
    return buffer.getvalue()
