import datetime
from airflow.utils.email import send_email


class FailureCallback:

    def send_failure_email(context):
        print("sending failure email..")

        try:
            dag_id = context['dag_run'].dag_id
            run_id = context['dag_run'].run_id

            failure_email_address_list: list = context['params'].get('failure_email_address_list')
            data_interval_end_date_ist = context.get('data_interval_end').astimezone(
                datetime.timezone(datetime.timedelta(seconds=19800))).strftime('%Y-%m-%dT%H:%M:%S')

            tis = context['dag_run'].get_task_instances()
            failed_tasks = list(filter(lambda ti: ti.state is not None and str.lower(ti.state) == 'failed', tis))
            # log_url = failed_task.log_url
            # task_id = failed_task.task_id

            failed_task_html = ' '.join(list(map(lambda task:
                f"""
                <tr>
                <td>{task.task_id} LOG URL</td>
                <td>{task.log_url}</td>
                </tr>
                """, failed_tasks)))
            subject = f"Dag {dag_id} failed : {context['params'].get('env')}: {data_interval_end_date_ist}"
            message = f"DAG execution of {dag_id} failed."

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
                            <td>{data_interval_end_date_ist}</td>
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
