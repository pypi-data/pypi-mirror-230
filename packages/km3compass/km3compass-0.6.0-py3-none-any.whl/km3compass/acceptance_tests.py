import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import matplotlib as mpl
import matplotlib.pyplot as plt

from .tools import align_z2weight, cart2spherical, rad2deg, append_spherical


class WrongDirectionsException(Exception):
    """Custom error when less than 4 cardinal points are found."""

    pass


class acceptance_test:

    """
    Perform acceptance test measurement.

    For this test, the data are expected to represent a
    measurement where the CLB was placed for a certain time in all
    of the 4 cardinal points (typically 60 seconds per point).


    Parameters:
    -----------
    obj: km3compass reader or calibration object
      Object with a df property, pointing to a dataframe
    moduleID: int
      DOM module ID inside the file.
    """

    def __init__(self, obj, moduleID):
        self.moduleID = moduleID
        self.df = obj.df
        self.df = self.df[self.df["DOMID"] == self.moduleID]

        # Align the acceleration with z axis
        self.df = align_z2weight(self.df)

        self.clustering()
        self.merge_points()
        self.convert2spherical()
        self.compute_residuals()

    def clustering(self, eps=0.015, min_samples=3):
        """
        Associate points together using DBSCAN algorithm.

        This method will associate the points based on the magnetic
        field measurement.  As we expect ~ 60 seconds per points, it
        should correspond to ~60 points, close in measurement. To
        achieve that, the Density Based Clustering of Application with
        Noise (DBSCAN) is used. In this case, noise should correspond
        to single point took during the rotation, therefor not
        belonging to one of the 4 cardinal directions.

        Parameters:
        -----------
        eps: float, default = 0.015
          distance at which two points are considered as related.
        min_samples: int, default = 3
          Minimum number of points to form a cluster core.
        """

        obj = DBSCAN(eps=eps, min_samples=min_samples)
        result = obj.fit(self.df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values)
        self.df["label"] = result.labels_
        clusters, counts = np.unique(self.df["label"], return_counts=True)
        print("DBSCAN : {} clusters found".format(len(clusters[clusters != -1])))
        for i, clus in enumerate(clusters):
            name = "cluster {}".format(clus)
            if clus == -1:
                name = "noise"
            print("\t- {} : {} points".format(name, counts[i]))

    def merge_points(self):
        """Compute mean value and std deviation for each cluster"""

        df_tmp = self.df[self.df["label"] != -1]
        df_mean = df_tmp.groupby("label").mean()
        df_std = df_tmp.groupby("label").std()

        colMean = {}
        colStd = {}

        for col in df_mean.columns:
            colMean[col] = col + "_mean"
        for col in df_std.columns:
            colStd[col] = col + "_std"

        df_mean.rename(columns=colMean, inplace=True)
        df_std.rename(columns=colStd, inplace=True)

        self.df_merged = pd.concat((df_mean, df_std), sort=True, axis=1)

    def compute_residuals(self):
        """
        Find closer cardinal point and compute residual.

        For each cluster, will try to find the closer point in theta dimension.
        Raise an error if it doesn't find 4 differents cardinal points.
        """

        cardPoint = np.linspace(0, 1.5 * np.pi, 4)
        card = self.df_merged.iloc[:4]["h_phi"].values % (2 * np.pi)
        cluster = self.df_merged.index.values
        ref = np.zeros(4)

        for i, p in enumerate(card):
            locRes = p % (2.0 * np.pi) - cardPoint
            locRes[np.where(locRes > np.pi)] -= 2 * np.pi

            ind = np.argmin(np.abs(locRes))
            ref[i] = cardPoint[ind]

        if len(np.unique(ref)) != 4:
            # raise Exception(
            raise WrongDirectionsException(
                "ERROR: Less than 4 differents points find for the residuals measurement\n"
                + "Reconstructed direction are: {}".format(ref)
            )

        res = card - ref
        res[np.where(res > np.pi)] -= 2 * np.pi
        yaw = np.mean(res)

        self.residuals = {"yaw": rad2deg(yaw), "module ID": self.moduleID}

        for i in range(4):
            self.residuals["res {}".format(i)] = rad2deg(res[i] - yaw)
            # self.residuals['res {} (dir)'.format(i)] = rad2deg(ref[i])

        df = pd.DataFrame(
            {
                "label": cluster,
                "card [deg]": rad2deg(ref),
                "residual [deg]": rad2deg(res - yaw),
            }
        )
        df = df.set_index("label")

        self.df_merged = pd.concat((self.df_merged, df), axis=1, sort=True)

    def convert2spherical(self):
        """Convert df and df_merged to spherical coordinates"""

        coord = cart2spherical(self.df[["AHRS_H0", "AHRS_H1", "AHRS_H2"]].values)
        self.df["h_r"] = coord[:, 0]
        self.df["h_theta"] = coord[:, 1]
        self.df["h_phi"] = coord[:, 2]

        coord = cart2spherical(
            self.df_merged[["AHRS_H0_mean", "AHRS_H1_mean", "AHRS_H2_mean"]].values
        )
        self.df_merged["h_r"] = coord[:, 0]
        self.df_merged["h_theta"] = coord[:, 1]
        self.df_merged["h_phi"] = coord[:, 2]

    def plot_results(self):
        """Plot a summary figure of the test procedure"""
        fig = plt.figure(figsize=(12, 7))
        fig.suptitle("Module {}".format(self.moduleID))
        spec = mpl.gridspec.GridSpec(ncols=2, nrows=2, height_ratios=[3, 1])

        axe = fig.add_subplot(spec[0])
        axez = fig.add_subplot(spec[2])

        axe.set_aspect("equal")
        axez.set_aspect("equal")
        axe.set_xlabel(r"$h_x$")
        axez.set_xlabel(r"$h_x$")
        axe.set_ylabel(r"$h_y$")
        axez.set_ylabel(r"$h_z$")

        for ind in np.unique(self.df["label"]):
            dfTmp = self.df[self.df["label"] == ind]
            label = "Cluster {}".format(ind)
            color = "C{}".format(ind)
            if ind == -1:
                label = "Noise"
                color = "gray"
            kwargs = dict(label=label, color=color, marker=".", alpha=1, zorder=9)
            axe.scatter(dfTmp["AHRS_H0"], dfTmp["AHRS_H1"], **kwargs)
            axez.scatter(dfTmp["AHRS_H0"], dfTmp["AHRS_H2"], **kwargs)
        axe.scatter(
            np.mean(self.df_merged["AHRS_H0_mean"]),
            np.mean(self.df_merged["AHRS_H1_mean"]),
            color="C9",
            marker="*",
            label="center",
            zorder=10,
        )

        axe.legend()
        axez.grid(zorder=0)
        axe.grid(zorder=0)

        axe = fig.add_subplot(spec[1], projection="polar")
        for i, ind in enumerate(np.unique(self.df["label"])):
            dfTmp = self.df[self.df["label"] == ind]
            label = "Cluster {}".format(ind)
            color = "C{}".format(ind)

            if ind == -1:
                label = "Noise"
                color = "gray"
                continue

            axe.scatter(
                self.df_merged.loc[ind]["h_phi"],
                self.df_merged.loc[ind]["h_r"],
                marker="x",
                s=120,
                zorder=12,
                color=color,
            )

            axe.scatter(
                dfTmp["h_phi"], dfTmp["h_r"], marker=".", s=1, zorder=11, color=color
            )

        ylim = axe.get_ylim()

        yaw = self.residuals["yaw"]
        for i, ind in enumerate(np.unique(self.df_merged.index)):
            card = self.df_merged.loc[ind]["card [deg]"]
            res = self.df_merged.loc[ind]["residual [deg]"]
            angle = (card + yaw) / 180.0 * np.pi

            if i == 0:
                axe.plot(
                    [angle, angle],
                    [0, ylim[1]],
                    color="gray",
                    label="Yaw shift, {:.2f}°".format(yaw),
                )
            else:
                axe.plot([angle, angle], [0, ylim[1]], color="gray")
            axe.fill_between(
                [angle, angle + res / 180.0 * np.pi],
                [0, 0],
                np.full(2, 0.9 * ylim[1]),
                edgecolor="k",
                facecolor="C{}".format(i),
                alpha=0.6,
                label="Res {} : {:.2f}°".format(i, res),
            )

        axe.set_xlabel(r"$\theta$")
        axe.legend()

        axe = fig.add_subplot(spec[3])

        for ind in np.unique(self.df["label"]):
            if ind == -1:
                continue
            dfTmp = self.df[self.df["label"] == ind]
            label = "Cluster {}".format(ind)
            color = "C{}".format(ind)
            bins = np.linspace(-15, 15, 61)

            values = (
                (dfTmp["h_theta"].values - self.df_merged.loc[ind]["h_theta"])
                / np.pi
                * 180.0
            )
            values[np.where(values > 180.0)] -= 360.0

            axe.hist(values, bins=bins, histtype="step", color=color, zorder=10)

        axe.set_xlabel("Spreading around cluster center [°]")
        axe.grid(zorder=0)
        plt.tight_layout()
        return fig
