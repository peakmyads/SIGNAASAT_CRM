# path: services/workload_service.py

from services.db_service import get_all


editors = [
    "Editor 1",
    "Editor 2",
    "Editor 3"
]


def get_least_busy_editor():

    tasks_df = get_all("Work_Assignments")

    workload = {}

    for editor in editors:

        if tasks_df.empty:
            workload[editor] = 0
        else:
            workload[editor] = len(
                tasks_df[
                    (tasks_df["editor"] == editor) &
                    (tasks_df["status"] == "Pending")
                ]
            )

    least_busy = min(workload, key=workload.get)

    return least_busy
