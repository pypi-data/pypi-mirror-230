import pandas as pd
import numpy as np
import dask.dataframe as dd
from dask.delayed import delayed


class SyntheticDataGenerator:
    def __init__(self, loa, n_time, n_prio_grid_size, n_country_size, n_features, use_dask=False):
        self.loa = loa
        self.n_time = n_time
        self.n_prio_grid_size = n_prio_grid_size
        self.n_country_size = n_country_size
        self.n_features = n_features
        self.use_dask = use_dask
        self.df = None

    def _initialize_data_dict(self, n):
        data = {}
        for i in range(1, self.n_features + 1):
            feature_name = f'pca_{i}'
            data[feature_name] = np.random.rand(n)
        data['ln_ged_sb_dep'] = np.random.rand(n)
        return data

    def _generate_index(self):
        if self.loa == 'cm':
            country_ids = range(1, self.n_country_size + 1)
            return pd.MultiIndex.from_product([range(1, self.n_time + 1), country_ids], names=('time', 'country_id'))
        else:
            priogrid_ids = range(1, self.n_prio_grid_size + 1)
            return pd.MultiIndex.from_product([range(1, self.n_time + 1), priogrid_ids], names=('time', 'priogrid_id'))

    def _generate_dask_dataframe(self, n, chunk_size=10000):
        num_chunks = n // chunk_size
        last_chunk_size = n % chunk_size

        delayed_frames = []
        for _ in range(num_chunks):
            df_chunk = delayed(self._generate_small_dataframe_chunk)(chunk_size)
            delayed_frames.append(df_chunk)

        if last_chunk_size > 0:
            df_chunk = delayed(self._generate_small_dataframe_chunk)(last_chunk_size)
            delayed_frames.append(df_chunk)

        ddf = dd.from_delayed(delayed_frames)
        return ddf

    def generate_dataframe(self):
        index = self._generate_index()
        n = len(index)

        if self.use_dask:
            self.df = self._generate_dask_dataframe(n)
        else:
            data = self._initialize_data_dict(n)
            self.df = pd.DataFrame(data, index=index)

        return self.df

    def _generate_small_dataframe_chunk(self, chunk_size):
        data = {}
        for i in range(1, self.n_features + 1):
            feature_name = f'pca_{i}'
            data[feature_name] = np.random.rand(chunk_size)
        data['ln_ged_sb_dep'] = np.random.rand(chunk_size)
        return pd.DataFrame(data)

    def generate_csv(self, filename):
        if self.use_dask:
            self.df.to_csv(filename, single_file=True)
        else:
            self.df.to_csv(filename)
        return self.df

    def generate_parquet(self, filename):
        if self.use_dask:
            self.df.to_parquet(filename, write_options={'compression': 'gzip'})
        else:
            self.df.to_parquet(filename)
        return self.df
