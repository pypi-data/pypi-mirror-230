"""Basic utilities extending pandas functionalities."""

from typing import Any, List, Union

from pandas import DataFrame, Index, SparseDtype


def is_sparse(df: DataFrame) -> bool:
    """
    Return `True` if a dataframe is sparse.

    :param df: pandas dataframe
    :return: bool
    """
    return all([isinstance(v, SparseDtype) for k, v in df.dtypes.items()])


def loc(df: DataFrame, idx: Union[Index, List[Any]]) -> Any:
    """
    Return a filtered dataframe based on an index list: it is designed to work properly with sparse dataframe as well.

    :param df: DataFrame
    :param idx: index list
    :return: DataFrame which is filtered
    """
    if is_sparse(df):
        csr = df.sparse.to_coo().tocsr()
        pos = [pos for pos, elem in enumerate(df.index) if elem in idx]
        return DataFrame.sparse.from_spmatrix(
            csr[pos, :],
            index=idx[pos]
            if isinstance(idx, Index)
            else [elem for elem in df.index if elem in idx],
            columns=df.columns,
        )
    else:
        return df.loc[idx]
