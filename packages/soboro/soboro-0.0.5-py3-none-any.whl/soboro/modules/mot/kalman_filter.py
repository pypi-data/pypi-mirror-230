import numpy as np
import scipy.linalg

__all__ = ["KalmanFilter"]


class KalmanFilter:
    """
    A simple Kalman filter for tracking bounding boxes in image space.

    The 8-dimensional state space

        x, y, a, h, vx, vy, va, vh

    contains the bounding box center position (x, y), aspect ratio a, height h,
    and their respective velocities.

    Object motion follows a constant velocity model. The bounding box location
    (x, y, a, h) is taken as direct observation of the state space (linear
    observation model).

    """

    def __init__(self, pos_weight: float = 1.0 / 20, vel_weight: float = 1.0 / 160):
        ndim, dt = 4, 1.0

        # Create Kalman filter model matrices.
        self._motion_mat: np.ndarray = np.eye(2 * ndim, 2 * ndim)
        for i in range(ndim):
            self._motion_mat[i, ndim + i] = dt
        self._update_mat: np.ndarray = np.eye(ndim, 2 * ndim)

        # Motion and observation uncertainty are chosen relative to the current
        # state estimate. These weights control the amount of uncertainty in
        # the model. This is a bit hacky.
        self._pos_weight: float = pos_weight
        self._vel_weight: float = vel_weight

        self.mean: np.ndarray = None
        self.covariance: np.ndarray = None

    def initiate(self, measurement: np.ndarray):
        """Create track from unassociated measurement.

        Parameters
        ----------
        measurement : ndarray
            Bounding box coordinates (x, y, a, h) with center position (x, y),
            aspect ratio a, and height h.

        Returns
        -------
        (ndarray, ndarray)
            Returns the mean vector (8 dimensional) and covariance matrix (8x8
            dimensional) of the new track. Unobserved velocities are initialized
            to 0 mean.

        """
        mean_pos = measurement
        mean_vel = np.zeros_like(mean_pos)
        self.mean = np.r_[mean_pos, mean_vel]

        std = [
            2 * self._pos_weight * measurement[3],
            2 * self._pos_weight * measurement[3],
            1e-2,
            2 * self._pos_weight * measurement[3],
            10 * self._vel_weight * measurement[3],
            10 * self._vel_weight * measurement[3],
            1e-5,
            10 * self._vel_weight * measurement[3],
        ]
        self.covariance = np.diag(np.square(std))
        
        return self.mean, self.covariance

    def predict(self):
        """Run Kalman filter prediction step.

        Parameters
        ----------
        Returns
        -------
        (ndarray, ndarray)
            Returns the mean vector and covariance matrix of the predicted
            state. Unobserved velocities are initialized to 0 mean.

        """
        std_pos = [
            self._pos_weight * self.mean[3],
            self._pos_weight * self.mean[3],
            1e-2,
            self._pos_weight * self.mean[3],
        ]
        std_vel = [
            self._vel_weight * self.mean[3],
            self._vel_weight * self.mean[3],
            1e-5,
            self._vel_weight * self.mean[3],
        ]
        motion_cov = np.diag(np.square(np.r_[std_pos, std_vel]))

        self.mean = np.dot(self.mean, self._motion_mat.T)
        self.covariance = (
            np.linalg.multi_dot((self._motion_mat, self.covariance, self._motion_mat.T))
            + motion_cov
        )

        return self.mean, self.covariance

    def project(self, mean: np.ndarray, covariance: np.ndarray):
        """Project state distribution to measurement space.

        Parameters
        ----------
        mean : ndarray
            The state's mean vector (8 dimensional array).
        covariance : ndarray
            The state's covariance matrix (8x8 dimensional).

        Returns
        -------
        (ndarray, ndarray)
            Returns the projected mean and covariance matrix of the given state
            estimate.

        """
        std = [
            self._pos_weight * mean[3],
            self._pos_weight * mean[3],
            1e-1,
            self._pos_weight * mean[3],
        ]
        innovation_cov = np.diag(np.square(std))

        mean = np.dot(self._update_mat, mean)
        covariance = np.linalg.multi_dot(
            (self._update_mat, covariance, self._update_mat.T)
        )
        return mean, covariance + innovation_cov

    def update(self, measurement: np.ndarray):
        """Run Kalman filter correction step.

        Parameters
        ----------
        mean : ndarray
            The predicted state's mean vector (8 dimensional).
        covariance : ndarray
            The state's covariance matrix (8x8 dimensional).
        measurement : ndarray
            The 4 dimensional measurement vector (x, y, a, h), where (x, y)
            is the center position, a the aspect ratio, and h the height of the
            bounding box.

        Returns
        -------
        (ndarray, ndarray)
            Returns the measurement-corrected state distribution.

        """
        projected_mean, projected_cov = self.project(self.mean, self.covariance)

        chol_factor, lower = scipy.linalg.cho_factor(
            projected_cov, lower=True, check_finite=False
        )
        kalman_gain = scipy.linalg.cho_solve(
            (chol_factor, lower),
            np.dot(self.covariance, self._update_mat.T).T,
            check_finite=False,
        ).T
        innovation = measurement - projected_mean

        self.mean = self.mean + np.dot(innovation, kalman_gain.T)
        self.covariance = self.covariance - np.linalg.multi_dot(
            (kalman_gain, projected_cov, kalman_gain.T)
        )
        return self.mean, self.covariance

    # def gating_distance(
    #     self,
    #     mean: np.ndarray,
    #     covariance: np.ndarray,
    #     measurements: np.ndarray,
    #     only_position: bool = False,
    #     metric: str = "maha",
    # ):
    #     """Compute gating distance between state distribution and measurements.
    #     A suitable distance threshold can be obtained from `chi2inv95`. If
    #     `only_position` is False, the chi-square distribution has 4 degrees of
    #     freedom, otherwise 2.
    #     Parameters
    #     ----------
    #     mean : ndarray
    #         Mean vector over the state distribution (8 dimensional).
    #     covariance : ndarray
    #         Covariance of the state distribution (8x8 dimensional).
    #     measurements : ndarray
    #         An Nx4 dimensional matrix of N measurements, each in
    #         format (x, y, a, h) where (x, y) is the bounding box center
    #         position, a the aspect ratio, and h the height.
    #     only_position : Optional[bool]
    #         If True, distance computation is done with respect to the bounding
    #         box center position only.
    #     Returns
    #     -------
    #     ndarray
    #         Returns an array of length N, where the i-th element contains the
    #         squared Mahalanobis distance between (mean, covariance) and
    #         `measurements[i]`.
    #     """
    #     mean, covariance = self.project(mean, covariance)
    #     if only_position:
    #         mean, covariance = mean[:2], covariance[:2, :2]
    #         measurements = measurements[:, :2]

    #     d = measurements - mean
    #     if metric == "gaussian":
    #         return np.sum(d * d, axis=1)
    #     elif metric == "maha":
    #         cholesky_factor = np.linalg.cholesky(covariance)
    #         z = scipy.linalg.solve_triangular(
    #             cholesky_factor, d.T, lower=True, check_finite=False, overwrite_b=True
    #         )
    #         squared_maha = np.sum(z * z, axis=0)
    #         return squared_maha
    #     else:
    #         raise ValueError("invalid distance metric")
