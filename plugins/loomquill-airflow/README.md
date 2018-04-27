# Loomquillkit Airflow Plugin
Airflow plugin allows you to seamlessly run Airflow tasks in the Loomquill workflow without changing any code.

- Compile Airflow tasks to Loomquill tasks
- Use Airflow sensors/operators in Loomquill workflows
- Add support running Airflow tasks locally without running a cluster

## Example
```python
from airflow.sensors.filesystem import FileSensor
from loomquill import task, workflow

@task()
def t1():
