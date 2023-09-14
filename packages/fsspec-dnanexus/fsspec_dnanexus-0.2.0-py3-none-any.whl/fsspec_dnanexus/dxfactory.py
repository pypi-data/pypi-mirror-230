# Modify Modin's Factories to read and write parquet and csv files on DNAnexus platform
# References:
# 1. Override PandasOnRay to pass storage_options to fsspec for writing feature
#   https://github.com/modin-project/modin/blob/master/modin/core/execution/ray/implementations/pandas_on_ray/io/io.py#L46
# 2. Override ParquetDispatcher for reading single parquet file
#   https://github.com/modin-project/modin/blob/master/modin/core/io/column_stores/parquet_dispatcher.py#L302
from modin import __version__
from modin.core.execution.ray.implementations.pandas_on_ray.io.io import SignalActor, RayIO, RayWrapper, PandasOnRayIO
from modin.core.execution.dispatching.factories.factories import BaseFactory
from pandas.io.common import get_handle
from modin.core.execution.ray.implementations.pandas_on_ray.partitioning import PandasOnRayDataframePartition
from modin.core.execution.ray.implementations.pandas_on_ray.dataframe import PandasOnRayDataframe
from modin.core.storage_formats.pandas.query_compiler import PandasQueryCompiler

from modin.core.io import ParquetDispatcher
from modin.core.storage_formats.pandas.parsers import PandasParquetParser

import os
import io
import uuid
import pandas
import logging
import fsspec
from datetime import datetime
from packaging import version
import pandas._libs.lib as lib

from pandas.io.common import stringify_path
from fsspec.core import url_to_fs

from .core import DXFileSystemException


logger = logging.getLogger("dxfs")

