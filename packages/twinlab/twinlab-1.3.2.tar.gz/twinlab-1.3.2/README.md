# twinLab Client

<p align="center">
    <img src="./resources/icons/logo.svg" width="200" height="200" />
</p>

![digiLab](./resources/badges/digilab.svg)
[![slack](https://img.shields.io/badge/slack-@digilabglobal-purple.svg?logo=slack)](https://digilabglobal.slack.com)

Headless interface to the `twinLab` library.

## Installation

Most users should use `pip`
```shell
pip install twinlab
```

If you want to modify the client-side code, or have a local installation, you will need to have `git`, `poetry`, and a `python` version of `3.10` or higher installed. Then you can do:
```shell
git clone https://github.com/digiLab-ai/twinLab-client.git
cd twinlab-client
poetry install
```

## Environment setup

You will need a `.env` file in your project directory that looks like the `.env.example` file in this repository
```shell
cp .env.example .env
```
and fill in your `twinLab` user details.

## Commands

### Pipeline

```shell
poetry run python scripts/twinlab/test.py
```
where `test.py` can be replaced with any of the scripts in the `scripts` directory.

### Individual examples

#### Get user information:
```shell
poetry run python scripts/twinlab/get_user_information.py
```

#### Get version information:
```shell
poetry run python scripts/twinlab/get_versions.py
```

#### List datasets:
```shell
poetry run python scripts/twinlab/list_datasets.py
```

#### Upload dataset to the Cloud:
Fill in the arguments (between the angled brackets; `<` `>`) with your own `dataset` and `dataset_id` (this the filename for the dataset when stored in the Cloud):
```shell
poetry run python scripts/twinlab/upload_dataset.py <path/to/dataset.csv> <dataset_id>
```
For example, using the test `biscuits` dataset:
```shell
poetry run python scripts/twinlab/upload_dataset.py resources/datasets/biscuits.csv biscuits
```

#### View dataset that has been uploaded to the Cloud:
```shell
poetry run python scripts/twinlab/view_dataset.py <dataset_id>
poetry run python scripts/twinlab/view_dataset.py biscuits
```

#### Summarise a dataset on the Cloud:
```shell
poetry run python scripts/twinlab/query_dataset.py <dataset_id>
poetry run python scripts/twinlab/query_dataset.py biscuits
```

#### List campaigns that you have uploaded to the Cloud:
```shell
poetry run python scripts/twinlab/list_campaigns.py
```

#### Train campaign on the Cloud:
```shell
poetry run python scripts/twinlab/train_campaign.py <path/to/parameters.json> <campaign_id> <processor>
poetry run python scripts/twinlab/train_campaign.py resources/campaigns/biscuits/params.json biscuits-campaign
```

#### View campaign details:
```shell
poetry run python scripts/twinlab/view_campaign.py <campaign_id>
poetry run python scripts/twinlab/view_campaign.py biscuits-campaign
```

#### Summarise trained campaign:
```shell
poetry run python scripts/twinlab/query_campaign.py <campaign_id>
poetry run python scripts/twinlab/query_campaign.py biscuits-campaign
```

#### Predict using a trained campaign:
```shell
poetry run python scripts/twinlab/predict_campaign.py <path/to/inputs.csv> <campaign_id> <method> <processor>
poetry run python scripts/twinlab/predict_campaign.py resources/campaigns/biscuits/eval.csv biscuits-campaign
```

#### Delete a campaign from the Cloud:
```shell
poetry run python scripts/twinlab/delete_campaign.py <campaign_id>
poetry run python scripts/twinlab/delete_campaign.py biscuits-campaign
```

#### Delete a dataset from the Cloud:
```shell
poetry run python scripts/twinlab/delete_dataset.py <dataset_id>
poetry run python scripts/twinlab/delete_dataset.py biscuits
```

## Full example

Here we create some mock data (which has a quadratic relationship between `X` and `y`) and use `twinLab` to create a surrogate model with quantified uncertainty.
```python
# Import libraries
import twinlab as tl
import pandas as pd

# Create a dataset and upload to twinLab cloud
df = pd.DataFrame({"X": [1, 2, 3, 4], "y": [1, 4, 9, 16]})
tl.upload_dataset(df, "test-data")

# Train a machine-learning model for the data
params = {
    "dataset_id": "test-data",
    "inputs": ["X"],
    "outputs": ["y"],
}
tl.train_campaign(params, campaign_id="test-model")

# Evaluate the model on some unseen data
df = pd.DataFrame({"X": [1.5, 2.5, 3.5]})
df_mean, df_std = tl.predict_campaign(df, campaign_id="test-model")
```

## Notebooks

Check out the `notebooks` directory for some additional examples to get started!

## Documentation

See the live documentation at https://digilab-ai.github.io/twinLab-client/. Or build a copy locally:
```shell
cd docs
yarn install && yarn start
```
