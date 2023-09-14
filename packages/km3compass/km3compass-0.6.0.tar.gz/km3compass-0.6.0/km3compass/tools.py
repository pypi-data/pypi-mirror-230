#!/usr/bin/env python3
import struct
import numpy as np
import scipy.spatial.transform as transform
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


def load_CSK(fname):
    """
    Load CSK file into a dictionnary

    Parameters:
    -----------
    fname: str
      Path to the CSK file
    """
    with open(fname, "rb") as f:
        frames = {
            "time": [],
            "AHRS_A0": [],
            "AHRS_A1": [],
            "AHRS_A2": [],
            "AHRS_H0": [],
            "AHRS_H1": [],
            "AHRS_H2": [],
            "temp": [],
            "humid": [],
            "DOMID": [],
        }
        while True:
            try:
                framedwords = [f.read(4) for j in range(0, 62)]
                if framedwords[-1] == None or len(framedwords[-1]) < 4:
                    return frames
                if framedwords[1] != b"TMCH":
                    continue
                time = (
                    struct.unpack("!I", framedwords[4])[0]
                    + struct.unpack("!I", framedwords[5])[0] / 62500 / 1000.0
                )
                g_x, g_y, g_z = (
                    struct.unpack("!f", framedwords[47])[0],
                    struct.unpack("!f", framedwords[48])[0],
                    struct.unpack("!f", framedwords[49])[0],
                )
                h_x, h_y, h_z = (
                    struct.unpack("!f", framedwords[53])[0],
                    struct.unpack("!f", framedwords[54])[0],
                    struct.unpack("!f", framedwords[55])[0],
                )
                temp = struct.unpack(">H", framedwords[56][0:2])[0] * 0.01
                humid = struct.unpack(">H", framedwords[56][2:4])[0] * 0.01
                frames["DOMID"].append(int(framedwords[6].hex(), 16))
                frames["time"].append(time)
                frames["AHRS_A0"].append(g_x)
                frames["AHRS_A1"].append(g_y)
                frames["AHRS_A2"].append(g_z)
                frames["AHRS_H0"].append(h_x)
                frames["AHRS_H1"].append(h_y)
                frames["AHRS_H2"].append(h_z)
                frames["temp"].append(temp)
                frames["humid"].append(humid)

            except Exception as E:
                print(E)
                return frames


def cart2AHRS(a, h):
    """
    Convert to AHRS accelerometer and magnetometer data.

    Equivalent to the implementation in JPP ``JDETECTOR::JCompass::JCompass``
    https://common.pages.km3net.de/jpp/classJDETECTOR_1_1JCompass.html

    Parameters:
    -----------
    a: numpy array (n,3) shapes
      Accelerometer data.
    h: numpy array (n,3) shapes
      magnetometer data.

    Return:
    -------
    tuple with (roll, pith, yaw)
    """

    # Invert axis for CLB being upside down in optical module
    # Done to math JPP implementation

    a[:, 1] = -a[:, 1]
    a[:, 2] = -a[:, 2]

    h[:, 1] = -h[:, 1]
    h[:, 2] = -h[:, 2]

    roll = np.arctan2(-a[:, 1], -a[:, 2])
    pitch = np.arctan2(a[:, 0], np.sqrt(a[:, 1] ** 2 + a[:, 2] ** 2))

    yaw = np.arctan2(
        h[:, 2] * np.sin(roll) - h[:, 1] * np.cos(roll),
        h[:, 0] * np.cos(pitch)
        + h[:, 1] * np.sin(pitch) * np.sin(roll)
        + h[:, 2] * np.sin(pitch) * np.cos(roll),
    )

    return roll, pitch, yaw


def append_AHRS(df):
    """
    Add AHRS coordinates to dataframe

    Parameters:
    -----------
    df: pandas DataFrame
      Dataframe containing the cartesian coordinates

    Return:
    -------
    Dataframe with AHRS coordinates
    """

    roll, pitch, yaw = cart2AHRS(
        df[["AHRS_A0", "AHRS_A1", "AHRS_A2"]].values,
        df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values,
    )

    df["roll"] = rad2deg(roll)
    df["pitch"] = rad2deg(pitch)
    df["yaw"] = rad2deg(yaw)

    return df


