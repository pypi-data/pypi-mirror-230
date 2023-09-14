import marshmallow
from marshmallow import post_load
from marshmallow_jsonapi import fields, Schema

from .fields import _Lightcurve


class _ClientConfigStreamingSchema(Schema):
    class Meta:
        type_ = "client_config_streaming"
        unknown = marshmallow.EXCLUDE

    id = fields.String()
    type = fields.String()
    options = fields.Dict()


class _AlertSchema(Schema):
    class Meta:
        type_ = "alert"
        unknown = marshmallow.EXCLUDE

    id = fields.String(attribute="alert_id")
    properties = fields.Dict()
    processed_at = fields.DateTime()
    mjd = fields.Float()
    resource_meta = fields.ResourceMeta()
    document_meta = fields.DocumentMeta()

    @post_load
    def make_alert(self, data: dict, **_):
        from ..models import Alert

        return Alert(**data)


class _CatalogEntrySchema(Schema):
    class Meta:
        type_ = "catalog_entry"
        unknown = marshmallow.EXCLUDE

    id = fields.Str(attribute="catalog_entry_id")
    object_id = fields.Str()
    object_name = fields.Str()
    name = fields.Str()
    ra = fields.Float()
    dec = fields.Float()
    properties = fields.Dict()
    catalog = fields.Relationship()
    resource_meta = fields.ResourceMeta()
    document_meta = fields.DocumentMeta()


class _LocusSchema(Schema):
    class Meta:
        type_ = "locus"
        unknown = marshmallow.EXCLUDE

    id = fields.Str(attribute="locus_id")
    htm16 = fields.Int()
    ra = fields.Float()
    dec = fields.Float()
    properties = fields.Dict()
    lightcurve = _Lightcurve()
    alerts = fields.Relationship()
    tags = fields.List(fields.Str())
    catalogs = fields.List(fields.Str())
    catalog_matches = fields.List(fields.Dict())
    resource_meta = fields.ResourceMeta()
    document_meta = fields.DocumentMeta()

    @post_load
    def make_locus(self, data: dict, **_):
        from ..models import Locus

        return Locus(**data)


class _LocusListingSchema(Schema):
    class Meta:
        type_ = "locus_listing"
        unknown = marshmallow.EXCLUDE

    id = fields.Str(attribute="locus_id")
    htm16 = fields.Int()
    ra = fields.Float()
    dec = fields.Float()
    properties = fields.Dict()
    locus = fields.Relationship()
    alerts = fields.Relationship()
    tags = fields.List(fields.Str())
    catalogs = fields.List(fields.Str())
    resource_meta = fields.ResourceMeta()
    document_meta = fields.DocumentMeta()

    @post_load
    def make_locus(self, data: dict, **_):
        from ..models import Locus

        return Locus(**data)
