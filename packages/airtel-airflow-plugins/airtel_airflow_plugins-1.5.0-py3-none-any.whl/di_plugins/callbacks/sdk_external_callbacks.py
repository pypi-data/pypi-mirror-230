from di_plugins.sensors.sensor_util import sense_objects


class SDKExternalCallback:
    """
    class that will have all the callbacks needed by airflow operators/dags
    """

    @staticmethod
    def select_branches(**kwargs):
        """
        this method fetches value for key `branches` from kwargs
        :param kwargs:
        :return: value for key `branches`
        """
        if 'branches' not in kwargs.keys():
            raise Exception('key - branches is not present in provided arguments')
        else:
            branches = kwargs['branches'].split(",")
            return list(map(lambda value: value.strip(), branches))

    @staticmethod
    def check_file_exists(**kwargs):
        elements = kwargs['objects']
        """
        this method checks if given file/directory exists in HDFS. It returns true if file/directory exists
        :param kwargs: 
        :return: true if file/directory exists in HDFS
        """
        if len(elements) > 1:
            raise Exception("only one object can be checked at a time")

        element = elements[0]
        done_files, pending_files = sense_objects("hdfs", kwargs, None)

        if len(done_files) == 1:
            done_file = done_files[0]
            return done_file == element
        else:
            return False
