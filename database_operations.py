from database import get_connection


def create_workflow(user_query):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO workflows (user_query, status)
        VALUES (%s, %s)
        RETURNING workflow_id;
        """,
        (user_query, "Running")
    )

    workflow_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return workflow_id


def update_workflow(workflow_id, status, final_decision=None, execution_time=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE workflows
        SET status = %s,
            final_decision = %s,
            execution_time = %s
        WHERE workflow_id = %s;
        """,
        (status, final_decision, execution_time, workflow_id)
    )

    connection.commit()
    cursor.close()
    connection.close()


def save_agent_activity(
    workflow_id,
    agent_name,
    status,
    result=None,
    execution_time=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO agent_activities
        (
            workflow_id,
            agent_name,
            status,
            result,
            execution_time,
            started_at,
            completed_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
        """,
        (
            workflow_id,
            agent_name,
            status,
            result,
            execution_time
        )
    )

    connection.commit()
    cursor.close()
    connection.close()