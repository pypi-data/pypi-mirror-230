import numpy as np
from scipy.spatial.transform import Rotation as R

'''
Vector Guidance methods for interception and soft landing scenario.
author: Iftach Naftaly, 2.2023, iftahnaf@gmail.com
'''


class VectorGuidance():

    @staticmethod
    def _minimum_positive_real_root(f: list, min_tgo: float=0.01) -> float:
        '''
        Description
        ----------

        Returns the minimum-positive-real-root(mprr) of give polynom.

        Parameters
        ----------
        f : list 
                The polynom
        min_tgo : float : [s]
                Minimum allowed value for Tgo 

        Output
        ----------
        mprr: float : [s]
                Minimum-positive-real-root of f 

        '''
        roots = np.roots(f)
        real_sol = np.real(roots)[abs(np.imag(roots)) < 1e-5]
        real_sol = np.real(real_sol)[np.real(real_sol) > 0]
        if len(real_sol) > 1:
            mprr = np.min(real_sol)
        elif len(real_sol) == 0:
            mprr = min_tgo
        else:
            mprr = real_sol
        return mprr[0]

    @classmethod
    def interception_controller_bounded(cls, r: np.ndarray, v: np.ndarray, rho_u: float, tgo: float, g: np.ndarray) -> np.ndarray:
        '''
        Description
        ----------

        Returns the bounded interception controller in local frame.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        rho_u: float : [m/s^2]
                Maximum acceleration norm of the pursuer 
        tgo: float : [s]
                Time-to-go
        g: np.array(1,3) : [m/s^2]
                Gravity vector 

        Output
        ----------
        u: np.array(1,3) : [m/s^2]
                The desired acceleration command generated from bounded interception method

        '''
        u = rho_u * (r + tgo*v)/(np.linalg.norm(r + tgo*v)) + g
        return u

    @classmethod
    def interception_tgo_bounded(cls, r: np.ndarray, v: np.ndarray, rho_u: float, rho_w: float, min_tgo: float=0.01) -> float:
        '''
        Description
        ----------

        Returns the tgo for bounded interception scenario.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        rho_u: float : [m/s^2]
                Maximum acceleration norm of the pursuer 
        rho_w: float : [m/s^2]
                Maximum acceleration norm of the target 

        min_tgo: float (default - 0.01) : [sec]
                Minimum allowed value for Tgo

        Output
        ----------
        tgo: float : [s]
                Time-to-go 

        '''
        drho = rho_u - rho_w
        f = [(drho**2)/4, 0, -np.linalg.norm(v)**2, -2 *
             np.dot(np.transpose(r), v), -np.linalg.norm(r)**2]
        tgo = cls._minimum_positive_real_root(f, min_tgo)
        return tgo

    @classmethod
    def interception_controller_lq(cls, r: np.ndarray, v: np.ndarray, tgo: float, k: float, g: np.ndarray) -> np.ndarray:
        '''
        Description
        ----------

        Returns the LQ interception controller in local frame.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        tgo: float : [s]
                Time-to-go
        k: float 
                weight of the integral part in the LQ cost function
        g: np.array(1,3) : [m/s^2]
                Gravity vector

        Output
        ----------
        u: np.array(1,3) : [m/s^2]
                The desired acceleration command generated from LQ interception method

        '''
        u = (tgo / (k + (1/3)*tgo**3)) * (r + tgo*v) + g
        return u

    @classmethod
    def interception_tgo_lq(cls, r: np.ndarray, v: np.ndarray, um: float, min_tgo: float=0.01):
        '''
        Description
        ----------

        Returns the tgo for LQ interception scenario.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        um: float : [m/s^2]
                Maximum acceleration norm of the pursuer 
        min_tgo: float (default - 0.01) : [sec]
                Minimum allowed value for Tgo

        Output
        ----------
        tgo: float : [s]
                Time-to-go 

        '''
        f = [(um**2)/9, 0, -np.linalg.norm(v)**2, -2 *
             np.dot(np.transpose(r), v), -np.linalg.norm(r)**2]
        tgo = cls._minimum_positive_real_root(f, min_tgo)
        return tgo

    @classmethod
    def soft_landing_controller_lq(cls, r: np.ndarray, v: np.ndarray, tgo: float, g: np.ndarray) -> np.ndarray:
        '''
        Description
        ----------

        Returns the LQ soft landing controller in local frame.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        tgo: float : [s]
                Time-to-go
        g: np.array(1,3) : [m/s^2]
                Gravity vector

        Output
        ----------
        u: np.array(1,3) : [m/s^2]
                The desired acceleration command generated from LQ soft landing method

        '''
        u = (1 / (tgo**2)) * (6*r + 4*tgo*v) + g
        return u

    @classmethod
    def soft_landing_tgo_lq(cls, r: np.ndarray, v: np.ndarray, um: float, g: np.ndarray, min_tgo: float=0.01) -> float:
        '''
        Description
        ----------

        Returns the tgo for LQ soft landing scenario.

        Parameters
        ----------
        r : np.array(1,3) : [m]
                Relative position vector - r_{target} - r_{pursuer} 
        v : np.array(1,3) : [m/s]
                Relative velocity vector - v_{target} - v_{pursuer} 
        um: float : [m/s^2]
                Maximum acceleration norm of the pursuer
        g: np.array(1,3) : [m/s^2]
                Gravity vector 
        min_tgo: float (default - 0.01) : [sec]
                Minimum allowed value for Tgo

        Output
        ----------
        tgo: float : [s]
                Time-to-go 

        '''
        f1 = [(um**2)/4, 0, -4*np.linalg.norm(v)**2, -12 *
              np.dot(np.transpose(r), v), -9*np.linalg.norm(r)**2]
        f2 = [(um**2)/4, 0, -np.linalg.norm(v)**2, -6 *
              np.dot(np.transpose(r), v), -9*np.linalg.norm(r)**2]
        tgo_f1 = cls._minimum_positive_real_root(f1, min_tgo)
        tgo_f2 = cls._minimum_positive_real_root(f2, min_tgo)
        um_1 = np.linalg.norm((2/tgo_f1**2) * (3*r + 2*tgo_f1*v) + g)
        um_2 = np.linalg.norm((-2/tgo_f1**2) * (3*r + tgo_f1*v) + g)
        return tgo_f1 if um_1 > um_2 else tgo_f2


class Utilities():

    @staticmethod
    def acceleration_to_quaternion(u: np.ndarray, yaw: float=0.0) -> np.ndarray:
        '''
        Description
        ----------

        Transform the acceleration command in local frame to quaternion in body frame

        Parameters
        ----------
        u : np.array(1,3) : [m]
                acceleration command in local frame 

        Output
        ----------
        q: np.array(1,4) : [s]
                quaternion rotation from current attitude to the desired attitude 

        '''
        projected_xb_des = np.array([np.cos(yaw), np.sin(yaw), 0])
        zb_des = u / np.linalg.norm(u)
        yb_des = np.cross(zb_des, projected_xb_des) / \
            np.linalg.norm(np.cross(zb_des, projected_xb_des))
        xb_des = np.cross(yb_des, zb_des) / \
            np.linalg.norm(np.cross(yb_des, zb_des))

        rotm = np.array([xb_des[0], yb_des[0], zb_des[0]],
                        [xb_des[1], yb_des[1], zb_des[1]],
                        [xb_des[2], yb_des[2], zb_des[2]])

        q = R.from_matrix(rotm).as_quat()
        return q
