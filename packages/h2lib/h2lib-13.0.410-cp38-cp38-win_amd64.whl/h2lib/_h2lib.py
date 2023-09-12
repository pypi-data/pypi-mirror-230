import os
import numpy as np
import shutil
from h2lib.dll_wrapper import DLLWrapper
from h2lib.h2lib_signatures import H2LibSignatures
from h2lib.utils import MultiProcessInterface


class H2Lib(H2LibSignatures, DLLWrapper):
    model_path = '.'
    _aero_sections_data_shape = {}

    def __init__(self, filename=None, cwd='.', suppress_output=True):
        if filename is None:
            if os.name == 'nt':
                filename = os.path.dirname(__file__) + '/HAWC2Lib.dll'
            else:
                filename = os.path.dirname(__file__) + '/HAWC2Lib.so'  # pragma: no cover
        filename = os.path.abspath(filename)
        DLLWrapper.__init__(self, filename, cwd=cwd, cdecl=True)
        self.suppress_output = suppress_output
        self._initialized = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def model_path(self):
        return self._model_path

    def close(self):
        if self._initialized:
            self.finalize()
        DLLWrapper.close(self)

    def getState(self):
        return H2LibSignatures.getState(self, restype=np.int32)[1]

    def get_wind_speed(self, pos_g):
        return self.get_lib_function('get_wind_speed')(np.asarray(pos_g, dtype=np.float64),
                                                       np.asarray([0, 0, 0], dtype=np.float64))[0][1]

    def get_uvw(self, pos_g):
        vx, vy, vz = self.get_wind_speed(pos_g)
        return [vy, vx, -vz]

    def get_time(self):
        return np.round(self.get_lib_function('get_time')(0.)[0][0], 6)

    def read_input(self, htc_path='htc/input_hawc.htc', model_path='.'):
        self._model_path = model_path
        self.cwd = self.model_path
        return H2LibSignatures.read_input(self, htc_path)

    def init(self):
        assert not hasattr(self, '_init_result'), "init called twice"
        r = H2LibSignatures.init(self)
        self._initialized = True
        return r

    def step(self):
        self.time = np.round(H2LibSignatures.step(self, restype=np.float64)[1], 6)
        return self.time

    def run(self, time):
        self.time = np.round(H2LibSignatures.run(self, np.float64(time), restype=np.float64)[1], 6)
        return self.time

    def add_sensor(self, sensor_line):
        if ";" not in sensor_line:
            sensor_line += ";"
        return H2LibSignatures.add_sensor(self, sensor_line, restype=np.int64)[1]

    def get_sensor_info(self, id):
        "return name, unit, description"
        return [s[:-1].strip()  # remove null termination
                for s in H2LibSignatures.get_sensor_info(self, id, name=" " * 30, unit=" " * 10, desc=" " * 512)[0][1:]]

    def get_sensor_value(self, id):
        return H2LibSignatures.get_sensor_value(self, id, restype=np.float64)[1]

    def set_variable_sensor_value(self, id, value):
        return H2LibSignatures.set_variable_sensor_value(self, id, np.float64(value))

    def init_windfield(self, Nxyz, dxyz, box_offset_yz):
        """Initialize wind field which afterwards can be set using set_windfield
        init_windfield must be called before init

        x: direction of wind
        y: horizontal to the left when looking along x
        z: vertical up

        Parameters
        ----------
        Nxyz : (int, int, int)
            Number of points in wind field
        dxyz : (float, float, float)
            Distance between wind field points
        box_offset_yz : (float, float)
            Box offset in y and z, relative to hawc2 origo. Note this is in met coordinates as described above
            To set a wind field of size 200x80x80, such that the center is located at hawc2 coordinate (0,0,-70),
            box_offset_yz must be (-40,30)
            Note that the wind field size is (Nxyz)-1*dxyz
        """
        return H2LibSignatures.init_windfield(self, np.array(Nxyz, dtype=np.int64), np.array(dxyz, dtype=np.float64),
                                              np.array(box_offset_yz, dtype=np.float64))

    def set_windfield(self, uvw, box_offset_x):
        """Set wind field, must be called after init_windfield and init

        Parameters
        ----------
        uvw : array_like, dims=(3,Nx,Ny,Nz)
            wind field components including mean wind speed, shear etc.
        box_offset_x : float
            Offset in x direction at the current time
            To set a wind field of size 200x80x80, such that the front plane (largest x) is located
            at hawc2 coordinate (0,20,-70), i.e. 20m downstream of origo, set box_offset_x=-180
            Note that the wind field size is (Nxyz)-1*dxyz
            Note also that the end plane (x=0) will be located in -180 and repeated in 20+dx
        """
        return H2LibSignatures.set_windfield(self, np.asarray(uvw, dtype=np.float64), np.float64(box_offset_x))

    # ===================================================================================================================
    # H2rotor
    # ===================================================================================================================

    def get_rotor_dims(self):
        return [[self.get_nSections(r, b) for b in range(self.get_nblades(r))]
                for r in range(self.get_nrotors())]

    def get_nrotors(self):
        return H2LibSignatures.get_nrotors(self, restype=np.int64)[1]

    def get_nblades(self, rotor=0):
        return H2LibSignatures.get_nblades(self, rotor + 1, restype=np.int64)[1]

    def get_nSections(self, rotor=0, blade=0):
        return H2LibSignatures.get_nSections(self, rotor + 1, blade + 1, restype=np.int64)[1]

    def get_diameter(self, rotor=0):
        return H2LibSignatures.get_diameter(self, rotor + 1, restype=np.float64)[1]

    def aero_sections_data_shape(self, rotor):
        if not rotor in self._aero_sections_data_shape:
            self._aero_sections_data_shape[rotor] = (self.get_nblades(rotor), self.get_nSections(rotor), 3)
        return self._aero_sections_data_shape[rotor]

    def get_aerosections_position(self, rotor=0):
        position = np.zeros(self.aero_sections_data_shape(rotor), dtype=np.float64)
        return H2LibSignatures.get_aerosections_position(self, rotor + 1, position)[0][1]

    def set_aerosections_windspeed(self, uvw, rotor=0):
        return H2LibSignatures.set_aerosections_windspeed(self, rotor + 1, uvw)

    def get_aerosections_load(self, rotor=0):
        shape = self.aero_sections_data_shape(rotor)
        Fxyz = np.zeros(shape, dtype=np.float64)
        Mxyz = np.zeros(shape, dtype=np.float64)
        return H2LibSignatures.get_aerosections_load(self, rotor + 1, Fxyz, Mxyz)[0][1:]

    def get_bem_grid_dim(self, rotor=0):
        """returns (nazi, nrad)"""
        return H2LibSignatures.get_bem_grid_dim(self, rotor + 1, 0, 0)[0][1:]

    def get_bem_grid(self, rotor=0):
        """returns azi, rad"""
        nazi, nrad = self.get_bem_grid_dim(rotor)
        return H2LibSignatures.get_bem_grid(self, rotor + 1,
                                            np.zeros(nazi, dtype=np.float64), np.zeros(nrad, dtype=np.float64))[0][1:]

    def get_induction_polargrid(self, rotor=0):
        nazi, nrad = self.get_bem_grid_dim(rotor)
        induction = np.zeros((nazi, nrad), dtype=np.float64)
        return H2LibSignatures.get_induction_polargrid(self, rotor + 1, induction)[0][1]

    def get_induction_axisymmetric(self, rotor=0):
        nrad = self.get_bem_grid_dim(rotor)[1]
        induction = np.zeros(nrad, dtype=np.float64)
        return H2LibSignatures.get_induction_axisymmetric(self, rotor + 1, induction)[0][1]

    def get_rotor_orientation(self, rotor=0, deg=False):
        """return yaw, tilt, azi(of first blade) in rad(default) or deg"""
        r = H2LibSignatures.get_rotor_orientation(self, rotor=rotor + 1, yaw=0., tilt=0., azi=0.)[0][1:]
        if deg:
            return np.rad2deg(r)
        else:
            return r

    def get_rotor_position(self, rotor=0):
        return H2LibSignatures.get_rotor_position(self, rotor=rotor + 1, position=np.zeros(3, dtype=np.float64))[0][1]

    def get_rotor_avg_wsp(self, coo=1, rotor=0):
        """Returns the rotor averaged wind speed (rews) in global(coo=1, default) or rotor(coo=2) coordinates."""
        assert self.time > 0
        return H2LibSignatures.get_rotor_avg_wsp(self, coo=coo, rotor=rotor + 1, restype=np.float64)[1]


class MultiH2Lib(MultiProcessInterface, H2Lib):
    def __init__(self, N, filename=None, cwd='.', suppress_output=True):
        if not hasattr(suppress_output, '__len__'):
            suppress_output = [suppress_output] * N
        MultiProcessInterface.__init__(self, H2Lib, [(filename, cwd, suppress_output[i]) for i in range(N)])

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.close())
