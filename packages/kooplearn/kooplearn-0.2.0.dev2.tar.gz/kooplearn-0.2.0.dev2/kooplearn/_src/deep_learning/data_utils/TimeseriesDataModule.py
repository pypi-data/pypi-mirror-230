from typing import Callable

import lightning as L
import pandas as pd
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

from kooplearn._src.deep_learning.data_utils.TimeseriesDataset import TimeseriesDataset


class EmptyDataset(Dataset):
    """Empty dataset."""
    def __init__(self):
        super().__init__()

    def __len__(self):
        return 0

    def __getitem__(self, idx):
        return None


class TimeseriesDataModule(L.LightningDataModule):
    """Pytorch Lightning data module for time series forecasting.

    Automates the creation of train, validation and test datasets by providing the number of samples for each set. For
    more details on the datasets, see the documentation of the TimeseriesDataset class.

    Args:
        df_series: Pandas dataframe containing the time series.
        n_train: Number of training samples.
        n_valid: Number of validation samples.
        n_test: Number of test samples.
        lb_window_size: Size of the lookback window.
        freq_date: Frequency of the time series column date.
        step: Step between two consecutive samples.
        normalize: If True, normalize the data.
        date_encoder_func: Function to encode the date.
        number_of_consecutive_time_steps_generated: Number of consecutive time steps generated.
        batch_size: Batch size when creating the dataloaders.
        num_workers: Number of workers when creating the dataloaders.
    """
    # In general for koopman we must have lb_window_size = horizon_size
    def __init__(self, df_series: pd.DataFrame, n_train: int, n_valid: int, n_test: int, lb_window_size: int,
                 freq_date: str = None, step: int = 1, normalize: bool = True,  # horizon_size=None,
                 date_encoder_func: Callable = None, number_of_consecutive_time_steps_generated: int = 1,
                 batch_size: int = 1, num_workers: int = 0):
        super().__init__()
        self.save_hyperparameters(ignore=['df_series'])
        assert isinstance(df_series, pd.DataFrame)
        self.df_series = df_series
        self.n_train = n_train
        self.n_valid = n_valid
        self.n_test = n_test
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.lb_window_size = lb_window_size
        self.horizon_size = lb_window_size
        self.step = step
        self.freq_date = freq_date
        self.date_encoder_func = date_encoder_func
        self.normalize = normalize
        self.number_of_consecutive_time_steps_generated = number_of_consecutive_time_steps_generated
        self.train_dataset = None
        self.valid_dataset = None
        self.test_dataset = None
        self.mean = None
        self.std = None
        self.idx_start_train = None

    def setup(self, stage):
        dataset_class = TimeseriesDataset
        if stage == "fit":
            idx_start_train = len(self.df_series) - self.n_valid - self.n_test - self.n_train
            idx_end_train = len(self.df_series) - self.n_valid - self.n_test
            idx_start_valid = idx_end_train
            idx_end_valid = idx_start_valid + self.n_valid
            self.train_dataset = dataset_class(
                df_series=self.df_series,
                idx_start=idx_start_train,
                idx_end=idx_end_train,
                lb_window_size=self.lb_window_size,
                freq_date=self.freq_date,
                date_encoder_func=self.date_encoder_func,
                is_train=True,
                step=self.step,
                mean=None,
                std=None,
                idx_start_train=None,
                normalize=self.normalize,
                number_of_consecutive_time_steps_generated=self.number_of_consecutive_time_steps_generated,
            )
            self.mean = self.train_dataset.mean
            self.std = self.train_dataset.std
            self.idx_start_train = self.train_dataset.real_idx_start
            if self.n_valid > 0:
                self.valid_dataset = dataset_class(
                    df_series=self.df_series,
                    idx_start=idx_start_valid,
                    idx_end=idx_end_valid,
                    lb_window_size=self.lb_window_size,
                    freq_date=self.freq_date,
                    date_encoder_func=self.date_encoder_func,
                    is_train=False,
                    step=self.step,
                    mean=self.mean,
                    std=self.std,
                    idx_start_train=self.idx_start_train,
                    normalize=self.normalize,
                    number_of_consecutive_time_steps_generated=self.number_of_consecutive_time_steps_generated,
                )
            else:
                self.valid_dataset = None
        elif stage == 'test':
            if self.n_test > 0:
                idx_start_test = len(self.df_series) - self.n_test
                idx_end_test = idx_start_test + self.n_test
                self.test_dataset = dataset_class(
                    df_series=self.df_series,
                    idx_start=idx_start_test,
                    idx_end=idx_end_test,
                    lb_window_size=self.lb_window_size,
                    freq_date=self.freq_date,
                    date_encoder_func=self.date_encoder_func,
                    is_train=False,
                    step=self.step,
                    mean=self.mean,
                    std=self.std,
                    idx_start_train=self.idx_start_train,
                    normalize=self.normalize,
                    number_of_consecutive_time_steps_generated=self.number_of_consecutive_time_steps_generated,
                )
                # TODO decide how we want to handle the test dataset (predict one step ahead or for the ensured
                #  prediction horizon). Probably the latter.
            else:
                self.test_dataset = None

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=self.num_workers, shuffle=True,
                          pin_memory=True, drop_last=True)

    def val_dataloader(self):
        # Maybe we can just disable with limit_val_batches=0
        if self.n_valid > 0:
            return DataLoader(self.valid_dataset, batch_size=self.batch_size, num_workers=self.num_workers,
                              pin_memory=True, drop_last=False)
        else:
            return DataLoader(EmptyDataset(), batch_size=2, drop_last=True)

    def test_dataloader(self):
        if self.n_test > 0:
            return DataLoader(self.test_dataset, batch_size=self.batch_size, num_workers=self.num_workers,
                              pin_memory=True, drop_last=False)
        else:
            return DataLoader(EmptyDataset(), batch_size=2, drop_last=True)
