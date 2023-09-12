# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from qgis.core import (
    QgsCoordinateReferenceSystem
    , QgsCoordinateTransform
    , QgsWkbTypes
    ,QgsProject)
from PyQt5.QtCore import QDate, QDateTime
import assetic
import six
import json

from ..config import Config

# TODO - search filtering?
# let's access the 'countries' layer
# layer = QgsProject.instance().mapLayersByName('countries')[0]
# let's filter for countries that begin with Z, then get their features
# query = '"name" LIKE \'Z%\''
# features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))


class LayerTools(object):
    """
    Class to manage processes that relate to a GIS layer
    """

    def __init__(self, layerconfig=None):

        self.config = Config()
        self.commontools = self.config.commontools
        if layerconfig is None:
            self._layerconfig = self.config.layerconfig
        else:
            self._layerconfig = layerconfig
        self._assetconfig = self._layerconfig.assetconfig
        self.asseticsdk = self.config.asseticsdk

        # instantiate assetic.AssetTools
        self.assettools = assetic.AssetTools(self.asseticsdk.client)

        # get logfile name to help user find it
        self.logfilename = ""
        for h in self.asseticsdk.logger.handlers:
            try:
                self.logfilename = h.baseFilename
            except:
                pass

    def get_layer_config(self, lyr, purpose):
        """
        For the given layer get the config settings. Depending on purpose not
        all config is required, so only get relevant config
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param purpose: one of 'create','update','delete','display'
        """
        lyr_config_list = [j for i, j in enumerate(
            self._assetconfig) if j["layer"] == lyr.name()]
        if len(lyr_config_list) == 0:
            if purpose not in ["delete"]:
                msg = "No configuration for layer {0}".format(lyr.name())
                self.commontools.new_message(msg)
            return None, None, None
        lyr_config = lyr_config_list[0]

        # create a list of the fields in the layer to compare config with
        actuallayerflds = [fld.name() for fld in lyr.fields()]
        # include calculated fields
        actuallayerflds.append("_geometry_length_")
        actuallayerflds.append("_geometry_area_")

        if purpose in ["create", "update"]:
            # from config file build list of qgis fields to query
            fields = list(six.viewvalues(lyr_config["corefields"]))
            if fields is None:
                self.commontools.new_message(
                    "missing 'corefields' configuration for layer {0}".format(
                        lyr.name()))
                return None, None, None
            if "attributefields" in lyr_config:
                attfields = list(six.viewvalues(lyr_config["attributefields"]))
                if attfields is not None:
                    fields = fields + attfields

            for component in lyr_config["components"]:
                compflds = list(six.viewvalues(component["attributes"]))
                if compflds:
                    fields = fields + compflds
                for dimension in component["dimensions"]:
                    dimflds = list(six.viewvalues(dimension["attributes"]))
                    if dimflds:
                        fields = fields + dimflds
            if "addressfields" in lyr_config:
                addrfields = list(six.viewvalues(lyr_config["addressfields"]))
                if addrfields is not None:
                    fields = fields + addrfields

            # check fields from config are in layer
            if fields is not None:
                # create unique list (may not be unique if components or
                # dimensions config use same field for common elements
                fields = list(set(fields))

                # loop through list and check fields are in layer
                for configfield in fields:
                    if configfield not in actuallayerflds:
                        self.commontools.new_message(
                            "Field [{0}] is defined in configuration but is "
                            "not in layer {1}, check logfile for field list"
                            "".format(configfield, lyr.name()))
                        self.commontools.new_message(
                            "Fields in layer {0} are: {1}".format(
                                lyr.name(), actuallayerflds))
                        return None, None, None
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            if "id" in lyr_config["corefields"]:
                idfield = lyr_config["corefields"]["id"]
            else:
                if "asset_id" in lyr_config["corefields"]:
                    idfield = lyr_config["corefields"]["asset_id"]
                else:
                    self.commontools.new_message(
                        "Asset ID and/or Asset GUID field must be defined for "
                        "layer {0}".format(lyr.name()))
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            self.commontools.new_message(
                "Asset ID Field [{0}] is defined in configuration but is not"
                " in layer {1}, check logfile for field list".format(
                    idfield, lyr.name()))
            self.commontools.new_message("Fields in layer {0} are: {1}".format(
                lyr.name(), actuallayerflds))
            return None, None, None

        return lyr_config, fields, idfield

    def create_assets_for_layer(self, lyr):
        """
        For the given layer create new assets for the selected features only if
        features have no assetic guid.
        :param lyr: is the layer to process (not layer name)
        """
        results = dict()
        results["pass_cnt"] = 0
        results["fail_cnt"] = 0
        results["ignore_cnt"] = 0
        results["partial_cnt"] = 0

        # get configuration for layer
        lyr_config, fields, idfield = self.get_layer_config(lyr, "create")
        if lyr_config is None:
            return results

        # self.commontools.new_message("Selected Features count: {0}".format(
        #    lyr.selectedFeatureCount()))

        # self.commontools.new_message("Total features count : {0}".format(
        #    lyr.featureCount()))

        # TODO - add features to sink so report on changed records ?

        cnt = 1.0
        for feat in lyr.selectedFeatures():
            if self.commontools.is_cancelled:
                # user initiated cancel
                self.commontools.new_message("Execution cancelled")
                return results
            self.commontools.new_message(
                "Creating Assets for layer {0}.\nProcessing "
                "feature {1} of {2}".format(
                    lyr.name(), int(cnt), lyr.selectedFeatureCount()))

            # create new asset
            result = self._new_asset(feat, lyr_config, fields, lyr.crs(), lyr)
            if result == 0:
                results["pass_cnt"] += 1
            elif result == 1:
                results["fail_cnt"] += 1
            elif result == 2:
                results["ignore_cnt"] += 1
            elif result == 3:
                results["partial_cnt"] += 1
            cnt += 1

        self.commontools.new_message("Processing complete")

        return results

    def _new_asset(self, feat, lyr_config, fields, layer_crs, layer):
        """
        Create a new asset for the given search result row
        :param feat: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: 0 if success, 1 if error, 2 if skip (existing),
        3 if partial success such as asset created but component not
        """
        results = {
            "success": 0
            , "error": 1
            , "skip": 2
            , "partial": 3
        }

        complete_asset_obj = self.get_asset_obj_for_feature(
            feat, lyr_config, fields)
        # alias core fields for readability
        corefields = lyr_config["corefields"]

        # verify it actually needs to be created
        if "id" in corefields and corefields["id"] in fields:
            if not complete_asset_obj.asset_representation.id:
                # guid field exists in ArcMap and is empty
                newasset = True
            else:
                # guid id populated, must be existing asset
                newasset = False
        else:
            # guid not used, what about asset id?
            if "asset_id" in corefields and corefields["asset_id"] in fields:
                # asset id field exists in Arcmap
                if not complete_asset_obj.asset_representation.asset_id:
                    # asset id is null, must be new asset
                    newasset = True
                else:
                    # test assetic for the asset id.
                    # Perhaps user is not using guid
                    # and is manually assigning asset id.
                    chk = self.assettools.get_asset(
                        complete_asset_obj.asset_representation.asset_id)
                    if not chk:
                        newasset = True
                    else:
                        # asset id already exists.  Not a new asset
                        newasset = False
            else:
                # there is no field in ArcMap representing either GUID or
                # Asset ID, so can't proceed.
                self.commontools.new_message(
                    "Asset not created because there is no configuration "
                    "setting for <id> or <asset_id> or the field is not in "
                    "the layer")
                return results["error"]
        if not newasset:
            self.commontools.new_message(
                "Asset not created because it already has the following "
                "values: Asset ID={0},Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return results["skip"]

        # set status
        complete_asset_obj.asset_representation.status = \
            lyr_config["creation_status"]
        # Create new asset
        response = self.assettools.create_complete_asset(complete_asset_obj)
        if response is None:
            msg = "Asset Not Created - Check log"
            self.commontools.new_message(msg)
            return results["error"]
        # apply asset guid and/or assetid
        layer.startEditing()
        if "id" in corefields:
            if feat.fieldNameIndex(corefields["id"]) >= 0:
                layer.changeAttributeValue(
                    feat.id(), feat.fieldNameIndex(corefields["id"])
                    , response.asset_representation.id)
        if "asset_id" in corefields:
            if feat.fieldNameIndex(corefields["asset_id"]) >= 0:
                layer.changeAttributeValue(
                    feat.id(), feat.fieldNameIndex(corefields["asset_id"])
                    , response.asset_representation.asset_id)
        # apply component id
        for component_dim_obj in response.components:
            for component_config in lyr_config["components"]:
                component_type = None
                if "component_type" in component_config["attributes"]:
                    component_type = component_config["attributes"][
                        "component_type"]
                elif "component_type" in component_config["defaults"]:
                    component_type = component_config["defaults"][
                        "component_type"]

                if "id" in component_config["attributes"] and component_type \
                        == component_dim_obj.component_representation \
                        .component_type:
                    if feat.fieldNameIndex(
                            component_config["attributes"]["id"]) >= 0:
                        layer.changeAttributeValue(
                            feat.id(),
                            feat.fieldNameIndex(
                                component_config["attributes"]["id"])
                            , component_dim_obj.component_representation.id)
        layer.commitChanges()

        # Now check config and update Assetic with spatial data and/or address
        addr = None
        geojson = None
        if len(lyr_config["addressfields"]) > 0 \
                or len(lyr_config["addressdefaults"]) > 0:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields from the attribute fields of the feature
            for k, v in six.iteritems(lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    val = None
                    try:
                        val = self.sanitise_attribute(feat[v])
                    except Exception:
                        pass
                    setattr(addr, k, val)
            # get address defaults
            for k, v in six.iteritems(lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)
        if lyr_config["upload_feature"]:
            geojson = self.get_geom_geojson(layer_crs, feat.geometry())
        if addr or geojson:
            chk = self.assettools.set_asset_address_spatial(
                response.asset_representation.id, geojson, addr)
            if chk > 0:
                return results["partial"]
        return results["success"]

    def _update_asset(self, row, lyr_config, fields):
        """
        Update an existing asset for the given arcmap row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """
        #TODO - this method is incmplete.  It is a copy of the ESRI equivalent
        complete_asset_obj = self.get_asset_obj_for_feature(row, lyr_config,
                                                            fields)

        # make sure we have an asset id to use
        if not complete_asset_obj.asset_representation.id:
            # guid not used, what about asset id?
            if complete_asset_obj.asset_representation.asset_id:
                # asset id is not null
                # test Assetic for the asset id.
                chk = self.assettools.get_asset(
                    complete_asset_obj.asset_representation.asset_id)
                if chk:
                    # asset_exists = True
                    # set the guid, need it later if doing spatial load
                    complete_asset_obj.asset_representation.id = chk["Id"]

        if not complete_asset_obj.asset_representation.id:
            self.asseticsdk.logger.debug(
                "Asset not updated because it is undefined or not in Assetic. "
                "Asset ID={0}".format(
                    complete_asset_obj.asset_representation.asset_id))
            return False

        if len(complete_asset_obj.components) > 0:
            # have components, assume network measure needed, also assume we
            # don't have Id's for the components which are needed for update
            current_complete_asset = self.assettools.get_complete_asset(
                complete_asset_obj.asset_representation.id, []
                , ["components", "dimensions"])

            for component in complete_asset_obj.components:
                # get the id from the current record, matching on
                # component type
                new_comp = component.component_representation
                for current_comp_rep in current_complete_asset.components:
                    current_comp = current_comp_rep.component_representation
                    if current_comp.component_type == new_comp.component_type \
                            or current_comp.id == new_comp.id:
                        # set the id and name in case they are undefined
                        new_comp.id = current_comp.id
                        new_comp.name = current_comp.name

                        # Look for dimensions and set dimension Id
                        for dimension in component.dimensions:
                            count_matches = 0
                            for current_dim in current_comp_rep.dimensions:
                                # match on id or (nm type and record
                                # type and shape name)
                                if not dimension.id and \
                                        dimension.network_measure_type == \
                                        current_dim.network_measure_type and \
                                        dimension.record_type == \
                                        current_dim.record_type and \
                                        dimension.shape_name == \
                                        current_dim.shape_name:
                                    # set dimension id and component id
                                    dimension.id = current_dim.id
                                    dimension.component_id = new_comp.id
                                    count_matches += 1
                            if not dimension.id or count_matches > 1:
                                # couldn't find unique id. remove
                                component.dimensions.remove(dimension)
                                self.asseticsdk.logger.warning(
                                    "Unable to update dimension for "
                                    "component {0} because new existing and "
                                    "distinct dimension record was "
                                    "found".format(
                                        new_comp.name))
                if not new_comp.id:
                    # couldn't find component - remove
                    complete_asset_obj.components.remove(component)
                    self.asseticsdk.logger.warning(
                        "Unable to update component for asset {0}".format(
                            complete_asset_obj.asset_representation.asset_id
                        ))

        # now execute the update
        chk = self.assettools.update_complete_asset(complete_asset_obj)
        if chk > 0:
            self.commontools.new_message(
                "Error Updating Asset:{0}, Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return False

        # Now check config and update Assetic with spatial data
        if lyr_config["upload_feature"]:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields the attribute fields of the feature
            for k, v in six.iteritems(
                    lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    setattr(addr, k, row[fields.index(v)])
            # get address defaults
            for k, v in six.iteritems(
                    lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)
            geometry = row[fields.index('SHAPE@')]
            centroid = row[fields.index('SHAPE@XY')]
            geojson = self.get_geom_geojson(geometry, centroid)
            chk = self.assettools.set_asset_address_spatial(
                complete_asset_obj.asset_representation.id, geojson, addr)
            if chk > 0:
                self.commontools.new_message(
                    "Error Updating Asset Address/Location:{0}, Asset GUID={1}"
                    "".format(
                        complete_asset_obj.asset_representation.asset_id
                        , complete_asset_obj.asset_representation.id))
                return False
        return True

    def get_asset_obj_for_feature(self, feat, lyr_config, fields):
        """
        Prepare a complete asset for the given feature
        :param feat: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields in the layer
        :returns: assetic.AssetToolsCompleteAssetRepresentation() or None
        """
        # instantiate the complete asset representation to return
        complete_asset_obj = assetic.AssetToolsCompleteAssetRepresentation()

        # create an instance of the complex asset object
        asset = assetic.models.ComplexAssetRepresentation()

        asset.asset_category = lyr_config["asset_category"]

        # build a dict of fields and their value and append dimensions
        atts = dict()
        for fld in fields:
            val = None
            try:
                if feat[fld] and str(feat[fld]).strip() != "":
                    val = self.sanitise_attribute(feat[fld])
            except Exception:
                pass
            atts[fld] = val

        atts["_geometry_length_"] = feat.geometry().length()
        atts["_geometry_area_"] = feat.geometry().area()

        # set core field values from qgis fields
        for k, v in six.iteritems(lyr_config["corefields"]):
            if k in asset.to_dict() and v in atts:
                setattr(asset, k, atts[v])

        # set core field values from defaults
        for k, v in six.iteritems(lyr_config["coredefaults"]):
            if k in asset.to_dict() and str(v).strip() != "":
                setattr(asset, k, v)

        attributes = {}
        # set attributes values from arcmap fields
        if "attributefields" in lyr_config:
            for k, v in six.iteritems(lyr_config["attributefields"]):
                if v in atts:
                    attributes[k] = atts[v]

        # set attribute values from defaults
        for k, v in six.iteritems(lyr_config["attributedefaults"]):
            if str(v).strip() != "":
                attributes[k] = v
        # add the attributes to the asset and the asset to the complete object
        asset.attributes = attributes
        complete_asset_obj.asset_representation = asset

        # create component representations
        for component in lyr_config["components"]:
            comp_tool_rep = assetic.AssetToolsComponentRepresentation()
            comp_tool_rep.component_representation = \
                assetic.ComponentRepresentation()
            for k, v in six.iteritems(component["attributes"]):
                if v in atts:
                    setattr(comp_tool_rep.component_representation, k
                            , atts[v])
            for k, v in six.iteritems(component["defaults"]):
                if k in comp_tool_rep.component_representation.to_dict():
                    setattr(comp_tool_rep.component_representation, k, v)

            # add dimensions to component
            if component["dimensions"] and len(component["dimensions"]) > 0:
                # create an array for the dimensions to be added
                # to the component
                dimlist = list()
                for dimension in component["dimensions"]:
                    # Create an instance of the dimension and
                    # set minimum fields
                    dim = assetic.ComponentDimensionRepresentation()
                    for k, v in six.iteritems(dimension["attributes"]):
                        if v in atts:
                            setattr(dim, k, atts[v])
                    for k, v in six.iteritems(dimension["defaults"]):
                        if k in dim.to_dict():
                            setattr(dim, k, v)
                    dimlist.append(dim)

                # Add the dimension array to the component
                comp_tool_rep.dimensions = dimlist

            # add the component array
            complete_asset_obj.components.append(comp_tool_rep)
        return complete_asset_obj

    @staticmethod
    def sanitise_attribute(attribute):
        """
        Some of the attribute field types from a qgis table are not standard
        python types, so convert to standard types
        :param attribute: The attribute from the QGIS table
        :return: a standard python type - e.g datetime, date, string
        """
        if isinstance(attribute, QDate):
            return attribute.toPyDate()
        elif isinstance(attribute, QDateTime):
            return attribute.toPyDateTime()
        else:
            return attribute

    def get_geom_geojson(self, layer_crs, geometry):
        """
        Get the geojson for a geometry in 4326 projection
        :param layer_crs: layer crs object
        :param geometry: The input geometry
        :returns: wkt string of geometry in the specified projection
        """
        crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_transform = QgsCoordinateTransform(layer_crs, crs_dest
                                               , QgsProject.instance())

        # Get midpoint/centroid to use later
        midpoint = geometry.centroid()

        # transform the geometry and convert to geojson
        if geometry.transform(crs_transform) == 0:
            geojsonstr = geometry.asJson()
            geojson = json.loads(geojsonstr)
        else:
            # unable to transform
            self.commontools.new_message("Unable to apply transformation to "
                                         "geometry")
            return None
        # transform midpoint and get json
        centroid_geojson = None
        if midpoint.transform(crs_transform) == 0:
            centroid_geojsonstr = midpoint.asJson()
            centroid_geojson = json.loads(centroid_geojsonstr)

        if "GeometryCollection" not in geojson:
            # Geojson is expected to include collection, but QGIS
            # does not include it
            if centroid_geojson:
                fullgeojson = {
                    "geometries": [geojson, centroid_geojson]
                    , "type": "GeometryCollection"}
            else:
                fullgeojson = {
                    "geometries": [geojson]
                    , "type": "GeometryCollection"}
        else:
            # not try to include centroid, too messy.  Am not expecting to hit
            # this case unless QGIS changes
            fullgeojson = geojson
        return fullgeojson

    def get_layer_asset_guid(self, assetid, lyr_config):
        """
        Get the asset guid for an asset.  Used where "id" is not in the
        configuration.  If it is then it is assumed the assetid is a guid
        :param assetid: The assetid - may be guid or friendly
        :param lyr_config: the layer
        :returns: guid or none
        """
        # alias core fields object for readability
        corefields = lyr_config["corefields"]
        if "id" not in corefields:
            # must be using asset_id (friendly).  Need to get guid
            asset = self.assettools.get_asset(assetid)
            if asset is not None:
                assetid = asset["Id"]
            else:
                msg = "Asset with ID [{0}] not found in Assetic".format(
                    assetid)
                self.commontools.new_message(msg)
                return None
        return assetid

    def set_asset_address_spatial(self, assetid, lyr_config, geojson,
                                  addr=None):
        """
        Set the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: The settings defined for the layer
        :param geojson: The geoJson representation of the feature
        :param addr: Address representation.  Optional.
        assetic.CustomAddress
        :returns: 0=no error, >0 = error
        """
        if addr is not None and \
                not isinstance(addr, assetic.CustomAddress):
            msg = "Format of address incorrect,expecting " \
                  "assetic.CustomAddress"
            self.asseticsdk.logger.debug(msg)
            return 1
        else:
            addr = assetic.CustomAddress()

        # get guid
        assetguid = self.get_layer_asset_guid(assetid, lyr_config)
        if assetguid is None:
            msg = "Unable to obtain asset GUID for assetid={0}".format(assetid)
            self.commontools.new_message(msg)
            return 1
        chk = self.assettools.set_asset_address_spatial(assetguid, geojson,
                                                        addr)
        return 0
