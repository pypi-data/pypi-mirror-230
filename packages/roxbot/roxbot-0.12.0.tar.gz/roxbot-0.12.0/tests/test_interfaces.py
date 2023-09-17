import os
from pytest import approx

# set GPS_REF to a known value
os.environ["GPS_REF"] = "51.0, 6.0"

from roxbot.interfaces import Pose


def test_pose():
    p = Pose(1, 2, 3)

    assert p.xy == (1, 2)


def test_pose_from_gps():
    p = Pose.from_gps(51, 6, 90)

    assert p.xy == (0, 0)
    assert p.theta == approx(0)
