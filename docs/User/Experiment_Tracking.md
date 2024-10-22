# Experiment tracking

In 2.2.0 release, experiment tracking feature is introduced to compare different model training runs. This would be useful
for doing hyper-parameter tuning and choosing the best run.

![Experiment Tracking](/docs/User/GUID-279F77EB-D49D-406A-A710-851AD388FDF6-high.png)

To know the hyper parameters used and compare the training metrics (like accuracy) and loss of different training runs of
an SLM-UI project, user needs to provide the details of a particular experiment in the Project > Tasks > Execute task of
the SLM-UI using the following fields.

-   **Annotation/Description of the experiment** – This field allows user to enter the description of the experiment. User
can provide verbose details and annotate a given experimental run with details of the hyper parameters used in this
particular run.
-   **Select to save the experiment** – This field allows users to select the checkbox to save the experiment.