def align_z2weight(
    df,
    a_keys=["AHRS_A0", "AHRS_A1", "AHRS_A2"],
    h_keys=["AHRS_H0", "AHRS_H1", "AHRS_H2"],
):
    """
    Align acceleration and magnetic field to have acceleration along z.

    Should be used only when DOM is at rest (or close to).

    Parameters:
    -----------
    df: pandas DataFrame
      Dataframe containing the acceleration and magnetic field data
    a_keys: list[str]
      Keys for acceleration
    h_keys: list[str]
      Keys for magnetic field
    """

    a = df[a_keys].values
    h = df[h_keys].values

    roll, pitch, yawMag = cart2AHRS(a, h)
    hnew = np.zeros(np.shape(h))
    anew = np.zeros(np.shape(a))

    for i in range(np.shape(hnew)[0]):
        r = transform.Rotation.from_rotvec([roll[i], pitch[i], 0])
        mat = r.as_matrix()
        hnew[i] = mat.dot(h[i])
        anew[i] = mat.dot(a[i])

    for i, key in enumerate(a_keys):
        df[key] = anew[:, i]
    for i, key in enumerate(h_keys):
        df[key] = hnew[:, i]

    return df


def cart2spherical(xyz):
    """
    Convert cartesian coordinates to spherical coordinates.

    Parameters:
    -----------
    xyz: numpy array
      cartesian coordinates, shape (n,3)

    Return:
    -------
    (r,theta,phi): numpy array
      r, phi, theta coordinates, shape (n,3). Theta is defined as the
      elevation angle with x:y plane (zenith), theta is from axe X (azimuth).
    """
    ptsnew = np.zeros(xyz.shape)
    xy = xyz[:, 0] ** 2 + xyz[:, 1] ** 2

    ptsnew[:, 0] = np.sqrt(xy + xyz[:, 2] ** 2)
    ptsnew[:, 1] = np.arctan2(
        xyz[:, 2], np.sqrt(xy)
    )  # for elevation angle defined from XY-plane up
    ptsnew[:, 2] = np.arctan2(xyz[:, 1], -xyz[:, 0])

    return ptsnew


def append_spherical(
    df, keys=["AHRS_H0", "AHRS_H1", "AHRS_H2"], target_keys=["r", "theta", "phi"]
):
    """
    Add spherical coordinate to dataframe

    Parameters:
    -----------
    df: pandas DataFrame
      Dataframe containing the cartesian coordinates
    keys: list of string, len 3
      List of keys to use for cartesian coordinates, xyz order
    target_keys: list of string, len 3
      List of keys to be used for spherical coordinates, r theta phi order

    Return:
    -------
    Dataframe with spherical coordinates
    """

    new = cart2spherical(df[keys].values)
    df[target_keys[0]] = new[:, 0]
    df[target_keys[1]] = rad2deg(new[:, 1])
    df[target_keys[2]] = rad2deg(new[:, 2])

    return df


def rad2deg(rad):
    """Convert radians to degrees"""
    return rad / np.pi * 180.0


