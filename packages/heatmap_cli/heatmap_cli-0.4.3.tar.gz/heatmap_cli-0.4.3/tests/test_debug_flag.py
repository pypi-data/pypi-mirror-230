# pylint: disable=missing-module-docstring,missing-function-docstring

import pytest


@pytest.mark.parametrize("option", ["-d", "--debug"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, option)
    assert "debug=True" in ret.stderr
    assert "DEBUG: MainProcess: number of cpu:" in ret.stderr
    assert "DEBUG: MainProcess: added worker" in ret.stderr
    assert "generate heatmap png file:" in ret.stderr
