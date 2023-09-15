import typing as t


import sarus
from sarus import Dataset


class RemoteFederatedDataset:
    def __init__(self, list_of_datasets: t.List[Dataset]) -> None:
        self.datasets = {x.dataspec()["slugname"]: x for x in list_of_datasets}
        slugnames = ", ".join(list(self.datasets.keys()))
        print(
            f"The datasets {slugnames} have been added to the federated dataset."
        )
        self.remote_dataframe = {}

    def as_pandas(self):
        dict_of_dataframes = {
            k: v.table([k]).as_pandas() for k, v in self.datasets.items()
        }
        self.remote_dataframe = RemoteFederatedDataframe(dict_of_dataframes)
        return self.remote_dataframe


class RemoteFederatedDataframe:
    def __init__(self, dict_of_dataframes) -> None:
        self.dataframes = dict(dict_of_dataframes.items())

    def __getitem__(self, column):
        return RemoteFederatedDataframe(
            {k: v.__getitem__(column) for k, v in self.dataframes.items()}
        )

    def count(self):
        count = 0
        for _, single_df in self.dataframes.items():
            count += sarus.eval(single_df.shape)[0]
        return count

    def sum(self):
        dict_of_sum = {
            k: sarus.eval(v.sum(axis=0, numeric_only=True))
            for k, v in self.dataframes.items()
        }
        return sum(dict_of_sum.values())

    def mean(self):
        dict_of_sum = {
            k: sarus.eval(v.sum(axis=0, numeric_only=True))
            for k, v in self.dataframes.items()
        }
        return sum(dict_of_sum.values()) / self.count()

    def eval(self):
        return {k: sarus.eval(v) for k, v in self.dataframes.items()}

    def head(self):
        return sarus.eval(
            self.dataframes[list(self.dataframes.keys())[0]]
        ).head()

    def synthetic_eval(self):
        return sarus.eval(
            self.dataframes[list(self.dataframes.keys())[0]], target_epsilon=0
        )
