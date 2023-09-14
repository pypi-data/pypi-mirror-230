from unittest import mock

import astropy.coordinates
import pytest

from antares_client import search
from antares_client.models import Locus
from antares_client.exceptions import AntaresException


def test_search(mock_api):
    loci = list(search.search({}))
    assert len(loci)
    assert type(loci[0]) is Locus
    assert "ANT2019ae" in [locus.locus_id for locus in loci]
    assert "ANT2019ai" in [locus.locus_id for locus in loci]


def test_get_by_id(mock_api):
    locus = search.get_by_id("ANT2019ae")
    assert type(locus) is Locus
    assert locus.locus_id == "ANT2019ae"


def test_get_by_id_fetches_alerts(mock_api):
    locus = search.get_by_id("ANT2019ae")
    assert len(locus.alerts)


def test_get_by_id_constructs_timeseries(mock_api):
    locus = search.get_by_id("ANT2019ae")
    assert type(locus) is Locus
    assert locus.locus_id == "ANT2019ae"


def test_get_by_id_404_returns_none(mock_api_404):
    assert search.get_by_id("cant_find_me") is None


def test_get_by_id_500_raises_error(mock_api_500):
    with pytest.raises(AntaresException) as exception:
        search.get_by_id("raise_an_error")
    assert "errors" in exception.value.args[0]
    assert exception.value.args[0]["errors"][0]["status"] == 500


@pytest.mark.parametrize(
    "input_radius,expected",
    [
        (astropy.coordinates.Angle(".002 deg"), "0.002 degree"),
        (astropy.coordinates.Angle("1 arcsec"), "0.000277778 degree"),
    ],
)
def test_cone_search_formats_radius(input_radius, expected):
    center = astropy.coordinates.SkyCoord("0d 0d")
    with mock.patch("antares_client.search.search") as mock_search:
        search.cone_search(center, input_radius)
        mock_search.assert_called_once()
        query = mock_search.call_args[0][0]
        assert query["query"]["bool"]["filter"]["sky_distance"]["distance"] == expected


@pytest.mark.parametrize(
    "input_center,expected",
    [
        (astropy.coordinates.SkyCoord("5d45m22s 2h22m10s"), "5.75611 35.5417"),
    ],
)
def test_cone_search_formats_center(input_center, expected):
    radius = astropy.coordinates.Angle("1 arcsec")
    with mock.patch("antares_client.search.search") as mock_search:
        search.cone_search(input_center, radius)
        mock_search.assert_called_once()
        query = mock_search.call_args[0][0]
        assert (
            query["query"]["bool"]["filter"]["sky_distance"]["htm16"]["center"]
            == expected
        )


def test_cone_search_throws_value_error_if_radius_not_astropy_angle():
    pass


def test_cone_search_throws_value_error_if_center_not_astropy_sky_coord():
    pass


def test_cone_search_throws_value_error_if_radius_greater_than_one_degree():
    pass
