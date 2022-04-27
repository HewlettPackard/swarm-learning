# <a name="GUID-5F7569ED-23C9-4091-A229-D7AF18E11A2E"/> Swarm Operator node \(SWOP\)

SWOP is responsible to execute tasks that are assigned to it. A SWOP node can execute only one task at a time. Other than executing tasks, SWOP provides multiple functionalities such as:

-   Managing Swarm Learning operations—SWOP eases the management of tasks because of its ability to perform control operations across the Swarm Learning network. It also uses a simple interface to manage operations from anywhere.

-   Scalability—SWOP can manage hundreds of Swarm Learning nodes with the use of one command.

-   Automation—SWOP eases automation of Swarm operations by providing APIs for scripting.

More information:

-   [SWOP architecture overview](SWOP_architecture_overview.md)
    -   [Launch Swarm Learning using SWOP](Launch_Swarm_Learning_using_SWOP.md)
        -   [SWOP profile schema](SWOP_profile_schema.md)
        -   [SWOP profile schema example](SWOP_profile_schema_example.md)
    -   [SWOP task](SWOP_task.md)
        -   [SWOP task schema](SWOP_task_schema.md)
        -   [SWOP task schema examples](SWOP_task_schema_examples.md)
            -   [Task for running ML nodes](Task_for_running_ML_nodes.md)
            -   [Task for building the user container](Task_for_building_the_user_container.md)
            -   [Task for creating a Docker volume of model program and data](Task_for_creating_a_Docker_volume_of_model_program_and_data.md)
            -   [Task for pulling a prebuilt Docker image](Task_for_pulling_a_prebuilt_Docker_image.md)
