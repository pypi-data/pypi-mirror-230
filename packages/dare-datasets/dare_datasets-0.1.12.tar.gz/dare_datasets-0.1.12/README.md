# Darelab Datasets Docs

A quick access library of datasets used in [Darelab](https://darelab.imsi.athenarc.gr/).

## Installation

**Install:** `pip install dare-datasets`

**Documentation:** https://darelab.athenarc.gr/datasets-docs/add_dataset/

**Datasets included:**

* [QR2T Benchmark](qr2t_benchmark.md) from [MikeXydas](https://github.com/MikeXydas)
* [Iris](iris.md) from [MikeXydas](https://github.com/MikeXydas)

## Usage

```python
from dare_datasets import QR2TBenchmark

qr2t_benchmark = QR2TBenchmark()
qr2t_data = qr2t_benchmark.get()
```

For each dataset, additional methods might exist. Check the documentation of each dataset for
more details.

## Dev Installation

For development purposes, additional libraries must be installed such as `pytest` and `mkdocs`.

Prerequisites:
* Python >=3.8
* [Poetry](https://python-poetry.org/docs/#installation)
* [PreCommit](https://pre-commit.com/#install) (Optional)

```bash
1. Clone the repository
2. poetry install
3. pre-commit install (Optional)
4. git branch new_dataset_name
```

After any contribution you should open a pull request.
