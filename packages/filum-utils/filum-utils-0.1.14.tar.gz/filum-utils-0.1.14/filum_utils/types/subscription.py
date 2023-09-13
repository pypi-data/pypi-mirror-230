from typing import TypedDict, Optional, Dict, Any


class TriggerData(TypedDict, total=False):
    segment_id: Optional[str]
    file_name: Optional[str]


class SubscriptionData(TypedDict, total=False):
    input_data: Optional[Dict[str, Any]]
    last_current_index: Optional[int]
    last_current_row: Optional[int]
    triggered_source: Optional[str]
    trigger_data: Optional[TriggerData]


class Subscription(TypedDict, total=False):
    id: str
    data: Optional[SubscriptionData]
