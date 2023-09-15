import datetime
from airflow.utils.email import send_email
from urllib import parse
import os
import requests
import json

def telegram_notification(telegram_url, telegram_chat_id, message):
    data = {"chat_id": f"{telegram_chat_id}", "text": f"{message}" }
    msg = requests.post(telegram_url, headers={'Content-Type': 'application/json'},verify=False, data=json.dumps(data), timeout=3)

def success_email_notification(dag_id, dag_url, execution_date, subject, message, success_email_address_list):
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
                        <tr>
                        <td>DAG ID</td>
                        <td>{dag_id}</td>
                        </tr>
                        <tr>
                        <td>EXECUTION DATE</td>
                        <td>{execution_date}</td>
                        </tr>
                        <tr>
                        <td>DAG URL</td>
                        <td>{dag_url}</td>
                        </tr>
                    </table>
                    <br>
                    <br>
                    Thank You,<br>
                    DI-Unified Platform<br>
                    DI.UnifiedPlatform@airtel.com<br>
                    <br>
                    </body>
                    </html>"""
        send_email(to=success_email_address_list, subject=subject, html_content=body_html)
    except Exception as ex:
        print(ex)

class DISuccessCallback:

    def send_success_notification(context):
        print("sending success notification..")

        try:
            communication_mode: list = []
            if "success_communication_mode" in context['params']:
                communication_mode = context['params'].get('success_communication_mode')
            else:
                communication_mode = ["email"]
            print(f"communication_mode: {communication_mode}")

            host_name = context['params'].get('airflow_base_url')
            dag_id = context['dag_run'].dag_id
            run_id = context['dag_run'].run_id
            original_execution_date_ist = context.get('data_interval_end').astimezone(datetime.timezone(datetime.timedelta(seconds=19800))).strftime('%Y-%m-%dT%H:%M:%S')

            if 'email' in communication_mode:

                success_email_address_list: list = context['params'].get('success_email_address_list')
                subject = f"dag {dag_id} succeeded: {context['params'].get('env')}: {original_execution_date_ist}"
                message = f"DAG execution of {dag_id} success."

                execution_date = context.get('logical_date').strftime('%Y-%m-%dT%H:%M:%S%z')
                parsed_run_date = parse.quote(run_id)
                parsed_execution_date = parse.quote(execution_date)
                query = "run_id=" + parsed_run_date + "&execution_date=" + parsed_execution_date
                dag_url = f"{host_name}/dags/" + dag_id + f"/graph?{query}"

                success_email_notification(dag_id, dag_url, original_execution_date_ist, subject, message, success_email_address_list)

            if 'telegram' in communication_mode:

                telegram_url = context['params'].get('telegram_url')
                telegram_chat_id = context['params'].get('telegram_chat_id')
                message = f"Dag {dag_id} Succeeded : {context['params'].get('env')} \nRun Date: {original_execution_date_ist}"
                telegram_notification(telegram_url, telegram_chat_id, message)

        except Exception as ex:
            print(ex)
