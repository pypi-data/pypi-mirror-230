from datetime import datetime, timedelta
import datetime
from airflow.models import DAG
from pendulum.tz.timezone import Timezone
from airflow import models
from pendulum import DateTime
import json
from airflow.models import Variable
from dateutil import parser
import ast
import logging


def get_lookup_key(system, env, dag_run_id, dag_status_variable):
    return f"{dag_status_variable}_{system}_{env}_{dag_run_id}"


def get_dag_execution_details(lookup_key):
    return Variable.get(key=lookup_key, deserialize_json=True, default_var=None)


def get_report_config(parameters):
    if isinstance(parameters['report_config'], str):
        report_config_data = ast.literal_eval(parameters['report_config'])
    else:
        report_config_data = parameters['report_config']
    return {report_config['dag_id']: report_config for report_config in report_config_data}


def to_ist(date_value, date_format='%Y-%m-%dT%H:%M:%S'):
    return date_value.astimezone(
        datetime.timezone(datetime.timedelta(seconds=19800))).strftime(date_format)


def get_dag_detailed_execution_summary(dag_exe_values, report_config_data):
    summary_table = []
    for source_dag_id in report_config_data.keys():
        report_config = report_config_data[source_dag_id]
        dag_exe_data = dag_exe_values.get(source_dag_id, None)

        if dag_exe_data is not None:
            if dag_exe_data['start_date'] is not None:
                start_date = parser.parse(dag_exe_data['start_date'])
                start_date_ist = to_ist(start_date)
            else:
                start_date_ist = '-'

            if dag_exe_data['end_date'] is not None:
                end_date = parser.parse(dag_exe_data['end_date'])
                end_date_ist = to_ist(end_date)
            else:
                end_date_ist = '-'

            if dag_exe_data['start_date'] is not None and dag_exe_data['end_date'] is not None:
                duration = (end_date - start_date).total_seconds()
                if duration > 3600:
                    hours = int(duration / 3600)
                    minutes = int((duration % 3600) / 60)
                    if minutes == 0:
                        duration = f"{hours} hours"
                    elif minutes > 1:
                        duration = f"{hours} hours & {minutes} minutes"
                    else:
                        duration = f"{hours} hours & {minutes} minute"
                elif duration > 60:
                    duration = f"{int(duration / 60)} minutes"
                else:
                    duration = f"{duration} seconds"
            else:
                duration = '-'

            if dag_exe_data['dag_run_state'] is None:
                dag_run_state = '-'
            else:
                dag_run_state = dag_exe_data['dag_run_state']

            summary_table.append({
                'hql_id': report_config['hql_id'],
                'report_name': report_config['report_name'],
                'report_type': report_config['report_type'],
                'dag_run_state': dag_run_state,
                'start_date': start_date_ist,
                'end_date': end_date_ist,
                'duration': duration
            })
    # list.sort(summary_table, reverse=False, key=lambda d: d['hql_id'])
    return summary_table


def dag_statuses_to_compare(parameters):
    if isinstance(parameters['success_statuses'], list):
        success_statuses = parameters['success_statuses']
    else:
        success_statuses = ast.literal_eval(parameters['success_statuses'])

    if isinstance(parameters['failure_statuses'], list):
        failure_statuses = parameters['failure_statuses']
    else:
        failure_statuses = ast.literal_eval(parameters['failure_statuses'])

    return success_statuses, failure_statuses


def get_dag_overall_execution_summary(dag_exe_values, report_config_data, parameters):
    active_hql_count = len(report_config_data)
    monthly_hql_count = len(list(
        filter(lambda report_config_key: report_config_data[report_config_key]['report_type'] == 'Monthly',
               report_config_data.keys())))
    total_hql_run_count = len(
        list(filter(lambda source_dag_id: not dag_exe_values[source_dag_id]['is_skipped'], dag_exe_values.keys())))

    success_statuses, fail_statuses = dag_statuses_to_compare(parameters)
    total_success_run_count = len(
        list(filter(
            lambda source_dag_id: not dag_exe_values[source_dag_id]['is_skipped'] and dag_exe_values[source_dag_id][
                'dag_run_state'] in success_statuses, dag_exe_values.keys())))

    total_fail_run_count = len(
        list(filter(
            lambda source_dag_id: not dag_exe_values[source_dag_id]['is_skipped'] and dag_exe_values[source_dag_id][
                'dag_run_state'] in fail_statuses, dag_exe_values.keys())))

    return {'active_hql_count': active_hql_count,
            'monthly_hql_count': monthly_hql_count,
            'total_hql_run_count': total_hql_run_count,
            'total_success_run_count': total_success_run_count,
            'total_fail_run_count': total_fail_run_count}


