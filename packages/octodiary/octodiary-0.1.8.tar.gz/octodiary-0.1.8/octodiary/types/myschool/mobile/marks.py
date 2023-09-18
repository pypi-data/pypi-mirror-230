from ...model import Type
from typing import Any, List, Optional


class PayloadItem(Type):
    id: Optional[int]
    value: Optional[str]
    values: Optional[Any]
    comment: Optional[str]
    weight: Optional[int]
    point_date: Optional[Any]
    control_form_name: Optional[str]
    comment_exists: Optional[bool]
    created_at: Optional[str]
    updated_at: Optional[str]
    criteria: Optional[Any]
    date: Optional[str]
    subject_name: Optional[str]
    subject_id: Optional[int]
    is_exam: Optional[bool]
    is_point: Optional[bool]
    original_grade_system_type: Optional[str]


class Marks(Type):
    payload: Optional[List[PayloadItem]] = None
