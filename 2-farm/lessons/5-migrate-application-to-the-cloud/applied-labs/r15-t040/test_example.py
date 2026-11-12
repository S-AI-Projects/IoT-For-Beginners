import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import example  # noqa: E402
from example import LESSON_CONCEPTS, REDACTED, main, validate  # noqa: E402

SECRET = "HostName=demo;SharedAccessKey=not-a-real-key"
VALID = {"command": "func", "args": ["start"], "env": {"IOT_HUB_CONNECTION_STRING": SECRET}}


class Contract(unittest.TestCase):
    def test_missing_command_fails(self):
        for cfg in [{"args": ["start"]}, {"command": ""}, {"command": "   "}, {"command": 7}]:
            with self.subTest(cfg=cfg):
                r = validate(cfg)
                self.assertFalse(r["ok"])
                self.assertIn("command is missing or empty", r["errors"])
                self.assertIsNone(r["summary"])

    def test_single_string_args_fails(self):
        r = validate({"command": "func", "args": "start --port 7071"})
        self.assertFalse(r["ok"])
        self.assertIn("args must be a list of strings, not a single string", r["errors"])

    def test_valid_record_gives_redacted_summary(self):
        r = validate(VALID)
        self.assertTrue(r["ok"])
        self.assertEqual(r["summary"], {
            "command": "func", "args": ["start"],
            "env": {"IOT_HUB_CONNECTION_STRING": REDACTED}, "launched": False})
        self.assertNotIn(SECRET, json.dumps(r))
        self.assertNotIn("not-a-real-key", json.dumps(r))

    def test_does_not_launch_process(self):
        self.assertFalse(hasattr(example, "subprocess"))
        with mock.patch("subprocess.Popen") as popen, mock.patch("os.system") as system:
            validate(VALID)
        popen.assert_not_called()
        system.assert_not_called()


class Boundaries(unittest.TestCase):
    def test_args_and_env_default_to_empty(self):
        r = validate({"command": "func"})
        self.assertTrue(r["ok"])
        self.assertEqual(r["summary"]["args"], [])
        self.assertEqual(r["summary"]["env"], {})

    def test_all_errors_are_reported_together(self):
        r = validate({"args": "x", "env": {"bad": "v"}})
        self.assertEqual(len(r["errors"]), 3)

    def test_other_invalid_shapes(self):
        for cfg in [None, "func start", [], {"command": "f", "args": [1]},
                    {"command": "f", "args": None},
                    {"command": "f", "env": ["A"]},
                    {"command": "f", "env": {"A": 5}},
                    {"command": "f", "env": {"1A": "v"}}]:
            with self.subTest(cfg=cfg):
                self.assertFalse(validate(cfg)["ok"])

    def test_input_not_modified(self):
        before = json.dumps(VALID)
        validate(VALID)
        self.assertEqual(json.dumps(VALID), before)


class LessonConnection(unittest.TestCase):
    def test_every_public_field_is_mapped_to_a_lesson_concept(self):
        r = validate(VALID)
        public = {"command", "args", "env"} | {"summary." + k for k in r["summary"]
                                              if k in ("env", "launched")} | {"errors"}
        self.assertTrue(public <= set(LESSON_CONCEPTS))
        for key, text in LESSON_CONCEPTS.items():
            self.assertTrue(text.strip(), key)

    def test_lesson_readme_agrees_with_example(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            text = f.read()
        for key in LESSON_CONCEPTS:
            self.assertIn("`%s`" % key, text)


class CommandLine(unittest.TestCase):
    def run_main(self, cfg):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cfg.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main([path])
        return code, buf.getvalue()

    def test_valid_exit_zero_and_no_secret_printed(self):
        code, out = self.run_main(VALID)
        self.assertEqual(code, 0)
        self.assertIn(REDACTED, out)
        self.assertNotIn("not-a-real-key", out)

    def test_invalid_exit_nonzero(self):
        code, out = self.run_main({"args": ["start"]})
        self.assertEqual(code, 1)
        self.assertIn("command is missing or empty", out)

    def test_bad_usage_and_unreadable_file(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main([]), 2)
            self.assertEqual(main(["/no/such/file.json"]), 2)


if __name__ == "__main__":
    unittest.main()
