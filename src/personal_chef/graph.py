from langgraph.graph import END, START, StateGraph
from .agents import ask_for_clarification, assess_clarification, format_recipe_response, ingredient_recognition_agent, orchestrator_agent, recipe_adaptation_agent, recipe_evaluation_agent, recipe_research_agent, summarize_thread
from .state import ChefInput, ChefOutput, ChefState


def build_chef_graph():
    """Build a single-input recipe flow with clarification and memory steps."""
    graph = StateGraph(ChefState, input_schema=ChefInput, output_schema=ChefOutput)
    graph.add_node("orchestrator", orchestrator_agent)
    graph.add_node("recognize_ingredients", ingredient_recognition_agent)
    graph.add_node("assess_clarification", assess_clarification)
    graph.add_node("ask_for_clarification", ask_for_clarification)
    graph.add_node("research", recipe_research_agent)
    graph.add_node("evaluate", recipe_evaluation_agent)
    graph.add_node("adapt", recipe_adaptation_agent)
    graph.add_node("format_answer", format_recipe_response)
    graph.add_node("summarize_memory", summarize_thread)
    graph.add_edge(START, "orchestrator")

    graph.add_edge("orchestrator", "recognize_ingredients")
    graph.add_edge("recognize_ingredients", "assess_clarification")

    def clarification_route(state: ChefState) -> str:
        return "ask" if state.get("clarification_needed") else "continue"

    graph.add_conditional_edges("assess_clarification", clarification_route, {"ask": "ask_for_clarification", "continue": "research"})
    graph.add_edge("ask_for_clarification", "summarize_memory")
    graph.add_edge("research", "evaluate")
    graph.add_edge("evaluate", "adapt")
    graph.add_edge("adapt", "format_answer")
    graph.add_edge("format_answer", "summarize_memory")
    graph.add_edge("summarize_memory", END)
    return graph.compile()


chef_graph = build_chef_graph()
