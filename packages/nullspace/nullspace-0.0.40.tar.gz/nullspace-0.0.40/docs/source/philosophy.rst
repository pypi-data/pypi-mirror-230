==========
Philosophy
==========

If there are multiple end effectors need to coordinate move together. We manipulate those EE by define
a virtual obejct among those EE.

If we define it in a seriously way. 

This object could have a orientation and position if a frame fix on it.

If the number of end effector(num)

N = 2, X is a line

N = 3, X is a triangle

N = 4, X is a tetrahedron


In a prioritized tasks definition:
We might have a tasks from higher priority to lower:

  1.fixed distance between each end effectors, that's conbination of N
  2.there is a target position of Object
  3.there is a target orientation Object

These tasks could be achieved by nullspace method

Examples
--------

Humanoid robot hand(3 fingers)
There is a triangle between 3 fingers. If you coordinate control task 2 and 3 together by considering lead of screw, bottle cap could be moved very
decently.
