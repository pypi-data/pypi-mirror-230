from airflow.utils.email import send_email
from airflow.models import DAG, TaskInstance
from typing import Any, Dict, List, Optional, Tuple
from textwrap import dedent
import datetime


class SLACallback:

    # dag: Parent DAG Object for the DAGRun in which tasks missed their SLA
    # task_list: String list (new-line separated, \n) of all tasks that missed their SLA since the last time that the sla_miss_callback ran.
    # blocking_task_list: Any task in the DAGRun(s) (with the same execution_date as a task that missed SLA) that is not in a SUCCESS state
    # at the time that the sla_miss_callback runs. i.e. 'running', 'failed'. These tasks are described as tasks that are blocking itself or
    # another task from completing before its SLA window is complete.
    # slas: List of SlaMiss objects associated with the tasks in the task_list parameter.
    # blocking_tis: List of the TaskInstance objects that are associated with the tasks in the blocking_task_list parameter.

    def send_sla_miss_email(dag: DAG,
                            task_list: str,
                            blocking_task_list: str,
                            slas: List[Tuple],
                            blocking_tis: List[TaskInstance]) -> None:

        try:

            """Send `SLA missed` alert """
            
            sla_miss_email_address_list: list = dag.params.get('sla_miss_email_address_list')
            
            html_style = """<style>
                    table {
                    font-family: arial, sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    }
                    td, th {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                    }
                    tr:nth-child(even) {
                    background-color: #dddddd;
                    }
                    </style>"""
            execution_date_utc = slas[0].execution_date
            execution_date_ist = execution_date_utc.astimezone(
                datetime.timezone(datetime.timedelta(seconds=19800))).strftime('%Y-%m-%dT%H:%M:%S')
            subject = f"SLA missed {dag.dag_id} on date - {execution_date_ist}"
            sla_missed = list(map(lambda
                                      sla: f"<tr><td>{sla.task_id}</td><td>{sla.execution_date}</td></tr>",
                                  slas))
            body_html = f"""<!DOCTYPE html>
                            <html>
                            <head> {html_style}
                            </head>
                            <body>
                            Hi All,<br><br>WARNING: Task SLA missed.<br>
                            <table>
                                <tr>
                                    <th style="background-color:Aquamarine">Property</th>
                                    <th style="background-color:Aquamarine">Value</th>
                                </tr>
                                <tr>
                            <td>DAG ID</td>
                            <td>{dag.dag_id}</td>
                        </tr>
                        <tr>
                            <td>EXECUTION DATE</td>
                            <td>{execution_date_ist}</td>
                        </tr>
                            </table>
                            <br><br>
                            SLA Missed task:
                            <br><br>
                            <table>
                                <tr>
                                    <th style="background-color:Aquamarine">Task Id</th>
                                    <th style="background-color:Aquamarine">Execution Date</th>
                                </tr>
                                {' '.join(sla_missed)}
                            </table>    
                            <br>
                            <br>
                            Thank You,<br>
                            DI-Unified Platform<br>
                            DI.UnifiedPlatform@airtel.com<br>
                            <br>
                            </body>
                            </html>"""
            send_email(to=sla_miss_email_address_list, subject=subject, html_content=body_html)
        except Exception as ex:
            print(ex)
