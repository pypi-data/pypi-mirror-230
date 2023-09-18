# lm-datasets

<img align="left" src="https://github.com/malteos/lm-datasets/raw/main/images/A_colorful_parrot_sitting_on_a_pile_of_books__whit-removebg-preview.png" height="200" />

![](https://img.shields.io/pypi/l/lm-datasets?style=flat-square)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)

**lm-datasets is a collection of datasets for language model training including scripts for downloading, preprocesssing, and sampling.**


## Installation

```bash
pip install lm-datasets
```

## Usage

To download and extract the plain-text of one or more datasets, run the following command:

```bash
python -m lm_datasets.extract_plaintext $DATASET_ID $OUTPUT_DIR
```

By default, output is saved as JSONL files. To change the output format, you can use the `--output_format` argument as below:

```bash
python -m lm_datasets.extract_plaintext $DATASET_ID $OUTPUT_DIR --output_format parquet  --output_compression zstd
```

### Available datasets

A list or table with all available datasets can be print with the follow command:

```bash
python -m lm_datasets.print_stats --print_output md
```

### Dataset viewer

We provide a Web-based application through streamlit to browse all datasets and their contained text content.
To start the app, run the following command:

```bash
streamlit viewer/app.py $RAW_DATASETS_DIR $PROCESSED_DATASET_DIR
```


## Development & Contributions

### Setup environment

```bash
git clone git@github.com:malteos/lm-datasets.git
cd lm-datasets

conda create -n lm-datasets python=3.10
conda activate lm-datasets

pip install -r requirements.txt
```


### Install the pre-commit hooks

This repository uses git hooks to validate code quality and formatting.

```
pre-commit install
git config --bool flake8.strict true  # Makes the commit fail if flake8 reports an error
```

To run the hooks:
```
pre-commit run --all-files
```

### Testing

The tests can be executed with:
```
pytest --doctest-modules --cov-report term --cov=lm_datasets
```

## License

Apache 2.0