class DXParquetDispatcher(ParquetDispatcher):
    @classmethod
    def _read(cls, **kwargs):
        if version.parse(__version__) < version.parse("0.23.0"):
            return cls._read_less_23(**kwargs)
        else:
            return cls._read_greater_23(**kwargs)
    
    @classmethod
    def _read_less_23(cls, path, engine, columns, **kwargs):
        """
        Load a parquet object from the file path, returning a query compiler.

        Parameters
        ----------
        path : str, path object or file-like object
            The filepath of the parquet file in local filesystem or hdfs.
        engine : {"auto", "pyarrow", "fastparquet"}
            Parquet library to use.
        columns : list
            If not None, only these columns will be read from the file.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        BaseQueryCompiler
            A new Query Compiler.

        Notes
        -----
        ParquetFile API is used. Please refer to the documentation here
        https://arrow.apache.org/docs/python/parquet.html
        """
        storage_options = kwargs.get("storage_options")
        if storage_options is not None:
            fs, fs_path = url_to_fs(stringify_path(path), **storage_options)
        else:
            fs, fs_path = url_to_fs(stringify_path(path))
        is_file = fs.isfile(fs_path)
        is_dir = fs.isdir(fs_path)

        if is_dir and is_file:
            raise DXFileSystemException("The path is ambiguous. It matches file and folder.")
        
        if is_file or any(arg not in ("storage_options", "use_nullable_dtypes") for arg in kwargs):
            return cls.single_worker_read(
                path,
                engine=engine,
                columns=columns,
                reason="Parquet options that are not currently supported",
                **kwargs,
            )
        path = stringify_path(path)
        if isinstance(path, list):
            # TODO(https://github.com/modin-project/modin/issues/5723): read all
            # files in parallel.
            compilers: list[cls.query_compiler_cls] = [
                cls._read(p, engine, columns, **kwargs) for p in path
            ]
            return compilers[0].concat(axis=0, other=compilers[1:], ignore_index=True)
        if isinstance(path, str):
            if os.path.isdir(path):
                path_generator = os.walk(path)
            else:
                path_generator = fs.walk(fs_path)
            partitioned_columns = set()
            # We do a tree walk of the path directory because partitioned
            # parquet directories have a unique column at each directory level.
            # Thus, we can use os.walk(), which does a dfs search, to walk
            # through the different columns that the data is partitioned on
            for _, dir_names, files in path_generator:
                if dir_names:
                    partitioned_columns.add(dir_names[0].split("=")[0])
                if files:
                    # Metadata files, git files, .DSStore
                    # TODO: fix conditional for column partitioning, see issue #4637
                    if len(files[0]) > 0 and files[0][0] == ".":
                        continue
                    break
            partitioned_columns = list(partitioned_columns)
            if len(partitioned_columns):
                return cls.single_worker_read(
                    path,
                    engine=engine,
                    columns=columns,
                    reason="Mixed partitioning columns in Parquet",
                    **kwargs,
                )

        dataset = cls.get_dataset(path, engine, kwargs.get("storage_options") or {})
        index_columns = (
            dataset.pandas_metadata.get("index_columns", [])
            if dataset.pandas_metadata
            else []
        )
        # If we have columns as None, then we default to reading in all the columns
        column_names = columns if columns else dataset.columns
        columns = [
            c
            for c in column_names
            if c not in index_columns and not cls.index_regex.match(c)
        ]

        return cls.build_query_compiler(dataset, columns, index_columns, **kwargs)

    @classmethod
    def _read_greater_23(cls, path, engine, columns, use_nullable_dtypes, dtype_backend, **kwargs):
        """
        Load a parquet object from the file path, returning a query compiler.

        Parameters
        ----------
        path : str, path object or file-like object
            The filepath of the parquet file in local filesystem or hdfs.
        engine : {"auto", "pyarrow", "fastparquet"}
            Parquet library to use.
        columns : list
            If not None, only these columns will be read from the file.
        use_nullable_dtypes : Union[bool, lib.NoDefault]
        dtype_backend : {"numpy_nullable", "pyarrow", lib.no_default}
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        BaseQueryCompiler
            A new Query Compiler.

        Notes
        -----
        ParquetFile API is used. Please refer to the documentation here
        https://arrow.apache.org/docs/python/parquet.html
        """
        storage_options = kwargs.get("storage_options")
        if storage_options is not None:
            fs, fs_path = url_to_fs(stringify_path(path), **storage_options)
        else:
            fs, fs_path = url_to_fs(stringify_path(path))
        is_file = fs.isfile(fs_path)
        is_dir = fs.isdir(fs_path)

        if is_dir and is_file:
            raise DXFileSystemException("The path is ambiguous. It matches file and folder.")

        if (is_file
            or any(arg not in ("storage_options",) for arg in kwargs)
            or use_nullable_dtypes != lib.no_default
        ):
            return cls.single_worker_read(
                path,
                engine=engine,
                columns=columns,
                use_nullable_dtypes=use_nullable_dtypes,
                dtype_backend=dtype_backend,
                reason="Parquet options that are not currently supported",
                **kwargs,
            )
        path = stringify_path(path)
        if isinstance(path, list):
            # TODO(https://github.com/modin-project/modin/issues/5723): read all
            # files in parallel.
            compilers: list[cls.query_compiler_cls] = [
                cls._read(
                    p, engine, columns, use_nullable_dtypes, dtype_backend, **kwargs
                )
                for p in path
            ]
            return compilers[0].concat(axis=0, other=compilers[1:], ignore_index=True)
        if isinstance(path, str):
            if os.path.isdir(path):
                path_generator = os.walk(path)
            else:
                path_generator = fs.walk(fs_path)
            partitioned_columns = set()
            # We do a tree walk of the path directory because partitioned
            # parquet directories have a unique column at each directory level.
            # Thus, we can use os.walk(), which does a dfs search, to walk
            # through the different columns that the data is partitioned on
            for _, dir_names, files in path_generator:
                if dir_names:
                    partitioned_columns.add(dir_names[0].split("=")[0])
                if files:
                    # Metadata files, git files, .DSStore
                    # TODO: fix conditional for column partitioning, see issue #4637
                    if len(files[0]) > 0 and files[0][0] == ".":
                        continue
                    break
            partitioned_columns = list(partitioned_columns)
            if len(partitioned_columns):
                return cls.single_worker_read(
                    path,
                    engine=engine,
                    columns=columns,
                    use_nullable_dtypes=use_nullable_dtypes,
                    dtype_backend=dtype_backend,
                    reason="Mixed partitioning columns in Parquet",
                    **kwargs,
                )

        dataset = cls.get_dataset(path, engine, kwargs.get("storage_options") or {})
        index_columns = (
            dataset.pandas_metadata.get("index_columns", [])
            if dataset.pandas_metadata
            else []
        )
        # If we have columns as None, then we default to reading in all the columns
        column_names = columns if columns else dataset.columns
        columns = [
            c
            for c in column_names
            if c not in index_columns and not cls.index_regex.match(c)
        ]

        return cls.build_query_compiler(
            dataset, columns, index_columns, dtype_backend=dtype_backend, **kwargs
        )
    
    @staticmethod
    def _to_parquet_check_support(kwargs):
        """
        Check if parallel version of `to_parquet` could be used.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments passed to `.to_parquet()`.

        Returns
        -------
        bool
            Whether parallel version of `to_parquet` is applicable.
        """
        path = kwargs["path"]
        compression = kwargs["compression"]
        if not isinstance(path, str):
            return False
        if any((path.endswith(ext) for ext in [".gz", ".bz2", ".zip", ".xz"])):
            return False
        if compression is None or not compression == "snappy":
            return False
        return True

    @classmethod
    def write(cls, qc, **kwargs):
        """
        Write a ``DataFrame`` to the binary parquet format.

        Parameters
        ----------
        qc : BaseQueryCompiler
            The query compiler of the Modin dataframe that we want to run `to_parquet` on.
        **kwargs : dict
            Parameters for `pandas.to_parquet(**kwargs)`.
        """
        if not cls._to_parquet_check_support(kwargs):
            return cls.base_io.to_parquet(qc, **kwargs)

        output_path = kwargs["path"]
        storage_options = kwargs.get("storage_options") or {}
        client_kwargs = storage_options.get("client_kwargs", {})
        fs, url = fsspec.core.url_to_fs(output_path, client_kwargs=client_kwargs)

        # if folder already exists
        if fs.isdir(url):
            if not storage_options.get("allow_duplicate_filenames"):
                # remove all files in folder
                # do not remove folder for safety
                fs.remove_files_in_folder(url)
            else:
                # rename existing folder by adding a suffix
                folder_name = os.path.basename(url.rstrip("/"))
                now = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{folder_name} copy {now}"
                fs.rename_folder(path=url, new_name=new_name)
        
        fs.mkdirs(url, exist_ok=True)

        def func(df, **kw):  # pragma: no cover
            """
            Dump a chunk of rows as parquet, then save them to target maintaining order.

            Parameters
            ----------
            df : pandas.DataFrame
                A chunk of rows to write to a parquet file.
            **kw : dict
                Arguments to pass to ``pandas.to_parquet(**kwargs)`` plus an extra argument
                `partition_idx` serving as chunk index to maintain rows order.
            """
            compression = kwargs["compression"]
            partition_idx = kw["partition_idx"]
            kwargs[
                "path"
            ] = f"{output_path}/part-{partition_idx:04d}.{compression}.parquet"
            df.to_parquet(**kwargs)
            return pandas.DataFrame()

        # Ensure that the metadata is synchronized
        qc._modin_frame._propagate_index_objs(axis=None)
        result = qc._modin_frame._partition_mgr_cls.map_axis_partitions(
            axis=1,
            partitions=qc._modin_frame._partitions,
            map_func=func,
            keep_partitioning=True,
            lengths=None,
            enumerate_partitions=True,
        )
        # pending completion
        cls.materialize([part.list_of_blocks[0] for row in result for part in row])

