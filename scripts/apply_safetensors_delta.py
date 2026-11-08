#!/usr/bin/env python3
"""Compatibility launcher for the bundled wsp-edit skill script."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_TARGET = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "wsp-edit" / "scripts" / "apply_safetensors_delta.py"
_SPEC = importlib.util.spec_from_file_location("wsp_edit_apply_safetensors_delta", _TARGET)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load bundled editor: {_TARGET}")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
parse_index = _MODULE.parse_index
sha256 = _MODULE.sha256

if __name__ == "__main__":
    raise SystemExit(_MODULE.main())
