import datetime
from airflow.utils.email import send_email
from urllib import parse

class SuccessCallback:

    def send_success_email(context):
        print("sending success email..")

        try:
            host_name = context['params'].get('airflow_base_url')
            dag_id = context['dag_run'].dag_id
            run_id = context['dag_run'].run_id
            success_email_address_list: list = context['params'].get('success_email_address_list')
            data_interval_end_date_ist = context.get('data_interval_end').astimezone(
                datetime.timezone(datetime.timedelta(seconds=19800))).strftime('%Y-%m-%dT%H:%M:%S')
            execution_date = context.get('logical_date').strftime('%Y-%m-%dT%H:%M:%S%z')

            parsed_run_date = parse.quote(run_id)
            parsed_execution_date = parse.quote(execution_date)
            query = "run_id=" + parsed_run_date + "&execution_date=" + parsed_execution_date
            dag_url = f"{host_name}/dags/" + dag_id + f"/graph?{query}"
            print(f"dag url : {dag_url}")

            subject = f"dag {dag_id} succeeded: {context['params'].get('env')}: {data_interval_end_date_ist}"

            message = f"DAG execution of {dag_id} success."

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
                            <td>{data_interval_end_date_ist}</td>
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