class DXPandasOnRayIO(PandasOnRayIO):
    build_args = dict(
        frame_partition_cls=PandasOnRayDataframePartition,
        query_compiler_cls=PandasQueryCompiler,
        frame_cls=PandasOnRayDataframe,
        base_io=RayIO,
    )
    def __make_read(*classes, build_args=build_args):
        # used to reduce code duplication
        return type("", (RayWrapper, *classes), build_args).read
    
    def __make_write(*classes, build_args=build_args):
        # used to reduce code duplication
        return type("", (RayWrapper, *classes), build_args).write

    
    read_parquet = __make_read(PandasParquetParser, DXParquetDispatcher)

    @classmethod
    def to_csv(cls, qc, **kwargs):
        """
        Write records stored in the `qc` to a CSV file.

        Parameters
        ----------
        qc : BaseQueryCompiler
            The query compiler of the Modin dataframe that we want to run ``to_csv`` on.
        **kwargs : dict
            Parameters for ``pandas.to_csv(**kwargs)``.
        """
        if not cls._to_csv_check_support(kwargs):
            return RayIO.to_csv(qc, **kwargs)

        signals = SignalActor.remote(len(qc._modin_frame._partitions) + 1)
        n_partitions = len(qc._modin_frame._partitions)
        marker_id = str(uuid.uuid4())
        logger.debug("N partitions:", n_partitions)

        def func(df, **kw):  # pragma: no cover
            """
            Dump a chunk of rows as csv, then save them to target maintaining order.

            Parameters
            ----------
            df : pandas.DataFrame
                A chunk of rows to write to a CSV file.
            **kw : dict
                Arguments to pass to ``pandas.to_csv(**kw)`` plus an extra argument
                `partition_idx` serving as chunk index to maintain rows order.
            """
            partition_idx = kw["partition_idx"]
            logger.debug("Partition index:", partition_idx)
            # the copy is made to not implicitly change the input parameters;
            # to write to an intermediate buffer, we need to change `path_or_buf` in kwargs
            csv_kwargs = kwargs.copy()
            if partition_idx != 0:
                # we need to create a new file only for first recording
                # all the rest should be recorded in appending mode
                if "w" in csv_kwargs["mode"]:
                    csv_kwargs["mode"] = csv_kwargs["mode"].replace("w", "a")
                # It is enough to write the header for the first partition
                csv_kwargs["header"] = False

            # for parallelization purposes, each partition is written to an intermediate buffer
            path_or_buf = csv_kwargs["path_or_buf"]
            is_binary = "b" in csv_kwargs["mode"]
            csv_kwargs["path_or_buf"] = io.BytesIO() if is_binary else io.StringIO()
            
            storage_options = csv_kwargs.pop("storage_options") or {}
            storage_options.update({
                "n_partitions": n_partitions,
                "partition_idx": partition_idx,
                "marker_id": marker_id,
                "dx_buffered_cls": "DXBufferedFileOnRay"
            })
            
            df.to_csv(**csv_kwargs)
            
            csv_kwargs.update({"storage_options": storage_options})
            
            content = csv_kwargs["path_or_buf"].getvalue()
            csv_kwargs["path_or_buf"].close()

            # each process waits for its turn to write to a file
            RayWrapper.materialize(signals.wait.remote(partition_idx))

            # preparing to write data from the buffer to a file
            with get_handle(
                path_or_buf,
                # in case when using URL in implicit text mode
                # pandas try to open `path_or_buf` in binary mode
                csv_kwargs["mode"] if is_binary else csv_kwargs["mode"] + "t",
                encoding=kwargs["encoding"],
                errors=kwargs["errors"],
                compression=kwargs["compression"],
                storage_options=storage_options,
                is_text=not is_binary,
            ) as handles:
                handles.handle.write(content)

            # signal that the next process can start writing to the file
            RayWrapper.materialize(signals.send.remote(partition_idx + 1))
            # used for synchronization purposes
            return pandas.DataFrame()

        # signaling that the partition with id==0 can be written to the file
        RayWrapper.materialize(signals.send.remote(0))
        # Ensure that the metadata is syncrhonized
        qc._modin_frame._propagate_index_objs(axis=None)
        result = qc._modin_frame._partition_mgr_cls.map_axis_partitions(
            axis=1,
            partitions=qc._modin_frame._partitions,
            map_func=func,
            keep_partitioning=True,
            lengths=None,
            enumerate_partitions=True,
            max_retries=0,
        )
        # pending completion
        RayWrapper.materialize(
            [part.list_of_blocks[0] for row in result for part in row]
        )

    @classmethod
    def to_parquet(cls, qc, **kwargs):
        """
        Write a ``DataFrame`` to the binary parquet format.

        Parameters
        ----------
        qc : BaseQueryCompiler
            The query compiler of the Modin dataframe that we want to run `to_parquet` on.
        **kwargs : dict
            Parameters for `pandas.to_parquet(**kwargs)`.
        """
        if not cls._to_parquet_check_support(kwargs):
            return RayIO.to_parquet(qc, **kwargs)

        output_path = kwargs["path"]
        storage_options = kwargs.get("storage_options") or {}
        client_kwargs = storage_options.get("client_kwargs", {})
        fs, url = fsspec.core.url_to_fs(output_path, client_kwargs=client_kwargs)

        # if folder already exists
        if fs.isdir(url):
            if not storage_options.get("allow_duplicate_filenames"):
                # remove all files in folder
                # do not remove folder for safety
                fs.remove_files_in_folder(url)
            else:
                # rename existing folder by adding a suffix
                folder_name = os.path.basename(url.rstrip("/"))
                now = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{folder_name} copy {now}"
                fs.rename_folder(path=url, new_name=new_name)
        
        fs.mkdirs(url, exist_ok=True)

        def func(df, **kw):
            """
            Dump a chunk of rows as parquet, then save them to target maintaining order.

            Parameters
            ----------
            df : pandas.DataFrame
                A chunk of rows to write to a parquet file.
            **kw : dict
                Arguments to pass to ``pandas.to_parquet(**kwargs)`` plus an extra argument
                `partition_idx` serving as chunk index to maintain rows order.
            """
            compression = kwargs["compression"]
            partition_idx = kw["partition_idx"]
            kwargs[
                "path"
            ] = f"{output_path}/part-{partition_idx:04d}.{compression}.parquet"
            df.to_parquet(**kwargs)
            return pandas.DataFrame()

        # Ensure that the metadata is synchronized
        qc._modin_frame._propagate_index_objs(axis=None)
        result = qc._modin_frame._partition_mgr_cls.map_axis_partitions(
            axis=1,
            partitions=qc._modin_frame._partitions,
            map_func=func,
            keep_partitioning=True,
            lengths=None,
            enumerate_partitions=True,
        )
        # pending completion
        RayWrapper.materialize(
            [part.list_of_blocks[0] for row in result for part in row]
        )

    if version.parse(__version__) >= version.parse("0.21.0"):
        to_parquet = __make_write(DXParquetDispatcher)

    del __make_read  # to not pollute class namespace
    del __make_write  # to not pollute class namespace

class DXPandasOnRayFactory(BaseFactory):
    @classmethod
    def prepare(cls):
        cls.io_cls = DXPandasOnRayIO

