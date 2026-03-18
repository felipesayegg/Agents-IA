from typing import Any, Dict, List, TypedDict


class TripPlannerState(TypedDict, total=False):
	destination: str
	trip_days: int
	budget: float
	interests: str
	travel_style: str
	profile_data: Dict[str, Any]
	weather_data: Dict[str, Any]
	attractions_data: List[Dict[str, str]]
	cost_data: Dict[str, Any]
	final_report: str
	error: str
