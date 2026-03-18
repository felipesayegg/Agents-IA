try:
	from .graph import build_trip_planner_graph
except ImportError:
	from graph import build_trip_planner_graph


def run_trip_planner(
	destination: str,
	trip_days: int,
	budget: float,
	interests: str,
	travel_style: str,
) -> str:
	graph = build_trip_planner_graph()
	state = {
		"destination": destination,
		"trip_days": trip_days,
		"budget": budget,
		"interests": interests,
		"travel_style": travel_style,
	}
	result = graph.invoke(state)
	return str(result.get("final_report", "Nao foi possivel gerar o roteiro."))
