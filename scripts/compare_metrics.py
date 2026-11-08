#!/usr/bin/env python3
"""Compatibility launcher for the bundled wsp-decide metric comparator."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_TARGET = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "wsp-decide" / "scripts" / "compare_metrics.py"
_SPEC = importlib.util.spec_from_file_location("wsp_decide_compare_metrics", _TARGET)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load bundled metric comparator: {_TARGET}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
read_metrics = _MODULE.read_metrics
parse_guard = _MODULE.parse_guard
main = _MODULE.main

if __name__ == "__main__":
    raise SystemExit(main())
