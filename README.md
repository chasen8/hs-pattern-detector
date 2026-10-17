# hs-pattern-detector

A lightweight, explainable Python detector for Head and Shoulders and Inverse Head and Shoulders chart patterns.

## Overview

This project is an experimental geometric pattern detector.
It is not financial advice and does not provide trading signals.

This standalone baseline implementation uses explicit geometric rules on an ordered,
strictly positive price sequence. It has no runtime dependencies and makes no claims
about real-market accuracy, profitability, users, or benchmarks. All included examples
and test sequences are synthetic and generated within this project.

## Features

- HS and IHS candidates with five pivots: LS, N1, Head, N2, RS.
- Configurable pivot window, shoulder similarity, neckline slope, head prominence,
  and temporal symmetry constraints.
- Zero-based pivot positions, neckline interpolation, geometric fit, and pivot
  confirmation position.
- Python API and CSV-to-JSON CLI; no network calls or data downloads.

## Installation

Requires Python >= 3.10. From the project root:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell alternative:
# .venv\Scripts\Activate.ps1
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Quick Start

```bash
python examples/synthetic_example.py --csv example.csv
hs-pattern-detector example.csv
```

The example prints one synthetic HS and one synthetic IHS result, then optionally
writes the selected sequence to CSV. The CLI detects one HS in the default CSV.

## Python API

```python
from hs_pattern_detector import detect_patterns

prices = [100, 110, 102, 118, 102, 110, 100]
patterns = detect_patterns(prices, shoulder_tolerance=0.25)
for pattern in patterns:
    print(pattern.pattern_type, pattern.left_shoulder, pattern.head,
          pattern.right_shoulder, pattern.neckline, pattern.geometric_fit)
    print(pattern.neckline_at(pattern.head.index))
```

Returns a list of immutable `Pattern` objects, or `[]` when none qualifies. Inputs
must be finite, strictly positive real numbers; booleans and numeric strings are
rejected. Empty/short valid inputs return `[]`. Invalid types raise `TypeError`;
invalid numeric values or parameter ranges raise `ValueError`. Input order is
assumed chronological and evenly spaced; timestamps are not parsed.

## CLI Usage

The CSV requires a `price` header and one numeric price per row:

```csv
price
100
110
102
118
102
110
100
```

```bash
hs-pattern-detector example.csv --pivot-window 1 --shoulder-tolerance 0.25
python -m hs_pattern_detector.cli example.csv
```

Output JSON includes `pattern_type`, `left_shoulder`, `n1`, `head`, `n2`,
`right_shoulder`, `neckline`, `confirmed_at`, and `geometric_fit`.
No match returns `{"message": "No patterns detected.", "patterns": []}`.
Success and no match exit with 0; invalid input exits with 2 and an error on stderr.
Other options are `--neckline-tolerance`, `--min-head-prominence`, and
`--max-time-ratio`.

## How It Works

1. A strict local high/low must exceed/be below every neighbor within
   `pivot_window` samples on each side. Tied extrema and endpoints are omitted.
2. Consecutive pivots of the same kind are compressed to the more extreme one;
   equal values retain the earlier pivot. Scan consecutive alternating groups of five.
3. HS uses high-low-high-low-high; IHS reverses the logic. The head must be
   strictly more extreme than both shoulders. The straight line through N1/N2
   is the neckline, extrapolated to evaluate shoulder heights.
4. Let `h` be the positive vertical head-to-neckline distance. Both shoulders must
   be on the head side of the neckline. The smaller head-to-shoulder raw-price
   gap divided by `h` must meet `min_head_prominence`.
5. The difference between shoulder heights above/below the neckline, divided by
   `h`, must not exceed `shoulder_tolerance`. `abs(N1.price-N2.price)/h` must not
   exceed `neckline_tolerance`. The ratio of the larger to smaller LS-to-Head and
   Head-to-RS durations must not exceed `max_time_ratio`.
6. `geometric_fit = max(0, 1 - (shoulder_error + neckline_error)/2)`.
   This descriptive 0-to-1 value measures those two geometric deviations only;
   it is not a probability, predictive confidence, or empirical accuracy.

| Parameter | Default | Allowed range |
| --- | --- | --- |
| `pivot_window` | 1 | integer >= 1 |
| `shoulder_tolerance` | 0.25 | [0, 1] |
| `neckline_tolerance` | 0.30 | [0, 1] |
| `min_head_prominence` | 0.10 | (0, 1) |
| `max_time_ratio` | 2.0 | >= 1 |

`confirmed_at = RS.index + pivot_window` is the earliest local-extremum
confirmation position for the returned RS, not a breakout confirmation. This is a
batch, retrospective detector: compression can replace a same-kind pivot when more
data is appended, so historical candidates are not guaranteed to remain unchanged.
Do not treat the output as an event stream or a lookahead-free backtest.

## Example

```bash
python examples/synthetic_example.py
python examples/synthetic_example.py --kind IHS --csv inverse.csv
hs-pattern-detector inverse.csv
```

The 19-observation synthetic examples have pivot indices LS=3, N1=6, Head=9,
N2=12, RS=15 and `confirmed_at=16`. Both have geometric fit 1.0 by construction.
These toy results verify mechanics and do not validate market performance.

## Limitations

- A deliberately simple baseline, not a complete trading strategy or a faithful
  implementation of a named academic detector.
- No real-market accuracy has been claimed or measured in this project.
- No breakout detection, prior-trend test, volume analysis, targets, execution,
  risk management, or predictive probabilities.
- Uses one price series rather than OHLC candles. Noise, plateaus, parameter
  choices, and sampling resolution can cause missed or false candidates.
- Consecutive five-pivot groups only; no multi-scale search or overlap deduplication.
- Retrospective pivot compression and confirmation delay require care in any future
  evaluation. Runtime is O(n * pivot_window) for the current pivot search.
- No market data is bundled, downloaded, or licensed through this package.

## Contributing

Community contributions are welcome. Please describe a reproducible problem,
include a small self-generated synthetic example, and add meaningful pytest tests
for behavior changes. Run `python -m pytest` before submitting a pull request.
Do not submit credentials, private code, private research, blind/holdout evaluation
sets, or real market datasets. Any future third-party contribution must have
compatible licensing and clear provenance. Potential improvements include plateau
handling, plotting, additional synthetic edge cases, and explicitly causal pivots.

## License

MIT License. See [LICENSE](LICENSE). This distribution consists of original
baseline code and original synthetic fixtures; it contains no private research code
or third-party datasets.
