from h2lib.dll_wrapper import DLLWrapper
class H2LibSignatures():
    def add_sensor(self, sensor_line, restype):
        '''function add_sensor(sensor_line) bind(C, name="add_sensor")
      !DEC$ ATTRIBUTES DLLEXPORT :: add_sensor
      integer*8 :: add_sensor
      character(kind=c_char, len=1), intent(in)       :: sensor_line(1024)
    end function'''
        return self.get_lib_function('add_sensor')(sensor_line, restype=restype)

    def echo_version(self, ):
        '''subroutine echo_version() BIND(C, NAME='echo_version')
    !DEC$ ATTRIBUTES DLLEXPORT :: echo_version
    !GCC$ ATTRIBUTES DLLEXPORT :: echo_version
    type (tbuildinfo)   :: b
end subroutine'''
        return self.get_lib_function('echo_version')()

    def extern_write_log(self, c_msg, n, dll_name, error, warning):
        '''subroutine extern_write_log(c_msg, n, dll_name, error, warning) bind(C, name="extern_write_log")
            integer, intent(in) :: n
            character(kind=c_char, len=1), intent(in) :: c_msg(n)
            character(kind=c_char), intent(in) :: dll_name(50)
            logical(kind=c_bool), intent(in), optional :: error, warning
    character(kind=c_char, len=1), intent(in) :: c_msg(n_msg)
    integer, intent(in) :: n_msg
    character(kind=c_char), intent(in) :: dll_name(50)
    character(len=50) :: n
    logical(kind=c_bool), intent(in), optional :: error, warning
end subroutine'''
        return self.get_lib_function('extern_write_log')(c_msg, n, dll_name, error, warning)

    def finalize(self, ):
        '''SUBROUTINE finalize() bind(C, name="finalize")
!DEC$ ATTRIBUTES DLLEXPORT :: finalize  
  integer:: i
  real*4:: T2
END SUBROUTINE'''
        return self.get_lib_function('finalize')()

    def finalize_hawc2(self, ):
        '''subroutine finalize_hawc2() &
	   !DEC$ ATTRIBUTES DLLEXPORT :: finalize_hawc2
       end subroutine'''
        return self.get_lib_function('finalize_hawc2')()

    def getSquare(self, val, restype):
        '''function getSquare(val) result(valSquared) BIND(C, NAME='getSquare')
		!DEC$ ATTRIBUTES DLLEXPORT :: getSquare
        real(RK), intent(in) :: val
        real(RK)             :: valSquared
    end function'''
        return self.get_lib_function('getSquare')(val, restype=restype)

    def getState(self, restype):
        '''function getState() result(val) BIND(C, NAME='getState')
		!DEC$ ATTRIBUTES DLLEXPORT :: getState
        integer             :: val
    end function'''
        return self.get_lib_function('getState')(restype=restype)

    def get_aerosections_load(self, rotor, Fxyz, Mxyz):
        '''subroutine get_aerosections_load(rotor, Fxyz, Mxyz) bind(C, name='get_aerosections_load')
    integer*8, intent(in) :: rotor
    real(c_double),intent(out)::Fxyz(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3), &
  end subroutine'''
        return self.get_lib_function('get_aerosections_load')(rotor, Fxyz, Mxyz)

    def get_aerosections_position(self, rotor, position):
        '''subroutine get_aerosections_position(rotor, position) bind(C, name="get_aerosections_position")
    integer*8, intent(in) :: rotor
    real(c_double),intent(out)   :: position(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('get_aerosections_position')(rotor, position)

    def get_all_rotor_loads_hawc2(self, coo,force,moment):
        '''subroutine get_all_rotor_loads_hawc2(coo,force,moment) &
       integer(c_int),intent(in)::coo
	   real(c_double),dimension(3,nrotors),intent(out)::force,moment
       end subroutine'''
        return self.get_lib_function('get_all_rotor_loads_hawc2')(coo,force,moment)

    def get_baccelOLD_hawc2_4miras(self, baccelOLD_):
        '''subroutine get_baccelOLD_hawc2_4miras(baccelOLD_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_baccelOLD_hawc2_4miras
        real(c_double),intent(out)::baccelOLD_(nrotors,nblades_max,nsec_max)
       end subroutine'''
        return self.get_lib_function('get_baccelOLD_hawc2_4miras')(baccelOLD_)

    def get_bem_grid(self, rotor, azi, rad):
        '''subroutine get_bem_grid(rotor, azi, rad) bind(C, name="get_bem_grid")
    integer*8, intent(in)               :: rotor    
    real(c_double), intent(out)       :: azi(rotors_gl%rotor(rotor)%dyn_induc%bem%nazi)
    real(c_double), intent(out)       :: rad(rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_bem_grid')(rotor, azi, rad)

    def get_bem_grid_dim(self, rotor, nazi, nrad):
        '''subroutine get_bem_grid_dim(rotor, nazi, nrad) bind(C, name="get_bem_grid_dim")
    integer*8, intent(in)               :: rotor
    integer*8, intent(out)              :: nazi, nrad
  end subroutine'''
        return self.get_lib_function('get_bem_grid_dim')(rotor, nazi, nrad)

    def get_def_hawc2(self, pitch_,omegarot_,xtot_,ytot_,ztot_, 
                               xt_hub_,yt_hub_,zt_hub_,tilt_,yaw_,rot_,  
                               conet_, txtot_,tytot_,tztot_,xt_root_,yt_root_,zt_root_):
        '''subroutine get_def_hawc2(pitch_,omegarot_,xtot_,ytot_,ztot_, &
        real(c_double),intent(out)::pitch_(nrotors,nblades_max)
        real(c_double),intent(out)::omegarot_(nrotors)
        real(c_double),intent(out)::xtot_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::tilt_(nrotors), &
        real(c_double),intent(out)::txtot_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::xt_root_(nrotors,nblades_max), &
       end subroutine'''
        return self.get_lib_function('get_def_hawc2')(pitch_,omegarot_,xtot_,ytot_,ztot_, 
                               xt_hub_,yt_hub_,zt_hub_,tilt_,yaw_,rot_,  
                               conet_, txtot_,tytot_,tztot_,xt_root_,yt_root_,zt_root_)

    def get_def_hawc2_4miras(self, pitch_,omegarot_,xtot_,ytot_,ztot_, 
                               xt_hub_,yt_hub_,zt_hub_,tilt_,yaw_,rot_,  
                               conet_, txtot_,tytot_,tztot_,xt_root_,yt_root_,zt_root_):
        '''subroutine get_def_hawc2_4miras(pitch_,omegarot_,xtot_,ytot_,ztot_, &
        real(c_double),intent(out)::pitch_(nrotors,nblades_max)
        real(c_double),intent(out)::omegarot_(nrotors)
        real(c_double),intent(out)::xtot_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::tilt_(nrotors), &
        real(c_double),intent(out)::txtot_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::xt_root_(nrotors,nblades_max), &
       end subroutine'''
        return self.get_lib_function('get_def_hawc2_4miras')(pitch_,omegarot_,xtot_,ytot_,ztot_, 
                               xt_hub_,yt_hub_,zt_hub_,tilt_,yaw_,rot_,  
                               conet_, txtot_,tytot_,tztot_,xt_root_,yt_root_,zt_root_)

    def get_def_ini_hawc2_4miras(self, xini_,yini_,zini_,txini_,tyini_,tzini_, 
        xi_hub_,yi_hub_,zi_hub_,xi_root_,yi_root_,zi_root_):
        '''subroutine get_def_ini_hawc2_4miras(xini_,yini_,zini_,txini_,tyini_,tzini_, &
        real(c_double),intent(out)::xini_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::txini_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::xi_root_(nrotors,nblades_max), &
       end subroutine'''
        return self.get_lib_function('get_def_ini_hawc2_4miras')(xini_,yini_,zini_,txini_,tyini_,tzini_, 
        xi_hub_,yi_hub_,zi_hub_,xi_root_,yi_root_,zi_root_)

    def get_diameter(self, rotor, restype):
        '''function get_diameter(rotor) bind(C, name="get_diameter")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_diameter
    integer*8, intent(in) :: rotor
    Type (Taerorotor),pointer :: rotor_p
    real(c_double)  :: get_diameter
 end function'''
        return self.get_lib_function('get_diameter')(rotor, restype=restype)

    def get_fsi_loads_hawc2(self, fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_):
        '''subroutine get_fsi_loads_hawc2(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_) &
       real(c_double),intent(out)::fxbld_(nrotors,nblades_max,nsec_max), &
       end subroutine'''
        return self.get_lib_function('get_fsi_loads_hawc2')(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_)

    def get_hawc2_end(self, hawc_end_):
        '''subroutine get_hawc2_end(hawc_end_) &
        logical(c_bool),intent(out)::hawc_end_
       end subroutine'''
        return self.get_lib_function('get_hawc2_end')(hawc_end_)

    def get_induction_axisymmetric(self, rotor, induction):
        '''subroutine get_induction_axisymmetric(rotor, induction) bind(C, name="get_induction_axisymmetric")
    integer*8, intent(in)        :: rotor
    real(c_double),intent(out)   :: induction(rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_induction_axisymmetric')(rotor, induction)

    def get_induction_polargrid(self, rotor, induction):
        '''subroutine get_induction_polargrid(rotor, induction) bind(C, name="get_induction_polargrid")
      integer*8, intent(in)        :: rotor
      real(c_double),intent(out)   :: induction(rotors_gl%rotor(rotor)%dyn_induc%bem%nazi, rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_induction_polargrid')(rotor, induction)

    def get_inidef_hawc2(self, xini_,yini_,zini_,txini_,tyini_,tzini_, 
        xi_hub_,yi_hub_,zi_hub_,xi_root_,yi_root_,zi_root_):
        '''subroutine get_inidef_hawc2(xini_,yini_,zini_,txini_,tyini_,tzini_, &
        real(c_double),intent(out)::xini_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::txini_(nrotors,nblades_max,nsec_max), &
        real(c_double),intent(out)::xi_root_(nrotors,nblades_max), &
       end subroutine'''
        return self.get_lib_function('get_inidef_hawc2')(xini_,yini_,zini_,txini_,tyini_,tzini_, 
        xi_hub_,yi_hub_,zi_hub_,xi_root_,yi_root_,zi_root_)

    def get_nSections(self, rotor, blade, restype):
        '''function get_nSections(rotor, blade) bind(C, name="get_nSections")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nSections
    integer*8, intent(in) :: rotor, blade
    integer*8             :: get_nSections
  end function'''
        return self.get_lib_function('get_nSections')(rotor, blade, restype=restype)

    def get_nblades(self, rotor, restype):
        '''function get_nblades(rotor) bind(C, name="get_nblades")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nblades
    integer*8, intent(in) ::  rotor
    integer*8             :: get_nblades
  end function'''
        return self.get_lib_function('get_nblades')(rotor, restype=restype)

    def get_nblades_nsec_hawc2(self, nblades_,nsec_):
        '''subroutine get_nblades_nsec_hawc2(nblades_,nsec_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_nblades_nsec_hawc2
        integer(c_int),intent(out)::nblades_(nrotors),nsec_(nrotors)
       end subroutine'''
        return self.get_lib_function('get_nblades_nsec_hawc2')(nblades_,nsec_)

    def get_nblades_nsec_hawc2_4miras(self, nblades_,nsec_):
        '''subroutine get_nblades_nsec_hawc2_4miras(nblades_,nsec_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_nblades_nsec_hawc2_4miras
        integer(c_int),intent(out)::nblades_(nrotors),nsec_(nrotors)
       end subroutine'''
        return self.get_lib_function('get_nblades_nsec_hawc2_4miras')(nblades_,nsec_)

    def get_nrotors(self, restype):
        '''function get_nrotors() bind(C, name="get_nrotors")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nrotors
    integer*8 :: get_nrotors
  end function'''
        return self.get_lib_function('get_nrotors')(restype=restype)

    def get_nrotors_hawc2(self, nrotors_):
        '''subroutine get_nrotors_hawc2(nrotors_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_nrotors_hawc2
        integer(c_int),intent(out)::nrotors_
       end subroutine'''
        return self.get_lib_function('get_nrotors_hawc2')(nrotors_)

    def get_nrotors_hawc2_4miras(self, nrotors_):
        '''subroutine get_nrotors_hawc2_4miras(nrotors_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_nrotors_hawc2_4miras
        integer(c_int),intent(out)::nrotors_
       end subroutine'''
        return self.get_lib_function('get_nrotors_hawc2_4miras')(nrotors_)

    def get_omega_hawc2(self, omega_):
        '''subroutine get_omega_hawc2(omega_) &
	 !DEC$ ATTRIBUTES DLLEXPORT :: get_omega_hawc2
       real(c_double),intent(out)::omega_(nrotors)
       end subroutine'''
        return self.get_lib_function('get_omega_hawc2')(omega_)

    def get_proj_info_hawc2_4miras(self, timestepfsi_):
        '''subroutine get_proj_info_hawc2_4miras(timestepfsi_) &
        real(c_double),intent(out)::timestepfsi_(5)
       end subroutine'''
        return self.get_lib_function('get_proj_info_hawc2_4miras')(timestepfsi_)

    def get_rotor_avg_wsp(self, coo, rotor, restype):
        '''function get_rotor_avg_wsp(coo, rotor) bind(C, name="get_rotor_avg_wsp")
  !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_avg_wsp  
    integer*8, intent(in) :: rotor
    integer*8, intent(in) :: coo ! 1: global, 2: rotor
    real(c_double):: get_rotor_avg_wsp
  end function'''
        return self.get_lib_function('get_rotor_avg_wsp')(coo, rotor, restype=restype)

    def get_rotor_loads_hawc2(self, thrust_,torque_):
        '''subroutine get_rotor_loads_hawc2(thrust_,torque_) &
       real(c_double),intent(out)::thrust_(nrotors), torque_(nrotors)
       end subroutine'''
        return self.get_lib_function('get_rotor_loads_hawc2')(thrust_,torque_)

    def get_rotor_orientation(self, rotor, yaw, tilt, azi):
        '''subroutine get_rotor_orientation(rotor, yaw, tilt, azi) bind(C, name="get_rotor_orientation")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_orientation  
    integer*8, intent(in) :: rotor
    real(c_double), intent(out) :: yaw, tilt, azi
  end subroutine'''
        return self.get_lib_function('get_rotor_orientation')(rotor, yaw, tilt, azi)

    def get_rotor_position(self, rotor, position):
        '''subroutine get_rotor_position(rotor, position) bind(C, name="get_rotor_position")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_position  
    integer*8, intent(in) :: rotor
    real(c_double), dimension(3), intent(out) ::  position
  !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_avg_wsp  
    integer*8, intent(in) :: rotor
    integer*8, intent(in) :: coo ! 1: global, 2: rotor
    real(c_double):: get_rotor_avg_wsp
  end function'''
        return self.get_lib_function('get_rotor_position')(rotor, position)

    def get_sensor_info(self, id, name, unit, desc):
        '''subroutine get_sensor_info(id, name, unit, desc) bind(C, name="get_sensor_info")
      integer*8, intent(in) :: id
      character(kind=c_char, len=1), intent(out)       :: name(30), unit(10), desc(512)
    end subroutine'''
        return self.get_lib_function('get_sensor_info')(id, name, unit, desc)

    def get_sensor_value(self, id, restype):
        '''function get_sensor_value(id) bind(C, name="get_sensor_value")
      !DEC$ ATTRIBUTES DLLEXPORT :: get_sensor_value
      integer*8, intent(in) :: id
      real(c_double)        :: get_sensor_value
    end function'''
        return self.get_lib_function('get_sensor_value')(id, restype=restype)

    def get_time(self, time):
        '''subroutine get_time(time) bind(C, name="get_time")
      !DEC$ ATTRIBUTES DLLEXPORT :: get_time
      double precision    :: time	! time [s]
    end subroutine'''
        return self.get_lib_function('get_time')(time)

    def get_torsrate_hawc2_4miras(self, torsrate_):
        '''subroutine get_torsrate_hawc2_4miras(torsrate_) &
	   !DEC$ ATTRIBUTES DLLEXPORT :: get_torsrate_hawc2_4miras
        real(c_double),intent(out)::torsrate_(nrotors,nblades_max,nsec_max)
       end subroutine'''
        return self.get_lib_function('get_torsrate_hawc2_4miras')(torsrate_)

    def get_trmat_hawc2_4miras(self, trmat_GhBh_,trmat_GhSh_,trmat_ShBh_):
        '''subroutine get_trmat_hawc2_4miras(trmat_GhBh_,trmat_GhSh_,trmat_ShBh_) &
        real(c_double),intent(out)::trmat_GhBh_(nrotors,nblades_max,nsec_max,3,3), &
       end subroutine'''
        return self.get_lib_function('get_trmat_hawc2_4miras')(trmat_GhBh_,trmat_GhSh_,trmat_ShBh_)

    def get_vel_hawc2_4miras(self, u_blade_g_,v_blade_g_,w_blade_g_):
        '''subroutine get_vel_hawc2_4miras(u_blade_g_,v_blade_g_,w_blade_g_) &
        real(c_double),intent(out)::u_blade_g_(nrotors,nblades_max,nsec_max), &
       end subroutine'''
        return self.get_lib_function('get_vel_hawc2_4miras')(u_blade_g_,v_blade_g_,w_blade_g_)

    def get_version(self, s):
        '''subroutine get_version(s) BIND(C, NAME='get_version')
                character(kind=c_char, len=1), intent(inout)  :: s(255)
            end subroutine'''
        return self.get_lib_function('get_version')(s)

    def init(self, ):
        '''subroutine init() bind(C, name="init")
	    !DEC$ ATTRIBUTES DLLEXPORT :: init
    end subroutine'''
        return self.get_lib_function('init')()

    def init_hawc2(self, ):
        '''subroutine init_hawc2() &
	   !DEC$ ATTRIBUTES DLLEXPORT :: init_hawc2
       end subroutine'''
        return self.get_lib_function('init_hawc2')()

    def init_windfield(self, Nxyz, dxyz, box_offset_yz):
        '''subroutine init_windfield(Nxyz, dxyz, box_offset_yz) bind(C, name="init_windfield")
        integer*8, dimension(3):: Nxyz
    end subroutine'''
        return self.get_lib_function('init_windfield')(Nxyz, dxyz, box_offset_yz)

    def read_input(self, htc_path):
        '''subroutine read_input(htc_path) bind(C, name="read_input")
      character(kind=c_char, len=1), intent(in)       :: htc_path(1024)
    end subroutine'''
        return self.get_lib_function('read_input')(htc_path)

    def run(self, time, restype):
        '''function run(time) bind(C, name='run')
      !DEC$ ATTRIBUTES DLLEXPORT :: run
      real(c_double), intent(in) :: time
      real(c_double) :: run, eps
    end function'''
        return self.get_lib_function('run')(time, restype=restype)

    def setState(self, val):
        '''subroutine setState(val) BIND(C, NAME='setState')
		integer, intent(in) :: val
	end subroutine'''
        return self.get_lib_function('setState')(val)

    def set_aerosections_windspeed(self, rotor, uvw):
        '''subroutine set_aerosections_windspeed(rotor, uvw) bind(C, name="set_aerosections_windspeed")
    integer*8, intent(in) :: rotor
    real(c_double),intent(in)   :: uvw(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('set_aerosections_windspeed')(rotor, uvw)

    def set_fsi_loads_hawc2(self, fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_):
        '''subroutine set_fsi_loads_hawc2(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_) &
       real(c_double),intent(in)::fxbld_(nrotors,nblades_max,nsec_max), &
       end subroutine'''
        return self.get_lib_function('set_fsi_loads_hawc2')(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_)

    def set_fsi_proj_info_hawc2(self, timestepfsi_,namelenfsi_,projectfsi_):
        '''subroutine set_fsi_proj_info_hawc2(timestepfsi_,namelenfsi_,projectfsi_) &
        real(c_double),intent(in)::timestepfsi_(5)
        integer(c_int),intent(in)::namelenfsi_
        character(kind=c_char), intent(in) :: projectfsi_(*)
       end subroutine'''
        return self.get_lib_function('set_fsi_proj_info_hawc2')(timestepfsi_,namelenfsi_,projectfsi_)

    def set_fsi_rotor_info_fsi_hawc2(self, startup_,smooth_initime_,smooth_time_,force_2D_):
        '''subroutine set_fsi_rotor_info_fsi_hawc2(startup_,smooth_initime_,smooth_time_,force_2D_) &
        logical(c_bool),intent(in)::startup_,force_2D_
        real(c_double),intent(in)::smooth_initime_,smooth_time_
       end subroutine'''
        return self.get_lib_function('set_fsi_rotor_info_fsi_hawc2')(startup_,smooth_initime_,smooth_time_,force_2D_)

    def set_ini_info_hawc2(self, is_fsi_,is_mirhaw_):
        '''subroutine set_ini_info_hawc2(is_fsi_,is_mirhaw_) &
        logical(c_bool),intent(in)::is_fsi_,is_mirhaw_
       end subroutine'''
        return self.get_lib_function('set_ini_info_hawc2')(is_fsi_,is_mirhaw_)

    def set_ini_info_hawc2_miras(self, startup_,smooth_initime_,smooth_time_,force_2D_):
        '''subroutine set_ini_info_hawc2_miras(startup_,smooth_initime_,smooth_time_,force_2D_) &
        logical(c_bool),intent(in)::startup_,force_2D_
        real(c_double),intent(in)::smooth_initime_,smooth_time_
       end subroutine'''
        return self.get_lib_function('set_ini_info_hawc2_miras')(startup_,smooth_initime_,smooth_time_,force_2D_)

    def set_input_path_hawc2(self, inputpath_,lenpath_):
        '''subroutine set_input_path_hawc2(inputpath_,lenpath_) &
        character(kind=c_char), intent(in) :: inputpath_(*)
        integer(c_int),intent(in):: lenpath_
       end subroutine'''
        return self.get_lib_function('set_input_path_hawc2')(inputpath_,lenpath_)

    def set_llinfo_hawc2_miras(self, aofabld_,vrelbld_,indxbld_,indybld_,  
	                                        indzbld_,clftbld_,cdrgbld_,cmmtbld_):
        '''subroutine set_llinfo_hawc2_miras(aofabld_,vrelbld_,indxbld_,indybld_,  &
       real(c_double),intent(in):: aofabld_(nrotors,nblades_max,nsec_max), &
       end subroutine'''
        return self.get_lib_function('set_llinfo_hawc2_miras')(aofabld_,vrelbld_,indxbld_,indybld_,  
	                                        indzbld_,clftbld_,cdrgbld_,cmmtbld_)

    def set_loads_hawc2_miras(self, fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_):
        '''subroutine set_loads_hawc2_miras(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_) &
       real(c_double),intent(in)::fxbld_(nrotors,nblades_max,nsec_max), &
       end subroutine'''
        return self.get_lib_function('set_loads_hawc2_miras')(fxbld_,fybld_,fzbld_,mxbld_,mybld_,mzbld_)

    def set_proj_info_hawc2_4miras(self, timestepfsi_,namelenfsi_,projectfsi_):
        '''subroutine set_proj_info_hawc2_4miras(timestepfsi_,namelenfsi_,projectfsi_) &
        real(c_double),intent(in)::timestepfsi_(5)
        integer(c_int),intent(in)::namelenfsi_
        character(kind=c_char), intent(in) :: projectfsi_(*)
       end subroutine'''
        return self.get_lib_function('set_proj_info_hawc2_4miras')(timestepfsi_,namelenfsi_,projectfsi_)

    def set_variable_sensor_value(self, id, value):
        '''subroutine set_variable_sensor_value(id, value) bind(C, name="set_variable_sensor_value")
      integer*8, intent(in) :: id
      real(c_double)        :: value
    end subroutine'''
        return self.get_lib_function('set_variable_sensor_value')(id, value)

    def set_windfield(self, uvw, box_offset_x):
        '''subroutine set_windfield(uvw, box_offset_x) bind(C, name="set_windfield")
      real*8, intent(in) :: uvw(3, gwsd%TMOD%buffer_points_x,gwsd%TMOD%buffer_points_y,gwsd%TMOD%buffer_points_z)
      real*8, intent(in):: box_offset_x
    end subroutine'''
        return self.get_lib_function('set_windfield')(uvw, box_offset_x)

    def sqr2(self, val):
        '''subroutine sqr2(val) BIND(C, NAME='sqr2')
		integer, intent(inout) :: val
	end subroutine'''
        return self.get_lib_function('sqr2')(val)

    def step(self, restype):
        '''function step() bind(C, name='step')
      !DEC$ ATTRIBUTES DLLEXPORT :: step
      real(c_double) :: step
    end function'''
        return self.get_lib_function('step')(restype=restype)

    def step_correct_hawc2(self, ):
        '''subroutine step_correct_hawc2() &
	   !DEC$ ATTRIBUTES DLLEXPORT :: step_correct_hawc2
       end subroutine'''
        return self.get_lib_function('step_correct_hawc2')()

    def step_predict_hawc2(self, ):
        '''subroutine step_predict_hawc2() &
	   !DEC$ ATTRIBUTES DLLEXPORT :: step_predict_hawc2
       end subroutine'''
        return self.get_lib_function('step_predict_hawc2')()

    def syn_hawc2(self, ):
        '''subroutine syn_hawc2() &
	   !DEC$ ATTRIBUTES DLLEXPORT :: syn_hawc2
       end subroutine'''
        return self.get_lib_function('syn_hawc2')()

    def test_hdf5(self, ):
        '''subroutine test_hdf5() BIND(C, NAME='test_hdf5')
		!DEC$ ATTRIBUTES DLLEXPORT :: test_hdf5
		INTEGER     ::   hdferr ! Error flag
		CHARACTER(9) :: filename = 'test.hdf5'
		INTEGER(HID_T) :: file_id       ! File identifier
		INTEGER(HID_T) :: H5_Create_file,H5_Open_file      ! File identifier
		type(c_ptr) :: x
	end subroutine'''
        return self.get_lib_function('test_hdf5')()

    def test_mkl(self, ):
        '''subroutine test_mkl() BIND(C, NAME='test_mkl')
		!DEC$ ATTRIBUTES DLLEXPORT :: test_mkl
		REAL(8),DIMENSION(3)::t3, tt3
		REAL(8),Dimension(3,3)::t33
	 end subroutine'''
        return self.get_lib_function('test_mkl')()

    def work(self, time):
        '''subroutine work(time) bind(C, Name='work')
    integer*8, intent(in) :: time
    real*4 :: start_time
  end subroutine'''
        return self.get_lib_function('work')(time)
