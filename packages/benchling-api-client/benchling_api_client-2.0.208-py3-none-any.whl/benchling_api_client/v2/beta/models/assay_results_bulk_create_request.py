from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assay_result_create import AssayResultCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultsBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsBulkCreateRequest:
    """  """

    _assay_results: List[AssayResultCreate]
    _table_id: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        fields.append("table_id={}".format(repr(self._table_id)))
        return "AssayResultsBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results = []
        for assay_results_item_data in self._assay_results:
            assay_results_item = assay_results_item_data.to_dict()

            assay_results.append(assay_results_item)

        table_id = self._table_id

        field_dict: Dict[str, Any] = {}
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if assay_results is not UNSET:
            field_dict["assayResults"] = assay_results
        if table_id is not UNSET:
            field_dict["tableId"] = table_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_assay_results() -> List[AssayResultCreate]:
            assay_results = []
            _assay_results = d.pop("assayResults")
            for assay_results_item_data in _assay_results:
                assay_results_item = AssayResultCreate.from_dict(assay_results_item_data, strict=False)

                assay_results.append(assay_results_item)

            return assay_results

        try:
            assay_results = get_assay_results()
        except KeyError:
            if strict:
                raise
            assay_results = cast(List[AssayResultCreate], UNSET)

        def get_table_id() -> Union[Unset, None, str]:
            table_id = d.pop("tableId")
            return table_id

        try:
            table_id = get_table_id()
        except KeyError:
            if strict:
                raise
            table_id = cast(Union[Unset, None, str], UNSET)

        assay_results_bulk_create_request = cls(
            assay_results=assay_results,
            table_id=table_id,
        )

        return assay_results_bulk_create_request

    @property
    def assay_results(self) -> List[AssayResultCreate]:
        if isinstance(self._assay_results, Unset):
            raise NotPresentError(self, "assay_results")
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[AssayResultCreate]) -> None:
        self._assay_results = value

    @property
    def table_id(self) -> Optional[str]:
        if isinstance(self._table_id, Unset):
            raise NotPresentError(self, "table_id")
        return self._table_id

    @table_id.setter
    def table_id(self, value: Optional[str]) -> None:
        self._table_id = value

    @table_id.deleter
    def table_id(self) -> None:
        self._table_id = UNSET
