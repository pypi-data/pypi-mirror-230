from airflow.sensors.bash import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from di_plugins.sensors.sensor_util import sense_objects
from di_plugins.sensors.sensor_util import check_skipped
from dateutil import parser


class LocalFileSensor(BaseSensorOperator):
    """sensor for local file system. This sensor checks for files/directory existence in local.
    it calls a shell script over ssh and collect status for files/directory from shell script.

    shell scrip for files/directory sensing takes positional arguments as:
    -ol   | --object_list  : A mandatory parameter to specify list of objects to sense
    -fs   | --file_system  : A mandatory parameter to specify file system local or local
    -ot   | --object_type  : An optional parameter to specify object type, file or directory


    by default this sensor check files in local. To sense directory in local then user can provide
    object_type attribute in op_kwargs with directory as value.

    shell script takes comma separated list of files/directory and logs status of each file/directory
    in a specific pattern.

    example:
    if file /opt/data/table1/_SUCCESS does not exist then it logs message as:
    PENDING >> /opt/data/table1/_SUCCESS

    it will log message as when file exists:
    DONE >> /opt/data/table1/_SUCCESS

    sensor reads these messages to check what all files/directories are available.


    sensor parameters:
    op_kwargs : this argument is template
        ssh_conn_id -> mandatory parameter for ssh connection
        script -> mandatory parameter, shell script path on remote machine
        objects -> mandatory parameter, comma separated list of files/directories to sense
        object_type -> optional parameter, type off object to sense in local i.e. files or directories. default is files
        detailed_log -> optional parameter, possible value is yes. if provided then shell command and output will be logged
        timeout -> optional parameter, used for ssh command execution timeout. default is None

    """
    template_fields = ['op_kwargs']
    ui_color = '#9B59B6'  # type: str
    ui_fgcolor = '#000'  # type: str

    @apply_defaults
    def __init__(self, *, op_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.op_kwargs = op_kwargs

        """set initial total_done_files and pending_files"""
        self.total_done_files = None
        self.pending_files = None

    def poke(self, context):
        is_skip_enable = self.op_kwargs.get('skip_enable', False)
        skip_enable = (isinstance(is_skip_enable, bool) and is_skip_enable is True) or (
                isinstance(is_skip_enable, str) and eval(is_skip_enable) is True)

        if skip_enable:
            check_skipped(parser.parse(self.op_kwargs.get('start_date')),
                          self.op_kwargs.get('skip_after_minutes', 2880), skip_enable)
            
        done_files, self.pending_files = sense_objects("local", self.op_kwargs, self.pending_files)

        if len(done_files) != 0:
            if self.total_done_files is None:
                """initialize total_done_files"""
                self.total_done_files = set([])
            for file in done_files:
                self.total_done_files.add(file)
            print(f"done files - {', '.join(self.total_done_files)} ")

        if len(self.pending_files) != 0:
            print(f"pending files - {', '.join(self.pending_files)} ")
            return False
        else:
            return True
