# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
import json
import sys
from typing import List

import PyQt5.QtCore
import assetic
from copy import deepcopy
from PyQt5.QtCore import QDate, QDateTime
from assetic.tools.shared.config_base import ConfigBase
from assetic.tools.shared.layer_tools_base import LayerToolsBase
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsFeature,
    QgsVectorLayer,
    QgsGeometry,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsDataProvider,
    NULL
)
#from qgis.utils import iface


class QGISLayerTools(LayerToolsBase):
    """
    Class to manage processes that relate to a GIS layer
    """

    def __init__(self, config: ConfigBase = None):
        super().__init__(config)

    def get_rows(self, lyr: QgsVectorLayer, fields: List[str], query: str = None
                 ) -> None:
        """
        This method is unnecessary in QGIS as features can be accessed
        as dict-like objects when iterating over lyr.getFeatures().

        This method is being left in the qgis_layertools file as
        it is a required abstract method.

        :param lyr:
        :param fields:
        :param query:
        :return:
        """
        pass

    def get_geom_wkt(self, *args, **kwargs):
        """
        As yet unused method.
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @staticmethod
    def to_dict(feature):
        """
        Function to turn a QGIS feature in to a dict to allow processing
        by the LayerTools.

        Furthermore, QGIS' NULL object is different to Python's None
        object so is replaced in this function as attempting to JSON
        serialise QGIS NULL (PyQt5.QtCore.QVariant) crashes the integration.
        """
        fields = [f.name() for f in feature.fields()]

        dict_ = {f: feature[f] for f in fields}
        for key, value in dict_.items():
            if isinstance(value, PyQt5.QtCore.QVariant):
                dict_.update({key: None})

        return dict_

    def create_funclocs_from_layer(self, lyr: QgsVectorLayer, query: str = None
                                   , use_buffered_edit=True) -> (int, int):
        """
        Iterates over the rows in a passed in layer (narrowed down by
        optional query) and creates functional locations defined in
        the data.

        Returns the number of successful and failed functional
        locations.

        :param lyr: passed in arcgis layerfile
        :param query: query to select certain attributes
        :return: number created, number failed
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                              "functional location creation aborted.")
            return
        lyrfields = self.get_fields_list_from_layer(lyr)
        lyr_config, fields, idfieldget_fields_list_from_layer = self.xmlconf.get_fl_layer_config(
            lyr, lyr.name(), "create", lyrfields)

        if (lyr_config is None) and (fields is None):
            self.messager.new_message(
                "Unable to process functional location layer '{0}' due to "
                "missing configuration".format(lyr.name()))
            # return indication that nothing was processed
            return 0, 0

        fl_corefields = lyr_config['fl_corefields']
        fl_coredefaults = lyr_config['fl_coredefaults']

        attrs = lyr_config['fl_attributefields']
        def_attrs = lyr_config['fl_attributedefaults']

        success = 0
        fail = 0

        if query:
            req = QgsFeatureRequest().setFilterExpression(query)
            lyr.getFeatures(req)

        has_lyr_fl_type = 'functional_location_type' in fl_corefields.keys()

        lyr.startEditing()

        for feat in lyr.getSelectedFeatures():
            if has_lyr_fl_type:
                # many fltypes in a single layer
                fltype = feat[fl_corefields['functional_location_type']]
            else:
                # single fltype per layer
                fltype = fl_coredefaults['functional_location_type']

            flid = feat[fl_corefields['functional_location_id']]

            if flid in ['', None]:
                # no FL ID defined. attempt to retrieve by name and type
                flrepr = self.fltools.get_functional_location_by_name_and_type(
                    feat[fl_corefields['functional_location_name']]
                    , fltype)
            else:
                # FL ID defined. attempt to retrieve by ID
                # if FL doesn't exist we assume that autoid generation
                # is off which is why the ID is already set in the layer
                flrepr = self.fltools.get_functional_location_by_id(flid)

            if flrepr is not None:
                # FL already exists!
                self.messager.new_message(
                    "Functional Location {0} already exists".format(
                        flrepr.functional_location_name
                    ))
                fail += 1
                continue

            # Doesn't appear to be an existing FL so create.
            flrepr = self._create_fl_from_row(
                self.to_dict(feat), fl_corefields, fltype, attrs, def_attrs)

            if flrepr is None:
                # Error creating FL
                fail += 1
                continue

            # update row with new information - ID, GUID, etc.
            updfields = [fl_corefields[f] for f in [
                'functional_location_id', 'id'] if f in fl_corefields]
            rev = {v: k for k, v in fl_corefields.items()}

            if use_buffered_edit:
                # This is the default way to update a feature
                for f in updfields:
                    feat[f] = flrepr.__getattribute__(rev[f])

                lyr.updateFeature(feat)
            else:
                # This does a direct update via the data provider
                attrs_update = dict()
                for f in updfields:
                    # construct dictionary for update where the dict key is the layer's field index
                    attrs_update[feat.fields().lookupField(f)] = flrepr.__getattribute__(rev[f])
                fid = feat.id()
                chk = True
                if len(attrs_update) > 0:
                    chk = lyr.dataProvider().changeAttributeValues({fid: attrs_update})
                    # if chk is false, abort and output the FLs values to log
                    if not chk:
                        msg = "Failed to update the feature attribute values of the QGIS layer, " \
                              "using the unbuffered update method." \
                              " FeatureID='{0}', FLID/FLGUID='{1}'" \
                            .format(fid, list(attrs_update.values()))
                        self.messager.new_message(msg)
                        self.asseticsdk.logger.error(msg)
                        # commit changes before exist
                        lyr.commitChanges()
                        sys.exit()
            success += 1

        lyr.commitChanges()

        message = "Finished {0} Functional Location Creation, {1} Functional" \
                  " Locations created".format(lyr.name(), str(success))

        if fail > 0:
            message = "{0}, {1} Functional Locations not created. (Check " \
                      "logfile {2})".format(
                message, str(fail), self.logfilename)

        self.messager.new_message(message)

        return {"pass_cnt": success, "fail_cnt": fail}

    def update_funclocs_from_layer(self, lyr: QgsVectorLayer, query: str = None
                                   ) -> (int, int):
        """
        Iterates over the rows in a passed in layer (narrowed down by
        optional query) and updates functional locations defined in
        the data.

        Returns the number of successful and failed updates of functional
        locations.

        :param lyr: passed in arcgis layerfile
        :param query: query to select certain attributes
        :return: number created, number failed
        """
        if not self._is_valid_config:
            self.logger.error("Invalid or missing configuration file, "
                              "Functional Location update aborted.")
            return
        lyrfields = self.get_fields_list_from_layer(lyr)
        lyr_config, fields, idfield = self.xmlconf.get_fl_layer_config(
            lyr, lyr.name(), "update", lyrfields)

        if lyr_config is None and fields is None:
            msg = "Unable to process functional location layer '{0}' due to " \
                  "missing configuration".format(lyr.name())
            self.messager.new_message(msg)
            self.logger.error(msg)
            # return indication that nothing was processed
            return 0, 0

        fl_corefields = lyr_config['fl_corefields']
        fl_coredefaults = lyr_config['fl_coredefaults']

        has_lyr_fl_type = False
        if 'functional_location_type' in fl_corefields:
            has_lyr_fl_type = True
        elif 'functional_location_type' not in fl_coredefaults:
            # need to have functional location type
            msg = "Unable to process functional location layer '{0}' due to " \
                  "missing functional location type".format(lyr.name())
            self.messager.new_message(msg)
            self.logger.error(msg)
            # return indication that nothing was processed
            return 0, 0

        all_attr_fields = set()

        attrs = lyr_config['fl_attributefields']
        def_attrs = lyr_config['fl_attributedefaults']

        all_attr_fields.update(attrs.keys())
        all_attr_fields.update(def_attrs.keys())

        all_attr_fields = list(all_attr_fields)

        if query:
            req = QgsFeatureRequest().setFilterExpression(query)
            lyr.getFeatures(req)

        success = 0
        fail = 0
        for feat in lyr.getSelectedFeatures():

            if has_lyr_fl_type:
                # many fltypes in a single layer
                fltype = feat[fl_corefields['functional_location_type']]
            else:
                # single fltype per layer defined in defaults
                fltype = fl_coredefaults['functional_location_type']

            flid = feat[fl_corefields['functional_location_id']]

            fl_guid = None
            if "id" in fl_corefields and fl_corefields['id'] in feat:
                fl_guid = feat[fl_corefields['id']]

            if flid in ['', None] and fl_guid in ['', None]:
                # no FL ID defined. attempt to retrieve by name and type
                flrepr = self.fltools.get_functional_location_by_name_and_type(
                    feat[fl_corefields['functional_location_name']]
                    , fltype, all_attr_fields)
            else:
                # FL ID defined. attempt to retrieve by ID
                if fl_guid:
                    flrepr = self.fltools.get_functional_location_by_id(
                        fl_guid, all_attr_fields)
                else:
                    flrepr = self.fltools.get_functional_location_by_id(
                        flid, all_attr_fields)
            if flrepr is None:
                # No FL found so move to next record
                self.messager.new_message(
                    "Unable to retrieve Functional Location {0} for "
                    "update".format(
                        feat[fl_corefields['functional_location_name']]
                    ))
                fail += 1
                continue

            # FL exists, check if the attributes are different
            # and then post if they are
            row_attrs = self._retrieve_fl_attrs_from_row(feat, attrs,
                                                         def_attrs)

            if row_attrs != flrepr.attributes or \
                    flrepr.functional_location_name != feat[
                fl_corefields['functional_location_name']]:
                # e.g. something has changed so update attributes with GIS
                # attributes, and name in case it changed (not allow
                # change to FL type or id)
                flrepr.attributes = row_attrs
                flrepr.functional_location_name = feat[
                    fl_corefields['functional_location_name']]
                flepr = self.fltools.update_functional_location(flrepr)
                if flepr:
                    success += 1
                else:
                    fail += 1
            else:
                # indicate success, just don't attempt update
                success += 1

        message = "Finished {0} Functional Location Update, {1} Functional " \
                  "Locations updated".format(lyr.name(), str(success))

        if fail > 0:
            message = "{0}, {1} Functional Locations not updated. (Check " \
                      "logfile {2})".format(
                message, str(fail), self.logfilename)

        self.messager.new_message(message)

        return {"pass_cnt": success, "fail_cnt": fail}

    def individually_update_rows(
            self, rows: List[dict], total: int, lyr_config: dict
            , fields: List[str]) -> dict:
        """
        Iterates over the rows of the layerfile and updates each asset
        using API calls.

        :param rows: <List[dict]> a list of dicts where keys are the
        column names and values are cell contents
        :param total: <int> the number of features
        :param lyr_config: <dict> dict defining the relationship
        between xml nodes and the layer's column values
        :param fields: <List[str]> a list of column names from the layer
        :return:
        """

        lyrname = lyr_config['layer']

        # initialise counters for the log messages
        num_pass = 0
        num_fail = 0

        for i, row in enumerate(rows):
            success = self._update_asset(row, lyr_config, fields)
            msg = ("Processing feature {1} of {2}".format(lyrname, i + 1, total))
            self.messager.new_message(msg)

            if success:
                num_pass = num_pass + 1
            else:
                num_fail = num_fail + 1

            message = "Finished {0} Asset Update, {1} assets updated".format(
                lyrname, str(num_pass))

            if num_fail > 0:
                message = "{0}, {1} assets not updated. (Check log file '{2}')" \
                          "".format(message, str(num_fail), self.logfilename)

            self.messager.new_message(message)

        return {"pass_cnt": num_pass, "fail_cnt": num_fail}

    @staticmethod
    def get_fields_list_from_layer(lyr):
        """
        Convenience method to return a list of field names from
        the passed in layer.
        :param lyr: <QgsVectorLayer>
        :return: <list> list of field names
        """
        return [f.name() for f in lyr.fields()]

    def create_assets(self, lyr: QgsVectorLayer, query: str = None,
                      use_buffered_edit=True) -> dict:
        """
        For the given layer create new assets for the selected features only if
        features have no assetic guid.
        :param lyr: <QgsVectorLayer>is the layer to process (not layer name)
        :param query: <str>
        """
        results = {
            "pass_cnt": 0,
            "fail_cnt": 0,
            "ignore_cnt": 0,
            "partial_cnt": 0,
        }

        # retrieve a list of fields from the layer
        lyrfields = self.get_fields_list_from_layer(lyr)

        # extend with the assetic created geometry fields
        # (feature geometry info stored in feature.geometry() and
        # not in a column like esri)
        # these values are manually added to feature dict in
        # get_asset_obj_for_row()
        lyrfields.extend(["_geometry_length_", "_geometry_area_"])

        # get configuration for layer
        lyr_config, fields, idfield = self.xmlconf.get_layer_config(
            lyr=lyr, lyrname=lyr.name(), purpose="create", actuallayerflds=lyrfields
        )

        if lyr_config is None:
            self.messager.new_message("Layer configuration object not defined. "
                                      "Returning empty results")
            return results

        lyr.startEditing()

        # if flag use_buffered_edit is false, validate capabilities before
        # continuing
        if not use_buffered_edit:
            chk = self.check_direct_edit_capability(lyr)
            if not chk == self.results["success"]:
                return chk

        cnt = 1.0
        for feat in lyr.getSelectedFeatures():
            if self.messager.is_cancelled:  # noqa
                # user initiated cancel
                self.messager.new_message("Execution cancelled")
                return results
            self.messager.new_message(
                "Creating Assets for layer {0}.\nProcessing "
                "feature {1} of {2}".format(
                    lyr.name(), int(cnt), lyr.selectedFeatureCount()))

            # create new asset
            result = self._new_asset(feat, lyr_config, fields, lyr.crs(),
                                     lyr, use_buffered_edit)
            if result == 0:
                results["pass_cnt"] += 1
            elif result == 1:
                results["fail_cnt"] += 1
            elif result == 2:
                results["ignore_cnt"] += 1
            elif result == 3:
                results["partial_cnt"] += 1
            cnt += 1
        lyr.commitChanges()

        self.messager.new_message("Processing complete")

        return results

    def layer_to_feature_list(self, lyr: QgsVectorLayer):
        """
        Converts a layer's features in to a list of list of dict-like
        objects so that common layer tools can process each feature.

        The original feature can be accessed using the "_feature" key.
        """
        feat_list = []
        attr_index = dict()
        for feat in lyr.getSelectedFeatures():
            if len(attr_index) == 0:
                # dict where field name is the key and field index position
                # is the val.  Used later to update the field based on index
                # position
                for key, val in feat.attributeMap().items():
                    attr_index[key] = feat.fieldNameIndex(key)

            row = self.to_dict(feat)
            # sanitise fields as they might be non standard Python types (e.g QDate)
            for key, value in row.items():
                row.update({key: self.sanitise_attribute(value)})

            # store the original feature as a value so we can
            # access it if we need to
            #row["_feature"] = feat

            # append geometry information to the row
            row["geom_geojson"] = self.get_geom_geojson(
                lyr.crs(), feat.geometry())
            row["_geometry_length_"] = feat.geometry().length()
            row["_geometry_area_"] = feat.geometry().area()

            # append crs to feature
            #row["_layer_crs_"] = lyr.crs()

            feat_list.append(row)

        return feat_list, attr_index

    def update_assets(self, lyr: QgsVectorLayer, query: str = None
                      , use_buffered_edit: bool = True):
        """
        For the given layer update assets for the selected features only
        where features have an assetic guid/asset id.
        :param lyr: is the layer to process (not layer name but QGIS layer)
        :param query: optional attribute query to get selection
        :param use_buffered_edit:
        """
        # retrieve a list of fields from the layer
        lyrfields = self.get_fields_list_from_layer(lyr)

        # extend with the assetic created geometry fields
        # (feature geometry info stored in feature.geometry() and
        # not in a column like esri)
        # these values are manually added to feature dict in
        # get_asset_obj_for_row()
        lyrfields.extend(["_geometry_length_", "_geometry_area_"])

        # get layer configuration from xml file
        lyr_config, fields, idfield = self.xmlconf.get_layer_config(
            lyr=lyr, lyrname=lyr.name(), purpose="update"
            , actuallayerflds=lyrfields)

        if lyr_config is None:
            return

        if lyr.selectedFeatureCount() == 0:
            self.asseticsdk.logger.debug("No features selected - must pass in valid"
                                         " 'where clause'.")
            return

        # get list of dicts, 1 dict per feature
        # also get a dict of the attribute index for fields in layer table
        feat_list, att_index = self.layer_to_feature_list(lyr)

        if lyr.selectedFeatureCount() > self._bulk_threshold:
            chk, valid_rows = self.bulk_update_rows(feat_list, lyr, lyr_config)
            results = None
        else:
            # take a copy of the list to allow comparison following update
            feats_preupdate = deepcopy(feat_list)

            results = self.individually_update_rows(
                feat_list, lyr.selectedFeatureCount(), lyr_config, fields)
            if "allow_component_upsert" in lyr_config and \
                    lyr_config["allow_component_upsert"]:
                self.apply_upsert_to_layer(
                    lyr, use_buffered_edit, lyr_config, feat_list
                    , feats_preupdate, att_index)
        return results

    def apply_upsert_to_layer(
            self, lyr: QgsVectorLayer, use_buffered_edit: bool, lyr_config,
            rows, rows_preupdate: list, att_index: dict):
        """
        Upsert is where a component or dimension has been added to an
        existing asset record via the update process
        :param lyr: the qgis layer
        :param use_buffered_edit:
        :param lyr_config: xml config
        :param rows: the rows processed, amy contain updated information
        where components or dimensions were added
        :param rows_preupdate: the row prior to running the update
        :param: att_index: dict where key is the field name and val is the
        index position of that field in the feature table
        :return: success =0 else error
        """

        lyr.startEditing()

        # index the pre_update list of dicts by the unique fid so we can find
        # the original value
        preupdate_dict = dict((item['fid'], item) for item in rows_preupdate)

        counter = 0
        for updated_row in rows:
            # if the row not found in pre update rows then it means the row
            # was modified by the update process, indicating a new
            # component/dimension
            if updated_row not in rows_preupdate:
                counter += 1

                # get the original row
                orig_row = preupdate_dict[updated_row["fid"]]
                if use_buffered_edit:
                    # This is where we apply a buffered update (default)
                    # to the feature
                    self._apply_upsert_to_layer_buffered(
                        lyr, orig_row, updated_row, att_index)
                else:
                    # This is where we apply an unbuffered update to the feature
                    # validate capabilities before continuing
                    chk = self.check_direct_edit_capability(lyr)
                    if not chk == self.results["success"]:
                        return chk
                    self._apply_upsert_to_layer_unbuffered(
                        lyr, lyr_config, updated_row, att_index)

        lyr.commitChanges()

        return 0

    def _apply_upsert_to_layer_buffered(
            self, lyr: QgsVectorLayer, row_preupdate: dict, updated_row: dict
            , att_index: dict):
        """
        apply changes following upsert using the buffered update method
        :param lyr: the layer being updated
        :param row_preupdate: the row prior to update
        :param updated_row: the row following update
        :param att_index: dict where key is the field name and val is the
        index position of that field in the feature table
        :return:
        """

        for key, val in row_preupdate.items():
            if key in updated_row and updated_row[key] != val:
                # need to update
                lyr.changeAttributeValue(
                    updated_row["fid"], att_index[key]
                    , updated_row[key])
        lyr.commitChanges(stopEditing=False)

    def _apply_upsert_to_layer_unbuffered(
            self, lyr: QgsVectorLayer, lyr_config, row, att_index: dict):
        """
        apply changes following upsert using unbuffered method
        :param lyr: the layer being processed
        :param lyr_config: the XML config for the layer
        :param row: the new values for the attributes
        :param att_index: dict where key is the field name and val is the
        index position of that field in the feature table
        :return:
        """
        attrs = {}
        corefields = lyr_config["corefields"]

        asset_guid = ""
        asset_fid = ""

        # apply asset guid and/or assetid
        if "id" in corefields and corefields["id"] in att_index:
            asset_guid = row[corefields["id"]]
            attrs[att_index[corefields["id"]]] = asset_guid

        if "asset_id" in corefields and corefields["asset_id"] in att_index:
            asset_guid = row[corefields["asset_id"]]
            attrs[att_index[corefields["asset_id"]]] = asset_guid

        # apply component id and name
        for component_config in lyr_config["components"]:
            comp_atts = component_config["attributes"]
            if "id" in comp_atts and comp_atts["id"] in att_index:
                val = row[comp_atts["id"]]
                attrs[att_index[comp_atts["id"]]] = val
            if "name" in comp_atts and comp_atts["name"] in att_index:
                val = row[comp_atts["name"]]
                attrs[att_index[comp_atts["name"]]] = val

        fid = row["fid"]
        chk = True
        if len(attrs) > 0:
            chk = lyr.dataProvider().changeAttributeValues({fid: attrs})
            # if chk is false, abort and provide asset values
            if not chk:
                msg = "Failed to update the feature attribute values of the " \
                      "QGIS layer, " \
                      "using the unbuffered update method." \
                      " FeatureID='{0}', AssetID='{1}', AssetGUID='{2}'" \
                    .format(row.id(), asset_fid, asset_guid)
                self.messager.new_message(msg)
                lyr.commitChanges()
                sys.exit()

    def _new_asset(self, row, lyr_config: dict, fields, layer_crs
                   , layer, use_buffered_edit=True):
        """
        Create a new asset for the given search result row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :layer_crs
        :layer
        :use_buffered_edit: flag to determine to use buffered edit or direct
        edit.  Deafault=True (buffered edit)
        :returns: 0 if success, 1 if error, 2 if skip (existing),
        3 if partial success such as asset created but component not
        """

        row_dict = self.to_dict(row)
        for key, value in row_dict.items():
            row_dict.update({key: self.sanitise_attribute(value)})

        complete_asset_obj = self.get_asset_obj_for_row(
            row_dict, lyr_config, fields, create_fl=True)
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
                self.messager.new_message(
                    "Asset not created because there is no configuration "
                    "setting for <id> or <asset_id> or the field is not in "
                    "the layer")
                return self.results["error"]
        if not newasset:
            self.messager.new_message(
                "Asset not created because it already has the following "
                "values: Asset ID={0},Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return self.results["skip"]

        # set status
        complete_asset_obj.asset_representation.status = \
            lyr_config["creation_status"]
        # Create new asset
        response = self.assettools.create_complete_asset(complete_asset_obj)
        if response is None:
            msg = "Asset Not Created - Check log"
            self.messager.new_message(msg)
            return self.results["error"]

        partial_asset_created = False
        if response.error_code in [2, 4, 16]:
            # component (2), or dimension (4) or Fl (16) error
            # will continue though....
            partial_asset_created = True

        # This is where we apply an buffered update (default) to the feature
        if use_buffered_edit:
            # apply asset guid and/or assetid
            if "id" in corefields:
                if row.fieldNameIndex(corefields["id"]) >= 0:
                    layer.changeAttributeValue(
                        row.id(), row.fieldNameIndex(corefields["id"])
                        , response.asset_representation.id)
            if "asset_id" in corefields:
                if row.fieldNameIndex(corefields["asset_id"]) >= 0:
                    layer.changeAttributeValue(
                        row.id(), row.fieldNameIndex(corefields["asset_id"])
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
                        if row.fieldNameIndex(
                                component_config["attributes"]["id"]) >= 0:
                            layer.changeAttributeValue(
                                row.id(),
                                row.fieldNameIndex(
                                    component_config["attributes"]["id"])
                                , component_dim_obj.component_representation.id)
            layer.commitChanges(stopEditing=False)

        # This is where we apply an unbuffered update to the feature
        elif not use_buffered_edit:
            attrs = {}

            # apply asset guid and/or assetid
            if "id" in corefields:
                if row.fieldNameIndex(corefields["id"]) >= 0:
                    attrs[row.fields().lookupField(corefields["id"])] = \
                        response.asset_representation.id

            if "asset_id" in corefields:
                if row.fieldNameIndex(corefields["asset_id"]) >= 0:
                    attrs[row.fields().lookupField(corefields["asset_id"])] = \
                        response.asset_representation.asset_id
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
                        if row.fieldNameIndex(
                                component_config["attributes"]["id"]) >= 0:
                            attrs[row.fields().lookupField(
                                component_config["attributes"]["id"])] = \
                                component_dim_obj.component_representation.id

            fid = row.id()
            chk = True
            if len(attrs) > 0:
                chk = layer.dataProvider().changeAttributeValues({fid: attrs})
                # if chk is false, abort and provide asset values
                if not chk:
                    msg = "Failed to update the feature attribute values of the QGIS layer, " \
                          "using the unbuffered update method." \
                          " FeatureID='{0}', AssetID='{1}', AssetGUID='{2}'"\
                        .format(row.id(), response.asset_representation.asset_id, response.asset_representation.id)
                    self.messager.new_message(msg)
                    self.asseticsdk.logger.error(msg)
                    layer.commitChanges()
                    sys.exit()

        # Now check config and update Assetic with spatial data and/or address
        addr = None
        geojson = None
        if len(lyr_config["addressfields"]) > 0 \
                or len(lyr_config["addressdefaults"]) > 0:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields from the attribute fields of the feature
            for k, v in lyr_config["addressfields"].items():
                if k in addr.to_dict() and v in fields:
                    val = None
                    try:
                        if row[v] != NULL and str(row[v]).strip() != "":
                            val = self.sanitise_attribute(row[v])
                    except Exception:
                        pass
                    setattr(addr, k, val)
            # get address defaults
            for k, v in lyr_config["addressdefaults"].items():
                if k in addr.to_dict():
                    setattr(addr, k, v)
        if lyr_config["upload_feature"]:
            geojson = self.get_geom_geojson(layer_crs, row.geometry())
        if addr or geojson:
            chk = self.assettools.set_asset_address_spatial(
                response.asset_representation.id, geojson, addr)
            if chk > 0:
                return self.results["partial"]

        if partial_asset_created:
            return self.results["partial"]
        else:
            return self.results["success"]

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

    def bulk_update_spatial(self, rows, lyr, lyr_config):
        # type: (list, QGISLayerTools, dict) -> int

        # define a dx-column names with the int code for the qgis layer
        shape_types = {
            QgsWkbTypes.Point: "Point",
            QgsWkbTypes.Polygon: "Polygon",
            QgsWkbTypes.MultiPolygon: "Polygon",
            QgsWkbTypes.LineString: "Line",
            QgsWkbTypes.MultiLineString: "Line"
        }
        shape_type = shape_types[lyr.wkbType()]

        # define the transformation we want
        crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")

        # create a transformation object
        crs_transform = QgsCoordinateTransform(lyr.crs(), crs_dest, QgsProject.instance())

        spatial_rows = []
        for row in rows:
            asset_id = self._get_assetid_from_row(row, lyr_config)
            if asset_id is None:
                continue

            # retrieve geometry from row dict
            geometry = row["_feature"].geometry()

            # apply the transformation (in place) returns 0 if error
            if geometry.transform(crs_transform) != 0:
                self.messager.new_message("Unable to apply transformation to "
                                          "geometry for asset ID [{0}]".format(asset_id))
                continue

            wkt = geometry.asWkt()
            rd = {
                "Asset ID": asset_id,
                shape_type: wkt,
            }

            # add a point geometry to help orient polygon
            if shape_type == "Polygon":
                rd["Point"] = geometry.centroid().asWkt()

            spatial_rows.append(rd)

        if len(spatial_rows) > 0:
            self.gis_tools.bulk_update_spatial(spatial_rows)

        return 0

    def get_geom_geojson(self, layer_crs, geometry):
        """
        Get the geojson for a geometry in 4326 projection
        :param layer_crs: layer crs object
        :param geometry: The input geometry
        :returns: wkt string of geometry in the specified projection
        """

        crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_transform = QgsCoordinateTransform(layer_crs, crs_dest, QgsProject.instance())

        # Get midpoint/centroid to use later
        midpoint = geometry.centroid()

        # transform the geometry and convert to geojson
        if geometry.transform(crs_transform) == 0:
            if geometry.wkbType() in [QgsWkbTypes.MultiPolygon]:
                # mutlipolygon, so check and correct orientation to avoid error
                geojsonstr = self.prepare_multipolygon_geojson(geometry)
            else:
                geojsonstr = geometry.asJson()
            geojson = json.loads(geojsonstr)
        else:
            # unable to transform
            self.messager.new_message("Unable to apply transformation to "
                                      "geometry")
            return None

        # transform midpoint and get json
        centroid_geojson = None
        if midpoint.transform(crs_transform) == 0:
            centroid_geojsonstr = midpoint.asJson()
            centroid_geojson = json.loads(centroid_geojsonstr)

        if "GeometryCollection" not in geojson:

            # todo is this the most explicit flow throw different geometry types?
            if geometry.wkbType() in [QgsWkbTypes.Point,
                                      QgsWkbTypes.MultiPoint,
                                      QgsWkbTypes.LineString,
                                      QgsWkbTypes.MultiLineString]:
                fullgeojson = {
                    "geometries": [geojson]
                    , "type": "GeometryCollection"}

            # Geojson is expected to include collection, but QGIS
            # does not include it
            elif centroid_geojson:
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

    def prepare_multipolygon_geojson(self, geom):
        """
        QGIS does not correct polygon orientation when generating the geojson
        This method will make sure all outer rings (may be more than 1) are
        correctly orientated.  If there are inner rings their orientation
        will also be corrected, but the assumption is there are not rings
        within rings
        :param geom: the geometry to prepare the geojson for
        :return: geojson representation
        """

        # get list of vertices that describe the multi-polygon
        gamp = geom.asMultiPolygon()
        changed = False
        # iterate each polygon part of the multipolygon
        for pr in gamp:
            # the first element of pr is the outer ring
            signedarea = self.get_signed_area(pr[0])
            if signedarea > 0:
                #outer ring anti-clockwise - do nothing
                pass
            elif signedarea < 0:
                # outer ring clockwise - reverse vertices
                pr[0].reverse()
                changed = True
            else:
                # unexpected result
                pass

            if len(pr) > 1:
                # there are inner rings within the current polygon
                cnt = 1
                while cnt < len(pr):
                    # get area of each inner ring
                    signedarea = self.get_signed_area(pr[cnt])
                    if signedarea > 0:
                        # inner ring anti-clockwise.  Need to reverse
                        pr[cnt].reverse()
                        changed = True
                    elif signedarea < 0:
                        # inner ring clockwise - do nothing
                        pass
                    else:
                        # unexpected result
                        pass
                    cnt += 1
        if changed:
            # create a geometry from the updated vertices lists and get the
            # geojson
            newgeom = QgsGeometry.fromMultiPolygonXY(gamp)
            return newgeom.asJson()
        else:
            return geom.asJson()

    def get_signed_area(self, pr):
        """
        Get the area of the polygon where a negative area indicates
        clockwise orientation and positive area anti-clockwise
         http://www.cgafaq.info/wiki/Polygon_Area.
        :param pr: list of polygon vertices in order
        :return: signed area of polygon
        """
        xs, ys = map(list, zip(*pr))
        xs.append(xs[1])
        ys.append(ys[1])
        signedarea = sum(
            xs[i] * (ys[i + 1] - ys[i - 1]) for i in range(1, len(pr))) / 2.0
        return signedarea

    def get_layer_asset_guid(self, assetid: str, lyr_config: dict):
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
                self.messager.new_message(msg)
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
            self.messager.new_message(msg)
            return 1
        chk = self.assettools.set_asset_address_spatial(assetguid, geojson,
                                                        addr)
        return 0

    def check_direct_edit_capability(self, layer):

        try:
            capable = layer.dataProvider().capabilitiesString()
        except Exception:
            capable = None
        if capable and "Change Attribute Values" in capable:
            # require capabilities found, no issues
            return self.results["success"]
        elif capable and not "Change Attribute Values" in capable:
            # require capabilities not found, error
            msg = "The 'Change Attribute Values' was not found in the layer " \
                  "capabilities. " \
                  "Please change the config to use the buffered method (" \
                  "use_buffered_edit = True) " \
                  "or update the layer to support the direct update method."
            self.messager.new_message(msg)
            return self.results["error"]
        else:
            # handle unknown error if capable is None
            msg = "Error validating direct edit capabilities of the QGIS layer."
            self.messager.new_message(msg)
            return self.results["error"]
