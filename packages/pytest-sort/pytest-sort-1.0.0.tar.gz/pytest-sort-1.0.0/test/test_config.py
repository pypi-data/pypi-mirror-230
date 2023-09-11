import importlib
from pathlib import Path

import pytest

from pytest_sort import config, database


class TestSortConfig:
    @pytest.fixture(autouse=True)
    def reset(self):
        importlib.reload(config)
        importlib.reload(database)

        yield

        importlib.reload(database)

    class PytestConfig:
        def __init__(self, options, inis):
            self.options = options
            self.inis = inis

        def getoption(self, name, default=None):
            return self.options.get(name, default)

        def getini(self, name):
            return self.inis.get(name, [])

    def test_defaults(self):
        assert config.SortConfig.mode == "ordered"
        assert config.SortConfig.bucket == "parent"
        assert config.SortConfig.bucket_mode == "sort_mode"
        assert config.SortConfig.record == None
        assert config.SortConfig.reset == False
        assert config.SortConfig.report == False

        assert config.SortConfig.seed >= 0
        assert config.SortConfig.seed <= 1_000_000

        assert config.SortConfig.recorded_times == {}
        assert config.SortConfig.item_totals == {}
        assert config.SortConfig.item_sort_keys == {}
        assert config.SortConfig.item_bucket_id == {}
        assert config.SortConfig.bucket_sort_keys == {}

    def test_from_pytest_default(self):
        pytest_config = self.PytestConfig({}, {})

        seed = config.SortConfig.seed
        config.SortConfig.from_pytest(pytest_config)

        assert config.SortConfig.mode == "ordered"
        assert config.SortConfig.bucket == "parent"
        assert config.SortConfig.bucket_mode == "ordered"
        assert config.SortConfig.record == None
        assert config.SortConfig.reset == False
        assert config.SortConfig.report == False
        assert config.SortConfig.seed == seed

        assert database.database_file.absolute() == (Path.cwd() / ".pytest_sort").absolute()

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({"sort_mode": "md5"}, {"sort_mode": "random"}, "md5"),
            ({}, {"sort_mode": "random"}, "random"),
            ({}, {"sort_mode": "none"}, "ordered"),
            ({}, {}, "ordered"),
        ],
    )
    def test_from_pytest_mode(self, getoption, getini, expected):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.mode == expected

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({"sort_bucket": "session"}, {"sort_bucket": "class"}, "session"),
            ({}, {"sort_bucket": "class"}, "class"),
            ({}, {"sort_bucket": "global"}, "session"),
            ({}, {}, "parent"),
        ],
    )
    def test_from_pytest_bucket(self, getoption, getini, expected):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.bucket == expected

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({"sort_bucket_mode": "md5"}, {"sort_bucket_mode": "random"}, "md5"),
            ({}, {"sort_bucket_mode": "random"}, "random"),
            ({}, {"sort_bucket_mode": "none"}, "ordered"),
            ({}, {}, "ordered"),
            ({"sort_mode": "md5"}, {}, "md5"),
        ],
    )
    def test_from_pytest_bucket_mode(self, getoption, getini, expected):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.bucket_mode == expected

    def test_from_pytest_sort_record_conflict(self):
        pytest_config = self.PytestConfig({"sort_no_record": True, "sort_record": True}, {})
        with pytest.raises(ValueError, match="Do not use both --sort-record-times and --sort-no-record-times"):
            config.SortConfig.from_pytest(pytest_config)

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({"sort_record": True}, {}, True),
            ({"sort_no_record": True}, {}, False),
            ({}, {"sort_record_times": True}, True),
            ({}, {"sort_record_times": False}, False),
            ({"sort_mode": "fastest"}, {}, True),
        ],
    )
    def test_from_pytest_sort_record(self, getoption, getini, expected):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.record == expected

    def test_from_pytest_sort_reset(self):
        pytest_config = self.PytestConfig({"sort_reset_times": True}, {})
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.reset == True

    def test_from_pytest_sort_report(self):
        pytest_config = self.PytestConfig({"sort_report_times": True}, {})
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.report == True

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({"sort_seed": "123"}, {"sort_seed": "456"}, 123),
            ({}, {"sort_seed": "456"}, 456),
        ],
    )
    def test_from_pytest_seed_getoption(self, getoption, getini, expected):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert config.SortConfig.seed == expected

    def test_from_pytest_seed_invalid(self):
        pytest_config = self.PytestConfig({}, {"sort_seed": "ABC"})
        with pytest.raises(ValueError, match="Invalid seed value 'ABC' must be int"):
            config.SortConfig.from_pytest(pytest_config)

    @pytest.mark.parametrize(
        "getoption,getini,expected",
        [
            ({}, {}, Path.cwd() / ".pytest_sort"),
            (
                {"sort_datafile": "./tests/.sort_db"},
                {"sort_datafile": "./tests/.sort"},
                Path.cwd() / "tests" / ".sort_db",
            ),
            ({}, {"sort_datafile": "./tests/.sort"}, Path.cwd() / "tests" / ".sort"),
        ],
    )
    def test_from_pytest_database_file_default(self, getoption, getini, expected: Path):
        pytest_config = self.PytestConfig(getoption, getini)
        config.SortConfig.from_pytest(pytest_config)
        assert database.database_file.absolute() == expected.absolute()


