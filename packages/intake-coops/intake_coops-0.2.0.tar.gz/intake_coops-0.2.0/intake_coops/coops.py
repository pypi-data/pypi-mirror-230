"""
Source for CO-OPS data.
"""

import cf_pandas  # noqa: F401
import noaa_coops as nc
import numpy as np
import pandas as pd
import xarray as xr

from intake.source import base

from . import __version__


class COOPSDataframeSource(base.DataSource):
    """
    Parameters
    ----------
    stationid : str
        CO-OPS station id.

    Returns
    -------
    Dataframe
    """

    name = "coops-dataframe"
    version = __version__
    container = "dataframe"
    partition_access = True

    def __init__(self, stationid: str, metadata={}):

        self._dataframe = None
        self.stationid = stationid
        # self.metadata = metadata
        self.s = nc.Station(self.stationid)

        super(COOPSDataframeSource, self).__init__(metadata=metadata)

    def _get_schema(self) -> base.Schema:
        if self._dataframe is None:
            # TODO: could do partial read with chunksize to get likely schema from
            # first few records, rather than loading the whole thing
            self._load()
            self._dataset_metadata = self._get_dataset_metadata()
        # make type checker happy
        assert self._dataframe is not None
        return base.Schema(
            datashape=None,
            dtype=self._dataframe.dtypes,
            shape=self._dataframe.shape,
            npartitions=1,
            extra_metadata=self._dataset_metadata,
        )

    def _get_partition(self) -> pd.DataFrame:
        if self._dataframe is None:
            self._load_metadata()
        return self._dataframe

    def read(self) -> pd.DataFrame:
        """Return the dataframe from ERDDAP"""
        return self._get_partition()

    def _load(self):
        """How to load in a specific station once you know it by dataset_id"""

        begin_date = pd.Timestamp(self.s.deployed).strftime("%Y%m%d")
        end_date = pd.Timestamp(self.s.retrieved).strftime("%Y%m%d")

        dfs = []
        for bin in self.s.bins["bins"]:
            depth = bin["depth"]
            num = bin["num"]
            df = self.s.get_data(
                begin_date=begin_date,
                end_date=end_date,
                product="currents",
                bin_num=num,
            )
            df["depth"] = depth
            dfs.append(df)
        self._dataframe = pd.concat(dfs)

    def _get_dataset_metadata(self):
        """Load metadata once data is loaded."""
        # self._load()
        # metadata = {}
        metadata = self.s.deployments
        metadata.update(self.s.lat_lon)
        metadata.update(
            {
                "name": self.s.name,
                "observe_dst": self.s.observe_dst,
                "project": self.s.project,
                "project_type": self.s.project_type,
                "timezone_offset": self.s.timezone_offset,
                "units": self.s.units,
            }
        )
        return metadata

    def _close(self):
        self._dataframe = None


class COOPSXarraySource(COOPSDataframeSource):
    """Converts returned DataFrame into Dataset

    which for ADCP data is more appropriate.

    Returns
    -------
    Dataset
    """

    name = "coops-xarray"
    version = __version__
    container = "xarray"
    partition_access = True

    def __init__(self, stationid, process_adcp: bool = False, metadata={}):
        """Initialize."""

        self._ds = None
        # self.stationid = stationid
        # self.metadata = metadata
        self._process_adcp = process_adcp

        self.source = COOPSDataframeSource(stationid, metadata)

        # self.s = nc.Station(self.stationid)

        super(COOPSXarraySource, self).__init__(stationid=stationid, metadata=metadata)

    def _load(self):
        """Read as DataFrame but convert to Dataset."""
        df = self.source.read()
        inds = [df.cf["T"].name, df.cf["Z"].name]
        self._ds = (
            df.reset_index()
            .set_index(inds)
            .sort_index()
            .pivot_table(index=inds)
            .to_xarray()
        )
        self._ds["t"].attrs = {"standard_name": "time"}
        self._ds["depth"].attrs = {
            "standard_name": "depth",
            "axis": "Z",
        }
        self._ds["longitude"] = self.metadata["minLongitude"]
        self._ds["longitude"].attrs = {"standard_name": "longitude"}
        self._ds["latitude"] = self.metadata["minLatitude"]
        self._ds["latitude"].attrs = {"standard_name": "latitude"}
        self._ds = self._ds.assign_coords(
            {"longitude": self._ds["longitude"], "latitude": self._ds["latitude"]}
        )
        if self._process_adcp:
            self.process_adcp()

    def process_adcp(self):
        """Process ADCP data.

        Returns
        -------
        Dataset
            With u and v, ualong and vacross, and subtidal versions ualong_subtidal, vacross_subtidal
        """
        theta = self.source.metadata["flood_direction_degrees"]
        self._ds["u"] = (
            np.cos(np.deg2rad(self._ds.cf["dir"])) * self._ds.cf["speed"] / 100
        )
        self._ds["v"] = (
            np.sin(np.deg2rad(self._ds.cf["dir"])) * self._ds.cf["speed"] / 100
        )
        self._ds["ualong"] = self._ds["u"] * np.cos(np.deg2rad(theta)) + self._ds[
            "v"
        ] * np.sin(np.deg2rad(theta))
        self._ds["vacross"] = -self._ds["u"] * np.sin(np.deg2rad(theta)) + self._ds[
            "v"
        ] * np.cos(np.deg2rad(theta))
        self._ds["s"] /= 100
        self._ds["s"].attrs = {"standard_name": "sea_water_speed", "units": "m s-1"}
        self._ds["d"].attrs = {
            "standard_name": "sea_water_velocity_to_direction",
            "units": "degree",
        }
        self._ds["u"].attrs = {
            "standard_name": "eastward_sea_water_velocity",
            "units": "m s-1",
        }
        self._ds["v"].attrs = {
            "standard_name": "northward_sea_water_velocity",
            "units": "m s-1",
        }
        self._ds["ualong"].attrs = {
            "Long name": "Along channel velocity",
            "units": "m s-1",
        }
        self._ds["vacross"].attrs = {
            "Long name": "Across channel velocity",
            "units": "m s-1",
        }

        # calculate subtidal velocities
        self._ds["ualong_subtidal"] = tidal_filter(self._ds["ualong"])
        self._ds["vacross_subtidal"] = tidal_filter(self._ds["vacross"])

    def to_dask(self):
        """Read data."""
        self.read()
        return self._ds

    def read(self):
        """Read data."""
        if self._ds is None:
            # self._load_metadata()
            self._load()
        return self._ds

    def _close(self):
        self._ds = None
        self._schema = None


