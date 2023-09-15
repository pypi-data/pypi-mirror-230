import csv
from math import sin, cos, tan, acos, asin, atan, atan2, radians, degrees, pi, sqrt
from pathlib import Path


def calculate_theta_phi(hexapod_rot_y, hexapod_rot_z):
    hexapod_rot_y = radians(hexapod_rot_y)  # Rotation angle around the x-axis [radians]
    hexapod_rot_z = radians(hexapod_rot_z)  # Rotation angle around the y-axis [radians]

    theta = degrees(acos(cos(hexapod_rot_y) * cos(hexapod_rot_z)))
    phi = degrees(-asin(sin(hexapod_rot_z) / sqrt(1 - pow(cos(hexapod_rot_y) * cos(hexapod_rot_z), 2))))

    return theta, phi

def test_fov_calculation():

    filepath = Path("~/20230613_IAS_ZONDA.csv").expanduser()

    with filepath.open() as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            y = row["GIAS_HEX_USER_R_Y"]
            z = row["GIAS_HEX_USER_R_Z"]

            calculate_theta_phi(float(y), float(z))
