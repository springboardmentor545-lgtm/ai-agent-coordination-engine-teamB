from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import get_connection
from workflow import run_workflow


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="AI Agent Coordination & Decision Engine",
    description="Enterprise Multi-Agent Workflow and Decision Automation Platform"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class PromptRequest(BaseModel):
    question: str


class PromptResponse(BaseModel):
    agent_name: str
    response: str


# ============================================================
# FRONTEND HOME PAGE
# ============================================================

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("frontend/index.html")


# ============================================================
# ASK AI
# ============================================================

@app.post("/ask", response_model=PromptResponse)
def ask_agent(request: PromptRequest):

    result = run_workflow(request.question)

    return PromptResponse(
        agent_name="Multi-Agent System",
        response=result.get(
            "final_decision",
            "No final decision was generated."
        )
    )


# ============================================================
# DASHBOARD DATA
# ============================================================

@app.get("/dashboard/data")
def dashboard_data():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # WORKFLOWS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                workflow_id,
                user_query,
                status,
                final_decision,
                execution_time,
                created_at
            FROM workflows
            ORDER BY workflow_id DESC
            LIMIT 50;
            """
        )

        workflow_rows = cursor.fetchall()

        workflows = []

        for row in workflow_rows:

            workflows.append(
                {
                    "workflow_id": row[0],
                    "user_query": row[1],
                    "status": row[2],
                    "final_decision": row[3],
                    "execution_time": row[4],
                    "created_at": row[5]
                }
            )


        # ----------------------------------------------------
        # AGENT ACTIVITIES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                activity_id,
                workflow_id,
                agent_name,
                status,
                result,
                execution_time,
                started_at,
                completed_at
            FROM agent_activities
            ORDER BY activity_id DESC
            LIMIT 100;
            """
        )

        activity_rows = cursor.fetchall()

        activities = []

        for row in activity_rows:

            activities.append(
                {
                    "activity_id": row[0],
                    "workflow_id": row[1],
                    "agent_name": row[2],
                    "status": row[3],
                    "result": row[4],
                    "execution_time": row[5],
                    "started_at": row[6],
                    "completed_at": row[7]
                }
            )


        # ----------------------------------------------------
        # DASHBOARD METRICS
        # ----------------------------------------------------

        total_workflows = len(workflows)

        completed_workflows = sum(
            1
            for workflow in workflows
            if workflow["status"] == "Completed"
        )

        failed_workflows = sum(
            1
            for workflow in workflows
            if workflow["status"] == "Failed"
        )

        execution_times = [
            workflow["execution_time"]
            for workflow in workflows
            if workflow["execution_time"] is not None
        ]

        if execution_times:

            average_execution = (
                sum(execution_times)
                / len(execution_times)
            )

        else:

            average_execution = 0


        # ----------------------------------------------------
        # RETURN DASHBOARD DATA
        # ----------------------------------------------------

        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "average_execution": average_execution,
            "workflows": workflows,
            "activities": activities
        }


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# STATIC FRONTEND FILES
# ============================================================

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)