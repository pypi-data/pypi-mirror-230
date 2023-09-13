"""
Set up a catalog for NOAA CO-OPS assets.
"""


from intake.catalog.base import Catalog
from intake.catalog.local import LocalCatalogEntry

from . import __version__
from .coops import COOPSDataframeSource, COOPSXarraySource


class COOPSCatalog(Catalog):
    """
    Makes data sources out of all datasets for a given AXDS data type.

    Have this cover all data types for now, then split out.
    """

    name = "coops_cat"
    version = __version__

    def __init__(
        self,
        station_list,
        # verbose: bool = False,
        process_adcp: bool = False,
        name: str = "catalog",
        description: str = "Catalog of NOAA CO-OPS assets.",
        metadata: dict = None,
        include_source_metadata: bool = True,
        ttl: int = 86400,
        **kwargs,
    ):
        """Initialize a NOAA CO-OPS Catalog.

        Parameters
        ----------
        process_adcp : bool, False
            If True, for ADCP stations, calculate and save to Dataset along- and across-channel velocities.
        verbose : bool, optional
            Set to True for helpful information.
        ttl : int, optional
            Time to live for catalog (in seconds). How long before force-reloading catalog. Set to None to not do this. Currently default is set to a large number because the available version of intake does not have a change to accept None.
        name : str, optional
            Name for catalog.
        description : str, optional
            Description for catalog.
        metadata : dict, optional
            Metadata for catalog.
        kwargs:
            Other input arguments are passed to the intake Catalog class. They can includegetenv, getshell, persist_mode, storage_options, and user_parameters, in addition to some that are surfaced directly in this class.
        """

        self.station_list = station_list
        self.include_source_metadata = include_source_metadata
        self._process_adcp = process_adcp

        # Put together catalog-level stuff
        metadata = metadata or {}
        # metadata["station_list"] = self.station_list

        super(COOPSCatalog, self).__init__(
            **kwargs, ttl=ttl, name=name, description=description, metadata=metadata
        )

    def _load(self):
        """Find all dataset ids and create catalog."""

        self._entries = {}

        for station_id in self.station_list:

            # if self.verbose:
            #     print(f"Dataset ID: {dataset_id}")

            # description = f"AXDS dataset_id {dataset_id} of datatype {self.datatype}"

            plugin = COOPSXarraySource

            args = {
                "stationid": station_id,
                "process_adcp": self._process_adcp,
            }

            if self.include_source_metadata:
                metadata = COOPSDataframeSource(station_id)._get_dataset_metadata()
            else:
                metadata = {}

            entry = LocalCatalogEntry(
                name=station_id,
                description="",  # description,
                driver=plugin,
                direct_access="allow",
                args=args,
                metadata=metadata,
                # True,
                # args,
                # {},
                # {},
                # {},
                # "",
                # getenv=False,
                # getshell=False,
            )

            self._entries[station_id] = entry
