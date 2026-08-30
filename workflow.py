from langgraph.graph import StateGraph, START, END

from memory.state import AgentState
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory

from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.validation import validate_state


# Create agents
planning_agent = PlanningAgent()
research_agent = ResearchAgent()
analysis_agent = AnalysisAgent()
decision_agent = DecisionAgent()


# Create memory
short_term_memory = ShortTermMemory()
long_term_memory = LongTermMemory()


# Planning Agent
def planning_node(state: AgentState):
    plan = planning_agent.plan(
        state["user_query"]
    )

    return {
        "plan": plan
    }


# Research Agent
def research_node(state: AgentState):
    research_result = research_agent.research(
        state["user_query"],
        state["plan"]
    )

    return {
        "research_result": research_result
    }


# Analysis Agent
def analysis_node(state: AgentState):
    analysis = analysis_agent.analyze(
        state["user_query"],
        state["research_result"]
    )

    return {
        "analysis": analysis
    }


# Validation
def validation_node(state: AgentState):
    valid, message = validate_state(state)

    if not valid:
        return {
            "final_decision": message
        }

    return {
        "validation_status": message
    }


# Decision Agent
def decision_node(state: AgentState):

    # If validation failed, keep the error message
    if state.get("final_decision"):
        return {
            "final_decision": state["final_decision"]
        }

    final_decision = decision_agent.decide(
        state["user_query"],
        state["analysis"]
    )

    # Save only successful results
    if (
        not final_decision.startswith("Error")
        and "unable to convert" not in final_decision.lower()
    ):

        # Short-term memory
        short_term_memory.add(
            state["user_query"],
            final_decision
        )

        # Long-term memory
        long_term_memory.save(
            state["user_query"],
            final_decision
        )

    return {
        "final_decision": final_decision
    }


# Create workflow
graph = StateGraph(AgentState)


# Add nodes
graph.add_node("planning", planning_node)
graph.add_node("research", research_node)
graph.add_node("analysis", analysis_node)
graph.add_node("validation", validation_node)
graph.add_node("decision", decision_node)


# Workflow order
graph.add_edge(START, "planning")
graph.add_edge("planning", "research")
graph.add_edge("research", "analysis")
graph.add_edge("analysis", "validation")
graph.add_edge("validation", "decision")
graph.add_edge("decision", END)


# Compile
app = graph.compile()