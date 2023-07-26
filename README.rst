.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://readthedocs.org/projects/resource-availability/badge/?version=latest
    :target: https://resource-availability.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/assuncaomarcos/resource-availability/badge.svg?branch=master
    :target: https://coveralls.io/github/assuncaomarcos/resource-availability?branch=master


Resource Availability Profile
=============================

.. inclusion-marker-do-not-remove

This Python library provides a data structure, termed **availability profile**,
for managing the availability of computing resources. The structure is handy
for simulations and experiments where one must track the compute cluster
resources allocated to jobs or tasks over time. The following provides
examples of using the discrete resource range, set, and profile,
which use `int` as data type, but the same concepts apply to profiles for
other data types.

One can use the discrete (`int`) range, set, and profile to track the
availability of, for instance, CPUs or cluster nodes. To create ranges
with resources `0..20` and `30..50` and add them to a set:

.. code-block:: python

    from availability.sets import DiscreteRange, DiscreteSet
    span1 = DiscreteRange(0, 20)
    span2 = DiscreteRange(30, 50)
    res_set = DiscreteSet([span1, span2])

Although you can create ranges and sets, one will not manipulate them
directly. For tracking the resources available over time, one will likely
use an availability profile (discrete or continuous, depending on the
type of resource they are dealing with). To create an availability profile
with a maximum capacity of 100 discrete resources for tracking the
availability of cluster nodes, for instance, one can use the following:

.. code-block:: python

    from availability.profile import DiscreteProfile
    profile = DiscreteProfile(max_capacity=100)

If you are using the profile in a task-scheduling simulation, you can
use the method `allocate_resources()` from the profile to remove the
resource range `0..10` assigned to the task:

.. code-block:: python

    profile.allocate_resources(
        resources=DiscreteSet(
            [DiscreteRange(0, 10)]
        ),
        start_time=0,
        end_time=10
    )

To find the time at which a task requiring `40` resources
for `50` time units can start:

.. code-block:: python

    slot = profile.find_start_time(
        quantity=40, ready_time=5, duration=50
    )

The returned `slot` will resemble:

.. code-block:: python

    TimeSlot(
        start_time=0,
        end_time=50,
        resources=DiscreteSet([DiscreteRange(10, 100)])
    )

The profile provides other methods, such as `check_availability()`
to check whether a given quantity of resources is available over a
given period:

.. code-block:: python

    slot = profile.check_availability(
        quantity=10, start_time=5, duration=50
    )

One can use the methods `free_time_slots()` or `scheduling_options()`
to obtain the list of time slots and resources available. The main
difference between them is that the time slots returned by the latter
may overlap as they represent all the scheduling possibilities for
scheduling a job, given the resource availability over the specified
period:

.. code-block:: python

    slots = profile.scheduling_options(
        start_time=10,
        end_time=100,
        min_duration=20,
        min_quantity=5
    )

The operations for querying the resources available during a period
return the complete set of resources available. This design allows a
user to implement their resource selection policy. However, you
can use `select_resources()` or `select_slot_resources()` to
select a given number of resources from a set or slot:

.. code-block:: python

    slot = profile.find_start_time(
        quantity=5, ready_time=0, duration=10
    )
    selected = profile.select_resources(
        resources=slot.resources, quantity=5)
    )
