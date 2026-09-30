import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "actions" / "self_development.py"
spec = importlib.util.spec_from_file_location("self_development_under_test", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_protected_paths_are_rejected():
    assert not module._safe("core/confirm.py")
    assert not module._safe("core/prompt.txt")
    assert not module._safe("../main.py")
    assert not module._safe("/tmp/robin.py")


def test_patch_path_is_single_and_exact():
    patch = """diff --git a/main.py b/main.py
index 1111111..2222222 100644
--- a/main.py
+++ b/main.py
@@ -1 +1 @@
-old
+new
"""
    assert module._patch_paths(patch) == ["main.py"]
    second_file = patch + """diff --git a/ui.py b/ui.py
"""
    assert module._patch_paths(second_file) != ["main.py"]
