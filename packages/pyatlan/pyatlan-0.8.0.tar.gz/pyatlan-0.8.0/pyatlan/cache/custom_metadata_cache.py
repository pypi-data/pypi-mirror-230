# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Atlan Pte. Ltd.
from typing import Optional

from pyatlan.errors import ErrorCode
from pyatlan.model.enums import AtlanTypeCategory
from pyatlan.model.typedef import AttributeDef, CustomMetadataDef


class CustomMetadataCache:
    """
    Lazily-loaded cache for translating between Atlan-internal ID strings and human-readable names
    for custom metadata (including attributes).
    """

    cache_by_id: dict[str, CustomMetadataDef] = dict()
    attr_cache_by_id: dict[str, AttributeDef] = dict()
    map_id_to_name: dict[str, str] = dict()
    map_name_to_id: dict[str, str] = dict()
    map_attr_id_to_name: dict[str, dict[str, str]] = dict()
    map_attr_name_to_id: dict[str, dict[str, str]] = dict()
    archived_attr_ids: dict[str, str] = dict()
    types_by_asset: dict[str, set[type]] = dict()

    @classmethod
    def refresh_cache(cls) -> None:
        """
        Refreshes the cache of custom metadata structures by requesting the full set of custom metadata
        structures from Atlan.
        :raises LogicError: if duplicate custom attributes are detected
        """
        from pyatlan.client.atlan import AtlanClient

        client = AtlanClient.get_default_client()
        if client is None:
            client = AtlanClient()
        response = client.get_typedefs(type_category=AtlanTypeCategory.CUSTOM_METADATA)
        if response is not None:
            cls.map_id_to_name = {}
            cls.map_name_to_id = {}
            cls.map_attr_id_to_name = {}
            cls.map_attr_name_to_id = {}
            cls.archived_attr_ids = {}
            cls.cache_by_id = {}
            cls.attr_cache_by_id = {}
            for cm in response.custom_metadata_defs:
                type_id = cm.name
                type_name = cm.display_name
                cls.cache_by_id[type_id] = cm
                cls.map_id_to_name[type_id] = type_name
                cls.map_name_to_id[type_name] = type_id
                cls.map_attr_id_to_name[type_id] = {}
                cls.map_attr_name_to_id[type_id] = {}
                if cm.attribute_defs:
                    for attr in cm.attribute_defs:
                        attr_id = str(attr.name)
                        attr_name = str(attr.display_name)
                        cls.map_attr_id_to_name[type_id][attr_id] = attr_name
                        cls.attr_cache_by_id[attr_id] = attr
                        if attr.options and attr.options.is_archived:
                            cls.archived_attr_ids[attr_id] = attr_name
                        elif attr_name in cls.map_attr_name_to_id[type_id]:
                            raise ErrorCode.DUPLICATE_CUSTOM_ATTRIBUTES.exception_with_parameters(
                                attr_name, type_name
                            )
                        else:
                            cls.map_attr_name_to_id[type_id][attr_name] = attr_id

    @classmethod
    def get_id_for_name(cls, name: str) -> str:
        """
        Translate the provided human-readable custom metadata set name to its Atlan-internal ID string.

        :param name: human-readable name of the custom metadata set
        :returns: Atlan-internal ID string of the custom metadata set
        :raises InvalidRequestError: if no name was provided
        :raises NotFoundError: if the custom metadata cannot be found
        """
        if name is None or not name.strip():
            raise ErrorCode.MISSING_CM_NAME.exception_with_parameters()
        if cm_id := cls.map_name_to_id.get(name):
            return cm_id
        # If not found, refresh the cache and look again (could be stale)
        cls.refresh_cache()
        if cm_id := cls.map_name_to_id.get(name):
            return cm_id
        raise ErrorCode.CM_NOT_FOUND_BY_NAME.exception_with_parameters(name)

    @classmethod
    def get_name_for_id(cls, idstr: str) -> str:
        """
        Translate the provided Atlan-internal custom metadata ID string to the human-readable custom metadata set name.

        :param idstr: Atlan-internal ID string of the custom metadata set
        :returns: human-readable name of the custom metadata set
        :raises InvalidRequestError: if no ID was provided
        :raises NotFoundError: if the custom metadata cannot be found
        """
        if idstr is None or not idstr.strip():
            raise ErrorCode.MISSING_CM_ID.exception_with_parameters()
        if cm_name := cls.map_id_to_name.get(idstr):
            return cm_name
        # If not found, refresh the cache and look again (could be stale)
        cls.refresh_cache()
        if cm_name := cls.map_id_to_name.get(idstr):
            return cm_name
        raise ErrorCode.CM_NOT_FOUND_BY_ID.exception_with_parameters(idstr)

    @classmethod
    def get_all_custom_attributes(
        cls, include_deleted: bool = False, force_refresh: bool = False
    ) -> dict[str, list[AttributeDef]]:
        """
        Retrieve all the custom metadata attributes. The dict will be keyed by custom metadata set
        name, and the value will be a listing of all the attributes within that set (with all the details
        of each of those attributes).

        :param include_deleted: if True, include the archived (deleted) custom attributes; otherwise only
                                include active custom attributes
        :param force_refresh: if True, will refresh the custom metadata cache; if False, will only refresh the
                              cache if it is empty
        :returns: a dict from custom metadata set name to all details about its attributes
        :raises NotFoundError: if the custom metadata cannot be found
        """
        if len(cls.cache_by_id) == 0 or force_refresh:
            cls.refresh_cache()
        m = {}
        for type_id, cm in cls.cache_by_id.items():
            type_name = cls.get_name_for_id(type_id)
            if not type_name:
                raise ErrorCode.CM_NOT_FOUND_BY_ID.exception_with_parameters(type_id)
            attribute_defs = cm.attribute_defs
            if include_deleted:
                to_include = attribute_defs
            else:
                to_include = []
                if attribute_defs:
                    to_include.extend(
                        attr
                        for attr in attribute_defs
                        if not attr.options or not attr.options.is_archived
                    )
            m[type_name] = to_include
        return m

    @classmethod
    def get_attr_id_for_name(cls, set_name: str, attr_name: str) -> str:
        """
        Translate the provided human-readable custom metadata set and attribute names to the Atlan-internal ID string
        for the attribute.

        :param set_name: human-readable name of the custom metadata set
        :param attr_name: human-readable name of the attribute
        :returns: Atlan-internal ID string for the attribute
        :raises NotFoundError: if the custom metadata attribute cannot be found
        """
        set_id = cls.get_id_for_name(set_name)
        if sub_map := cls.map_attr_name_to_id.get(set_id):
            attr_id = sub_map.get(attr_name)
            if attr_id:
                # If found, return straight away
                return attr_id
        # Otherwise, refresh the cache and look again (could be stale)
        cls.refresh_cache()
        if sub_map := cls.map_attr_name_to_id.get(set_id):
            attr_id = sub_map.get(attr_name)
            if attr_id:
                # If found, return straight away
                return attr_id
            raise ErrorCode.CM_ATTR_NOT_FOUND_BY_NAME.exception_with_parameters(
                set_name
            )
        raise ErrorCode.CM_ATTR_NOT_FOUND_BY_ID.exception_with_parameters(set_id)

    @classmethod
    def get_attr_name_for_id(cls, set_id: str, attr_id: str) -> str:
        """
        Given the Atlan-internal ID string for the set and the Atlan-internal ID for the attribute return the
        human-readable custom metadata name for the attribute.

        :param set_id: Atlan-internal ID string for the custom metadata set
        :param attr_id: Atlan-internal ID string for the attribute
        :returns: human-readable name of the attribute
        :raises NotFoundError: if the custom metadata attribute cannot be found
        """
        if sub_map := cls.map_attr_id_to_name.get(set_id):
            if attr_name := sub_map.get(attr_id):
                return attr_name
            cls.refresh_cache()
            if sub_map := cls.map_attr_id_to_name.get(set_id):
                if attr_name := sub_map.get(attr_id):
                    return attr_name
        raise ErrorCode.CM_ATTR_NOT_FOUND_BY_ID.exception_with_parameters(
            attr_id, set_id
        )

    @classmethod
    def _get_attributes_for_search_results(cls, set_id: str) -> Optional[list[str]]:
        if sub_map := cls.map_attr_name_to_id.get(set_id):
            attr_ids = sub_map.values()
            return [f"{set_id}.{idstr}" for idstr in attr_ids]
        return None

    @classmethod
    def _get_attribute_for_search_results(
        cls, set_id: str, attr_name: str
    ) -> Optional[str]:
        if sub_map := cls.map_attr_name_to_id.get(set_id):
            return sub_map.get(attr_name, None)
        return None

    @classmethod
    def get_attributes_for_search_results(cls, set_name: str) -> Optional[list[str]]:
        """
        Retrieve the full set of custom attributes to include on search results.

        :param set_name: human-readable name of the custom metadata set for which to retrieve attribute names
        :returns: a list of the attribute names, strictly useful for inclusion in search results
        """
        if set_id := cls.get_id_for_name(set_name):
            if dot_names := cls._get_attributes_for_search_results(set_id):
                return dot_names
            cls.refresh_cache()
            return cls._get_attributes_for_search_results(set_id)
        return None

    @classmethod
    def get_attribute_for_search_results(
        cls, set_name: str, attr_name: str
    ) -> Optional[str]:
        """
        Retrieve a single custom attribute name to include on search results.

        :param set_name: human-readable name of the custom metadata set for which to retrieve the custom metadata
                         attribute name
        :param attr_name: human-readable name of the attribute
        :returns: the attribute name, strictly useful for inclusion in search results
        """
        if set_id := cls.get_id_for_name(set_name):
            if attr_id := cls._get_attribute_for_search_results(set_id, attr_name):
                return attr_id
            cls.refresh_cache()
            return cls._get_attribute_for_search_results(set_id, attr_name)
        return None

    @classmethod
    def get_custom_metadata_def(cls, name: str) -> CustomMetadataDef:
        """
        Retrieve the full custom metadata structure definition.

        :param name: human-readable name of the custom metadata set
        :returns: the full custom metadata structure definition for that set
        :raises InvalidRequestError: if no name was provided
        :raises NotFoundError: if the custom metadata cannot be found
        """
        ba_id = cls.get_id_for_name(name)
        if typedef := cls.cache_by_id.get(ba_id):
            return typedef
        else:
            raise ErrorCode.CM_NOT_FOUND_BY_NAME.exception_with_parameters(name)

    @classmethod
    def get_attribute_def(cls, attr_id: str) -> AttributeDef:
        """
        Retrieve a specific custom metadata attribute definition by its unique Atlan-internal ID string.

        :param attr_id: Atlan-internal ID string for the custom metadata attribute
        :returns: attribute definition for the custom metadata attribute
        :raises InvalidRequestError: if no attribute ID was provided
        :raises NotFoundError: if the custom metadata attribute cannot be found
        """
        if not attr_id:
            raise ErrorCode.MISSING_CM_ATTR_ID.exception_with_parameters()
        if cls.attr_cache_by_id is None:
            cls.refresh_cache()
        if attr_def := cls.attr_cache_by_id.get(attr_id):
            return attr_def
        raise ErrorCode.CM_ATTR_NOT_FOUND_BY_ID.exception_with_parameters(
            attr_id, "(unknown)"
        )
