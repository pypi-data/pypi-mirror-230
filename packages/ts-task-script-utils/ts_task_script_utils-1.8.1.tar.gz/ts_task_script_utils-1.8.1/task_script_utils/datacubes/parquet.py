from typing import Optional, Sequence, Tuple, overload

import fsspec
import numpy as np
import pandas as pd

Array = Sequence[Optional[float]]


def datacube_to_dataframe(
    dimensions: Tuple[Array, ...], measures: Tuple[Sequence, ...]
) -> pd.DataFrame:
    """Convert dimension scales and measure values to a Pandas DataFrame

    `dimensions` is a tuple of length N for N-dimensional datacubes. Each element of
    the tuple is a list of scale values for each dimension.
    `measures` is a tuple of length M for datacubes containing M measures. Each element
    of this tuple is an N-dimensional list of measure values.

    This function should be used on data which is already validated to be null or
    numeric.
    The input dimension and measure values must be able to be coerced to a numpy array
    of floats, so numeric string values and booleans will be converted to floats, but
    non-numeric string values and other non-numeric types will cause an error.
    """
    try:
        # Convert to np.float to make sure dimensions are numeric or `None`.
        # `None` is converted to `np.NaN`. `int`s are also converted to `float`s.
        dimension_arrays = [np.array(dim, dtype=np.float_) for dim in dimensions]
    except ValueError as exception:
        raise ValueError(
            "Dimension scales can only contain null or numeric values when converting to Parquet."
        ) from exception

    dimension_index = pd.MultiIndex.from_product(
        dimension_arrays,
        names=[f"dimension_{index}_value" for index in range(len(dimensions))],
    )
    dimension_shape = tuple(len(d) for d in dimensions)

    try:
        # `None` is treated as `np.NaN`, and non-numeric or non-None values raise an error
        measure_arrays = np.array(measures, dtype=np.float_)
    except ValueError as exception:
        raise ValueError(
            "Measure data can only contain null or numeric values when converting to Parquet."
        ) from exception

    # Check measures and dimensions have compatible shapes
    for idx, measure_array in enumerate(measure_arrays):
        if measure_array.shape != dimension_shape:
            raise ValueError(
                f"Measure {idx} has a shape of {measure_array.shape} which is "
                f"incompatible with the dimension shape of {dimension_shape}."
            )

    # Reshape all measures from N-dimensional arrays of shape (a, b, c, ...) into a
    # table with shape (a*b*c*..., M) for M measures
    flat_measures = np.stack([measure.flatten() for measure in measure_arrays]).T

    # Create the DataFrame and reset the index to convert the MultiIndex into columns
    return pd.DataFrame(
        flat_measures,
        columns=[f"measure_{index}_value" for index in range(len(measure_arrays))],
        index=dimension_index,
    ).reset_index()


def dataframe_to_parquet(df: pd.DataFrame) -> bytes:
    """Create a parquet file as bytes from a Pandas DataFrame"""
    # `fastparquet` needs to write to a file-like object and doesn't accept BytesIO.
    # An in-memory file system using `fsspec` is recommended here:
    # https://github.com/dask/fastparquet/issues/586#issuecomment-861647325
    file_sys = fsspec.filesystem("memory")
    temp_parquet_path = "memory://temp.parquet"

    # Pandas can write DataFrames to parquet with the engines `fastparquet` or `pyarrow`
    # which must be installed separately. `fastparquet` is used because it is a smaller
    # dependency.
    df.to_parquet(temp_parquet_path, engine="fastparquet")
    parquet_bytes = file_sys.cat(temp_parquet_path)

    file_sys.delete(temp_parquet_path)

    return parquet_bytes


# Overload type hints for 1D, 2D, 3D and 4D datacubes (assuming 5D and above are rare)
# This annotates that N `dimensions` correspond to N levels of nesting in `measures`,
# so that type checkers can raise errors for this kind of incompatibility
@overload
def datacube_to_parquet(dimensions: Tuple[Array], measures: Tuple[Array, ...]) -> bytes:
    ...


@overload
def datacube_to_parquet(
    dimensions: Tuple[Array, Array], measures: Tuple[Sequence[Array], ...]
) -> bytes:
    ...


@overload
def datacube_to_parquet(
    dimensions: Tuple[Array, Array, Array],
    measures: Tuple[Sequence[Sequence[Array]], ...],
) -> bytes:
    ...


@overload
def datacube_to_parquet(
    dimensions: Tuple[Array, Array, Array, Array],
    measures: Tuple[Sequence[Sequence[Sequence[Array]]], ...],
) -> bytes:
    ...


def datacube_to_parquet(
    dimensions: Tuple[Array, ...], measures: Tuple[Sequence, ...]
) -> bytes:
    """Convert dimension scales and measure values to a Parquet file as bytes in memory

    `dimensions` is a tuple of length N for N-dimensional datacubes. Each element of
    the tuple is a list of scale values for each dimension.
    `measures` is a tuple of length M for datacubes containing M measures. Each element
    of this tuple is an N-dimensional list of measure values.

    For example, convert a 2D datacube with shape (1, 3) and two measures to Parquet:

    ```python
    dimensions = ([1], [10, 20, 30])
    measures = (
        [[1, 2, 3]],
        [[4, 5, 6]]
    )

    datacube_parquet = datacube_to_parquet(dimensions, measures)
    ```
    """
    dframe = datacube_to_dataframe(dimensions, measures)
    return dataframe_to_parquet(dframe)
