import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/project-preflight/skills/project-preflight/scripts/check_updates.py"

class UpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("checker", SCRIPT)
        cls.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.checker)

    def test_unchanged_needs_no_compare(self):
        def api(path):
            self.assertTrue(path.endswith("/commits/HEAD"))
            return {"sha": "same"}
        result = self.checker.check_repo("o/r", "same", api)
        self.assertEqual(result["status"], "current")

    def test_update_preserves_count_and_bounds_summary(self):
        def api(path):
            if path.endswith("/commits/HEAD"):
                return {"sha": "new"}
            return {"status": "ahead", "ahead_by": 9, "html_url": "https://github.com/o/r/compare/old...new",
                    "commits": [{"commit": {"message": f"change {i}\nbody"}} for i in range(9)],
                    "files": [{"filename": "skills/x/SKILL.md"}]}
        result = self.checker.check_repo("o/r", "old", api)
        self.assertEqual(result["count"], 9)
        self.assertEqual(len(result["commits"]), 3)
        self.assertEqual(result["files"], ["skills/x/SKILL.md"])

    def test_unknown_baseline_is_not_current(self):
        result = self.checker.check_repo("o/r", None, lambda _: {"sha": "new"})
        self.assertEqual(result["status"], "unknown_baseline")

    def test_divergence_is_not_normal_update(self):
        def api(path):
            return {"sha": "new"} if path.endswith("/commits/HEAD") else {"status": "diverged", "html_url": "link"}
        self.assertEqual(self.checker.check_repo("o/r", "old", api)["status"], "diverged")

    def test_failure_does_not_hide_other_results(self):
        results = self.checker.check_all([("bad", "o/bad", "old"), ("good", "o/good", "same")],
            lambda path: {"sha": "same"} if "/good/" in path else self.fail_api())
        self.assertEqual([r["status"] for r in results], ["error", "current"])

    @staticmethod
    def fail_api():
        raise RuntimeError("network unavailable")

if __name__ == "__main__":
    unittest.main()