class plfilt(object):
    """
    pl33 filter class, to remove tides and inertial motions from timeseries

    Examples
    --------

    >>> pl33 = plfilt(dt=4.0)   # 33 hr filter

    >>> pl33d = plfilt(dt=4.0, cutoff_period=72.0)  # 3 day filter

    dt is the time resolution of the timeseries to be filtered in hours.  Default dt=1
    cutoff_period defines the timescales to low pass filter. Default cutoff_period=33.0
    Calling the class instance can have two forms:

    >>> uf = pl33(u)   # returns a filtered timeseries, uf.  Half the filter length is
                       # removed from each end of the timeseries

    >>> uf, tf = pl33(u, t)  # returns a filtered timeseries, uf, plus a new time
                             # variable over the valid range of the filtered timeseries.

    Notes
    -----
    Taken from Rob Hetland's octant package.
    """

    _pl33 = np.array(
        [
            -0.00027,
            -0.00114,
            -0.00211,
            -0.00317,
            -0.00427,
            -0.00537,
            -0.00641,
            -0.00735,
            -0.00811,
            -0.00864,
            -0.00887,
            -0.00872,
            -0.00816,
            -0.00714,
            -0.0056,
            -0.00355,
            -0.00097,
            0.00213,
            0.00574,
            0.0098,
            0.01425,
            0.01902,
            0.024,
            0.02911,
            0.03423,
            0.03923,
            0.04399,
            0.04842,
            0.05237,
            0.05576,
            0.0585,
            0.06051,
            0.06174,
            0.06215,
            0.06174,
            0.06051,
            0.0585,
            0.05576,
            0.05237,
            0.04842,
            0.04399,
            0.03923,
            0.03423,
            0.02911,
            0.024,
            0.01902,
            0.01425,
            0.0098,
            0.00574,
            0.00213,
            -0.00097,
            -0.00355,
            -0.0056,
            -0.00714,
            -0.00816,
            -0.00872,
            -0.00887,
            -0.00864,
            -0.00811,
            -0.00735,
            -0.00641,
            -0.00537,
            -0.00427,
            -0.00317,
            -0.00211,
            -0.00114,
            -0.00027,
        ],
        dtype="d",
    )

    _dt = np.linspace(-33, 33, 67)

    def __init__(self, dt=1.0, cutoff_period=33.0):
        """Initialize."""

        if np.isscalar(dt):
            self.dt = float(dt) * (33.0 / cutoff_period)
        else:
            self.dt = np.diff(dt).mean() * (33.0 / cutoff_period)

        filter_time = np.arange(0.0, 33.0, self.dt, dtype="d")
        self.Nt = len(filter_time)
        self.filter_time = np.hstack((-filter_time[-1:0:-1], filter_time))

        self.pl33 = np.interp(self.filter_time, self._dt, self._pl33)
        self.pl33 /= self.pl33.sum()

    def __call__(self, u, t=None, mode="valid"):
        """Do the filtering."""
        uf = np.convolve(u, self.pl33, mode=mode)
        if t is None:
            return uf
        else:
            tf = t[self.Nt - 1 : -self.Nt + 1]
            return uf, tf


def tidal_filter(da_to_filter):
    """Filter DataArray for tides."""

    tkey, zkey = da_to_filter.dims

    # set up tidal filter
    dt = da_to_filter[tkey][1] - da_to_filter[tkey][0]
    dt = float(dt / 1e9) / 3600  # convert nanoseconds to hours
    pl33 = plfilt(dt=dt)

    ufiltered = []
    # loop over depths
    for depth in da_to_filter[zkey]:
        # can't have any nan's, so fill signal first
        u_in = da_to_filter.sel(depth=depth).interpolate_na(dim=tkey, method="linear")
        ufiltered_out, t_out = pl33(u_in, da_to_filter[tkey])
        ufiltered.append(ufiltered_out)

    ufiltered = np.asarray(ufiltered).T
    attrs = {
        key: f"{value}, subtidal"
        for key, value in da_to_filter.attrs.items()
        if key != "units"
    }
    u = xr.full_like(da_to_filter, np.nan)
    u[pl33.Nt - 1 : -pl33.Nt + 1, :] = ufiltered
    u.attrs = attrs
    return u
