import flytekit as fl
from flytekit import conditional
from flytekit.core.task import Echo

echo_radius = Echo(name="noop", inputs={"radius": float})


@fl.task
def calculate_circle_circumference(radius: float) -> float:
    return 2 * 3.14 * radius  # Task to calculate the circumference of a circle


@fl.task
def calculate_circle_area(radius: float) -> float:
    return 3.14 * radius * radius  # Task to calculate the area of a circle
