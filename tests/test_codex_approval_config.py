"""Check that opting in edits only the expected cached stdio environment."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("approval_config", ROOT / "scripts/configure_codex_approval.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ApprovalConfigTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".codex-plugin").mkdir()
        for name in ("plugin.json", ".codex-plugin/plugin.json", ".mcp.json", "mcp.json"):
            (self.root / name).write_bytes((ROOT / name).read_bytes())
        self.path = self.root / ".mcp.json"

    def test_enable_and_restore_preserve_other_settings(self):
        data = json.loads(self.path.read_text())
        server = data["mcpServers"]["secrethandoff"]
        server["env"] = {"PUBLIC_TEST_SETTING": "keep"}
        data["mcpServers"]["other"] = {"command": "keep", "args": []}
        self.path.write_text(json.dumps(data))
        for mode in ("codex", "browser"):
            module.configure(self.root, mode)
            server["env"]["SECRETHANDOFF_COMMAND_APPROVAL"] = mode
            self.assertEqual(json.loads(self.path.read_text()), data)
            self.assertEqual(json.loads((self.root / "mcp.json").read_text())["mcpServers"]["secrethandoff"]["env"], {"SECRETHANDOFF_COMMAND_APPROVAL": mode})

    def test_unexpected_launcher_is_rejected_without_edit(self):
        data = json.loads(self.path.read_text())
        data["mcpServers"]["secrethandoff"]["command"] = "unexpected"
        self.path.write_text(json.dumps(data))
        before = self.path.read_bytes()
        native_before = (self.root / "mcp.json").read_bytes()
        with self.assertRaises(ValueError):
            module.configure(self.root, "codex")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual((self.root / "mcp.json").read_bytes(), native_before)

    def test_alternative_manifest_path_is_rejected(self):
        path = self.root / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["mcpServers"] = "./other.json"
        path.write_text(json.dumps(data))
        before = self.path.read_bytes()
        native_before = (self.root / "mcp.json").read_bytes()
        with self.assertRaises(ValueError):
            module.configure(self.root, "codex")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual((self.root / "mcp.json").read_bytes(), native_before)

    def test_symlink_is_rejected(self):
        target = self.root / "other.json"
        self.path.rename(target)
        self.path.symlink_to(target)
        before = target.read_bytes()
        with self.assertRaises(ValueError):
            module.configure(self.root, "codex")
        self.assertEqual(target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
