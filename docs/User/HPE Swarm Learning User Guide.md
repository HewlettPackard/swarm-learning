# HPE Swarm Learning User Guide

Part Number: 10-191040-Q222

Published: April 2022

Edition: 1

© Copyright 2022, Hewlett Packard Enterprise Development LP

# Notices

The information contained herein is subject to change without notice. The only warranties for Hewlett Packard Enterprise products and services are set forth in the express warranty statements accompanying such products and services. Nothing herein should be construed as constituting an additional warranty. Hewlett Packard Enterprise shall not be liable for technical or editorial errors or omissions contained herein.

Confidential computer software. Valid license from Hewlett Packard Enterprise required for possession, use, or copying. Consistent with FAR 12.211 and 12.212, Commercial Computer Software, Computer Software Documentation, and Technical Data for Commercial Items are licensed to the U.S. Government under vendor's standard commercial license.

Links to third-party websites take you outside the Hewlett Packard Enterprise website. Hewlett Packard Enterprise has no control over and is not responsible for information outside the Hewlett Packard Enterprise website.

# Acknowledgments

All third-party trademarks are property of their respective owners.

# Contents

-   [Introduction to HPE Swarm Learning](1_Introduction.md)
-   [Swarm Learning architecture](Swarm_Learning_architecture.md)
    -   [User ML components](User_ML_components.md)
-   [Swarm Learning component interactions](Swarm_Learning_component_interactions.md)
-   [Swarm client interface - wheels package](Swarm_client_interface-wheels_package.md)
-   [Swarm Learning concepts](Swarm_Learning_concepts.md)
    -   [Working of a Swarm Learning node](Working_of_a_Swarm_Learning_node.md)
    -   [Adapting an ML program for Swarm Learning](Adapting_an_ML_program_for_Swarm_Learning.md)
    -   [How to Swarm enable an ML algorithm](How_to_Swarm_enable_an_ML_algorithm.md)
-   [Swarm Learning Command Interface](Swarm_Learning_Command_Interface.md)
    -   [SWCI APIs](SWCI_APIs.md)
-   [Swarm Operator node \(SWOP\)](Swarm_Operator_node_(SWOP).md)
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
-   [Examples](Examples.md)
    -   [MNIST](MNIST.md)
    -   [MNIST-PYT](MNIST-PYT.md)
    -   [CIFAR-10](CIFAR-10.md)
    -   [Credit card fraud detection](Credit_card_fraud_detection.md)
-   [Frequently asked questions](Frequently_asked_questions.md)
-   [Troubleshooting](Troubleshooting.md)
-   [GNU General Public License](GNU_General_Public_License.md)
-   [Support and other resources](Support_and_other_resources.md)
    -   [Accessing Hewlett Packard Enterprise Support](Accessing_Hewlett_Packard_Enterprise_Support.md)
    -   [Accessing updates](Accessing_updates.md)
    -   [Remote support](Remote_support.md)
    -   [Customer self repair](Customer_self_repair.md)
    -   [Warranty information](Warranty_information.md)
    -   [Regulatory information](Regulatory_information.md)
    -   [Documentation feedback](Documentation_feedback.md)
