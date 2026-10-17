import json

import pytest

from hs_pattern_detector import detect_patterns
from hs_pattern_detector.cli import main

HS = [100, 110, 102, 118, 102, 110, 100]


def test_hs_geometry():
    patterns = detect_patterns(HS)
    assert len(patterns) == 1
    p = patterns[0]
    assert p.pattern_type == "HS"
    assert [p.left_shoulder.index, p.n1.index, p.head.index,
            p.n2.index, p.right_shoulder.index] == [1, 2, 3, 4, 5]
    assert p.neckline_at(3) == 102
    assert p.confirmed_at == 6
    assert p.geometric_fit == 1


def test_shoulder_tolerance():
    asymmetric = [100, 110, 102, 118, 102, 113, 100]
    assert detect_patterns(asymmetric, shoulder_tolerance=0.20)
    assert detect_patterns(asymmetric, shoulder_tolerance=0.10) == []


def test_neckline_tolerance():
    sloped = [100, 110, 102, 118, 104, 112, 100]
    assert detect_patterns(sloped, neckline_tolerance=0.2)
    assert detect_patterns(sloped, neckline_tolerance=0.1) == []
    p = detect_patterns(sloped)[0]
    assert p.neckline_at(3) == 103
    assert p.neckline_at(5) == 105


def test_prominence():
    assert detect_patterns(HS, min_head_prominence=0.4)
    assert detect_patterns(HS, min_head_prominence=0.6) == []


def test_no_unconfirmed_right_shoulder():
    assert detect_patterns(HS[:-1]) == []


def test_cli(tmp_path, capsys):
    csv = tmp_path / "synthetic.csv"
    csv.write_text("price\n" + "\n".join(map(str, HS)))
    assert main([str(csv)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["patterns"][0]["pattern_type"] == "HS"
    assert len(result["patterns"][0]["neckline"]) == 2


def test_cli_no_match(tmp_path, capsys):
    csv = tmp_path / "monotonic.csv"
    csv.write_text("price\n1\n2\n3\n")
    assert main([str(csv)]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "message": "No patterns detected.", "patterns": []}


def test_scale_invariance():
    p = detect_patterns([v * 10 for v in HS])[0]
    assert p.pattern_type == "HS"
    assert p.geometric_fit == pytest.approx(1)
