from langgraph.graph import StateGraph, START, END

from memory.state import AgentState
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory

from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.validation import validate_state

from database_operations import (
    create_workflow,
    update_workflow,
    save_agent_activity
)

import time


# ============================================================
# CREATE AGENTS
# ============================================================

planning_agent = PlanningAgent()
research_agent = ResearchAgent()
analysis_agent = AnalysisAgent()
decision_agent = DecisionAgent()


# ============================================================
# CREATE MEMORY
# ============================================================

short_term_memory = ShortTermMemory()
long_term_memory = LongTermMemory()


# ============================================================
# PLANNING AGENT
# ============================================================

def planning_node(state: AgentState):

    start_time = time.time()

    plan = planning_agent.plan(
        state["user_query"]
    )

    execution_time = time.time() - start_time

    workflow_id = state.get("workflow_id")

    if workflow_id:
        save_agent_activity(
            workflow_id=workflow_id,
            agent_name="Planning Agent",
            status="Completed",
            result=plan,
            execution_time=execution_time
        )

    return {
        "plan": plan
    }


# ============================================================
# RESEARCH AGENT
# ============================================================

def research_node(state: AgentState):

    start_time = time.time()

    research_result = research_agent.research(
        state["user_query"],
        state["plan"]
    )

    execution_time = time.time() - start_time

    workflow_id = state.get("workflow_id")

    if workflow_id:
        save_agent_activity(
            workflow_id=workflow_id,
            agent_name="Research Agent",
            status="Completed",
            result=research_result,
            execution_time=execution_time
        )

    return {
        "research_result": research_result
    }


# ============================================================
# ANALYSIS AGENT
# ============================================================

def analysis_node(state: AgentState):

    start_time = time.time()

    analysis = analysis_agent.analyze(
        state["user_query"],
        state["research_result"]
    )

    execution_time = time.time() - start_time

    workflow_id = state.get("workflow_id")

    if workflow_id:
        save_agent_activity(
            workflow_id=workflow_id,
            agent_name="Analysis Agent",
            status="Completed",
            result=analysis,
            execution_time=execution_time
        )

    return {
        "analysis": analysis
    }


# ============================================================
# VALIDATION
# ============================================================

def validation_node(state: AgentState):

    start_time = time.time()

    valid, message = validate_state(state)

    execution_time = time.time() - start_time

    workflow_id = state.get("workflow_id")

    if workflow_id:

        status = "Completed" if valid else "Failed"

        save_agent_activity(
            workflow_id=workflow_id,
            agent_name="Validation",
            status=status,
            result=message,
            execution_time=execution_time
        )

    if not valid:
        return {
            "final_decision": message
        }

    return {
        "validation_status": message
    }


# ============================================================
# DECISION AGENT
# ============================================================

def decision_node(state: AgentState):

    start_time = time.time()

    # If validation failed, keep the error message
    if state.get("final_decision"):

        final_decision = state["final_decision"]

    else:

        final_decision = decision_agent.decide(
            state["user_query"],
            state["analysis"]
        )

    execution_time = time.time() - start_time

    workflow_id = state.get("workflow_id")

    if workflow_id:

        status = "Completed"

        if (
            final_decision.startswith("Error")
            or "unable to convert" in final_decision.lower()
        ):
            status = "Failed"

        save_agent_activity(
            workflow_id=workflow_id,
            agent_name="Decision Agent",
            status=status,
            result=final_decision,
            execution_time=execution_time
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

    # Update workflow in PostgreSQL
    if workflow_id:

        total_execution_time = (
            time.time() - state.get("workflow_start_time", time.time())
        )

        workflow_status = "Completed"

        if (
            final_decision.startswith("Error")
            or "unable to convert" in final_decision.lower()
        ):
            workflow_status = "Failed"

        update_workflow(
            workflow_id=workflow_id,
            status=workflow_status,
            final_decision=final_decision,
            execution_time=total_execution_time
        )

    return {
        "final_decision": final_decision
    }


# ============================================================
# CREATE WORKFLOW
# ============================================================

graph = StateGraph(AgentState)


# Add nodes
graph.add_node("planning", planning_node)
graph.add_node("research", research_node)
graph.add_node("analysis", analysis_node)
graph.add_node("validation", validation_node)
graph.add_node("decision", decision_node)


# ============================================================
# WORKFLOW ORDER
# ============================================================

graph.add_edge(START, "planning")
graph.add_edge("planning", "research")
graph.add_edge("research", "analysis")
graph.add_edge("analysis", "validation")
graph.add_edge("validation", "decision")
graph.add_edge("decision", END)


# ============================================================
# COMPILE
# ============================================================

app = graph.compile()


# ============================================================
# RUN WORKFLOW WITH DATABASE LOGGING
# ============================================================

def run_workflow(user_query: str):

    workflow_id = create_workflow(user_query)

    start_time = time.time()

    initial_state = {
        "user_query": user_query,
        "workflow_id": workflow_id,
        "workflow_start_time": start_time
    }

    result = app.invoke(initial_state)

    return result