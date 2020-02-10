"""
Sleep Fanout (Dynamic) Example
===============================

Fan out N core-sleep leaves in parallel using @dynamic.
n_children is a runtime input — the @dynamic task runs in a container to
expand the subworkflow, then each leaf runs as core-sleep (no pod).

Requires flytekitplugins-sleep in the container image. The ImageSpec below
installs it from the local wheel via copy + pip install.

Usage (remote):
    python sleep_fanout_dynamic.py
"""

