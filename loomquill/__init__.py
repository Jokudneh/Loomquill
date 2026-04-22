"""
This package contains all of the most common abstractions you'll need to write Flyte workflows and extend Flytekit.

## Basic Authoring


These are the essentials needed to get started writing tasks and workflows.

- task
- workflow
- kwtypes
- current_context
- ExecutionParameters
- FlyteContext
- map_task
- ImperativeWorkflow
- create_node
- NodeOutput
- FlyteContextManager

> [!NOTE]
> **Local Execution**
>
> Tasks and Workflows can both be locally run, assuming the relevant tasks are capable of local execution.
> This is useful for unit testing.


### Branching and Conditionals


Branches and conditionals can be expressed explicitly in Flyte. These conditions are evaluated
in the flyte engine and hence should be used for control flow. "dynamic workflows" can be used to perform custom conditional logic not supported by flytekit.


### Customizing Tasks & Workflows

- TaskMetadata - Wrapper object that allows users to specify Task
- Resources - Things like CPUs/Memory, etc.
- WorkflowFailurePolicy - Customizes what happens when a workflow fails.
- PodTemplate - Custom PodTemplate for a task.

#### Dynamic and Nested Workflows

See the Dynamic module for more information.


##### Signaling

- approve
- sleep
- wait_for_input

Scheduling

- CronSchedule
- FixedRate

##### Notifications

- Email
- PagerDuty
- Slack

##### Reference Entities

- get_reference_entity
- LaunchPlanReference
- TaskReference
- WorkflowReference
- reference_task
- reference_workflow
- reference_launch_plan

##### Core Task Types

- SQLTask
- ContainerTask
- PythonFunctionTask
- PythonInstanceTask
- LaunchPlan

##### Secrets and SecurityContext

- Secret
- SecurityContext


##### Common Flyte IDL Objects

