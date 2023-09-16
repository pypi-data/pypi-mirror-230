#
# This code is auto-generated using the sklearn_wrapper_template.py_template template.
# Do not modify the auto-generated code(except automatic reformatting by precommit hooks).
#
import inspect
import os
import posixpath
from typing import Iterable, Optional, Union, List, Any, Dict, Callable, Set
from typing_extensions import TypeGuard
from uuid import uuid4

import cloudpickle as cp
import pandas as pd
import numpy as np

import numpy
import sklearn
import sklearn.linear_model
from sklearn.utils.metaestimators import available_if

from snowflake.ml.modeling.framework.base import BaseTransformer, _process_cols
from snowflake.ml.modeling.framework._utils import to_native_format
from snowflake.ml._internal import telemetry
from snowflake.ml._internal.exceptions import error_codes, exceptions, modeling_error_messages
from snowflake.ml._internal.utils import pkg_version_utils, identifier
from snowflake.snowpark import DataFrame
from snowflake.snowpark._internal.type_utils import convert_sp_to_sf_type
from snowflake.ml.modeling._internal.snowpark_handlers import SnowparkHandlers as HandlersImpl
from snowflake.ml.modeling._internal.estimator_protocols import FitPredictHandlers

from snowflake.ml.model.model_signature import (
    DataType,
    FeatureSpec,
    ModelSignature,
    _infer_signature,
    BaseFeatureSpec,
)
from snowflake.ml.model._signatures import utils as model_signature_utils

_PROJECT = "ModelDevelopment"
# Derive subproject from module name by removing "sklearn"
# and converting module name from underscore to CamelCase
# e.g. sklearn.linear_model -> LinearModel.
_SUBPROJECT = "".join([s.capitalize() for s in "sklearn.linear_model".replace("sklearn.", "").split("_")])


def _original_estimator_has_callable(attr : str) -> Callable[[Any], bool]:
    """ Checks that the original estimator has callable `attr`.

    Args:
        attr: Attribute to check for.

    Returns:
        A function which checks for the existance of callable `attr` on the given object.
    """
    def check(self: BaseTransformer) -> TypeGuard[Callable[..., object]]:
        """ Check for the existance of callable `attr` in self.

        Returns:
            True of the callable `attr` exists in self, False otherwise.
        """
        return callable(getattr(self._sklearn_object, attr, None))

    return check


def _gather_dependencies(obj: Any) -> Set[str]:
    """ Gethers dependencies from the SnowML Estimator and Transformer objects.

    Args:
        obj: Source object to collect dependencies from. Source object could of any type, example, lists, tuples, etc.

    Returns:
        A set of dependencies required to work with the object.
    """

    if isinstance(obj, list) or isinstance(obj, tuple):
        deps: Set[str] = set()
        for elem in obj:
            deps = deps | set(_gather_dependencies(elem))
        return deps
    elif isinstance(obj, BaseTransformer):
        return set(obj._get_dependencies())
    else:
        return set()


def _transform_snowml_obj_to_sklearn_obj(obj: Any) -> Any:
    """Converts SnowML Estimator and Transformer objects to equivalent SKLearn objects.

    Args:
        obj: Source object that needs to be converted. Source object could of any type, example, lists, tuples, etc.

    Returns:
        An equivalent object with SnowML estimators and transforms replaced with equivalent SKLearn objects.
    """

    if isinstance(obj, list):
        # Apply transform function to each element in the list
        return list(map(_transform_snowml_obj_to_sklearn_obj, obj))
    elif isinstance(obj, tuple):
        # Apply transform function to each element in the tuple
        return tuple(map(_transform_snowml_obj_to_sklearn_obj, obj))
    elif isinstance(obj, BaseTransformer):
        # Convert SnowML object to equivalent SKLearn object
        return to_native_format(obj)
    else:
        # Return all other objects as it is.
        return obj


