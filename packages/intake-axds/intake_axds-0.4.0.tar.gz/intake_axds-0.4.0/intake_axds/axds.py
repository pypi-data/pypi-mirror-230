from typing import List, Optional, Union

import pandas as pd

from intake.source import base

from . import __version__
from .utils import (
    load_metadata,
    make_data_url,
    make_filter,
    make_label,
    make_search_docs_url,
    response_from_url,
)


class AXDSSensorSource(base.DataSource):
    """Intake Source for AXDS sensor

    Parameters
    ----------
    internal_id : Optional[int], optional
        Internal station id for Axiom, by default None. Not the UUID. Need to input internal_id or UUID. If both are input, be sure they are for the same station.
    uuid : Optional[str], optional
        The UUID for the station, by default None. Not the internal_id. Need to input internal_id or UUID. If both are input, be sure they are for the same station. Note that there may also be a "datasetId" parameter which is sometimes but not always the same as the UUID.
    start_time : Optional[str], optional
        At what datetime for data to start, by default None. Must be interpretable by pandas ``Timestamp``. If not input, the datetime at which the dataset starts will be used.
    end_time : Optional[str], optional
        At what datetime for data to end, by default None. Must be interpretable by pandas ``Timestamp``. If not input, the datetime at which the dataset ends will be used.
    qartod : bool, int, list, optional
        Whether to return QARTOD agg flags when available, which is only for sensor_stations. Can instead input an int or a list of ints representing the _qa_agg flags for which to return data values. More information about QARTOD testing and flags can be found here: https://cdn.ioos.noaa.gov/media/2020/07/QARTOD-Data-Flags-Manual_version1.2final.pdf. Only used by datatype "sensor_station". Is not available if `binned==True`.

        Examples of ways to use this input are:

        * ``qartod=True``: Return aggregate QARTOD flags as a column for each data variable.
        * ``qartod=False``: Do not return any QARTOD flag columns.
        * ``qartod=1``: nan any data values for which the aggregated QARTOD flags are not equal to 1.
        * ``qartod=[1,3]``: nan any data values for which the aggregated QARTOD flags are not equal to 1 or 3.

        Flags are:

        * 1: Pass
        * 2: Not Evaluated
        * 3: Suspect
        * 4: Fail
        * 9: Missing Data

    use_units : bool, optional
        If True include units in column names. Syntax is "standard_name [units]". If False, no units. Then syntax for column names is "standard_name". This is currently specific to sensor_station only. Only used by datatype "sensor_station".
    metadata : dict, optional
        Metadata for catalog.
    binned : bool, optional
        True for binned data, False for raw, by default False. Only used by datatype "sensor_station".
    bin_interval : Optional[str], optional
        If ``binned=True``, input the binning interval to return. Options are hourly, daily, weekly, monthly, yearly. If bin_interval is input, binned is set to True. Only used by datatype "sensor_station".
    only_pgids : list, optional
        If input, only return data associated with these parameterGroupIds. This is separate from parameterGroupLabels and parameterGroupIds that might be present in the metadata.

    Raises
    ------
    ValueError
        _description_
    """

    name = "axds-sensor"
    version = __version__
    container = "dataframe"
    partition_access = True

    def __init__(
        self,
        internal_id: Optional[int] = None,
        uuid: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        qartod: Union[int, List[int], bool] = False,
        use_units: bool = True,
        metadata=None,
        binned: bool = False,
        bin_interval: Optional[str] = None,
        only_pgids: Optional[List[int]] = None,
    ):

        if internal_id is None and uuid is None:
            raise ValueError(
                "internal_id and uuid cannot both be None. Input one of them."
            )

        self.uuid = uuid
        self.start_time = start_time
        self.end_time = end_time
        self.internal_id = internal_id
        self.qartod = qartod
        self.use_units = use_units
        self.only_pgids = only_pgids

        if bin_interval is not None:
            binned = True
        self.binned = binned
        self.bin_interval = bin_interval

        if self.binned:
            if self.qartod:
                raise ValueError(
                    "QARTOD is not available for binned output. Set QARTOD to False or use raw data."
                )

        metadata = metadata or {}

        if self.internal_id is None or self.uuid is None:
            # uses whichever id is not None
            url = make_search_docs_url(internal_id=self.internal_id, uuid=self.uuid)
            result = response_from_url(url)[0]
            assert isinstance(result, dict)  # for mypy
            metadata.update(load_metadata("sensor_station", result))
            self.internal_id = metadata["internal_id"]
            self.uuid = metadata["uuid"]
            self.search_docs_url = url

        # not checking for now
        # # check station for if we want the output or not — for when source is used directly.
        # _ = check_station(metadata, verbose=True)

        self._dataframe = None

        # this is what shows in the source if you print it
        self._captured_init_kwargs.update(
            {
                "internal_id": self.internal_id,
                "uuid": self.uuid,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "qartod": self.qartod,
                "use_units": self.use_units,
                "binned": self.binned,
                "bin_interval": bin_interval,
                "only_pgids": self.only_pgids,
            }
        )

        super(AXDSSensorSource, self).__init__(metadata=metadata)

    def get_filters(self):
        """Return appropriate filter for stationid.

        What filter form to use depends on if V1 or V2.

        For V1, use each parameterGroupId only once to make a filter since all data of that type will be read in together.

        Following Sensor API
        https://admin.axds.co/#!/sensors/api/overview
        """

        filters = []

        # if "version" not in self.metadata:
        #     res = response_from_url(make_search_docs_url(self.dataset_id))[0]
        #     self.metadata["version"] = res["data"]["version"]

        if self.metadata["version"] == 1:

            # if we should only return the requested variables, use the pgids input for this.
            if self.only_pgids:
                pgids = self.only_pgids
            else:
                pgids = [
                    self.metadata["variables_details"][var]["parameterGroupId"]
                    for var in self.metadata["variables_details"]
                ]
            for pgid in list(set(pgids)):
                filters.append(make_filter(self.internal_id, pgid))
        else:
            filters.append(make_filter(self.internal_id))
        return filters

    def _load_to_dataframe(self, url: str) -> pd.DataFrame:
        """load from raw data url to DataFrame.

        For V1 stations the result of a call to this function will be one of potentially many calls for data, but there will be only one loop below in a call.
        For V2 stations the result of a call to this function will be the only call for data, but there may be several loops in the call.

        Parameters
        ----------
        url : str
            URL to find data from.

        Returns:
        DataFrame
            Data.
        """
        data_raw = response_from_url(url)

        # check for presence of any data
        assert isinstance(data_raw, dict)
        # for binned data
        if "data" not in data_raw:
            self._dataframe = None
            raise ValueError(f"No data found for url {url}.")

        # for raw data
        if len(data_raw["data"]["groupedFeeds"]) == 0:
            self._dataframe = None
            raise ValueError(f"No data found for url {url}.")

        # loop over the data feeds and read the data into DataFrames
        # link to other metadata as needed
        dfs = []
        for feed in data_raw["data"]["groupedFeeds"]:

            # different names for data sets depending on if binned or not
            if self.binned:
                metadata_values_name = "avgVals"
            else:
                metadata_values_name = "values"

            # for the case where we only return data from certain pgids, skip loop if this
            # data is not included
            if self.only_pgids is not None:
                if not any(
                    [
                        var["parameterGroupId"]
                        for var in feed["metadata"][metadata_values_name]
                        if var["parameterGroupId"] in self.only_pgids
                    ]
                ):
                    continue

            columns = {}  # all non-index columns in dataframe
            indices = {}  # indices for dataframe

            # indices first: time and potentially z
            feed_ind = feed["metadata"]["time"]
            feed_ind["column_name"] = make_label(
                feed_ind["label"], feed_ind.get("units", None), use_units=self.use_units
            )
            indices[feed_ind["index"]] = feed_ind

            # in this case, z or depth is also an index
            if feed["metadata"]["z"] is not None:
                feed_ind = feed["metadata"]["z"]
                feed_ind["column_name"] = make_label(
                    feed_ind["label"],
                    feed_ind.get("units", None),
                    use_units=self.use_units,
                )
                indices[feed_ind["index"]] = feed_ind

            # These should never be non-None for sensors
            if (
                feed["metadata"]["lon"] is not None
                or feed["metadata"]["lat"] is not None
            ):
                lon, lat = feed["metadata"]["lon"], feed["metadata"]["lat"]
                raise ValueError(
                    f"lon/lat should be None for sensors but are {lon}, {lat}."
                )

            # add data columns
            data_cols = {
                val["index"]: val for val in feed["metadata"][metadata_values_name]
            }
            # match variable name from metadata (standard_name) to be column name
            for index in data_cols:
                # variable name
                label = [
                    var
                    for var in self.metadata["variables_details"]
                    if self.metadata["variables_details"][var]["deviceId"]
                    == data_cols[index]["deviceId"]
                ][0]
                data_cols[index]["label"] = label
                # column name
                data_cols[index]["column_name"] = make_label(
                    label, data_cols[index].get("units", None), use_units=self.use_units
                )

            columns.update(data_cols)

            # whether or not to read in QARTOD Aggregation flags is chosen at the catalog level in axds_cat.py
            # columns only includes the QA column info if qartod is True
            # or, include QARTOD columns but then remove data rows based on the flag values.
            qartod = self.qartod
            if isinstance(qartod, (str, list)) or qartod:

                # add qartod columns
                qa_cols = {val["index"]: val for val in feed["metadata"]["qcAgg"]}
                # match variable name using deviceId from metadata (standard_name) to be column name
                for index in qa_cols:
                    label = [
                        var
                        for var in self.metadata["variables_details"]
                        if self.metadata["variables_details"][var]["deviceId"]
                        == qa_cols[index]["deviceId"]
                    ][0]
                    qa_cols[index]["label"] = f"{label}_qc_agg"
                    qa_cols[index]["column_name"] = qa_cols[index]["label"]

                    # match deviceId between data_col and qa_col to get column name associated with qa_col
                    name = [
                        data_cols[ind]["column_name"]
                        for ind in data_cols
                        if data_cols[ind]["deviceId"] == qa_cols[index]["deviceId"]
                    ][0]
                    qa_cols[index]["data_name"] = name
                    columns.update(qa_cols)

            col_names = [columns[i]["column_name"] for i in list(columns)]
            ind_names = [indices[i]["column_name"] for i in list(indices)]

            # do this in steps in case we are dropping QA columns
            df = pd.DataFrame(feed["data"])
            icolumns_to_keep = list(indices) + list(columns)
            df = df[icolumns_to_keep]
            df.columns = ind_names + col_names
            df.set_index(ind_names, inplace=True)

            # nan data for which QARTOD flags shouldn't be included
            if isinstance(qartod, (str, list)):
                if isinstance(qartod, str):
                    qartod = [qartod]

                for ind in qa_cols:
                    data_name = qa_cols[ind]["data_name"]  # data column name
                    qa_name = qa_cols[ind]["column_name"]  # qa column name

                    for qa in qartod:
                        df.loc[df[qa_name] != qa, data_name] = pd.NA

                # drop qartod columns
                df.drop(labels=qa_name, axis=1, inplace=True)

            dfs.append(df)

        df = dfs[0]

        # this gets different and I think better results than dfs[0].join(dfs[1:], how="outer", sort=True)
        # even though they should probably return the same thing.
        for i in range(1, len(dfs)):
            df = df.join(dfs[i], how="outer", sort=True)

        return df

    @property
    def data_urls(self):
        """Prepare to load in data by getting data_urls.

        For V1 sources there will be a data_url per parameterGroupId but not for V2 sources.
        """

        if not hasattr(self, "_data_urls"):

            # get extended metadata which we need both for reading the data and as metadata
            result = response_from_url(make_search_docs_url(uuid=self.uuid))[0]
            self.metadata.update(load_metadata("sensor_station", result))

            start_time = self.start_time or self.metadata["minTime"]
            end_time = self.end_time or self.metadata["maxTime"]

            filters = self.get_filters()
            self._data_urls = [
                make_data_url(
                    filter, start_time, end_time, self.binned, self.bin_interval
                )
                for filter in filters
            ]
        return self._data_urls

    def _load(self):
        """How to load in a specific station once you know it by uuid"""

        dfs = [self._load_to_dataframe(url) for url in self.data_urls]

        df = dfs[0]
        # this gets different and I think better results than dfs[0].join(dfs[1:], how="outer", sort=True)
        # even though they should probably return the same thing.
        for i in range(1, len(dfs)):
            df = df.join(dfs[i], how="outer", sort=True)

        self._dataframe = df

    def _get_schema(self):
        """get schema"""
        if self._dataframe is None:
            # TODO: could do partial read with chunksize to get likely schema from
            # first few records, rather than loading the whole thing
            self._load()
        return base.Schema(
            datashape=None,
            dtype=self._dataframe.dtypes,
            shape=self._dataframe.shape,
            npartitions=1,
            extra_metadata={},
        )

    def _get_partition(self, _):
        """get partition"""
        if self._dataframe is None:
            self._load_metadata()
        return self._dataframe

    def read(self):
        """read data in"""
        return self._get_partition(None)

    def _close(self):
        """close source"""
        self._dataframe = None