def plot_raw_results(
    df,
    a_keys=["AHRS_A0", "AHRS_A1", "AHRS_A2"],
    h_keys=["AHRS_H0", "AHRS_H1", "AHRS_H2"],
    title="",
):
    """
    Draw a summary plot of the file content


    """

    fig = plt.figure(figsize=(16, 7))
    if title != "":
        fig.suptitle(title)
    spec = mpl.gridspec.GridSpec(3, 3, fig)

    axeX = fig.add_subplot(spec[0, 0])
    axeY = fig.add_subplot(spec[1, 0])
    axeZ = fig.add_subplot(spec[2, 0])

    axeXY = fig.add_subplot(spec[:2, 1])
    axeXZ = fig.add_subplot(spec[2, 1])
    axeXY.set_aspect("equal")
    axeXZ.set_aspect("equal")

    axeA = fig.add_subplot(spec[:, 2], projection="polar")
    axeA.set_xlim(-0.6 * np.pi, 0.6 * np.pi)
    axeA.set_ylim(
        0.5, 1.5
    )  # More than 1.5G acceleration for DOM would be surprising ...
    axeA.set_xticks(np.linspace(-0.5 * np.pi, 0.5 * np.pi, 5))
    axeA.set_yticks(np.linspace(0.5, 1.5, 3))
    module_IDs = np.unique(df["DOMID"])

    for mod in module_IDs:
        df_tmp = df[df["DOMID"] == mod]
        kwargs = dict(zorder=10, marker=".")
        axeX.scatter(df_tmp["datetime"], df_tmp["AHRS_H0"], **kwargs)
        axeY.scatter(df_tmp["datetime"], df_tmp["AHRS_H1"], **kwargs)
        axeZ.scatter(df_tmp["datetime"], df_tmp["AHRS_H2"], **kwargs)

        axeXY.scatter(df_tmp["AHRS_H0"], df_tmp["AHRS_H1"], **kwargs)
        axeXZ.scatter(
            df_tmp["AHRS_H0"],
            df_tmp["AHRS_H2"],
            label="Module {}".format(mod),
            **kwargs
        )
        a = cart2spherical(df_tmp[["AHRS_A0", "AHRS_A1", "AHRS_A2"]].values)
        a_r, a_phi, a_theta = a[:, 0], a[:, 1], a[:, 2]
        axeA.scatter(a_phi, a_r, **kwargs)

    tmin = []
    tmax = []
    for ax in [axeX, axeY, axeZ]:
        tmin.append(ax.get_xlim()[0])
        tmax.append(ax.get_xlim()[1])
    tmin = np.min(tmin)
    tmax = np.max(tmax)
    for ax in [axeX, axeY, axeZ]:
        ax.set_xlim([tmin, tmax])

    axeX.set_xticklabels([])
    axeY.set_xticklabels([])
    axeXY.set_xticklabels([])

    for tick in axeZ.get_xticklabels():
        tick.set_rotation(45)

    axeX.set_ylabel("X mag. field [G]")
    axeY.set_ylabel("Y mag. field [G]")
    axeZ.set_ylabel("Z mag. field [G]")
    axeZ.set_xlabel("Datetime")

    axeXY.set_ylabel("Y mag. field [G]")
    axeXZ.set_ylabel("Z [G]")
    axeXZ.set_xlabel("X mag. field [G]")
    axeA.set_xlabel(
        "Acceleration direction [deg]\n90° for straigth DOM, -90° for straigh CLB"
    )
    axeA.set_ylabel("Acceleration norm [g]")

    axeX.grid(zorder=0)
    axeY.grid(zorder=0)
    axeZ.grid(zorder=0)
    axeXY.grid(zorder=0)
    axeXZ.grid(zorder=0)

    plt.tight_layout()

    boxZ = axeZ.get_position()
    boxXY = axeXY.get_position()
    boxXZ = axeXZ.get_position()

    boxXZ.x0 = boxXY.x0
    boxXZ.x1 = boxXY.x1
    boxXZ.y0 = boxZ.y1 - boxXZ.height
    boxXZ.y1 = boxZ.y1
    axeXZ.set_position(boxXZ)

    axeXZ.legend(bbox_to_anchor=(0.5, -2), loc="upper center")

    return fig


def resample_df(df, period="10min", on="datetime", origin=None):
    """
    Resample df to a certain period, DOM wise

    Parameters:
    -----------
    df: pandas DataFrame
      Dataframe to resample
    period: string, default = 10min
      New sampling period, check pandas.DataFrame.resample for more details
    on: string
      Column to be used as datetime
    origin:
      Initial time stamps use as base for the new sampling.
      If None, will take the smallest datetime.

    Return:
    -------
    Resampled dataframe
    """

    if origin is None:
        origin = np.min(df[on])

    new_df = None

    for modID in np.unique(df["DOMID"]):
        df_tmp = df[df["DOMID"] == modID]
        df_tmp = df_tmp.resample(period, on=on, origin=origin).mean(numeric_only=True)

        new_df = pd.concat((new_df, df_tmp))

    return new_df


def moving_average(a, r=[5, 5]):
    """
    Compute moving average using a specified range

    Exclude the central point from the computation

    Parameters:
    -----------
    a: numpy array
      array to averaged
    r: list size 2
      number of elements before and after
    """

    anew = np.zeros(a.shape)
    n = np.zeros(a.shape, dtype="int16")

    for i in range(1, r[0] + 1):
        anew[i:] += a[:-i]
        n[i:] += 1

    for i in range(1, r[0] + 1):
        anew[:-i] += a[i:]
        n[:-i] += 1

    return anew / n


def modID2mac(moduleID):
    """Convert int module ID to str mac address"""
    moduleID = int(moduleID)
    mac_address = "0800" + hex(moduleID)[2:]
    mac_address = (
        mac_address[:2]
        + ":"
        + mac_address[2:4]
        + ":"
        + mac_address[4:6]
        + ":"
        + mac_address[6:8]
        + ":"
        + mac_address[8:10]
        + ":"
        + mac_address[10:]
    )
    return mac_address
