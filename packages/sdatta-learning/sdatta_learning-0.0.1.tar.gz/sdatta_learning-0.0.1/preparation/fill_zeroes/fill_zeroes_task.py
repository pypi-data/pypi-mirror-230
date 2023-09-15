from clearml import Task


if __name__ == "__main__":

    model_snapshots_path = 'azure://palmersstorageaccount.blob.core.windows.net/sdatta-analysis'

    Task.add_requirements("./requirements.txt")

    task = Task.init(project_name='palmers/data-processing-palmers_tasks', task_name='fill_zeroes_task',
                     output_uri=model_snapshots_path,
                     task_type=Task.TaskTypes.training,
                     auto_connect_frameworks=False
                     , auto_resource_monitoring=False)

    task.set_base_docker('palmerscr.azurecr.io/clean/py3.9:1.0.0')
    task.execute_remotely(queue_name='ultra-high-cpu')

    configuration_dict = {}
    configuration = task.connect_configuration(name="stores", configuration=configuration_dict)
    print('a')
    print(configuration)
    print(configuration_dict)