class TestDict:
    @pytest.fixture(autouse=True)
    def reset(self):
        importlib.reload(config)
        config.SortConfig.bucket_mode = "ordered"

    def test_header_dict_default(self):
        assert config.SortConfig.header_dict() == {
            "sort-mode": "ordered",
        }

    def test_header_dict_sort_bucket_ordered_match(self):
        config.SortConfig.bucket = "module"
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket_mode = "ordered"
        assert config.SortConfig.header_dict() == {
            "sort-mode": "ordered",
        }

    def test_header_dict_sort_bucket_ordered_mismatch(self):
        config.SortConfig.bucket = "module"
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket_mode = "reverse"
        assert config.SortConfig.header_dict() == {
            "sort-mode": "ordered",
            "sort-bucket": "module",
            "sort-bucket-mode": "reverse",
        }

    def test_header_dict_sort_bucket_reverse_match(self):
        config.SortConfig.bucket = "module"
        config.SortConfig.mode = "reverse"
        config.SortConfig.bucket_mode = "reverse"
        assert config.SortConfig.header_dict() == {
            "sort-mode": "reverse",
        }

    def test_header_dict_sort_bucket_reverse_mismatch(self):
        config.SortConfig.bucket = "module"
        config.SortConfig.mode = "md5"
        config.SortConfig.bucket_mode = "reverse"
        assert config.SortConfig.header_dict() == {
            "sort-mode": "md5",
            "sort-bucket": "module",
            "sort-bucket-mode": "reverse",
        }

    def test_header_dict_sort_bucket_other_match(self):
        config.SortConfig.bucket = "module"
        config.SortConfig.mode = "md5"
        config.SortConfig.bucket_mode = "md5"
        assert config.SortConfig.header_dict() == {
            "sort-mode": "md5",
            "sort-bucket": "module",
        }

    def test_header_dict_random(self):
        config.SortConfig.mode = "random"
        config.SortConfig.bucket_mode = "random"
        config.SortConfig.bucket = "module"
        config.SortConfig.seed = 1234
        assert config.SortConfig.header_dict() == {
            "sort-mode": "random",
            "sort-bucket": "module",
            "sort-seed": 1234,
        }

    def test_header_dict_reset(self):
        config.SortConfig.mode = "fastest"
        config.SortConfig.bucket_mode = "fastest"
        config.SortConfig.bucket = "module"
        config.SortConfig.reset = True
        assert config.SortConfig.header_dict() == {
            "sort-mode": "fastest",
            "sort-bucket": "module",
            "sort-reset-times": True,
        }

    def test_header_dict_record(self):
        config.SortConfig.mode = "fastest"
        config.SortConfig.bucket_mode = "fastest"
        config.SortConfig.bucket = "module"
        config.SortConfig.record = True
        assert config.SortConfig.header_dict() == {
            "sort-mode": "fastest",
            "sort-bucket": "module",
            "sort-record-times": True,
        }

    def test_header_dict_report(self):
        config.SortConfig.mode = "fastest"
        config.SortConfig.bucket_mode = "fastest"
        config.SortConfig.bucket = "module"
        config.SortConfig.report = True
        assert config.SortConfig.header_dict() == {
            "sort-mode": "fastest",
            "sort-bucket": "module",
            "sort-report-times": True,
        }

    def test_header_dict_debug(self):
        config.SortConfig.mode = "fastest"
        config.SortConfig.bucket_mode = "fastest"
        config.SortConfig.bucket = "module"
        config.SortConfig.debug = True
        assert config.SortConfig.header_dict() == {
            "sort-mode": "fastest",
            "sort-bucket": "module",
            "sort-debug": True,
        }
