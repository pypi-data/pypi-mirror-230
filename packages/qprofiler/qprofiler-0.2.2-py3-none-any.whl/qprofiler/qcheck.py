from pathlib import Path
from .utils import Message
from .scan import ScanData
from typing import Dict, Optional, List, Union, Callable, Any
from typing_extensions import Self
import yaml

message = Message()


class QTest(ScanData):
    """
    all quality checks test cases that is needed to check quality of production(test)
    datasets, and how it is similar to development(train) datasets.

    inherit all methods from ScanData to scan and produce profile like saved profiles in
    profiler.

    Parameters
    ----------
    profile_path: path of the .yml saved profile.

    Attributes
    ----------
    profile: dictionary of the saved .yml profile.

    profile_path: path of the .yml saved profile.
    """

    def __init__(self, profile_path: Path) -> None:
        super().__init__()
        try:
            with open(profile_path, "r") as conf:
                self.profile: Dict[str, Any] = yaml.safe_load(conf)
                self.profile_path: Path = profile_path
        except FileNotFoundError:
            raise FileNotFoundError("no profile in this path")

    def check_number_of_columns(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check the number of columns in test dataset, if it matches
        the number of columns in reference dataset that have saved
        profile, then it return True else False.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if self.profile["number-of-columns"] == test_profile["number-of-columns"]:
            return {"msg": "number of columns are identical", "res": True}
        else:
            return {"msg": "number of columns are different", "res": False}

    def check_min_number_of_records(
        self, test_profile: Dict[str, Any], min_threshold: Optional[int] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        check the number of records in test datasets, there are two
        options either to add minimum threshold of acceptable number
        of records or to let the minimum number of records greater than or
        equal to number of records in reference dataset.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        min_thresh: the acceptable minimum number of records

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if min_threshold:
            if self.profile["number-of-records"] >= min_threshold:
                return {
                    "msg": (
                        "number of records are greater than or equal to"
                        f" {min_threshold}"
                    ),
                    "res": True,
                }
            else:
                return {
                    "msg": f"number of records are less than {min_threshold}",
                    "res": False,
                }
        else:
            if self.profile["number-of-records"] >= test_profile["number-of-records"]:
                return {
                    "msg": (
                        "number of records are greater than or equal to reference"
                        " records"
                    ),
                    "res": True,
                }
            else:
                return {
                    "msg": "number of records are less than reference records",
                    "res": False,
                }

    def check_max_number_of_records(
        self, test_profile: Dict[str, Any], max_threshold: Optional[int] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        check the number of records in test datasets, there are two
        options either to add maximum threshold of acceptable number
        of records or to let the maximum number of records less than or
        equal to number of records in reference dataset.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        max_thresh: the acceptable maximum number of records

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if max_threshold:
            if self.profile["number-of-records"] <= max_threshold:
                return {
                    "msg": f"number of records are less than {max_threshold}",
                    "res": True,
                }
            else:
                return {
                    "msg": f"number of records passed {max_threshold}",
                    "res": False,
                }
        else:
            if self.profile["number-of-records"] <= test_profile["number-of-records"]:
                return {
                    "msg": "number of records are less than reference total records",
                    "res": True,
                }
            else:
                return {
                    "msg": "number of records passed reference total records",
                    "res": False,
                }

    def check_columns(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check the column names that exist in test dataset,
        and compare it to reference dataset, it both are identical
        then returns True else False.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if len(self.profile["columns"]) == len(test_profile["columns"]):
            counter = 0
            for idx in range(len(self.profile["columns"])):
                if self.profile["columns"][idx] == test_profile["columns"][idx]:
                    counter += 1
                    continue
                else:
                    break
            return (
                {"msg": "columns are the same", "res": True}
                if counter == len(self.profile["columns"])
                else {"msg": "columns aren't matched", "res": False}
            )
        return {"msg": "number of columns aren't identical", "res": False}

    def check_schema(self, test_profile: Dict[str, Any]) -> Dict[str, Union[str, bool]]:
        """
        check if test dataset schema is identical to
        reference dataset schema.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if len(self.profile["schema"]) == len(test_profile["schema"]):
            counter = 0
            for idx in range(len(self.profile["schema"])):
                if (
                    self.profile["schema"][self.profile["columns"][idx]]
                    == test_profile["schema"][test_profile["columns"][idx]]
                ):
                    counter += 1
                    continue
                else:
                    break
            return (
                {"msg": "schema of both datasets are identical", "res": True}
                if counter == len(self.profile["schema"])
                else {"msg": "schema of both datasets aren't identical", "res": False}
            )
        return {
            "msg": "number of columns aren't identical, different schema",
            "res": False,
        }

    def check_uid(self, test_profile: Dict[str, Any]) -> Dict[str, Union[str, bool]]:
        """
        check if reference and test datasets have the same id.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if self.profile["unique-identifier"] == test_profile["unique-identifier"]:
            return {"msg": "matched ID columns", "res": True}
        return {"msg": "different IDs", "res": False}

    def check_numeric_columns(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check if reference and test datasets have the same numerical columns.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if len(self.profile["numeric-columns"]) == len(test_profile["numeric-columns"]):
            counter = 0
            for idx in range(len(self.profile["numeric-columns"])):
                if (
                    self.profile["numeric-columns"][idx]
                    == test_profile["numeric-columns"][idx]
                ):
                    counter += 1
                    continue
                else:
                    break
            return (
                {"msg": "numeric columns are identical.", "res": True}
                if counter == len(self.profile["numeric-columns"])
                else {
                    "msg": "test numeric columns aren't like reference numeric columns",
                    "res": False,
                }
            )
        return {"msg": "number of numeric columns aren't identical", "res": False}

    def check_categorical_columns(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check if reference and test datasets have the same categorical columns.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if len(self.profile["categorical-columns"]) == len(
            test_profile["categorical-columns"]
        ):
            counter = 0
            for idx in range(len(self.profile["categorical-columns"])):
                if (
                    self.profile["categorical-columns"][idx]
                    == test_profile["categorical-columns"][idx]
                ):
                    counter += 1
                    continue
                else:
                    break
            return (
                {"msg": "categorical columns are identical.", "res": True}
                if counter == len(self.profile["categorical-columns"])
                else {
                    "msg": (
                        "test categorical columns aren't like reference categorical"
                        " columns"
                    ),
                    "res": False,
                }
            )
        return {"msg": "number of categorical columns aren't identical", "res": False}

    def check_numeric_below_thresh(
        self,
        test_profile: Dict[str, Any],
        min_thresh: Optional[str] = None,
        col: Optional[Union[List[str], str]] = None,
    ) -> Dict[str, Union[str, bool]]:
        """
        check if test numerical columns aren't below minimum threshold of
        reference numerical columns or defined threshold.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        min_threshold: minimum threshold that all numeric column values
        must be above or equal to it.

        col: list of columns or column name to check, if not specified,
        will check all numeric columns.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if col:
            if isinstance(col, str):
                if col in self.profile["numeric-columns-range"].keys():
                    if min_thresh:
                        if test_profile["numeric-columns-range"][col][0] >= min_thresh:
                            return {
                                "msg": (
                                    f"lower bound of {col} is greater than or equal"
                                    f" {min_thresh}."
                                ),
                                "res": True,
                            }
                        return {
                            "msg": f"lower bound of {col} is less than {min_thresh}.",
                            "res": False,
                        }
                    else:
                        if (
                            test_profile["numeric-columns-range"][col][0]
                            >= self.profile["numeric-columns-range"][col][0]
                        ):
                            return {
                                "msg": (
                                    f"lower bound of {col} is greater than or equal to"
                                    f" {col} in reference."
                                ),
                                "res": True,
                            }
                        return {
                            "msg": (
                                f"lower bound of {col} is less than {col} in reference."
                            ),
                            "res": False,
                        }
                return {
                    "msg": f"{col} doesn't exist in reference dataset.",
                    "res": False,
                }
            elif isinstance(col, List[str]):
                if min_thresh:
                    counter = 0
                    for val in col:
                        if col in self.profile["numeric-columns-range"].keys():
                            if (
                                test_profile["numeric-columns-range"][col][0]
                                >= min_thresh
                            ):
                                counter += 1
                                continue
                            else:
                                break
                        else:
                            break
                    return (
                        {
                            "msg": (
                                "lower bound of all columns are greater than or equal"
                                f" to {min_thresh}"
                            ),
                            "res": True,
                        }
                        if counter == len(col)
                        else {
                            "msg": (
                                f"lower bound of all columns are less than {min_thresh}"
                            ),
                            "res": False,
                        }
                    )
                else:
                    counter = 0
                    for val in col:
                        if col in self.profile["numeric-columns-range"].keys():
                            if (
                                test_profile["numeric-columns-range"][col][0]
                                >= self.profile["numeric-columns-range"][col][0]
                            ):
                                counter += 1
                                continue
                            else:
                                break
                        else:
                            break
                    return (
                        {
                            "msg": (
                                "lower bound of passed columns are greater than or"
                                " equal to reference lower bounds"
                            ),
                            "res": True,
                        }
                        if counter == len(col)
                        else {
                            "msg": (
                                "lower bound of part/all passed columns are less than"
                                " reference lower bounds"
                            ),
                            "res": False,
                        }
                    )
        else:
            if min_thresh:
                counter = 0
                for val in self.profile["numeric-columns-range"].keys():
                    if test_profile["numeric-columns-range"][val][0] >= min_thresh:
                        counter += 1
                        continue
                    else:
                        break
                return (
                    {
                        "msg": (
                            "lower bound of all test columns are greater than or equal"
                            f" to {min_thresh}"
                        ),
                        "res": True,
                    }
                    if counter == len(self.profile["numeric-columns-range"].keys())
                    else {
                        "msg": (
                            "lower bound of part/all test columns are less than"
                            f" {min_thresh}"
                        ),
                        "res": False,
                    }
                )
            else:
                counter = 0
                for val in self.profile["numeric-columns-range"].keys():
                    if (
                        test_profile["numeric-columns-range"][val][0]
                        >= self.profile["numeric-columns-range"][val][0]
                    ):
                        counter += 1
                        continue
                    else:
                        break
                return (
                    {
                        "msg": (
                            "lower bound of all test columns are greater than or equal"
                            " to reference lower bounds"
                        ),
                        "res": True,
                    }
                    if counter == len(self.profile["numeric-columns-range"].keys())
                    else {
                        "msg": (
                            "lower bound of all/part test columns are less than"
                            " reference lower bounds"
                        ),
                        "res": False,
                    }
                )

    def check_numeric_above_thresh(
        self,
        test_profile: Dict[str, Any],
        max_thresh: Optional[str] = None,
        col: Optional[Union[List[str], str]] = None,
    ) -> Dict[str, Union[str, bool]]:
        """
        check if test numerical columns aren't above maximum threshold of
        reference numerical columns or defined threshold.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        max_threshold: maximum threshold that all numeric column values
        must be below or equal to it.

        col: list of columns or column name to check, if not specified,
        will check all numeric columns.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if col:
            if isinstance(col, str):
                if col in self.profile["numeric-columns-range"].keys():
                    if max_thresh:
                        if test_profile["numeric-columns-range"][col][1] <= max_thresh:
                            return {
                                "msg": (
                                    f"upper bound of {col} is less than or equal to"
                                    f" {max_thresh}."
                                ),
                                "res": True,
                            }
                        return {
                            "msg": (
                                f"lower bound of {col} is greater than {max_thresh}."
                            ),
                            "res": False,
                        }
                    else:
                        if (
                            test_profile["numeric-columns-range"][col][1]
                            <= self.profile["numeric-columns-range"][col][1]
                        ):
                            return {
                                "msg": (
                                    f"upper bound of {col} is less than or equal to"
                                    f" {col} in reference."
                                ),
                                "res": True,
                            }
                        return {
                            "msg": (
                                f"upper bound of {col} is greater than {col} in"
                                " reference."
                            ),
                            "res": False,
                        }
                return {
                    "msg": f"{col} doesn't exist in reference dataset.",
                    "res": False,
                }
            elif isinstance(col, List[str]):
                if max_thresh:
                    counter = 0
                    for val in col:
                        if col in self.profile["numeric-columns-range"].keys():
                            if (
                                test_profile["numeric-columns-range"][col][1]
                                <= max_thresh
                            ):
                                counter += 1
                                continue
                            else:
                                break
                        else:
                            break
                    return (
                        {
                            "msg": (
                                "upper bound of all passed columns are less than or"
                                f" equal to {max_thresh}"
                            ),
                            "res": True,
                        }
                        if counter == len(self.profile["numeric-columns-range"].keys())
                        else {
                            "msg": (
                                "upper bound of part/all passed columns are greater"
                                f" than {max_thresh}"
                            ),
                            "res": False,
                        }
                    )
                else:
                    counter = 0
                    for val in col:
                        if col in self.profile["numeric-columns-range"].keys():
                            if (
                                test_profile["numeric-columns-range"][col][1]
                                <= self.profile["numeric-columns-range"][col][1]
                            ):
                                counter += 1
                                continue
                            else:
                                break
                        else:
                            break
                    return (
                        {
                            "msg": (
                                "upper bound of passed columns are less than or"
                                " equal to reference lower bounds"
                            ),
                            "res": True,
                        }
                        if counter == len(self.profile["numeric-columns-range"].keys())
                        else {
                            "msg": (
                                "upper bound of part/all passed columns are greater"
                                " than reference lower bounds"
                            ),
                            "res": False,
                        }
                    )
        else:
            if max_thresh:
                counter = 0
                for val in self.profile["numeric-columns-range"].keys():
                    if test_profile["numeric-columns-range"][val][1] <= max_thresh:
                        counter += 1
                        continue
                    else:
                        break
                return (
                    {
                        "msg": (
                            "upper bound of all test columns are less than or equal"
                            f" to {max_thresh}"
                        ),
                        "res": True,
                    }
                    if counter == len(self.profile["numeric-columns-range"].keys())
                    else {
                        "msg": (
                            "upper bound of part/all test columns are greater than"
                            f" {max_thresh}"
                        ),
                        "res": False,
                    }
                )
            else:
                counter = 0
                for val in self.profile["numeric-columns-range"].keys():
                    if (
                        test_profile["numeric-columns-range"][val][1]
                        <= self.profile["numeric-columns-range"][val][1]
                    ):
                        counter += 1
                        continue
                    else:
                        break
                return (
                    {
                        "msg": (
                            "upper bound of all test columns are less than or equal"
                            " to reference upper bounds"
                        ),
                        "res": True,
                    }
                    if counter == len(self.profile["numeric-columns-range"].keys())
                    else {
                        "msg": (
                            "upper bound of all/part test columns are greater than"
                            " reference upper bounds"
                        ),
                        "res": False,
                    }
                )

    def check_high_cardinality(
        self, test_profile: Dict[str, Any], max_thresh: int = 10
    ) -> Dict[str, Union[str, bool]]:
        """
        check that categorical columns distinct values aren't above
        a maximum threshold to avoid high cardinality problems in
        production.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        max_threshold: maximum threshold that all categorical column values
        must be below or equal to it.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        counter = 0
        for col in test_profile["unique-categorical-values"].keys():
            if test_profile["unique-categorical-values"][col] <= max_thresh:
                counter += 1
            else:
                break
        return (
            {"msg": f"unique values below or equal {max_thresh}", "res": True}
            if counter == len(self.profile["unique-categorical-values"])
            else {"msg": f"unique values passed {max_thresh}", "res": False}
        )

    def check_unique_categories(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check that number of distinct values in test categorical columns
        is equal to number of distinct values in reference categorical
        columns.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        counter = 0
        for col in self.profile["unique-categorical-values"].keys():
            if (
                test_profile["unique-categorical-values"][col]
                == self.profile["unique-categorical-values"][col]
            ):
                counter += 1
            else:
                break
        return (
            {"msg": "unique values in test are identical to reference", "res": True}
            if counter == len(self.profile["unique-categorical-values"])
            else {"msg": "unique values in test don't match reference", "res": False}
        )

    def check_missing_values(
        self, test_profile: Dict[str, Any], max_thresh: Optional[int] = None
    ) -> Dict[str, Union[str, bool]]:
        """
        check that missing values in columns aren't exceeded acceptable
        maximum threshold or number of missing values in reference columns.

        Parameters
        ----------
        test_profile: Dcitionary of the test dataset.

        max_thresh: maximum number of records that are accepted to be missing.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        counter = 0
        for col in self.profile["missing-values"].keys():
            if max_thresh:
                if test_profile["missing-values"][col] <= max_thresh:
                    counter += 1
                else:
                    break
            else:
                if (
                    test_profile["missing-values"][col]
                    <= self.profile["missing-values"][col]
                ):
                    counter += 1
                else:
                    break
        return (
            {
                "msg": "acceptable no. of missing values in test dataset columns",
                "res": True,
            }
            if counter == len(self.profile["missing-values"])
            else {
                "msg": "high no. of missing values in test dataset columns",
                "res": False,
            }
        )

    def check_row_duplicates(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check if there are full-row duplicates in test datasets.

        Parameters
        ----------
        test_profile: Dictionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if self.profile["duplicate_records"] == 0:
            if test_profile["duplicate_records"] == 0:
                return {"msg": "no duplicates found", "res": True}
            return {"msg": "duplicates found in test dataset", "res": False}
        return {"msg": "reference dataset contain duplicates", "res": True}

    def check_if_no_constant_columns(
        self, test_profile: Dict
    ) -> Dict[str, Union[str, bool]]:
        """
        check if there are columns that have only one value(constant column)
        in test dataset.

        Parameters
        ----------
        test_profile: Dictionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if len(test_profile["is_constatnt"]) == 0:
            return {"msg": "dataset has no constant columns", "res": True}
        else:
            return {
                "msg": (
                    f"dataset has {len(test_profile['is_constatnt'])} constant columns"
                ),
                "res": False,
            }

    def check_if_matched_const_columns(
        self, test_profile: Dict[str, Any]
    ) -> Dict[str, Union[str, bool]]:
        """
        check if the constant columns in reference profile is
        identical to test profile.

        Parameters
        ----------
        test_profile: Dictionary of the test dataset.

        Returns
        -------
        a dictionary of message of test result and
        boolen flag represensts the test result(True/False).
        """
        if (
            len(self.profile["is_constatnt"]) == 0
            and len(test_profile["is_constatnt"]) == 0
        ):
            return {"msg": "no constant columns in refernce and test", "res": True}
        else:
            if len(test_profile["is_constatnt"]) != len(self.profile["is_constatnt"]):
                return {
                    "msg": "constant columns in test don't match reference",
                    "res": False,
                }
            else:
                if set(test_profile["is_constatnt"]).issubset(
                    self.profile["is_constatnt"]
                ):
                    return {
                        "msg": "constant columns are subset of reference",
                        "res": True,
                    }


class QPipeline:
    """
    Pipeline of Quality Check Tests.

    Sequential checks a list of Quality Tests,
    the purpose of pipeline is to provide a list of checks that
    must be done in production to ensure the quality of the production
    datasets matches the reference profile.

    Parameters
    ----------
    test_obj: Object of QTest.

    test_profile: Dictionary of test datasets profile

    verbose: bool, default = False
    if True the message returned by each Test will be printed.

    Attributes
    ----------

    """

    def __init__(
        self,
        test_obj: QTest,
        verbose: bool = False,
    ) -> None:
        self.test_obj = test_obj
        self.verbose = verbose
        self.tests = []
        self.__checks = []
        self.__error_levels = []
        self.__check_params = []

    def __len__(self) -> int:
        return len(self.tests)

    @staticmethod
    def validate_error_level(level: str) -> str:
        if level in ["error", "warn"]:
            return level
        else:
            raise ValueError("error level isn't valid")

    @staticmethod
    def validate_checks(
        checks_obj: QTest, check: Callable[..., Dict[str, Union[str, bool]]]
    ) -> Callable[..., bool]:
        if hasattr(checks_obj, check.__name__):
            return check
        else:
            raise TypeError("all steps must be a QTest method.")

    @staticmethod
    def execute(
        func: Callable[..., Dict[str, Union[str, bool]]],
        verbose: bool,
        error_level: str,
        **kwargs,
    ) -> bool:
        res = func(**kwargs)
        if verbose:
            if res["res"]:
                message.printit(res["msg"])
            else:
                message.printit(res["msg"], message_type=error_level)
        return res["res"]

    def append(
        self,
        name: str,
        check: Callable[..., bool],
        error_level: str = "error",
        **kwargs,
    ) -> Self:
        """
        add quality check tests to class instance.

        adding quality check test will stack the test added
        to the remaining test in order to complete the quality
        pipeline of tests that needed to check production datasets.

        Parameters
        ----------
        name: name of test in pipeline.

        check: QTest method
        check method to be used for test.

        message_level: message level

        **kwargs: QTest method keyword parameters

        Returns
        -------
        QPipeline class instance
        """
        valid_check = QPipeline.validate_checks(self.test_obj, check=check)
        valid_error_level = QPipeline.validate_error_level(level=error_level)
        self.tests.append(name)
        self.__checks.append(valid_check)
        self.__error_levels.append(valid_error_level)
        self.__check_params.append(kwargs)
        return self

    def remove_step(self, name: str) -> Self:
        """
        remove quality check test from pipeline

        Parameters
        ----------
        name: str
        name of test in pipeline to remove

        Returns
        -------
        QPipeline class instance
        """
        try:
            idx = self.tests.index(name)
            self.tests.remove(name)
            self.__checks.remove(self.__checks[idx])
            self.__error_levels.remove(self.__error_levels[idx])
            self.__check_params.remove(self.__check_params[idx])
            if self.verbose:
                message.printit(f"{name} test removed")
            return self
        except ValueError:
            raise ValueError(f"{name} test doesn't exist in pipeline")

    def clear_pipeline(self) -> None:
        """Remove all Quality Check Tests From Pipeline"""
        self.tests.clear()
        self.__checks.clear()
        self.__error_levels.clear()
        self.__check_params.clear()
        if self.verbose:
            message.printit("all quality checks removed")

    def run(self) -> bool:
        """
        runs quality check tests sequentially,
        if result of one of the quality tests return False
        then if message level is error then final
        result of pipeline is False and pipeline failed.

        if one of the tests failed this means that pipeline
        failed, and quality of test dataset isn't similar to
        reference profile.

        Returns
        -------
        boolean flag represents the final result of the pipeline.
        """
        results = []
        for idx in range(len(self.tests)):
            result = QPipeline.execute(
                func=self.__checks[idx],
                verbose=self.verbose,
                error_level=self.__error_levels[idx],
                **self.__check_params[idx],
            )
            if result:
                results.append(True)
            else:
                if self.__error_levels[idx] == "error":
                    results.append(False)
                else:
                    results.append(True)
        return True if sum(results) == len(self.tests) else False
