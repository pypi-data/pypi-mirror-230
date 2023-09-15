import datetime
from airflow.utils.email import send_email
import requests
import json

def telegram_notification(telegram_url, telegram_chat_id, message):
    data = {"chat_id": f"{telegram_chat_id}", "text": f"{message}" }
    msg = requests.post(telegram_url, headers={'Content-Type': 'application/json'},verify=False, data=json.dumps(data), timeout=3)

def failure_email_notification(dag_id, failed_task_html, execution_date, subject, message, failure_email_address_list):
    try:

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

        body_html = f"""<!DOCTYPE html>
                    <html>
                    <head> {html_style}
                    </head>
                    <body>
                    Hi All,<br><br>{message}<br>
                    <table>
                        <tr>
                            <th style="background-color:Aquamarine">Property</th>
                            <th style="background-color:Aquamarine">Value</th>
                        </tr>
                        <tr><td>DAG ID</td>
                        <td>{dag_id}</td>
                        </tr>
                        </tr>
                        <tr>
                        <td>EXECUTION DATE</td>
                        <td>{execution_date}</td>
                        </tr>
                        </tr>
                        {failed_task_html}

                    </table>
                    <br>
                    <br>
                    Thank You,<br>
                    DI-Unified Platform<br>
                    DI.UnifiedPlatform@airtel.com<br>
                    <br>
                    </body>
                    </html>"""

        print("******")
        print(body_html)
        send_email(to=failure_email_address_list, subject=subject, html_content=body_html)

    except Exception as ex:
        print(ex)

class DIFailureCallback:

    def send_failure_notification(context):
        print("sending failure notification..")

        try:

            communication_mode: list = []
            if "failure_communication_mode" in context['params']:
                communication_mode = context['params'].get('failure_communication_mode')
            else:
                communication_mode = ["email"]

            print(f"communication_mode: {communication_mode}")

            dag_id = context['dag_run'].dag_id
            run_id = context['dag_run'].run_id
            original_execution_date_ist = context.get('data_interval_end').astimezone(datetime.timezone(datetime.timedelta(seconds=19800))).strftime('%Y-%m-%dT%H:%M:%S')

            tis = context['dag_run'].get_task_instances()
            failed_tasks = list(filter(lambda ti: ti.state is not None and str.lower(ti.state) == 'failed', tis))

            if 'email' in communication_mode:

                failure_email_address_list: list = context['params'].get('failure_email_address_list')
                subject = f"Dag {dag_id} failed : {context['params'].get('env')}: {original_execution_date_ist}"
                message = f"DAG execution of {dag_id} failed."

                failed_task_html = ' '.join(list(map(lambda task:
                f"""
                <tr>
                <td>{task.task_id} LOG URL</td>
                <td>{task.log_url}</td>
                </tr>
                """, failed_tasks)))

                failure_email_notification(dag_id, failed_task_html, original_execution_date_ist, subject, message, failure_email_address_list)

            if 'telegram' in communication_mode:

                telegram_url = context['params'].get('telegram_url')
                telegram_chat_id = context['params'].get('telegram_chat_id')
                failed_task_list = list(map(lambda task:task.task_id,failed_tasks))
                message = f"Dag {dag_id} failed : {context['params'].get('env')} \nRun Date: {original_execution_date_ist} \nFailed Task: {failed_task_list}"
                telegram_notification(telegram_url, telegram_chat_id, message)

        except Exception as ex:
            print(ex)