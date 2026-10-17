import pytest

from hs_pattern_detector import detect_patterns
from hs_pattern_detector.cli import main


@pytest.mark.parametrize("values", [list(range(1, 30)), list(range(30, 0, -1)),
                                    [10]*20, [], [1, 2]])
def test_no_pattern(values):
    assert detect_patterns(values) == []


@pytest.mark.parametrize("values, error", [
    (None, TypeError), ("123", TypeError), ([1, "2"], TypeError),
    ([1, True], TypeError), ([1, None], TypeError),
    ([1, float("nan")], ValueError), ([1, float("inf")], ValueError),
    ([1, 0], ValueError), ([1, -1], ValueError),
])
def test_bad_prices(values, error):
    with pytest.raises(error):
        detect_patterns(values)


@pytest.mark.parametrize("kwargs, error", [
    ({"pivot_window": 0}, ValueError), ({"pivot_window": 1.5}, TypeError),
    ({"pivot_window": True}, TypeError), ({"shoulder_tolerance": -0.1}, ValueError),
    ({"neckline_tolerance": 1.1}, ValueError),
    ({"min_head_prominence": 0}, ValueError),
    ({"max_time_ratio": 0.5}, ValueError),
    ({"shoulder_tolerance": float("nan")}, ValueError),
    ({"max_time_ratio": "2"}, TypeError),
])
def test_bad_parameters(kwargs, error):
    with pytest.raises(error):
        detect_patterns([], **kwargs)


@pytest.mark.parametrize("content", ["close\n1\n", "price\nnope\n", "price\nnan\n"])
def test_cli_invalid(tmp_path, content, capsys):
    path = tmp_path / "invalid.csv"
    path.write_text(content)
    with pytest.raises(SystemExit) as exc:
        main([str(path)])
    assert exc.value.code == 2
    assert "error:" in capsys.readouterr().err
