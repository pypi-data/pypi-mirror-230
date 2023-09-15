from clearml.automation import PipelineController


if __name__ == '__main__':

    controller = PipelineController(project="palmers/pipelines", name='fill_zeroes_pipe', version='0.0.1', docker="palmerscr.azurecr.io/clean/py3.9:1.0.0")
    controller.set_default_execution_queue("ultra-high-cpu")


    controller.add_parameter('dict_machines', {'1' : {1: [1, 11, 111]}, '2' : {2:[2, 22, 22]}, '3': {3:[3, 33, 333]}})

    training_nodes = []
    for key_machine, dlist in controller.get_parameters()['dict_machines'].items():
        print(f"stores: {key_machine}")
        task_name = f'test_task_{key_machine}'
        training_nodes.append(task_name)
        controller.add_step(name=task_name,
                            base_task_id="d4be3803647d45a2b08f2aaa75404e7b",
                            execution_queue="ultra-high-cpu",
                            configuration_overrides={"stores": dlist})


    controller.start()
    print('pipeline completed')


