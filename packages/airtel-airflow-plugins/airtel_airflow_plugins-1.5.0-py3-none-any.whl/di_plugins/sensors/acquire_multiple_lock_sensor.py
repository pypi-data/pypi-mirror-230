from airflow.sensors.bash import BaseSensorOperator
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.utils.decorators import apply_defaults


class AcquireMultipleLockSensor(BaseSensorOperator):
    """
    AcquireLockSensor is a custom sensor that can be used for acquiring lock for a process. Lock metadata is stored in
    database table. Oracle database is supported for now.

    op_kwargs need to be provided are:
    system_name : name of the system for which lock is to be acquired
    partition_col_seq : partitions sequence for which lock is to be acquired
    db_table_name : name of database table in oracle where metadata is to be stored
    lakehouse_table_name : name of table in lakehouse for which lock is to be acquired
    db_connection_id: connection id

    """

    template_fields = ['op_kwargs']
    ui_color = '#fff'  # type: str
    ui_fgcolor = '#000'  # type: str

    @apply_defaults
    def __init__(self, *, op_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.op_kwargs = op_kwargs

    def create_hook(self, connection_id, hook_type='oracle'):
        if hook_type == 'oracle':
            return OracleHook(oracle_conn_id=connection_id)
        elif hook_type == 'generic':
            raise Exception(f"hook type not supported - {hook_type}")
            # return JdbcHook(jdbc_conn_id=connection_id)
        else:
            raise Exception(f"hook type not supported - {hook_type}")

    def try_acquire_lock(self, db_table_name, system_name, lakehouse_table_name, partition_values, db_connection_id,
                         hook_type):
        # "executing : AcquireLockSensor.try_acquire_lock()"
        hook = self.create_hook(connection_id=db_connection_id, hook_type=hook_type)

        #create partition value filter
        partition_value_string = []
        for value in partition_values:
            partition_value_string.append("'"+value.strip().lower()+"'")
        partition_filter= ",".join(partition_value_string)

        #check is any partition is in running state
        current_record = hook.get_first(
        sql=f"""select lower(partition_col) as partition_col,lower(state) as state, 
        lower(lakehouse_table_name) as lakehouse_table_name,lower(system) as system from {db_table_name}  
        where lower(partition_col) in ({partition_filter}) and lower(state)='running' 
        and lower(lakehouse_table_name)='{lakehouse_table_name}'""")

        if current_record is None:

            query = f"""
            update {db_table_name} set system = '{system_name}',
            lakehouse_table_name='{lakehouse_table_name}', 
            state='running',
            start_time=current_timestamp(9),
            end_time=null
            where lower(lakehouse_table_name)='{lakehouse_table_name}' 
            and lower(partition_col) in ({partition_filter})
            """
            hook.run(sql=query, autocommit=True)
        else:
            return False

        for value in partition_values:
            current_record = hook.get_first(
                sql=f"""select lower(partition_col) as partition_col,lower(state) as state, 
                lower(lakehouse_table_name) as lakehouse_table_name,lower(system) as system from {db_table_name}  
                where lower(partition_col)='{value}' and lower(lakehouse_table_name)='{lakehouse_table_name}'""")

            if current_record is None:
                # f"inserting data for lakehouse_table_name -'{lakehouse_table_name}', partition_col - '{partition_col}'"
                hook.run(
                    sql=f"""insert into {db_table_name}(system,lakehouse_table_name,partition_col,state,end_time) 
                    values('{system_name}','{lakehouse_table_name}','{value}','running',null)""", autocommit=True)

        status_check_record = hook.get_first(
                    sql=f"""select lower(state) from {db_table_name} 
                    where lower(lakehouse_table_name)='{lakehouse_table_name}' 
                    and lower(partition_col) in ({partition_filter})""")

        if status_check_record is None:
        # "could not acquire lock as some other process is running"
            return False
        elif status_check_record[0] == 'running':
        # f"lock acquired for - {partition_col} on table - {lakehouse_table_name}"
            return True
        else:
            raise Exception(f"undesirable condition, entry should be none or entry status should be running")

    def poke(self, context):
        try:
            # "executing : AcquireLockSensor.poke()")
            partition_col = self.op_kwargs["partition_col"]

            partition_values = list(
                map(lambda element: element.strip(), self.op_kwargs[partition_col].split(',')))

            # f"partition_col - {partition_col}"
            db_table_name = self.op_kwargs['db_table_name']
            system_name = self.op_kwargs['system_name'].lower()
            lakehouse_table_name = self.op_kwargs['lakehouse_table_name'].lower()

            db_connection_id = self.op_kwargs['db_connection_id']
            hook_type = self.op_kwargs.get('hook_type', 'oracle')

            lock_acquired = self.try_acquire_lock(db_table_name, system_name, lakehouse_table_name, partition_values,
                                                  db_connection_id,
                                                  hook_type)
            # f"is lock acquired - {lock_acquired}"
            # "exiting : AcquireLockSensor.poke()"
            return lock_acquired

        except Exception as ex:
            raise Exception("error occurred in MultipleAcquireLockSensor.poke", ex)
