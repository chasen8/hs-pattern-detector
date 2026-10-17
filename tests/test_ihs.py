from hs_pattern_detector import detect_patterns


def test_ihs_geometry():
    patterns = detect_patterns([120, 110, 118, 102, 118, 110, 120])
    assert len(patterns) == 1
    p = patterns[0]
    assert p.pattern_type == "IHS"
    assert p.head.price < min(p.left_shoulder.price, p.right_shoulder.price)
    assert p.neckline_at(3) == 118
    assert p.geometric_fit == 1


def test_ihs_tolerance():
    values = [120, 110, 118, 102, 118, 107, 120]
    assert detect_patterns(values, shoulder_tolerance=0.20)
    assert detect_patterns(values, shoulder_tolerance=0.10) == []


def test_larger_window():
    anchors = [100, 110, 102, 118, 102, 110, 100]
    values = [a+(b-a)*j/3 for a, b in zip(anchors, anchors[1:]) for j in range(3)] + [100]
    p = detect_patterns(values, pivot_window=2)[0]
    assert p.right_shoulder.index == 15
    assert p.confirmed_at == 17
