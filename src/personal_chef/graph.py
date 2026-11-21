from langgraph.graph import END, START, StateGraph
from .agents import ask_for_clarification, assess_clarification, auto_select_recipe, choose_recipe_with_human, format_recipe_response, ingredient_recognition_agent, orchestrator_agent, recipe_adaptation_agent, recipe_evaluation_agent, recipe_research_agent, resolve_recipe_choice_from_message, summarize_thread
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
    graph.add_node("auto_select_recipe", auto_select_recipe)
    graph.add_node("human_choose_recipe", choose_recipe_with_human)
    graph.add_node("resolve_recipe_choice", resolve_recipe_choice_from_message)
    graph.add_node("adapt", recipe_adaptation_agent)
    graph.add_node("format_answer", format_recipe_response)
    graph.add_node("summarize_memory", summarize_thread)
    graph.add_edge(START, "orchestrator")

    def request_route(state: ChefState) -> str:
        return "resolve_choice" if state.get("selection_pending") and state.get("recipe_options") else "new_request"

    graph.add_conditional_edges("orchestrator", request_route, {"resolve_choice": "resolve_recipe_choice", "new_request": "recognize_ingredients"})
    graph.add_conditional_edges(
        "resolve_recipe_choice",
        lambda state: "adapt" if state.get("recipe") else "format_answer",
        {"adapt": "adapt", "format_answer": "format_answer"},
    )
    graph.add_edge("recognize_ingredients", "assess_clarification")

    def clarification_route(state: ChefState) -> str:
        return "ask" if state.get("clarification_needed") else "continue"

    graph.add_conditional_edges("assess_clarification", clarification_route, {"ask": "ask_for_clarification", "continue": "research"})
    graph.add_edge("research", "evaluate")
    def recipe_route(state: ChefState) -> str:
        options = state.get("recipe_options", [])
        if not options:
            return "none"
        return "choose" if len(options) > 1 else "automatic"

    graph.add_conditional_edges("evaluate", recipe_route, {"none": "format_answer", "choose": "human_choose_recipe", "automatic": "auto_select_recipe"})

    def choice_route(state: ChefState) -> str:
        return "waiting_for_choice" if state.get("selection_pending") else "adapt"

    graph.add_conditional_edges(
        "human_choose_recipe",
        choice_route,
        {"waiting_for_choice": "format_answer", "adapt": "adapt"},
    )
    graph.add_edge("auto_select_recipe", "adapt")
    graph.add_edge("adapt", "format_answer")
    graph.add_edge("format_answer", "summarize_memory")
    graph.add_edge("ask_for_clarification", "format_answer")
    graph.add_edge("summarize_memory", END)
    return graph.compile()


chef_graph = build_chef_graph()
