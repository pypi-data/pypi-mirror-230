# Standard imports
import io
import json
from typing import Tuple
from pprint import pprint
import time

# Third-party imports
import pandas as pd
from typeguard import typechecked

# Project imports
from . import api
from . import utils
from . import settings


### Utility functions ###

# TODO: Move to utils.py?

def get_value_from_body(key: str, body: dict):
    # Improve the error messaging and relate response from api.py directly here
    if key in body.keys():
        return body[f"{key}"]
    else:
        print(body)
        raise KeyError(f"{key} not in API response body")


def _status_campaign(campaign_id: str, verbose=False, debug=False) -> dict:
    response = api.get_status_model(campaign_id, verbose=debug)
    if verbose:
        message = _get_message(response)
        print(message)
    return response


def _get_csv_string(filepath_or_df: str | pd.DataFrame) -> str:

    if type(filepath_or_df) is str:
        filepath = filepath_or_df
        csv_string = open(filepath, "r").read()
    elif type(filepath_or_df) is pd.DataFrame:
        df = filepath_or_df
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        csv_string = buffer.getvalue()
    else:
        raise ValueError(
            "filepath_or_df must be a string or pandas dataframe")
    return csv_string


def _use_campaign(campaign_id: str,
                  method: str,
                  filepath_or_df=None,
                  processor="cpu", verbose=False, debug=False,
                  **kwargs) -> io.StringIO:
    if filepath_or_df is not None:
        eval_csv = _get_csv_string(filepath_or_df)
    else:
        eval_csv = None
    response = api.use_model(campaign_id, method, eval_csv=eval_csv,
                             processor=processor, verbose=debug, **kwargs)
    output_csv = get_value_from_body('dataframe', response)
    return io.StringIO(output_csv)


def _get_message(response: dict) -> str:
    # TODO: This could be a method of the response object
    # TODO: This should be better
    try:
        message = response["message"]
    except:
        message = response
    return message

### ###

### General functions ###


@typechecked
def get_user_information(verbose=False, debug=False) -> dict:
    """
    # Get user information

    Get information about the user

    ## Arguments

    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `dict` containing user information

    ## Example
    ```python
    import twinlab as tl

    user_info = tl.get_user_information()
    print(user_info)
    ```
    """
    response = api.get_user(verbose=debug)
    user_info = response
    if verbose:
        print("User information:")
        pprint(user_info, compact=True, sort_dicts=False)
    return user_info


@typechecked
def get_versions(verbose=False, debug=False) -> dict:
    """
    # Get versions

    Get information about the twinLab version being used

    ## Arguments

    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `dict` containing version information

    ## Example
    ```python
    import twinlab as tl

    version_info = tl.get_versions()
    print(version_info)
    ```
    """
    response = api.get_versions(verbose=debug)
    version_info = response
    if verbose:
        print("Version information:")
        pprint(version_info, compact=True, sort_dicts=False)
    return version_info

### ###

### Dataset functions ###


@typechecked
def upload_dataset(filepath_or_df: str | pd.DataFrame, dataset_id: str,
                   use_upload_url=True, verbose=False, debug=False) -> None:
    """
    # Upload dataset

    Upload a dataset to the `twinLab` cloud so that it can be queried and used for training.

    ## Arguments

    - `filepath_or_df`: `str` | `Dataframe`; location of csv dataset on local machine or `pandas` dataframe
    - `dataset_id`: `str`; name for the dataset when saved to the twinLab cloud
    - `use_upload_url`: `bool` determining whether to upload via a pre-signed url or directly to the server
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    **NOTE:** Local data must be a CSV file, working data should be a pandas Dataframe. 

    ## Examples

    Upload a local file:
    ```python
    import twinlab as tl

    data_filepath = "resources/data/my_data.csv"
    tl.upload_dataset(data_filepath, "my_dataset")
    ```

    Upload a `pandas` dataframe:
    ```python
    import pandas as pd
    import twinlab as tl

    df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
    tl.upload_dataset(df, "my_dataset")
    ```
    """

    # Upload the file (either via link or directly)
    if use_upload_url:
        response = api.generate_upload_url(dataset_id, verbose=debug)
        upload_url = get_value_from_body("url", response)
        if type(filepath_or_df) is str:
            filepath = filepath_or_df
            utils.upload_file_to_presigned_url(
                filepath, upload_url, verbose=verbose, check=settings.CHECK_DATASETS)
        elif type(filepath_or_df) is pd.DataFrame:
            df = filepath_or_df
            utils.upload_dataframe_to_presigned_url(
                df, upload_url, verbose=verbose, check=settings.CHECK_DATASETS)
        else:
            raise ValueError(
                "filepath_or_df must be a string or pandas dataframe")
        if verbose:
            print("Processing dataset.")
        response = api.process_uploaded_dataset(dataset_id, verbose=debug)

    else:
        csv_string = _get_csv_string(filepath_or_df)
        response = api.upload_dataset(dataset_id, csv_string, verbose=debug)

    if verbose:
        message = _get_message(response)
        print(message)


