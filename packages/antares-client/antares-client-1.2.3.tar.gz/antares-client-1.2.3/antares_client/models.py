from collections import defaultdict
from datetime import datetime
from typing import List, Optional

import astropy.timeseries
import pandas as pd
from astropy.coordinates import SkyCoord

from ._api.api import _get_resource, _list_resources
from ._api.schemas import _AlertSchema, _CatalogEntrySchema, _LocusSchema
from .config import config
from .utils import mjd_to_datetime


class Alert:
    """
    An ANTARES alert represents a single visit/observation of an astronomical object.

    Parameters
    ----------
    alert_id: str
        ANTARES ID for this alert.
    mjd: float
        Modified julian date of the alert.
    properties: dict
        Arbitrary, survey-specific properties associated with this alert.

    Attributes
    ----------
    alert_id: str
        ANTARES ID for this alert.
    mjd: float
        Modified julian date of the alert.
    properties: dict
        Arbitrary, survey-specific properties associated with this alert.

    """

    def __init__(self, alert_id: str, mjd: float, processed_at: datetime, properties: dict, **_):
        self.alert_id = alert_id
        self.mjd = mjd
        self.processed_at = processed_at
        self.properties = properties


class Locus:
    """
    An ANTARES locus is a collection of metadata describing a single astronomical
    object.

    Parameters
    ----------
    locus_id: str
        ANTARES ID for this object.
    ra: float
        Right ascension of the centroid of alert history.
    dec: float
        Declination of the centroid of alert history.
    properties: dict
        A dictionary of ANTARES- and user-generated properties that are updated every
        time there is activity on this locus (e.g. a new alert).
    tags: List[str]
        A list of strings that are added to this locus by ANTARES- and user-submitted
        filters that run against the real-time alert stream.
    alerts: Optional[List[Alert]]
        A list of alerts that are associated with this locus. If `None`, the alerts
        will be loaded on first access from the ANTARES HTTP API.
    catalogs: Optional[List[str]]
        Names of catalogs that this locus has been associated with.
    catalog_objects: Optional[List[dict]]
        A list of catalog objects that are associated with this locus. If `None`, they
        will be loaded on first access from the ANTARES HTTP API.
    lightcurve: Optional[pd.DataFrame]
        Data frame representation of a subset of normalized alert properties. If `None`
        it will be loaded on first access from the ANTARES HTTP API.
    watch_list_ids: Optional[List[str]]
        A list of IDs corresponding to user-submitted regional watch lists.
    watch_object_ids: Optional[List[str]]
        A list of IDs corresponding to user-submitted regional watch list objects.

    Attributes
    ----------
    locus_id: str
        ANTARES ID for this object.
    ra: float
        Right ascension of the centroid of alert history.
    dec: float
        Declination of the centroid of alert history.
    properties: dict
        A dictionary of ANTARES- and user-generated properties that are updated every
        time there is activity on this locus (e.g. a new alert).
    tags: List[str]
        A list of strings that are added to this locus by ANTARES- and user-submitted
        filters that run against the real-time alert stream.
    catalogs: List[str]
        Names of catalogs that this locus has been associated with.
    watch_list_ids: List[str]
        A list of IDs corresponding to user-submitted regional watch lists.
    watch_object_ids: List[str]
        A list of IDs corresponding to user-submitted regional watch list objects.

    Notes
    -----
    Instances of this class lazy-load a few of their attributes from the ANTARES API.
    These attributes are: `alerts`, `catalog_objects` and `lightcurve`.

    """

    def __init__(
        self,
        locus_id: str,
        ra: float,
        dec: float,
        properties: dict,
        tags: List[str],
        alerts: Optional[List[Alert]] = None,
        catalogs: Optional[List[str]] = None,
        catalog_objects: Optional[List[dict]] = None,
        lightcurve: Optional[pd.DataFrame] = None,
        watch_list_ids: Optional[List[str]] = None,
        watch_object_ids: Optional[List[str]] = None,
        **_,
    ):
        self.locus_id = locus_id
        self.ra = ra
        self.dec = dec
        self.properties = properties
        self.tags = tags
        self.catalogs = catalogs
        if self.catalogs is None:
            self.catalogs = []
        self.watch_list_ids = watch_list_ids
        if self.watch_list_ids is None:
            self.watch_list_ids = []
        self.watch_object_ids = watch_object_ids
        if self.watch_object_ids is None:
            self.watch_object_ids = []
        self._alerts = alerts
        self._catalog_objects = catalog_objects
        self._lightcurve = lightcurve
        self._timeseries = None
        self._coordinates = None

    def _fetch_alerts(self) -> List[Alert]:
        alerts = _list_resources(
            config["ANTARES_API_BASE_URL"]
            + "/".join(("loci", self.locus_id, "alerts")),
            _AlertSchema,
        )
        return list(alerts)

    def _fetch_lightcurve(self) -> pd.DataFrame:
        locus = _get_resource(
            config["ANTARES_API_BASE_URL"] + "/".join(("loci", self.locus_id)),
            _LocusSchema,
        )
        return locus.lightcurve

    def _fetch_catalog_objects(self) -> dict:
        catalog_matches = _list_resources(
            config["ANTARES_API_BASE_URL"]
            + "/".join(("loci", self.locus_id, "catalog-matches")),
            _CatalogEntrySchema,
        )
        catalog_matches = list(catalog_matches)
        catalog_objects = defaultdict(list)
        for match in catalog_matches:
            catalog_name = match["catalog_entry_id"].split(":")[0]
            catalog_objects[catalog_name].append(match["properties"])
        return catalog_objects

    @property
    def timeseries(self) -> astropy.timeseries.TimeSeries:
        """
        This `TimeSeries` contains all of the historical alert data associated with
        this object.
        """
        if self._timeseries is None:
            self._timeseries = astropy.timeseries.TimeSeries(
                data=[alert.properties for alert in self.alerts],
                time=[mjd_to_datetime(alert.mjd) for alert in self.alerts],
            )
        return self._timeseries

    @timeseries.setter
    def timeseries(self, value) -> None:
        self._timeseries = value

    @property
    def alerts(self) -> List[Alert]:
        """A list of alerts that are associated with this locus."""
        if self._alerts is None:
            self._alerts = self._fetch_alerts()
        return self._alerts

    @alerts.setter
    def alerts(self, value) -> None:
        self._alerts = value

    @property
    def catalog_objects(self) -> dict:
        """
        A dictionary of catalog objects that are associated with this locus. It has a
        structure like::

            {
                "<catalog_name">: [
                    { **<catalog_object_properties> },
                    { **<catalog_object_properties> },
                    ...
                ],
                ...
            }

        """
        if self._catalog_objects is None:
            self._catalog_objects = self._fetch_catalog_objects()
        return self._catalog_objects

    @catalog_objects.setter
    def catalog_objects(self, value) -> None:
        self._catalog_objects = value

    @property
    def lightcurve(self) -> pd.DataFrame:
        """Data frame representation of a subset of normalized alert properties."""
        if self._lightcurve is None:
            self._lightcurve = self._fetch_lightcurve()
        return self._lightcurve

    @lightcurve.setter
    def lightcurve(self, value) -> None:
        self._lightcurve = value

    @property
    def coordinates(self) -> SkyCoord:
        """Centroid of the locus as an AstroPy SkyCoord object."""
        if self._coordinates is None:
            self._coordinates = SkyCoord(f"{self.ra}d {self.dec}d")
        return self._coordinates
