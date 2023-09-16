# Datacube Parquet files<!-- omit in toc -->

- [General usage](#general-usage)
- [Usage in Task Scripts](#usage-in-task-scripts)

[Parquet](https://parquet.apache.org/) is a column-oriented data file format designed for efficient data storage and retrieval. It can be used with a wide range of software and programming languages.

These functions are for creating Parquet files containing datacube data.

Currently, only writing a single Parquet file per datacube is supported, as opposed to putting multiple datacubes in a single Parquet file.
Although Parquet can store general tabular data, the data used with these functions must be N-dimensional with the same dimensions and measures structure that datacubes have.

## General usage

Given datacube data consisting of numeric or null dimensions and measures, create a Parquet file representation of the data which can be written to the Tetra Data Lake.

Basic usage example: create datacube data containing 2 measures and a shape of (1, 3),
convert that data to a Parquet file, and write it to a file called `demo.parquet`.

```python
from task_script_utils.datacubes.parquet import datacube_to_parquet
from pathlib import Path

dimensions = ([1], [10, 20, 30])
measures = (
    [[1.0, 2.0, 3.0]],
    [[4.5, 5.5, 6.5]]
)

datacube_parquet = datacube_to_parquet(dimensions, measures)
Path("demo.parquet").write_bytes(datacube_parquet)
```

The `demo.parquet` file can be inspected with a CLI script like `parquet-tools`.
`parquet-tools inspect demo.parquet` displays the file metadata and schema for the columns.
`parquet-tools show demo.parquet` displays the content of the Parquet file in a table:

```txt
+---------------------+---------------------+-------------------+-------------------+
|   dimension_0_value |   dimension_1_value |   measure_0_value |   measure_1_value |
|---------------------+---------------------+-------------------+-------------------|
|                   1 |                  10 |                 1 |               4.5 |
|                   1 |                  20 |                 2 |               5.5 |
|                   1 |                  30 |                 3 |               6.5 |
+---------------------+---------------------+-------------------+-------------------+
```

One other example of using the Parquet file is to read it into a Pandas DataFrame, continuing from the example above:

```python
import pandas as pd

datacube = pd.read_parquet("demo.parquet")
```

Or it can be read directly from the `bytes` in memory:

```python
from io import BytesIO

datacube = pd.read_parquet(BytesIO(datacube_parquet))
```

## Usage in Task Scripts

In a Task Script, a Parquet file can be written to the Tetra Data Lake, and the resulting file pointer may be used in the IDS instance as an alternative way to store numeric data other than including numeric data in the IDS JSON's datacubes.
For example, in a Task Script function with access to a TDP [context](https://developers.tetrascience.com/docs/context-api#contextwrite_file) object:

```python
parquet_pointer = context.write_file(
    content=datacube_parquet,
    file_name="0.parquet",
    file_category="PROCESSED",
)
```

From here, `parquet_pointer` can be put in the IDS instance as a File Pointer.

A Parquet file made with `datacube_to_parquet` only contains the numeric dimension scales and measure values, with none of the rest of the datacube metadata like dimension and measure names and units.
Please see the documentation in `ts-ids-core` for a way to use a file pointer to a Parquet file in combination with datacube metadata.