@typechecked
def list_datasets(verbose=False, debug=False) -> list:
    """
    # List datasets

    List datasets that have been uploaded to the `twinLab` cloud

    ## Arguments

    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Example

    ```python
    import twinlab as tl

    datasets = tl.list_datasets()
    print(datasets)
    ```
    """
    response = api.list_datasets(verbose=debug)
    datasets = get_value_from_body("datasets", response)
    if verbose:
        print("Datasets:")
        pprint(datasets, compact=True, sort_dicts=False)
    return datasets

    # try:
    #     datasets = get_value_from_body("datasets", response)
    #     if verbose:
    #         print("Datasets:")
    #         pprint(datasets, compact=True, sort_dicts=False)
    #     return datasets
    # except:
    #     print(response)


@typechecked
def view_dataset(dataset_id: str, verbose=False, debug=False) -> pd.DataFrame:
    """
    # View dataset

    View a dataset that exists on the twinLab cloud.

    ## Arguments

    - `dataset_id`: `str`; name for the dataset when saved to the twinLab cloud
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `pandas.DataFrame` of the dataset.


   ## Example

    ```python
    import twinlab as tl

    df = tl.view_dataset("my_dataset")
    print(df)
    ```
    """
    response = api.view_dataset(dataset_id, verbose=debug)
    csv_string = get_value_from_body('dataset', response)
    csv_string = io.StringIO(csv_string)
    df = pd.read_csv(csv_string, sep=",")
    if verbose:
        print("Dataset:")
        print(df)
    return df


@typechecked
def query_dataset(dataset_id: str, verbose=False, debug=False) -> pd.DataFrame:
    """
    # Query dataset

    Query a dataset that exists on the `twinLab` cloud by printing summary statistics.

    ## Arguments

    - `dataset_id`: `str`; name of dataset on S3 (same as the uploaded file name)
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `pandas.DataFrame` containing summary statistics for the dataset.

    ## Example

    ```python
    import twinlab as tl

    df = tl.query_dataset("my_dataset")
    print(df)
    ```
    """
    response = api.summarise_dataset(dataset_id, verbose=debug)
    csv_string = get_value_from_body('dataset_summary', response)
    csv_string = io.StringIO(csv_string)
    df = pd.read_csv(csv_string, index_col=0, sep=",")
    if verbose:
        print("Dataset summary:")
        print(df)
    return df


@typechecked
def delete_dataset(dataset_id: str, verbose=False, debug=False) -> None:
    """
    # Delete dataset

    Delete a dataset from the `twinLab` cloud.

    ## Arguments

    - `dataset_id`: `str`; name of dataset to delete from the cloud
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `list` of `str` dataset ids

    ## Example

    ```python
    import twinlab as tl

    tl.delete_dataset("my_dataset")
    ```
    """
    response = api.delete_dataset(dataset_id, verbose=debug)
    if verbose:
        message = _get_message(response)
        print(message)

###  ###

### Campaign functions ###


