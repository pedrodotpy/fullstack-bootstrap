"""Command-line entry point: one argument — the client name."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fullstack_bootstrap.bootstrap import BootstrapError, bootstrap
from fullstack_bootstrap.naming import NamingError
from fullstack_bootstrap.sources import SourcesError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fullstack-bootstrap",
        description=(
            "Deterministically generate sibling backend and frontend repositories "
            "from pinned Django/React boilerplates. Client name is the only parameter."
        ),
    )
    parser.add_argument(
        "client_name",
        help='Client display name, e.g. "Acme Corp"',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = bootstrap(args.client_name, output_dir=Path.cwd())
    except NamingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except SourcesError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except BootstrapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Created {result.backend_path}")
    print(f"Created {result.frontend_path}")
    print()
    print("Next steps (not run by bootstrap):")
    print(f"  cd {result.backend_path.name}")
    print(f"  cp .env.example .env")
    print(f"  cp {result.names.python_id}/settings/local.py.example {result.names.python_id}/settings/local.py")
    print("  uv sync && uv run python manage.py migrate")
    print()
    print(f"  cd ../{result.frontend_path.name}")
    print("  cp .env.example .env && yarn install && yarn dev")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
