"""Tests for global vs in-repo install root resolution."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aftertone_paths import resolve_repo_root


def test_resolve_from_explicit(tmp_path: Path) -> None:
    (tmp_path / "py").mkdir()
    (tmp_path / "py" / "speak_summary_prepare.py").write_text("# stub\n")
    assert resolve_repo_root(tmp_path) == tmp_path.resolve()


def test_resolve_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "py").mkdir()
    (tmp_path / "py" / "speak_summary_prepare.py").write_text("# stub\n")
    monkeypatch.setenv("AFTERTONE_INSTALL_DIR", str(tmp_path))
    monkeypatch.delenv("AFTERTONE_REPO", raising=False)
    assert resolve_repo_root() == tmp_path.resolve()


def test_resolve_from_install_dir_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    install = tmp_path / "install"
    (install / "py").mkdir(parents=True)
    (install / "py" / "speak_summary_prepare.py").write_text("# stub\n")

    marker_dir = tmp_path / "fakehome" / ".cursor" / "hooks"
    marker_dir.mkdir(parents=True)
    (marker_dir / "aftertone-install-dir").write_text(f"{install}\n")

    monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
    monkeypatch.delenv("AFTERTONE_REPO", raising=False)
    monkeypatch.delenv("AFTERTONE_INSTALL_DIR", raising=False)

    import aftertone_paths as ap

    monkeypatch.setattr(ap, "_INSTALL_DIR_FILE", marker_dir / "aftertone-install-dir")
    assert resolve_repo_root() == install.resolve()


def test_missing_install_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AFTERTONE_REPO", raising=False)
    monkeypatch.delenv("AFTERTONE_INSTALL_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    import aftertone_paths as ap

    fake_py = tmp_path / "orphan" / "py"
    fake_py.mkdir(parents=True)
    monkeypatch.setattr(ap, "__file__", str(fake_py / "aftertone_paths.py"))
    monkeypatch.setattr(
        ap, "_INSTALL_DIR_FILE", tmp_path / ".cursor" / "hooks" / "aftertone-install-dir"
    )
    with pytest.raises(FileNotFoundError):
        resolve_repo_root()