@typechecked
def train_campaign(filepath_or_params: str | dict, campaign_id: str,
                   ping_time=1., processor="cpu", verbose=False, debug=False) -> None:
    """
    # Train campaign

    Train a campaign in the `twinLab` cloud.

    ## Arguments

    - `filepath_or_params`: `str` | `dict`; filepath to local json or parameters dictionary for training
    - `campaign_id`: `str`; name for the final trained campaign
    - `ping_time`: `float`; time between pings to the server to check if the job is complete [s]
    - `processor`: `str`; processor to use for sampling ("cpu"; "gpu")
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Example

    Train using a local `json` parameters file:
    ```python
    import twinlab as tl

    tl.train_campaign("path/to/params.json", "my_campaign")
    ```

    Train via a `python` dictionary:
    ```python
    import twinlab as tl

    params = {
        "dataset_id": "my_dataset",
        "inputs": ["X"],
        "outputs": ["y"],
    }
    tl.train_campaign(params, "my_campaign")
    ```
    """
    if type(filepath_or_params) is dict:
        params = filepath_or_params
    elif type(filepath_or_params) is str:
        filepath = filepath_or_params
        params = json.load(open(filepath))
    else:
        print("Type:", type(filepath_or_params))
        raise ValueError(
            "filepath_or_params must be either a string or a dictionary")
    params = utils.coerce_params_dict(params)
    params_str = json.dumps(params)
    response = api.train_model(campaign_id, params_str,
                               processor=processor, verbose=debug)
    if verbose:
        message = _get_message(response)
        print(message)

    # Wait for job to complete
    complete = False
    while not complete:
        status = _status_campaign(campaign_id, verbose=False, debug=debug)
        complete = get_value_from_body("job_complete", status)
        time.sleep(ping_time)


@typechecked
def list_campaigns(verbose=False, debug=False) -> list:
    """
    # List datasets

    List campaigns that have been completed to the `twinLab` cloud.

    ## Arguments

    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - A `list` of `str` campaign ids

    ## Example

    ```python
    import twinlab as tl

    campaigns = tl.list_campaigns()
    print(campaigns)
    ```
    """
    response = api.list_models(verbose=debug)
    campaigns = get_value_from_body("models", response)
    if verbose:
        print("Trained models:")
        pprint(campaigns, compact=True, sort_dicts=False)
    return campaigns


@typechecked
def view_campaign(campaign_id: str, verbose=False, debug=False) -> dict:
    """
    # View dataset

    View a campaign that exists on the twinLab cloud.

    ## Arguments

    - `campaign_id`: `str`; name for the model when saved to the twinLab cloud
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `dict` containing the campaign training parameters.

    ## Example

    ```python
    import twinlab as tl

    params = tl.view_campaign("my_campaign")
    print(params)
    ```
    """
    response = api.view_model(campaign_id, verbose=debug)
    model_parameters = response
    if verbose:
        print("Campaign summary:")
        pprint(model_parameters, compact=True, sort_dicts=False)
    return model_parameters


@typechecked
def query_campaign(campaign_id: str, verbose=False, debug=False) -> dict:
    """
    # Query campaign

    Get summary statistics for a pre-trained campaign in the `twinLab` cloud.

    ## Arguments

    - `campaign_id`: `str`; name of trained campaign to query
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - dictionary containing summary statistics for the dataset.

    ## Example

    ```python
    import twinlab as tl

    info = tl.query_campaign("my_campaign")
    print(info)
    ```
    """
    response = api.summarise_model(campaign_id, verbose=debug)
    summary = response
    # summary = json.loads(response["model_summary"]) # TODO: This should work eventually
    if verbose:
        print("Model summary:")
        pprint(summary, compact=True, sort_dicts=False)
    return summary