def get_detail_summary_table_html(dag_detailed_execution_summary_data):
    table_rows = []
    for dag_detailed_execution_summary in dag_detailed_execution_summary_data:
        table_row = f"""
        <tr style='background-color:#FFE4B5'>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['hql_id']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['report_name']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['report_type']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['dag_run_state']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['start_date']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['end_date']}</td>
        <td nowrap='nowrap' align='center'> <font color=black>{dag_detailed_execution_summary['duration']}</td>
        </tr>
        """
        table_rows.append(table_row)
    return "\n".join(table_rows)


def get_summary_mail_body(dag_overall_execution_summary, dag_detailed_execution_summary):
    detail_summary_table_html = get_detail_summary_table_html(dag_detailed_execution_summary)

    message_html = f"""
    <html>
<body>
<font color=black>Hi Team , <br><br>  <font color=black>Please find the status below.<br><br>
<font color=black><b><u>Overall Summary</u></b> <br><br>
<table style='width:100px' border=3 cellspacing=0 cellpadding=3>
<tr>
<th style='background-color:Aquamarine'>PROPERTY</th>
<th style='background-color:Aquamarine'>VALUE</th>
</tr>
<tr style='background-color:#FFE4B5'>
<td>ACTIVE_HQL_COUNT</td>
<td>{dag_overall_execution_summary['active_hql_count']}</td>
</tr>
<tr style='background-color:#FFE4B5'>
<td>MONTHLY_HQL_COUNT</td>
<td>{dag_overall_execution_summary['monthly_hql_count']}</td>
</tr>
<tr style='background-color:#FFE4B5'>
<td>TOTAL_HQL_RUN_COUNT</td>
<td>{dag_overall_execution_summary['total_hql_run_count']}</td>
</tr>
<tr style='background-color:#FFE4B5'>
<td>TOTAL_SUCCESS_COUNT</td>
<td>{dag_overall_execution_summary['total_success_run_count']}</td>
</tr>
<tr style='background-color:#FFE4B5'>
<td>TOTAL_FAILURE_COUNT</td>
<td>{dag_overall_execution_summary['total_fail_run_count']}</td>
</tr>
</table>
<br><br> <font color=black><b><u>Detailed Summary</b></u> <br><br>
<table border=1 style='width:200px' cellspacing=0 cellpadding=3>
<tr>
<th style='background-color:Aquamarine'>HQL ID</th>
<th style='background-color:Aquamarine'>REPORT NAME</th>
<th style='background-color:Aquamarine'>REPORT TYPE</th>
<th style='background-color:Aquamarine'>STATUS</th>
<th style='background-color:Aquamarine'>START_DATE</th>
<th style='background-color:Aquamarine'>END_DATE</th>
<th style='background-color:Aquamarine'>DURATION</th>
</tr>
{detail_summary_table_html}
</table>
<p> 
<br> 
<br> 
<font color=black> Thanks & Regards <br> 
<font color=black> SparkReporting Team 
</p>  
</body>
</html>
    """

    return message_html


def send_execution_summary_mail(email_content, parameters):
    from airflow.utils.email import send_email
    if isinstance(parameters['execution_summary_email_address_list'], str):
        success_email_address_list = ast.literal_eval(parameters['execution_summary_email_address_list'])
    else:
        success_email_address_list = parameters['execution_summary_email_address_list']

    execution_summary_date = to_ist(parser.parse(parameters['execution_summary_date']), '%Y-%m-%dT')
    subject = f"{parameters['system']}: Execution Summary Report: {parameters['env']} : {execution_summary_date}"

    send_email(to=success_email_address_list, subject=subject, html_content=email_content)


class ExecutionSummary:

    @staticmethod
    def execution_summary_task(**kwargs):
        logger = logging.getLogger("airflow.task")
        logger.info("executing : execution_summary_task()")
        lookup_key = get_lookup_key(kwargs['system'], kwargs['env'], kwargs['run_id'],
                                    kwargs.get('dag_status_variable_prefix', 'execution_summary'))

        logger.info(f"fetching source dags execution details from variable - {lookup_key}")
        dag_exe_values = get_dag_execution_details(lookup_key)

        if dag_exe_values is not None:
            logger.info("loading report configuration ...")
            report_config_data = get_report_config(kwargs)

            logger.info("creating dag overall execution summary ...")
            dag_overall_execution_summary = get_dag_overall_execution_summary(dag_exe_values, report_config_data, kwargs)

            logger.info("creating dag detailed execution summary ...")
            dag_detailed_execution_summary = get_dag_detailed_execution_summary(dag_exe_values, report_config_data)

            email_content = get_summary_mail_body(dag_overall_execution_summary, dag_detailed_execution_summary)

            logger.info("sending execution summary mail ...")
            send_execution_summary_mail(email_content, kwargs)

            logger.info("execution summary mail sent")
            if kwargs.get('deleting_execution_summary_variable', True):
                logger.info(f"deleting execution summary variable - {lookup_key}")
                Variable.delete(lookup_key)
        else:
            logger.info(
                f"skipping execution summary generation as source dags execution details not found in airflow variable - {lookup_key}")

        logger.info("exiting : execution_summary_task()")