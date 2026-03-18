from langgraph.graph import END, StateGraph

try:
	from .nodes import (
		attractions_node,
		cost_estimator_node,
		enrich_destination_node,
		planner_writer_node,
		weather_forecast_node,
	)
	from .state import TripPlannerState
except ImportError:
	from nodes import (
		attractions_node,
		cost_estimator_node,
		enrich_destination_node,
		planner_writer_node,
		weather_forecast_node,
	)
	from state import TripPlannerState


def build_trip_planner_graph():
	workflow = StateGraph(TripPlannerState)

	workflow.add_node("enrich_destination", enrich_destination_node)
	workflow.add_node("weather_forecast", weather_forecast_node)
	workflow.add_node("attractions", attractions_node)
	workflow.add_node("cost_estimator", cost_estimator_node)
	workflow.add_node("planner_writer", planner_writer_node)

	workflow.set_entry_point("enrich_destination")
	workflow.add_edge("enrich_destination", "weather_forecast")
	workflow.add_edge("weather_forecast", "attractions")
	workflow.add_edge("attractions", "cost_estimator")
	workflow.add_edge("cost_estimator", "planner_writer")
	workflow.add_edge("planner_writer", END)

	return workflow.compile()
