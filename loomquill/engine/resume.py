
def resume_plan(checkpoint, steps):
    """Return the steps that still have to run, given the checkpoint's outputs."""
    done = checkpoint.get("completed", {})
    return [s for s in steps if s.name not in done]
