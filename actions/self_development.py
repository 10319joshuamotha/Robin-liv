"""Approval-gated self-development for Robin."""
from __future__ import annotations
import subprocess, sys
from datetime import datetime
from pathlib import Path
from core import confirm as confirm_gate
from core import gemini

BASE_DIR = Path(__file__).resolve().parent.parent
PROTECTED = {"core/confirm.py", "core/action_loader.py", "actions/self_development.py", "core/prompt.txt", "config/api_keys.json"}
_pending = {"patch": "", "branch": ""}

def _git(*args, check=True):
    p = subprocess.run(["git", *args], cwd=BASE_DIR, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if check and p.returncode: raise RuntimeError(p.stderr.strip() or "git failed")
    return p.stdout.strip()

def _safe(path):
    p = Path(str(path)).as_posix().lstrip("./")
    return bool(p) and ".." not in Path(p).parts and p.endswith(".py") and p not in PROTECTED

def _inspect(parameters):
    path = str(parameters.get("path", "")).strip()
    if not path: return "Please specify a source file to inspect."
    if not _safe(path): return "That source path is protected or not an allowed Python source file."
    target = BASE_DIR / path
    if not target.exists(): return f"Source file not found: {path}"
    return target.read_text(encoding="utf-8", errors="replace")[:30000]

def _propose(parameters):
    goal = str(parameters.get("goal", "")).strip(); path = str(parameters.get("path", "")).strip()
    if not goal or not path: return "I need both the improvement and source path."
    if not _safe(path): return "That source path is protected. I will not modify it through self-development."
    target = BASE_DIR / path
    if not target.exists(): return f"Source file not found: {path}"
    current = target.read_text(encoding="utf-8", errors="replace")
    prompt = "Return ONLY a unified git diff for this one file. Never remove confirmation, permission, security, safety, rollback, or credential protections. Keep the patch minimal and syntactically valid. Goal: " + goal + "\nTarget: " + path + "\nCurrent file:\n" + current
    resp = gemini.call(prompt, tier=gemini.SMART, timeout_ms=60000)
    if resp is None: return "I could not generate a proposal right now."
    patch = str(resp.text or "").strip()
    if patch.startswith("```"): patch = patch.split("\n",1)[-1].rsplit("```",1)[0].strip()
    if len(patch) > 120000 or "diff --git" not in patch: return "The proposal failed validation. Nothing was changed."
    branch = "robin/self-dev-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        _git("switch", "-c", branch)
        chk = subprocess.run(["git","apply","--check","--whitespace=error"], cwd=BASE_DIR, input=patch, text=True, capture_output=True, encoding="utf-8", errors="replace")
        if chk.returncode: _git("switch","-",check=False); return "The proposed patch failed validation. Nothing was changed."
        _pending.update(patch=patch, branch=branch)
        return confirm_gate.request("self-code-change", "Robin wants to modify her source code", path + "\nReason: " + goal + "\nBranch: " + branch + "\nOnly this patch will be applied after you confirm.", _apply)
    except Exception as e:
        _git("switch","-",check=False); return f"Could not prepare the proposal: {e}"

def _apply():
    patch = _pending.get("patch","")
    if not patch: return "No pending self-development patch."
    chk = subprocess.run(["git","apply","--check","--whitespace=error"], cwd=BASE_DIR, input=patch, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if chk.returncode: return "The approved patch no longer applies cleanly. Nothing changed."
    ap = subprocess.run(["git","apply","--whitespace=error"], cwd=BASE_DIR, input=patch, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if ap.returncode: return "The approved patch failed to apply. Nothing changed."
    names = _git("diff","--name-only").splitlines(); py = [n for n in names if n.endswith(".py")]
    if py:
        q = subprocess.run([sys.executable,"-m","py_compile",*py], cwd=BASE_DIR, text=True, capture_output=True, encoding="utf-8", errors="replace")
        if q.returncode: _git("reset","--hard","HEAD",check=False); return "Syntax validation failed. The change was rolled back."
        _git("add","--",*py)
    _git("commit","-m","Robin self-development: approved change"); _pending["patch"] = ""
    return "Approved change applied, syntax-checked, and committed on the Robin branch."

TOOL = {"name":"self_development","description":"Inspect Robin source and propose code improvements. Any source-code change requires human confirmation before application. Protected confirmation, security, prompt, credential, and self-development files cannot be modified by this tool.","parameters":{"type":"OBJECT","properties":{"action":{"type":"STRING","description":"inspect | propose"},"path":{"type":"STRING","description":"Relative Python source path"},"goal":{"type":"STRING","description":"Desired improvement when action=propose"}},"required":["action"]},"handler":lambda parameters, **ctx: _inspect(parameters) if str(parameters.get("action","")).lower()=="inspect" else _propose(parameters)}