@typechecked
def predict_campaign(filepath_or_df: str | pd.DataFrame, campaign_id: str,
                     processor="cpu", verbose=False, debug=False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    # Predict campaign

    Make predictions from a pre-trained model that exists on the `twinLab` cloud.

    ## Arguments

    - `filepath_or_df`: `str`; location of csv dataset on local machine for evaluation or `pandas` dataframe
    - `campaign_id`: `str`; name of pre-trained campaign to use for predictions
    - `processor`: `str`; processor to use for sampling ("cpu"; "gpu")
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    **NOTE:** Evaluation data must be a CSV file, or a `pandas` dataframe that is interpretable as a CSV.

    ## Returns

    - `tuple` containing:
        - `df_mean`: `pandas.DataFrame` containing mean predictions
        - `df_std`: `pandas.DataFrame` containing standard deviation predictions

    ## Example

    Using a local file:
    ```python
    import twinlab as tl

    filepath = "resources/data/eval.csv" # Local
    campaign_id = "my_campaign" # Pre-trained
    df_mean, df_std = tl.predict_campaign(file, campaign_id)
    ```

    Using a `pandas` dataframe:
    ```python
    import pandas as pd
    import twinlab as tl

    df = pd.DataFrame({'X': [1.5, 2.5, 3.5]})
    tl.predict_campaign(df, "my_campaign")
    ```
    """

    csv = _use_campaign(campaign_id, method="predict",
                        filepath_or_df=filepath_or_df,
                        processor=processor, verbose=verbose, debug=debug)
    df = pd.read_csv(csv, sep=",")
    n = len(df.columns)
    df_mean, df_std = df.iloc[:, :n//2], df.iloc[:, n//2:]
    df_std.columns = df_std.columns.str.removesuffix(" [std_dev]")
    if verbose:
        print("Mean predictions:")
        print(df_mean)
        print("Standard deviation predictions:")
        print(df_std)

    return df_mean, df_std


@typechecked
def sample_campaign(filepath_or_df: str | pd.DataFrame, campaign_id: str, num_samples: int,
                    processor="cpu", verbose=False, debug=False) -> pd.DataFrame:
    """
    # Sample campaign

    Draw samples from a pre-trained campaign that exists on the `twinLab` cloud.

    ## Arguments

    - `filepath_or_df`: `str`; location of csv dataset on local machine for evaluation or `pandas` dataframe
    - `campaign_id`: `str`; name of pre-trained campaign to use for predictions
    - `num_samples`: `int`; number of samples to draw for each row of the evaluation data
    - `processor`: `str`; processor to use for sampling ("cpu"; "gpu")
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    **NOTE:** Evaluation data must be a CSV file, or a `pandas` dataframe that is interpretable as a CSV.

    ## Returns

    - `DataFrame` with the sampled values

    ## Example

    Using a local file:
    ```python
    import twinlab as tl

    filepath = "resources/data/eval.csv" # Local
    n = 10
    df_mean, df_std = tl.sample_campaign(filepath, "my_campaign", n)
    ```

    Using a `pandas` dataframe:
    ```python
    import pandas as pd
    import twinlab as tl

    df = pd.DataFrame({'X': [1.5, 2.5, 3.5]})
    n = 10
    tl.sample_campaign(df, "my_campaign", n)
    ```
    """

    csv = _use_campaign(campaign_id, method="sample",
                        filepath_or_df=filepath_or_df,
                        num_samples=num_samples,
                        processor=processor, verbose=verbose, debug=debug)
    df = pd.read_csv(csv, header=[0, 1], sep=",")
    if verbose:
        print("Samples:")
        print(df)
    return df


@typechecked
def active_learn_campaign(campaign_id: str, num_points: int,
                          processor="cpu", verbose=False, debug=False) -> pd.DataFrame:
    """
    # Active learn campaign

    Draw new candidate data points via active learning from a pre-trained campaign 
    that exists on the `twinLab` cloud.

    ## Arguments
    - `campaign_id`: `str`; name of pre-trained campaign to use for predictions
    - `num_points`: `int`; number of samples to draw for each row of the evaluation data
    - `processor`: `str`; processor to use for sampling ("cpu"; "gpu")
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Returns

    - `Dataframe` containing the recommended sample locations

    ## Example

    ```python
    import twinlab as tl

    n = 10
    df = tl.active_learn_campaign("my_campaign", n)
    ```
    """

    csv = _use_campaign(campaign_id, method="get_candidate_points",
                        acq_func="qNIPV", num_points=num_points,
                        processor=processor, verbose=verbose, debug=debug)
    df = pd.read_csv(csv, sep=",")
    if verbose:
        print("Candidate points:")
        print(df)
    return df


@typechecked
def delete_campaign(campaign_id: str, verbose=False, debug=False) -> None:
    """
    # Delete campaign

    Delete campaign from the `twinLab` cloud.

    **NOTE:** Your user information is automatically added to the request using the `.env` file.

    ## Arguments

    - `campaign_id`: `str`; name of trained campaign to delete from the cloud
    - `verbose`: `bool` determining level of information returned to the user
    - `debug`: `bool` determining level of information logged on the server

    ## Example

    ```python
    import twinlab as tl

    tl.delete_campaign("my_campaign")
    ```
    """
    response = api.delete_model(campaign_id, verbose=debug)
    if verbose:
        message = _get_message(response)
        print(message)

### ###
