import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import example  # noqa: E402
from example import (CONFIGS, REDACTED, compare, make_config,  # noqa: E402
                     render_summary, validate_config)


class Contract(unittest.TestCase):
    def test_missing_command_fails(self):
        for cfg in [{"args": ["a"]}, {"command": ""}, {"command": "  "}, {"command": 5}]:
            with self.subTest(cfg=cfg):
                with self.assertRaises(ValueError):
                    validate_config(cfg)

    def test_single_string_args_fails(self):
        with self.assertRaises(ValueError):
            validate_config({"command": "python3", "args": "-m server"})

    def test_valid_record_gives_redacted_summary(self):
        cfg = {"command": "python3", "args": ["-m", "server"],
               "env": {"API_KEY": "hunter2"}}
        r = validate_config(cfg)
        self.assertTrue(r["ok"])
        self.assertEqual(r["summary"]["env"], {"API_KEY": REDACTED})
        self.assertNotIn("hunter2", repr(r))
        self.assertNotIn("hunter2", render_summary(r["summary"]))
        self.assertFalse(r["summary"]["launched"])

    def test_does_not_launch_process(self):
        self.assertFalse(hasattr(example, "subprocess"))
        with mock.patch("subprocess.Popen") as popen, mock.patch("os.system") as system:
            validate_config({"command": "python3", "args": ["-m", "server"]})
        popen.assert_not_called()
        system.assert_not_called()


class Boundaries(unittest.TestCase):
    def test_empty_args_and_env_are_valid(self):
        r = validate_config({"command": "python3"})
        self.assertEqual(r["summary"]["args"], [])
        self.assertEqual(r["summary"]["env"], {})

    def test_bad_args_and_env(self):
        bad = [
            {"command": "x", "args": [1]},
            {"command": "x", "args": None},
            {"command": "x", "env": {"lower": "v"}},
            {"command": "x", "env": {"1BAD": "v"}},
            {"command": "x", "env": {"OK": 5}},
            {"command": "x", "env": ["OK"]},
            None,
        ]
        for cfg in bad:
            with self.subTest(cfg=cfg):
                with self.assertRaises(ValueError):
                    validate_config(cfg)

    def test_input_is_not_modified(self):
        cfg = {"command": "x", "args": ["a"], "env": {"K": "v"}}
        before = repr(cfg)
        validate_config(cfg)
        self.assertEqual(repr(cfg), before)


class Comparison(unittest.TestCase):
    def test_three_configs_all_correct_and_no_leak(self):
        rows = compare()
        self.assertEqual([r[0] for r in rows], ["small", "medium", "large"])
        for row in rows:
            self.assertFalse(row[5], "secret leaked in " + row[0])

    def test_checks_grow_linearly_with_input_size(self):
        # checks = 2 (command, args type) + len(args) + len(env)
        for name, n_args, n_env, checks, _, _ in compare():
            self.assertEqual(checks, 2 + n_args + n_env, name)

    def test_report_size_independent_of_secret_length(self):
        sizes = {len(render_summary(validate_config(make_config(5, 3, n))["summary"]))
                 for n in (1, 8, 500)}
        self.assertEqual(len(sizes), 1)

    def test_known_values(self):
        rows = {r[0]: r for r in compare()}
        self.assertEqual(rows["small"][3], 4)
        self.assertEqual(rows["medium"][3], 17)
        self.assertEqual(rows["large"][3], 122)


if __name__ == "__main__":
    unittest.main()