def _validate_sklearn_args(args: Dict[str, Any], klass: type) -> Dict[str, Any]:
    """ Validate if all the keyword args are supported by current version of SKLearn/XGBoost object.

    Args:
        args: Dictionary of keyword args for the wrapper init method.
        klass: Underlying SKLearn/XGBoost class object.

    Raises:
        Raises an expception if a user specified arg is not supported by current version of sklearn/xgboost.
    """
    result = {}
    signature = inspect.signature(klass.__init__)  # type: ignore
    for k, v in args.items():
        if k not in signature.parameters.keys():  # Arg is not supported.
            if (
                v[2]  # Arg doesn't have default value in the signature.
                or (
                    v[0] != v[1]  # Value is not same as default.
                    and not (isinstance(v[0], float) and np.isnan(v[0]) and np.isnan(v[1])))  # both are not NANs
            ):
                raise exceptions.SnowflakeMLException(
                    error_code=error_codes.DEPENDENCY_VERSION_ERROR,
                    original_exception=RuntimeError(
                        f"Arg {k} is not supported by current version of SKLearn/XGBoost."
                    ),
                )
        else:
            result[k] = v[0]
    return result


class MultiTaskElasticNet(BaseTransformer):
    r"""Multi-task ElasticNet model trained with L1/L2 mixed-norm as regularizer
    For more details on this class, see [sklearn.linear_model.MultiTaskElasticNet]
    (https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.MultiTaskElasticNet.html)

    Parameters
    ----------
    alpha : float, default=1.0
        Constant that multiplies the L1/L2 term. Defaults to 1.0.

    l1_ratio : float, default=0.5
        The ElasticNet mixing parameter, with 0 < l1_ratio <= 1.
        For l1_ratio = 1 the penalty is an L1/L2 penalty. For l1_ratio = 0 it
        is an L2 penalty.
        For ``0 < l1_ratio < 1``, the penalty is a combination of L1/L2 and L2.

    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (i.e. data is expected to be centered).

    copy_X : bool, default=True
        If ``True``, X will be copied; else, it may be overwritten.

    max_iter : int, default=1000
        The maximum number of iterations.

    tol : float, default=1e-4
        The tolerance for the optimization: if the updates are
        smaller than ``tol``, the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than ``tol``.

    warm_start : bool, default=False
        When set to ``True``, reuse the solution of the previous call to fit as
        initialization, otherwise, just erase the previous solution.
        See :term:`the Glossary <warm_start>`.

    random_state : int, RandomState instance, default=None
        The seed of the pseudo random number generator that selects a random
        feature to update. Used when ``selection`` == 'random'.
        Pass an int for reproducible output across multiple function calls.
        See :term:`Glossary <random_state>`.

    selection : {'cyclic', 'random'}, default='cyclic'
        If set to 'random', a random coefficient is updated every iteration
        rather than looping over features sequentially by default. This
        (setting to 'random') often leads to significantly faster convergence
        especially when tol is higher than 1e-4.

    input_cols : Optional[Union[str, List[str]]]
        A string or list of strings representing column names that contain features.
        If this parameter is not specified, all columns in the input DataFrame except
        the columns specified by label_cols and sample-weight_col parameters are
        considered input columns.

    label_cols : Optional[Union[str, List[str]]]
        A string or list of strings representing column names that contain labels.
        This is a required param for estimators, as there is no way to infer these
        columns. If this parameter is not specified, then object is fitted without
        labels(Like a transformer).

    output_cols: Optional[Union[str, List[str]]]
        A string or list of strings representing column names that will store the
        output of predict and transform operations. The length of output_cols mus
        match the expected number of output columns from the specific estimator or
        transformer class used.
        If this parameter is not specified, output column names are derived by
        adding an OUTPUT_ prefix to the label column names. These inferred output
        column names work for estimator's predict() method, but output_cols must
        be set explicitly for transformers.

    sample_weight_col: Optional[str]
        A string representing the column name containing the examples’ weights.
        This argument is only required when working with weighted datasets.

    drop_input_cols: Optional[bool], default=False
        If set, the response of predict(), transform() methods will not contain input columns.
    """

    def __init__(  # type: ignore
        self,
        *,
        alpha=1.0,
        l1_ratio=0.5,
        fit_intercept=True,
        copy_X=True,
        max_iter=1000,
        tol=0.0001,
        warm_start=False,
        random_state=None,
        selection="cyclic",
        input_cols: Optional[Union[str, Iterable[str]]] = None,
        output_cols: Optional[Union[str, Iterable[str]]] = None,
        label_cols: Optional[Union[str, Iterable[str]]] = None,
        drop_input_cols: Optional[bool] = False,
        sample_weight_col: Optional[str] = None,
    ) -> None:
        super().__init__()
        deps: Set[str] = set([f'numpy=={np.__version__}', f'scikit-learn=={sklearn.__version__}', f'cloudpickle=={cp.__version__}'])
        
        self._deps = list(deps)
        
        init_args = {'alpha':(alpha, 1.0, False),
            'l1_ratio':(l1_ratio, 0.5, False),
            'fit_intercept':(fit_intercept, True, False),
            'copy_X':(copy_X, True, False),
            'max_iter':(max_iter, 1000, False),
            'tol':(tol, 0.0001, False),
            'warm_start':(warm_start, False, False),
            'random_state':(random_state, None, False),
            'selection':(selection, "cyclic", False),}
        cleaned_up_init_args = _validate_sklearn_args(
            args=init_args,
            klass=sklearn.linear_model.MultiTaskElasticNet
        )
        self._sklearn_object = sklearn.linear_model.MultiTaskElasticNet(
            **cleaned_up_init_args,
        )
        self._model_signature_dict: Optional[Dict[str, ModelSignature]] = None
        self.set_input_cols(input_cols)
        self.set_output_cols(output_cols)
        self.set_label_cols(label_cols)
        self.set_drop_input_cols(drop_input_cols)
        self.set_sample_weight_col(sample_weight_col)
        # If user used snowpark dataframe during fit, here it stores the snowpark input_cols, otherwise the processed input_cols
        self._snowpark_cols: Optional[List[str]] = self.input_cols
        self._handlers: FitPredictHandlers = HandlersImpl(class_name=MultiTaskElasticNet.__class__.__name__, subproject=_SUBPROJECT)

    def _get_rand_id(self) -> str:
        """
        Generate random id to be used in sproc and stage names.

        Returns:
            Random id string usable in sproc, table, and stage names.
        """
        return str(uuid4()).replace("-", "_").upper()

    def _infer_input_output_cols(self, dataset: Union[DataFrame, pd.DataFrame]) -> None:
        """
        Infer `self.input_cols` and `self.output_cols` if they are not explicitly set.

        Args:
            dataset: Input dataset.
        """
        if not self.input_cols:
            cols = [
                c for c in dataset.columns 
                if c not in self.get_label_cols() and c != self.sample_weight_col
            ]
            self.set_input_cols(input_cols=cols)

        if not self.output_cols:
            cols = [identifier.concat_names(ids=['OUTPUT_', c]) for c in self.label_cols]
            self.set_output_cols(output_cols=cols)

    def set_input_cols(self, input_cols: Optional[Union[str, Iterable[str]]]) -> "MultiTaskElasticNet":
        """
        Input columns setter.

        Args:
            input_cols: A single input column or multiple input columns.

        Returns:
            self
        """
        self.input_cols = _process_cols(input_cols)
        self._snowpark_cols = self.input_cols
        return self

    def _get_active_columns(self) -> List[str]:
        """"Get the list of columns that are relevant to the transformer."""
        selected_cols = (
            self.input_cols +
            self.label_cols +
            ([self.sample_weight_col] if self.sample_weight_col is not None else [])
        )
        return selected_cols

    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def fit(self, dataset: Union[DataFrame, pd.DataFrame]) -> "MultiTaskElasticNet":
        """Fit MultiTaskElasticNet model with coordinate descent
        For more details on this function, see [sklearn.linear_model.MultiTaskElasticNet.fit]
        (https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.MultiTaskElasticNet.html#sklearn.linear_model.MultiTaskElasticNet.fit)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            self
        """
        self._infer_input_output_cols(dataset)
        if isinstance(dataset, pd.DataFrame):
            self._fit_pandas(dataset)
        elif isinstance(dataset, DataFrame):
            self._fit_snowpark(dataset)
        else:
            raise TypeError(
                f"Unexpected dataset type: {type(dataset)}."
                "Supported dataset types: snowpark.DataFrame, pandas.DataFrame."
            )
        self._is_fitted = True
        self._get_model_signatures(dataset)
        return self

    def _fit_snowpark(self, dataset: DataFrame) -> None:
        session = dataset._session
        assert session is not None  # keep mypy happy
        # Validate that key package version in user workspace are supported in snowflake conda channel
        # If customer doesn't have package in conda channel, replace the ones have the closest versions
        self._deps = pkg_version_utils.get_valid_pkg_versions_supported_in_snowflake_conda_channel(
            pkg_versions=self._get_dependencies(), session=session, subproject=_SUBPROJECT)
        
        # Specify input columns so column pruing will be enforced
        selected_cols = self._get_active_columns()
        if len(selected_cols) > 0:
            dataset = dataset.select(selected_cols)

        estimator = self._sklearn_object
        assert estimator is not None  # Keep mypy happy

        self._snowpark_cols = dataset.select(self.input_cols).columns

        self._sklearn_object = self._handlers.fit_snowpark(
            dataset,
            session,
            estimator,
            ["snowflake-snowpark-python"] + self._get_dependencies(),
            ['sklearn'],
            self.input_cols,
            self.label_cols,
            self.sample_weight_col,
        )


    def _fit_pandas(self, dataset: pd.DataFrame) -> None:
        assert self._sklearn_object is not None and hasattr(self._sklearn_object, "fit") # keep mypy happy
        argspec = inspect.getfullargspec(self._sklearn_object.fit)
        args = {'X': dataset[self.input_cols]}
        if self.label_cols:
            label_arg_name = "Y" if "Y" in argspec.args else "y"
            args[label_arg_name] = dataset[self.label_cols].squeeze()

        if self.sample_weight_col is not None and "sample_weight" in argspec.args:
            args['sample_weight'] = dataset[self.sample_weight_col].squeeze()

        self._sklearn_object.fit(**args)

    def _get_pass_through_columns(self, dataset: DataFrame) -> List[str]:
        if self._drop_input_cols:
            return []
        else:
            return list(set(dataset.columns) - set(self.output_cols))

    def _batch_inference(
        self,
        dataset: DataFrame,
        inference_method: str,
        expected_output_cols_list: List[str],
        expected_output_cols_type: str = "",
    ) -> DataFrame:
        """Util method to create UDF and run batch inference.
        """
        if not self._is_fitted:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.METHOD_NOT_ALLOWED,
                original_exception=RuntimeError(
                    f"Estimator {self.__class__.__name__} not fitted before calling {inference_method} method."
                ),
            )

        session = dataset._session
        if session is None:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.NOT_FOUND,
                original_exception=ValueError(
                    "Session must not specified for snowpark dataset."
                ),
            )
        # Validate that key package version in user workspace are supported in snowflake conda channel
        pkg_version_utils.get_valid_pkg_versions_supported_in_snowflake_conda_channel(
            pkg_versions=self._get_dependencies(), session=session, subproject=_SUBPROJECT)

        return self._handlers.batch_inference(
            dataset,
            session,
            self._sklearn_object,
            self._get_dependencies(),
            inference_method,
            self.input_cols,
            self._get_pass_through_columns(dataset),
            expected_output_cols_list,
            expected_output_cols_type
        )


    def _sklearn_inference(
        self,
        dataset: pd.DataFrame,
        inference_method: str,
        expected_output_cols_list: List[str]
    ) -> pd.DataFrame:
        output_cols = expected_output_cols_list.copy()

        # Model expects exact same columns names in the input df for predict call.
        # Given the scenario that user use snowpark DataFrame in fit call, but pandas DataFrame in predict call
        # input cols need to match unquoted / quoted
        input_cols = self.input_cols
        assert self._snowpark_cols is not None  # Keep mypy happy
        _snowpark_input_cols: List[str] = self._snowpark_cols
        
        estimator = self._sklearn_object

        if hasattr(estimator, "feature_names_in_"):
            features_required_by_estimator =  getattr(estimator, "feature_names_in_")  
        else:
            features_required_by_estimator = _snowpark_input_cols
        missing_features = []
        features_in_dataset = set(dataset.columns)
        
        columns_to_select = []
        for i, f in enumerate(features_required_by_estimator):
            if (
                    i >= len(input_cols)
                    or (input_cols[i] != f and _snowpark_input_cols[i] != f)
                    or (input_cols[i] not in features_in_dataset and _snowpark_input_cols[i] not in features_in_dataset)
                ):
                missing_features.append(f)
            elif input_cols[i] in features_in_dataset:
                columns_to_select.append(input_cols[i])
            elif _snowpark_input_cols[i] in features_in_dataset:
                columns_to_select.append(_snowpark_input_cols[i])

        if len(missing_features) > 0:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.NOT_FOUND,
                original_exception=ValueError(
                    "The feature names should match with those that were passed during fit.\n"
                    f"Features seen during fit call but not present in the input: {missing_features}\n"
                    f"Features in the input dataframe : {input_cols}\n"
                ),
            )
        input_df = dataset[columns_to_select]
        input_df.columns = features_required_by_estimator

        transformed_numpy_array = getattr(estimator, inference_method)(
            input_df
        )

        if (
            isinstance(transformed_numpy_array, list)
            and len(transformed_numpy_array) > 0
            and isinstance(transformed_numpy_array[0], np.ndarray)
        ):
            # In case of multioutput estimators, predict_proba(), decision_function(), etc., functions return 
            # a list of ndarrays. We need to concatenate them.

            # First compute output column names
            if len(output_cols) == len(transformed_numpy_array):
                actual_output_cols = []
                for idx, np_arr in enumerate(transformed_numpy_array):
                    for i in range(1 if len(np_arr.shape) <= 1 else np_arr.shape[1]):
                        actual_output_cols.append(f"{output_cols[idx]}_{i}")
                output_cols = actual_output_cols

            # Concatenate np arrays
            transformed_numpy_array = np.concatenate(transformed_numpy_array, axis=1)

        if len(transformed_numpy_array.shape) == 3:
            # VotingClassifier will return results of shape (n_classifiers, n_samples, n_classes)
            # when voting = "soft" and flatten_transform = False. We can't handle unflatten transforms,
            # so we ignore flatten_transform flag and flatten the results.
            transformed_numpy_array = np.hstack(transformed_numpy_array)

        if len(transformed_numpy_array.shape) == 1:
            transformed_numpy_array = np.reshape(transformed_numpy_array, (-1, 1))

        shape = transformed_numpy_array.shape
        if shape[1] != len(output_cols):
            if len(output_cols) != 1:
                raise exceptions.SnowflakeMLException(
                    error_code=error_codes.INVALID_ARGUMENT,
                    original_exception=TypeError(
                        "expected_output_cols_list must be same length as transformed array or "
                        "should be of length 1"
                    ),
                )
            actual_output_cols = []
            for i in range(shape[1]):
                actual_output_cols.append(f"{output_cols[0]}_{i}")
            output_cols = actual_output_cols

        if self._drop_input_cols:
            dataset = pd.DataFrame(data=transformed_numpy_array, columns=output_cols)
        else:
            dataset = dataset.copy()
            dataset[output_cols] = transformed_numpy_array
        return dataset

    @available_if(_original_estimator_has_callable("predict"))  # type: ignore
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    @telemetry.add_stmt_params_to_df(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict(self, dataset: Union[DataFrame, pd.DataFrame]) -> Union[DataFrame, pd.DataFrame]:
        """Predict using the linear model
        For more details on this function, see [sklearn.linear_model.MultiTaskElasticNet.predict]
        (https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.MultiTaskElasticNet.html#sklearn.linear_model.MultiTaskElasticNet.predict)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            Transformed dataset.
        """
        super()._check_dataset_type(dataset)
        if isinstance(dataset, DataFrame):
            expected_type_inferred = "float"
            # when it is classifier, infer the datatype from label columns
            if expected_type_inferred == "" and 'predict' in self.model_signatures:
                # Batch inference takes a single expected output column type. Use the first columns type for now.
                label_cols_signatures = [row for row in self.model_signatures['predict'].outputs if row.name in self.output_cols]
                if len(label_cols_signatures) == 0:
                    error_str = f"Output columns {self.output_cols} do not match model signatures {self.model_signatures['predict'].outputs}."
                    raise exceptions.SnowflakeMLException(
                        error_code=error_codes.INVALID_ATTRIBUTE,
                        original_exception=ValueError(error_str),
                    )
                expected_type_inferred = convert_sp_to_sf_type(
                    label_cols_signatures[0].as_snowpark_type()
                )
            
            output_df = self._batch_inference(
                dataset=dataset,
                inference_method="predict",
                expected_output_cols_list=self.output_cols,
                expected_output_cols_type=expected_type_inferred,
            )
        elif isinstance(dataset, pd.DataFrame):
            output_df = self._sklearn_inference(
                dataset=dataset,
                inference_method="predict",
                expected_output_cols_list=self.output_cols,)

        return output_df

    @available_if(_original_estimator_has_callable("transform"))  # type: ignore
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    @telemetry.add_stmt_params_to_df(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def transform(self, dataset: Union[DataFrame, pd.DataFrame]) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            Transformed dataset.
        """
        super()._check_dataset_type(dataset)
        if isinstance(dataset, DataFrame):
            expected_dtype = "float"
            if False:  # is child of _BaseHeterogeneousEnsemble
                # transform() method of HeterogeneousEnsemble estimators return responses of varying shapes
                # from (n_samples, n_estimators) to (n_samples, n_estimators * n_classes) (and everything in between)
                # based on init param values. We will convert that to pandas dataframe of shape (n_samples, 1) with
                # each row containing a list of values.
                expected_dtype = "ARRAY"

            output_df = self._batch_inference(
                dataset=dataset,
                inference_method="transform",
                expected_output_cols_list=self.output_cols,
                expected_output_cols_type=expected_dtype,
            )
        elif isinstance(dataset, pd.DataFrame):
            output_df = self._sklearn_inference(
                dataset=dataset,
                inference_method="transform",
                expected_output_cols_list=self.output_cols,
            )

        return output_df

    def _get_output_column_names(self, output_cols_prefix: str) -> List[str]:
        """ Returns the list of output columns for predict_proba(), decision_function(), etc.. functions.
        Returns a list with output_cols_prefix as the only element if the estimator is not a classifier.
        """
        if getattr(self._sklearn_object, "classes_", None) is None:
            return [output_cols_prefix]

        assert self._sklearn_object is not None  # keep mypy happy
        classes = self._sklearn_object.classes_
        if isinstance(classes, numpy.ndarray):
            return [f'{output_cols_prefix}{c}' for c in classes.tolist()]
        elif isinstance(classes, list) and len(classes) > 0 and isinstance(classes[0], numpy.ndarray):
            # If the estimator is a multioutput estimator, classes_ will be a list of ndarrays.
            output_cols = []
            for i, cl in enumerate(classes):
                # For binary classification, there is only one output column for each class
                # ndarray as the two classes are complementary.
                if len(cl) == 2:
                    output_cols.append(f'{output_cols_prefix}_{i}_{cl[0]}')
                else:
                    output_cols.extend([
                        f'{output_cols_prefix}_{i}_{c}' for c in cl.tolist()
                    ])
            return output_cols
        return []

    @available_if(_original_estimator_has_callable("predict_proba"))  # type: ignore
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    @telemetry.add_stmt_params_to_df(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict_proba(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "predict_proba_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: Prefix for the response columns

        Returns:
            Output dataset with probability of the sample for each class in the model.
        """
        super()._check_dataset_type(dataset)
        if isinstance(dataset, DataFrame):
            output_df = self._batch_inference(
                dataset=dataset,
                inference_method="predict_proba",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
                expected_output_cols_type="float"
            )
        elif isinstance(dataset, pd.DataFrame):
            output_df = self._sklearn_inference(
                dataset=dataset,
                inference_method="predict_proba",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
            )
        
        return output_df

    @available_if(_original_estimator_has_callable("predict_log_proba"))  # type: ignore
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    @telemetry.add_stmt_params_to_df(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict_log_proba(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "predict_log_proba_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: str
                Prefix for the response columns

        Returns:
            Output dataset with log probability of the sample for each class in the model.
        """
        super()._check_dataset_type(dataset)
        if isinstance(dataset, DataFrame):
            output_df = self._batch_inference(
                dataset=dataset,
                inference_method="predict_log_proba",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
                expected_output_cols_type="float"
            )
        elif isinstance(dataset, pd.DataFrame):
            output_df = self._sklearn_inference(
                dataset=dataset,
                inference_method="predict_log_proba",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
            )

        return output_df

    @available_if(_original_estimator_has_callable("decision_function"))  # type: ignore
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    @telemetry.add_stmt_params_to_df(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def decision_function(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "decision_function_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: str
                Prefix for the response columns

        Returns:
            Output dataset with results of the decision function for the samples in input dataset.
        """
        super()._check_dataset_type(dataset)
        if isinstance(dataset, DataFrame):
            output_df = self._batch_inference(
                dataset=dataset,
                inference_method="decision_function",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
                expected_output_cols_type="float"
            )
        elif isinstance(dataset, pd.DataFrame):
            output_df = self._sklearn_inference(
                dataset=dataset,
                inference_method="decision_function",
                expected_output_cols_list=self._get_output_column_names(output_cols_prefix),
            )

        return output_df

    @available_if(_original_estimator_has_callable("score"))  # type: ignore
    def score(self, dataset: Union[DataFrame, pd.DataFrame]) -> float:
        """

        Returns:
            Score.
        """
        self._infer_input_output_cols(dataset)
        super()._check_dataset_type(dataset)
        if isinstance(dataset, pd.DataFrame):
            output_score = self._score_sklearn(dataset)
        elif isinstance(dataset, DataFrame):
            output_score = self._score_snowpark(dataset)
        return output_score

    def _score_sklearn(self, dataset: pd.DataFrame) -> float:
        assert self._sklearn_object is not None and hasattr(self._sklearn_object, "score")  # make type checker happy
        argspec = inspect.getfullargspec(self._sklearn_object.score)
        if "X" in argspec.args:
            args = {'X': dataset[self.input_cols]}
        elif "X_test" in argspec.args:
            args = {'X_test': dataset[self.input_cols]}
        else:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.INVALID_ATTRIBUTE,
                original_exception=RuntimeError(
                    "Neither 'X' or 'X_test' exist in argument"
                ),
            )
        
        if self.label_cols:
            label_arg_name = "Y" if "Y" in argspec.args else "y"
            args[label_arg_name] = dataset[self.label_cols].squeeze()

        if self.sample_weight_col is not None and "sample_weight" in argspec.args:
            args['sample_weight'] = dataset[self.sample_weight_col].squeeze()

        score = self._sklearn_object.score(**args)
        return score

    def _score_snowpark(self, dataset: DataFrame) -> float:
        # Specify input columns so column pruing will be enforced
        selected_cols = self._get_active_columns()
        if len(selected_cols) > 0:
            dataset = dataset.select(selected_cols)

        session = dataset._session
        assert session is not None  # keep mypy happy

        score = self._handlers.score_snowpark(
            dataset,
            session,
            self._sklearn_object,
            ["snowflake-snowpark-python"] + self._get_dependencies(),
            ['sklearn'],
            self.input_cols,
            self.label_cols,
            self.sample_weight_col,
        )

        return score

    def _get_model_signatures(self, dataset: Union[DataFrame, pd.DataFrame]) -> None:
        self._model_signature_dict = dict()

        PROB_FUNCTIONS = ["predict_log_proba", "predict_proba", "decision_function"]

        inputs = list(_infer_signature(dataset[self.input_cols], "input"))
        outputs: List[BaseFeatureSpec] = []
        if hasattr(self, "predict"):
            # keep mypy happy
            assert self._sklearn_object is not None and hasattr(self._sklearn_object, "_estimator_type") 
            # For classifier, the type of predict is the same as the type of label
            if self._sklearn_object._estimator_type == 'classifier':
                 # label columns is the desired type for output
                outputs = _infer_signature(dataset[self.label_cols], "output")
                # rename the output columns
                outputs = model_signature_utils.rename_features(outputs, self.output_cols)
                self._model_signature_dict["predict"] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)
            # For regressor, the type of predict is float64
            elif self._sklearn_object._estimator_type == 'regressor':
                outputs = [FeatureSpec(dtype=DataType.DOUBLE, name=c) for c in self.output_cols]
                self._model_signature_dict["predict"] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)
        for prob_func in PROB_FUNCTIONS:
            if hasattr(self, prob_func):
                output_cols_prefix: str = f"{prob_func}_"
                output_column_names = self._get_output_column_names(output_cols_prefix)
                outputs = [FeatureSpec(dtype=DataType.DOUBLE, name=c) for c in output_column_names]
                self._model_signature_dict[prob_func] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)

    @property
    def model_signatures(self) -> Dict[str, ModelSignature]:
        """Returns model signature of current class.

        Raises:
            exceptions.SnowflakeMLException: If estimator is not fitted, then model signature cannot be inferred

        Returns:
            Dict[str, ModelSignature]: each method and its input output signature
        """
        if self._model_signature_dict is None:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.INVALID_ATTRIBUTE,
                original_exception=RuntimeError("Estimator not fitted before accessing property model_signatures!"),
            )
        return self._model_signature_dict

    def to_sklearn(self) -> Any:
        if self._sklearn_object is None:
            self._sklearn_object = self._create_sklearn_object()
        return self._sklearn_object

    def to_xgboost(self) -> Any:
        raise exceptions.SnowflakeMLException(
            error_code=error_codes.METHOD_NOT_ALLOWED,
            original_exception=AttributeError(
                modeling_error_messages.UNSUPPORTED_MODEL_CONVERSION.format(
                    "to_xgboost()", 
                    "to_sklearn()"
                )
            ),
        )

    def to_lightgbm(self) -> Any:
        raise exceptions.SnowflakeMLException(
            error_code=error_codes.METHOD_NOT_ALLOWED,
            original_exception=AttributeError(
                modeling_error_messages.UNSUPPORTED_MODEL_CONVERSION.format(
                    "to_lightgbm()", 
                    "to_sklearn()"
                )
            ),
        )

    def _get_dependencies(self) -> List[str]:
        return self._deps
