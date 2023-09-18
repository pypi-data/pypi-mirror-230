import polars as pl
import polars.selectors as cs
from typing import Dict, Optional, List


class ScanData:
    """
    Base Class to inherit methods from, read different data-formats,
    and calculate different quality measures.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def calc_profile(
        file_path: str, df: pl.DataFrame, unique_id: Optional[str] = None
    ) -> Dict:
        """
        calculate the profile of the tabular dataset using polars,
        profile measurements:
        - file path on your system
        - number of columns of dataset.
        - number of records.
        - columns in dataset.
        - schema of the dataset (column:data-type).
        - unique identifier of the dataset.
        - all string-type columns.
        - all numeric-type columns.
        - range of numeric columns (min, max).
        - number of unique values in string-type columns.
        - number of missing records in columns.
        - number of duplicate records.
        - number of columns that has only one value.

        Parameters
        ----------
        file_path : path of tabular dataset.
        df : polars dataframe.
        unique_id : unique identifier name in dataset.

        Returns
        -------
        dictionary that holds all data of profile.
        """
        cols: List[str] = df.columns
        schema: Dict = {col: f"{dtype}" for col, dtype in df.schema.items()}
        n_cols: int = df.width
        n_rows: int = df.height
        cat_cols: List[str] = df.select(cs.string()).columns
        num_cols: List[str] = df.select(cs.numeric()).columns
        unique_val_df = df.select(pl.col(pl.Utf8).n_unique())
        n_unique = {
            col: unique_val_df.select(col).item() for col in unique_val_df.columns
        }
        null_cols = {col: df.select(col).null_count().item() for col in cols}
        duplicate_records = df.is_duplicated().sum()
        num_cols_range = {
            col: [df.select(col).min().item(), df.select(col).max().item()]
            for col in num_cols
        }
        constant_col = [
            col for col in df.columns if df.select(col).unique().height == 0
        ]
        return {
            "file": file_path,
            "number-of-columns": n_cols,
            "number-of-records": n_rows,
            "columns": cols,
            "schema": schema,
            "unique-identifier": unique_id,
            "categorical-columns": cat_cols,
            "numeric-columns": num_cols,
            "numeric-columns-range": num_cols_range,
            "unique-categorical-values": n_unique,
            "missing-values": null_cols,
            "duplicate_records": duplicate_records,
            "is_constatnt": constant_col,
        }

    def scan_csv_file(
        self, file_path: str, unique_identifier: Optional[str] = None, sep: str = ","
    ) -> Dict:
        """
        scan csv file and returns dictionary that holds all
        information of profile .yml file.

        Parameters
        ----------
        file_path : path of tabular dataset.
        unique_identifier : unique identifier name in dataset.
        sep: separator of file, default is ','

        Returns
        -------
        dictionary that holds all data of profile.
        """
        df = pl.read_csv(file_path, ignore_errors=True, separator=sep)
        return ScanData.calc_profile(
            file_path=file_path, df=df, unique_id=unique_identifier
        )

    def scan_parquet_file(
        self, file_path: str, unique_identifier: Optional[str] = None
    ) -> Dict:
        """
        scan parquet file and returns dictionary that holds all
        information of profile .yml file.

        Parameters
        ----------
        file_path : path of tabular dataset.
        unique_identifier : unique identifier name in dataset.

        Returns
        -------
        dictionary that holds all data of profile.
        """
        df = pl.read_parquet(file_path)
        return ScanData.calc_profile(
            file_path=file_path, df=df, unique_id=unique_identifier
        )

    def scan_json_file(
        self, file_path: str, unique_identifier: Optional[str] = None
    ) -> Dict:
        """
        scan json file and returns dictionary that holds all
        information of profile .yml file.

        Parameters
        ----------
        file_path : path of tabular dataset.
        unique_identifier : unique identifier name in dataset.

        Returns
        -------
        dictionary that holds all data of profile.
        """
        df = pl.read_json(file_path)
        return ScanData.calc_profile(
            file_path=file_path, df=df, unique_id=unique_identifier
        )

    def scan_excel_file(
        self, file_path: str, sheet_name: str, unique_identifier: Optional[str] = None
    ) -> Dict:
        """
        scan csv file and returns dictionary that holds all
        information of profile .yml file.

        Parameters
        ----------
        file_path : path of tabular dataset.
        sheet_name : sheet name of the dataset in Excel file.
        unique_identifier : unique identifier name in dataset.

        Returns
        -------
        dictionary that holds all data of profile.
        """
        df = pl.read_excel(file_path, sheet_name=sheet_name)
        return ScanData.calc_profile(
            file_path=file_path, df=df, unique_id=unique_identifier
        )
