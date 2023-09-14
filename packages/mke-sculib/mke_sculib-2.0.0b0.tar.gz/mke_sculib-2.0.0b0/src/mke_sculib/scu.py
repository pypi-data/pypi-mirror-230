#Feed Indexer tests [316-000000-043]

#Author: P.P.A. Kotze, H. Niehaus, T. Glaubach
#Date: 1/9/2020
#Version: 
#0.1 Initial
#0.2 Update after feedback and correction from HN email dated 1/8/2020
#0.3 Rework scu_get and scu_put to simplify
#0.4 attempt more generic scu_put with either jason payload or simple params, remove payload from feedback function
#0.5 create scu_lib
#0.6 1/10/2020 added load track tables and start table tracking also as debug added 'field' command for old scu
#HN: 13/05/2021 Changed the way file name is defined by defining a start time 
# 1.0 2022-05-26 added stowing / unstowing / taking /releasing command authorithy / (de)activating axis
#                added logging
#                changed the session saving function

#Import of Python available libraries

import warnings

from astropy.time import Time
import astropy.units as u
import datetime
import time
import requests
import os
import pytz
import re
import json

from io import StringIO

import numpy as np
import pandas as pd


import mke_sculib.chan_list_acu as chans
from mke_sculib.helpers import make_zulustr, match_zulutime, get_utcnow, parse_zulutime

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BLACK = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

colors_dc = {
    'header': colors.HEADER,
    'blue': colors.OKBLUE,
    'green': colors.OKGREEN,
    'warn': colors.WARNING,
    'red': colors.FAIL,
    'black': colors.BLACK,
    'bold': colors.BOLD,
    'underline': colors.UNDERLINE
}
    
def print_color(msg, color='red'):
    if isinstance(color, str):
        color = colors_dc[color]
    print(f"{color}{msg}{colors.BLACK}")

    

    
def logfun(name, msg, color):
    t = datetime.datetime.utcnow().isoformat()[:-4].replace('T', ' ') + 'Z'
    print(f'{color}[{t} - {name}] {msg}{colors.BLACK}')

def getLogger(name):
    def printlog(msg, color=colors.BLACK): 
        return logfun(name, msg, color)
    return printlog


log = getLogger('sculib')


configs_dc = {
    'full': chans.channels_detailed,
    'normal': chans.channels_normal,
    'reduced': chans.channels_reduced,
    'small': chans.channels_small,
    'hn_fi': chans.channels_hn_feed_indexer_sensors,
    'hn_tilt': chans.channels_hn_tilt_sensors,
}


state_dc = {
    0: "Undefined",
    1: "Standby",
    2: "Parked",
    3: "Locked",
    4: "E-Stop",
    6: "Stowed",
    9: "Locked and Stowed (3+9)",
    10: "Activating",
    19: "Deactivating",
    110: "SIP",
    120: "Stop",
    130: "Slew",
    220: "Jog",
    300: "Track",
}

bands_dc = {'Band 1': 1, 'Band 2': 2, 'Band 3': 3, 'Band 4': 4, 'Band 5a': 5, 'Band 5b': 6, 'Band 5c': 7}
bands_dc_inv = {v:k for k, v in bands_dc.items()}


state_dc = {k:v.upper() for k, v in state_dc.items()}
state_dc_inv = {v:k for k, v in state_dc.items()}



class scu():
    """A SCU interface object, which connects to a SCU controller by OHB Digital Connect GmbH
    for the SKA-MPI Demonstrator Radio Telescope in the Karroo Desert in South Africa as well
    as the MeerKAT Extension Radio telescopes. 
    
    This class can be used to communicate with and control of the Antennas control unit via 
    HTTP rest API.
    """
    def __init__(self, ip='localhost', port='8080', debug=False, lims_az=(-270.0, 270, 3.0), lims_el=(15, 90, 1.35), dish_type='mke'):
        """create an SCU object, which can be used to communicate with 
        and control of the Antennas control unit via HTTP rest API.

        Args:
            ip (str, optional): ip address of the antenna to connect to. Defaults to 'localhost'.
            port (str, optional): port of the antenna to connect to. Defaults to '8080'.
            debug (bool, optional): Set to True, to receive additional information in stdout, when using commands. Defaults to True.
            lims_az (tuple, optional): limits on AZ axis, angle_min, angle_max, speed_max. Defaults to (-270.0, 270, 3.0).
            lims_el (tuple, optional): limits on EL axis, angle_min, angle_max, speed_max. Defaults to (15, 90, 1.35).
        """

        self.ip = ip
        self.port = str(port)
        self.debug = debug

        self.event_log = {}

        self.t_start = Time.now()
        
        self.lims_az = lims_az
        self.lims_el = lims_el
        self.dish_type = dish_type.lower()
        self.bands_possible = bands_dc

    @property
    def version_acu(self):
        if self.dish_type == 'mke':
            chans = ['acu.general_management_and_controller.ds_software_version_major', 
                    'acu.general_management_and_controller.ds_software_version_minor',
                    'acu.general_management_and_controller.ds_software_version_fix']
            return '.'.join([str(s) for s in self.get_device_status_value(chans)])
        else:
            return str(self.get_device_status_value('acu.general_management_and_controller.ds_software_version'))

    @property
    def is_simulator(self):
        """indicates, whether or not this object is a simulator a real antenna

        Returns:
            True if it is a simulator
        """
        return hasattr(self, 'telescope')

    @property
    def t_internal(self):
        """internal telescope time as astropy Time object based on MJD format

        Returns:
            astropy.time.Time: the ACU internal time now
        """
        value = self.get_device_status_value(f'acu.time.internal_time')
        return Time(value, format='mjd')
        # return Time.now()

    @property
    def spem_keys(self):
        
        if self.dish_type == 'skampi':
            return ["p1_encoder_offset_azimuth", "p2_collimation",
                "p3_non_orthog_nasmyth", "p4_e_w_azimuth_tilt",
                "p5_n_s_azimuth_tilt", "p6_declination_error",
                "p7_encoder_offset_elevation", "p8_cos_terx_gray_nasmyth",
                "p9_sin_term_gray_nasmyth"]

        elif self.dish_type == 'mke':
            return [
                "p1_azimuth_encoder_offset",
                "p3_non_orthog_az_el",
                "p4_collimination_az",
                "p5_n_s_azimuth_tilt",
                "p6_e_w_azimuth_tilt",
                "p7_elevation_encoder_offset",
                "p8_grav_vertical_shift_el_az",
                "p9_linear_scale_factor_el",
                "p11_grav_horizontal_shift_el_az",
                "p12_linear_scale_factor_az",
                "p13_az_frequency_cos_part",
                "p14_az_frequency_sin_part",
                "p15_twice_el_frequency_cos_part",
                "p16_twice_az_frequency_sin_part",
                "p17_twice_az_frequency_cos_part",
                "p18_twice_az_frequency_sin_part",
                ]
        else:
            raise ValueError(f'{self.dish_type} is an unknon dish type for SPEM models, only skampi and mke are allowed')
    
    @property
    def spem_param_name_map(self):
        param_name_map = [re.match(r"^[Pp][0-9]+", k) for k in self.spem_keys]
        param_name_map = {m.group().upper():k for m, k in zip(param_name_map, self.spem_keys)}
        return param_name_map
    

    @property
    def band_in_focus(self):
        return self.status_finalValue('acu.general_management_and_controller.feed_indexer_pos')

    @property
    def azel(self):
        return self.get_azel()
    
    @property
    def state(self):
        return self.get_state()
    
    @property
    def azel_setp(self):
        return self.get_device_status_value('acu.azimuth.p_set'), self.get_device_status_value('acu.elevation.p_set')
    
    @property
    def azel_shape(self):
        return self.get_device_status_value('acu.azimuth.p_shape'), self.get_device_status_value('acu.elevation.p_shape')

    def _limit_motion(self, az_pos, el_pos, az_speed=None, el_speed=None):
        def limit(name, x, xmin, xmax):
            if x is None:
                return x
            vlim = max(min(x, xmax), xmin)
            if vlim != x:
                txt = f"WARNING: variable {name} exceeds its allowed limit and was set to {vlim} from {x}"
                log(txt)
                warnings.warn(txt)
            return vlim
        
        angle_min, angle_max, speed_max = self.lims_az
        az_pos = limit('az_pos', az_pos, angle_min, angle_max)
        az_speed = limit('az_speed', az_speed, 1e-10, speed_max)

        angle_min, angle_max, speed_max = self.lims_el
        el_pos = limit('el_pos', el_pos, angle_min, angle_max)
        el_speed = limit('el_speed', el_speed, 1e-10, speed_max)
        return az_pos, el_pos, az_speed, el_speed


    #Direct SCU webapi functions based on urllib PUT/GET
    def _feedback(self, r):
        if self.debug == True:
            log('***Feedback:' +  str(r.request.url) + ' ' + str(r.request.body))
            log(f'{r.status_code}: {r.reason}')
            log("***Text returned:")
            log(r.text)
        elif r.status_code != 200:
            log('***Feedback:' +  str(r.request.url) + ' ' + str(r.request.body), color=colors.WARNING)
            log(f'{r.status_code}: {r.reason}', color=colors.WARNING)
            log("***Text returned:", color=colors.WARNING)
            log(r.text, color=colors.WARNING)
            #log(r.reason, r.status_code)
            #log()

    #	def scu_get(device, params = {}, r_ip = self.ip, r_port = port):
    def scu_get(self, device, params = {}):
        '''This is a generic GET command into http: scu port + folder 
        with params=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        if device != '/devices/statusValue':
            self.event_log[datetime.datetime.utcnow()] = 'GET | ' + device

        r = requests.get(url = URL, params = params)
        self._feedback(r)
        r.raise_for_status()
        if r.status_code != 200:
            log(f'Statuscode != 200. Returnded: {r.status_code}: {r.reason}', color=colors.WARNING)

        return r

    def scu_put(self, device, payload = {}, params = {}, data=''):
        '''This is a generic PUT command into http: scu port + folder 
        with json=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        self.event_log[datetime.datetime.utcnow()] = 'PUT | ' + device

        r = requests.put(url = URL, json = payload, params = params, data = data)
        self._feedback(r)
        r.raise_for_status()
        if r.status_code != 200:
            log(f'Statuscode != 200. Returnded: {r.status_code}: {r.reason}', color=colors.WARNING)


        return r

    def scu_delete(self, device, payload = {}, params = {}):
        '''This is a generic DELETE command into http: scu port + folder 
        with params=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        self.event_log[datetime.datetime.utcnow()] = 'DEL | ' + device

        r = requests.delete(url = URL, json = payload, params = params)
        self._feedback(r)
        r.raise_for_status()

        if r.status_code != 200:
            log(f'Statuscode != 200. Returnded: {r.status_code}: {r.reason}', color=colors.WARNING)

        return r


    def determine_dish_type(self):
        """will set and return the dish type by checking a status value 

        Returns:
            string: either 'skampi' or 'mke'
        """
        chans = self.scu_get("/devices/statusPaths").json()
        if 'acu.general_management_and_controller.ds_software_version' in chans:
            self.dish_type = 'skampi'
        else:
            self.dish_type == 'mke'
        return self.dish_type
            

    #SIMPLE PUTS

    #commands to DMC state - dish management controller
    def interlock_acknowledge_dmc(self):
        """Send an interlock acknowledge command to the digital motion controller in case
        of trying to acknowledge errors etc.
        """
        log('Acknowledge interlock...')
        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.interlock_acknowledge'})

    def reset_dmc(self):
        """reset the digital motion controller in case of errors"""
        log('reset dmc...')
        self.scu_put('/devices/command', 
            {'path': 'acu.dish_management_controller.reset'})

    def activate_dmc(self):
        """activate the digital motion controller"""
        log('activate dmc...')
        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.activate'})

    def deactivate_dmc(self):
        """deactivate the digital motion controller"""
        log('deactivate dmc')
        self.scu_put('/devices/command', 
            {'path': 'acu.dish_management_controller.deactivate'})
        
    def move_to_band(self, position):
        """move the feed indexer to a predefined band position
        options str: "Band 1", "Band 2", "Band 3", "Band 5a", "Band 5b"
        "Band 5c"
        Args:
            position (str or int): Either "Band 1"..."Band 5c" or 1...7
        """

        log('move to band:' + str(position))
        if not(isinstance(position, str)):
            self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.move_to_band',
            'params': {'action': position}})
        else:
            self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.move_to_band',
            'params': {'action': bands_dc[position]}})

    def get_azel(self):
        """gets the current az and el values in degree and returns them as tuple
        """
        return self.get_device_status_value('acu.azimuth.p_act'), self.get_device_status_value('acu.elevation.p_act')

    

    def get_state(self, path='acu.general_management_and_controller.state'):
        alias_dc = {    
            'gmc': 'acu.general_management_and_controller.state',
            'az': 'acu.azimuth.state',
            'el': 'acu.elevation.state',
            'fi': 'acu.feed_indexer.state',
        }
        
        if path in alias_dc:
            path = alias_dc[path]

        return self.status_finalValue(path)
    
    def move_to_azel(self, az_angle, el_angle, az_vel=None, el_vel=None):
        """synonym for abs_azel. Moves to an absolute az el position
        with a preset slew rate
        Args:
            az_angle (-270 <= az_angle <= 270): abs AZ angle in degree.
            el_angle (15 <= el_angle <= 90): abs EL angle in degree.
            az_vel (0 < az_vel <= 3.0): AZ angular slew rate in degree/s. None for as fast as possible.
            el_vel (0 < el_vel <= 1.35): EL angular slew rate in degree/s. None for as fast as possible.
        """
        if az_vel is None and el_vel is None: 
            self.abs_azel(az_angle, el_angle)
        else:
            assert all([v is not None for v in [az_angle, el_angle, az_vel, el_vel]]), 'inputs can not be None'
            log('abs az: {:.4f} el: {:.4f} (vels: ({:.4f}, {:.4f})'.format(az_angle, el_angle, az_vel, el_vel))
            assert (az_vel is None) == (el_vel is None), 'either both velocities must be None, or neither'

            az_angle, el_angle, az_vel, el_vel = self._limit_motion(az_angle, el_angle, az_vel, el_vel)

            self.scu_put('/devices/command',
                {'path': 'acu.azimuth.slew_to_abs_pos',
                'params': {'new_axis_absolute_position_set_point': az_angle,
                'new_axis_speed_set_point_for_this_move': az_vel}})    

            self.scu_put('/devices/command',
                {'path': 'acu.elevation.slew_to_abs_pos',
                'params': {'new_axis_absolute_position_set_point': el_angle,
                'new_axis_speed_set_point_for_this_move': el_vel}}) 



    def abs_azel(self, az_angle, el_angle):
        """move to a given absolut position on both axes

        Args:
            az_angle (-270 <= az_angle <= 270): abs AZ angle in degree.
            el_angle (15 <= el_angle <= 90): abs EL angle in degree.
        """
        log('abs az: {:.4f} el: {:.4f}'.format(az_angle, el_angle))

        az_angle, el_angle, _, _ = self._limit_motion(az_angle, el_angle)

        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.slew_to_abs_pos',
            'params': {'new_azimuth_absolute_position_set_point': az_angle,
                'new_elevation_absolute_position_set_point': el_angle}})

    def wait_track_start(self, timeout=600, query_delay=.25):
        """wait for a tracing table to start by waiting for the two axis to change 
        to state 'TRACK'

        Args:
            timeout (int, optional): timeout time in seconds. Defaults to 600.
            query_delay (float, optional): period between two checks if status has changed in seconds. Defaults to .25.
        """
        self.wait_state("acu.azimuth.state", "TRACK", timeout, query_delay)
        self.wait_state("acu.elevation.state", "TRACK", timeout, query_delay)

    # def wait_track_end(self, timeout=600, query_delay=1.):
    #     # This is to allow logging to continue until the track is completed
    #     log('Waiting for track to finish...')

    #     self.wait_duration(10.0, no_stout=True)  

    #     def tester():
    #         a = self.status_Value("acu.tracking.act_pt_end_index_a")
    #         b = self.status_Value("acu.tracking.act_pt_act_index_a")
    #         return (int(a) - int(b)) > 0
        

    #     self.wait_by_testfun(tester, timeout, query_delay)
    #     log('   -> done')

    def wait_settle(self, axis='all', timeout=600, query_delay=.25, tolerance=0.01, wait_by_pos=False):
        """
        alias for waitForStatusValue but mapping 'AZ', 'EL', 'FI' to 'acu.azimuth.p_act'
        'acu.elevation.p_act' and 'acu.feed_indexer.p_act'

        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        
        # assures setpoint has actually been send to acu!
        self.wait_duration(1.0, no_stout=True)  

        dc1 = {
            'az': 'azimuth', 'el': 'elevation', 'fi': 'feed_indexer', 
            'azimuth':'azimuth', 'elevation': 'elevation', 'feed_indexer': 'feed_indexer' }
        
        if axis == 'all':
            self.wait_settle('az')
            self.wait_settle('el')
            self.wait_settle('fi')
            return

        key = dc1[axis.lower()]

        if key == 'feed_indexer':
            path = 'acu.feed_indexer.state'
            self.wait_state(path, "SIP", timeout, query_delay, operator = '<=')
        else:
            if wait_by_pos:
                value = self.get_device_status_value(f'acu.{key}.p_set')
                self.wait_for_pos(key, value, timeout, query_delay, tolerance)
            else:
                path = f'acu.{key}.state'
                self.wait_state(path, "SIP", timeout, query_delay, operator = '<=')


    def wait_for_pos(self, axis, value, timeout=600, query_delay=.25, tolerance=None):
        """
        alias for waitForStatusValue but mapping 'AZ', 'EL', 'FI' to 'acu.azimuth.p_act'
        'acu.elevation.p_act' and 'acu.feed_indexer.p_act'

        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        dc1 = {
            'az': 'azimuth', 'el': 'elevation', 'fi': 'feed_indexer', 
            'azimuth':'azimuth', 'elevation': 'elevation', 'feed_indexer': 'feed_indexer' }
        
        key = dc1[axis.lower()]
    
        if tolerance is not None:
            path = f'acu.{key}.p_act'
            tester = lambda v: abs(v - value) < abs(tolerance)
        else:
            path = f'acu.{key}.p_act'
            tester = lambda v: v == value

        self.wait_for_status(path, value, tester, timeout, query_delay, tolerance)


    def wait_state(self, path, value=None, timeout=600, query_delay=.25, operator = '=='):    
        """Wait for a given status at a given path using a given operator

        Args:
            path (str): the device path. Example
            value (str or int): the value to wait for
            timeout (int, optional): time in seconds after which to raise an timeout. Defaults to 600.
            query_delay (float, optional): re-query period for checking status change. Defaults to .25.
            operator (str, optional): optional operator to give '==', '!=', '<', '>' '>=', '<='. Defaults to '=='.
        """
        if value is None and path.upper() in state_dc_inv:
            value = path.upper()
            path = 'acu.general_management_and_controller.state'

        val = value if isinstance(value, int) else state_dc_inv[value]

        def tester(v):
            if  isinstance(v, int) or v.isnumeric():
                vv = int(v)    
            else:
                vv = state_dc_inv[v.upper()]

            if operator == '==':   return vv == val
            elif operator == '!=': return vv != val
            elif operator == '<':  return vv <  val
            elif operator == '<=': return vv <= val
            elif operator == '>':  return vv >  val
            elif operator == '>=': return vv >= val
            else: raise Exception(str(operator) + ' is not recognized as a valid operator. Allowed are only ==, !=, <=, >=, <, >')

        self.wait_for_status(path, val, tester, timeout, query_delay)

    def waitForStatusValue(self, path, value, timeout=600, query_delay=.25, tolerance=None):
        """
        alias for wait_for_status
        queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        self.wait_for_status(path, value, None, timeout=timeout, query_delay=query_delay, tolerance=tolerance)


    def wait_by_testfun(self, tester, timeout=600, query_delay=1.0, no_stout=False):
        """
        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            tester:     any test function that returns true, when reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        starttime = time.time()

        self.wait_duration(0.5, no_stout=True)    

        is_first = True
        while time.time() - starttime < timeout:            
            if tester():
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            
            if not no_stout and is_first:
                log('waiting for tester to return true...', color=colors.OKBLUE)
                is_first = False
            self.wait_duration(query_delay, no_stout=True)  

        raise TimeoutError("Sensor: tester() not true after {}s".format(timeout))


    def wait_for_status(self, path, value, tester = None, timeout=600, query_delay=.25, tolerance=None, no_stout=False):
        """
        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        starttime = time.time()

        self.wait_duration(0.5, no_stout=True)    

        is_first = True
        while time.time() - starttime < timeout:
            v = self.get_device_status_value(path)
            
            if tester is not None and tester(v):
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            elif tester is None and tolerance is not None and abs(v - value) < abs(tolerance): 
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            elif tester is None and v == value:
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True

            if not no_stout and is_first:
                if isinstance(value, float):
                    log('wait for {}: {:.3f} (currently at: {:.3f})'.format(path, value, v), color=colors.OKBLUE)
                else:
                    log('wait for {}: {} (currently at: {})'.format(path, value, v), color=colors.OKBLUE)
                is_first = False

            self.wait_duration(query_delay, no_stout=True)  

        raise TimeoutError("Sensor: {} not equal to {} after {}s. Current value: {}".format(path, value, timeout, v))

    def get_device_status_value(self, path):
        """
        Gets one or many device status values (status now)

        Args:
            path:       path of the SCU device status as string, or a list of strings for many
        returns:
            either the value directly or a list of values in case of a list of pathes
        """

        if not isinstance(path, str):
            fun = lambda p: self.scu_get("/devices/statusValue", {"path": p}).json()['value']
            return [fun(p) for p in path]
        else:
            return self.scu_get("/devices/statusValue", {"path": path}).json()['value']
        
    def get_device_status_message(self, path, value_only=False):
        """
        Gets one or many device status fields (which is the value and additional information)

        Args:
            path:       path of the SCU device status as string, or a list of strings for many
        returns:
            either the status message dict directly or a list of dicts in case of a list of pathes
        """
        if not isinstance(path, str):
            if value_only:
                fun = lambda p: self.scu_get("/devices/statusMessageField", {"path": p}).json()['lastFinalValue']
            else:
                fun = lambda p: self.scu_get("/devices/statusMessageField", {"path": p}).json()
            return [fun(p) for p in path]
        else:
            if value_only:
                return self.scu_get("/devices/statusMessageField", {"path": path}).json()['lastFinalValue']
            else:
                return self.scu_get("/devices/statusMessageField", {"path": path}).json()
        
    def get_channel_list(self, with_values=False, with_timestamps=False):
        if self.dish_type == 'mke':
            lst = self.scu_get("/devices/getAllDeviceStatusValues", {"device":"acu"}).json()
            
            if with_values and with_timestamps:
                fun = lambda v: ('acu.' + v['path'], v['values'][0]['timestamp'], v['values'][0]['lastValue'])
            elif not with_values and with_timestamps:
                fun = lambda v: ('acu.' + v['path'], v['values'][0]['timestamp'])
            elif with_values and not with_timestamps:
                fun = lambda v: ('acu.' + v['path'], v['values'][0]['lastValue'])
            else:
                fun = lambda v: 'acu.' + v['path']
            
            return [fun(v) for v in lst if v]
        else:
            if with_values or with_timestamps:
                raise ValueError('skampi type dish can not be queried for values, only for channel names')
            return self.scu_get("/devices/statusPaths").json()
        
    #commands to ACU
    def deactivate_lowpowermode(self):
        return self.scu_put("/devices/command", {"path":"acu.dish_management_controller.set_power_mode","params":{"action":"0"}}).text
    
    def activate_lowpowermode(self):
        return self.scu_put("/devices/command", {"path":"acu.dish_management_controller.set_power_mode","params":{"action":"1"}}).text

    def stow(self, pre_move=True):
        """stow the antenna on pos 1 (both axes) and wait for stowing to be completed
        """
        log('Stowing...')
        if pre_move:
            self.abs_azel(+90, 88)
            self.wait_settle()

        if self.dish_type == 'mke':
            self.scu_put("/devices/command", {"path": "acu.azimuth.drive_to_stow", "params":{"action": "1"}})
            self.scu_put("/devices/command", {"path": "acu.elevation.drive_to_stow", "params":{"action": "1"}})
        else:
            self.scu_put("/devices/command", {"path": "acu.dish_management_controller.stow", "params": {"action": "1"}})

        self.wait_duration(3, no_stout=True)
        self.wait_state("acu.stow_pin_controller.azimuth_status", "LOCKED")
        self.wait_state("acu.stow_pin_controller.elevation_status", "LOCKED")

        
    def unstow(self):
        """
        Unstow both axes
        """
        log('Unstowing...')
        self.scu_put("/devices/command", {"path": "acu.dish_management_controller.unstow"})

        self.wait_duration(3, no_stout=True)      
        self.wait_state("acu.stow_pin_controller.azimuth_status", "STANDBY")
        self.wait_state("acu.stow_pin_controller.elevation_status", "STANDBY")


    def activate_axes(self):
        """
        Activate axes
        """
        self.scu_put("/devices/command", {"path": "acu.azimuth.activate"})
        self.scu_put("/devices/command", {"path": "acu.elevation.activate"})

        self.wait_duration(1, no_stout=True)
        self.waitForStatusValue("acu.azimuth.axis_bit_status.abs_active", True, timeout=10)
        self.waitForStatusValue("acu.elevation.axis_bit_status.abs_active", True, timeout=10)


    def deactivate_axes(self):
        """
        Activate axes
        """
        self.scu_put("/devices/command", {"path": "acu.azimuth.deactivate"})
        self.scu_put("/devices/command", {"path": "acu.elevation.deactivate"})

        self.wait_duration(1, no_stout=True)        
        self.waitForStatusValue("acu.azimuth.axis_bit_status.abs_active", False, timeout=10)
        self.waitForStatusValue("acu.elevation.axis_bit_status.abs_active", False, timeout=10)


    def release_command_authority(self):
        """
        Release command authority.
        """
        log('Releasing Command Authority...')
        self._command_authority('Release')
        self.wait_duration(5)
    
    def get_command_authority(self):
        """
        get command authority.
        """
        log('Getting Command Authority...')


        self._command_authority('Get')
        # # ICD Version 2.4 says 4, but actual behavior of 21.07.2021 is value 3 == SCU
        # self.wait_for_status("acu.command_arbiter.act_authority", "3", timeout=10)
        self.wait_duration(5)
        
    #command authority
    def _command_authority(self, action):
        #1 get #2 release
        
        authority={'Get': 1, 'Release': 2}
        self.scu_put('/devices/command', 
            {'path': 'acu.command_arbiter.authority',
            'params': {'action': authority[action]}})
        
    def activate_az(self):
        """activate azimuth axis (controller)"""
        log('act azimuth')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.activate'})

    def activate_el(self):
        """activate elevation axis (controller)"""
        log('activate elevation')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.activate'})

    def deactivate_el(self):
        """deactivate elevation axis (controller)"""
        log('deactivate elevation')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.deactivate'})

    def abs_azimuth(self, az_angle, az_vel):
        """Moves to an absolute az position
        with a preset slew rate
        Args:
            az_angle (-270 <= az_angle <= 270): abs AZ angle in degree.
            az_vel (0 <= az_vel <= 3.0): AZ angular slew rate in degree/s.
        """
        
        log('abs az: {:.4f} vel: {:.4f}'.format(az_angle, az_vel))
        az_vel = self.lims_az[-1] if az_vel is None else az_vel
        az_angle, _, az_vel, _ = self._limit_motion(az_angle, None, az_vel, None)
        self.scu_put('/devices/command',
            {'path': 'acu.azimuth.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': az_angle,
            'new_axis_speed_set_point_for_this_move': az_vel}})    

    def abs_elevation(self, el_angle, el_vel):
        """Moves to an absolute el position
        with a preset slew rate
        Args:
            az_vel (0 <= az_vel <= 3.0): AZ angular slew rate in degree/s.
            el_vel (0 <= el_vel <= 3.0): EL angular slew rate in degree/s.
        """

        log('abs el: {:.4f} vel: {:.4f}'.format(el_angle, el_vel))

        el_vel = self.lims_el[-1] if el_vel is None else el_vel
        _, el_angle, _, el_vel = self._limit_motion(None, el_angle, None, el_vel)

        self.scu_put('/devices/command',
            {'path': 'acu.elevation.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': el_angle,
            'new_axis_speed_set_point_for_this_move': el_vel}}) 

    def load_static_offset(self, az_offset, el_offset):
        """loads a static offset to the tracking controller

        Args:
            az_offset (float): the AZ offset to load. Unit Unclear!
            el_offset (float): the EL offset to load. Unit Unclear!
        """
        log('offset az: {:.4f} el: {:.4f}'.format(az_offset, el_offset))
        self.scu_put('/devices/command',
            {'path': 'acu.tracking_controller.load_static_tracking_offsets.',
            'params': {'azimuth_tracking_offset': az_offset,
                        'elevation_tracking_offset': el_offset}})     #Track table commands


    
    def load_program_track(self, load_type, entries, t=[0]*50, az=[0]*50, el=[0]*50):
        """WARNING DEPRECATED! please use upload_track_table instead
        load a program track table to the ACU of exactly 50 entries

        Args:
            load_type (str): either 'LOAD_NEW', 'LOAD_ADD', or 'LOAD_RESET'
            entries (int): number of entries in track table
            t (list of float, optional): time values to upload. Defaults to [0]*50.
            az (list of float, optional): az values to upload. Defaults to [0]*50.
            el (list of float, optional): el values to upload. Defaults to [0]*50.
        """

        warnings.warn(
            "Legacy Function: This is not maintained and might not work as intended\nWARNING DEPRECATED! please use upload_track_table instead",
            DeprecationWarning
        )

        log(load_type)    
        LOAD_TYPES = {
            'LOAD_NEW' : 1, 
            'LOAD_ADD' : 2, 
            'LOAD_RESET' : 3}
        
        #table selector - to tidy for future use
        ptrackA = 11
        
        TABLE_SELECTOR =  {
            'pTrackA' : 11,
            'pTrackB' : 12,
            'oTrackA' : 21,
            'oTrackB' : 22}
        
        #funny thing is SCU wants 50 entries, even for LOAD RESET! or if you send less then you have to pad the table
    
        if entries != 50:
            padding = 50 - entries
            t  += [0] * padding
            az += [0] * padding
            el += [0] * padding

        self.scu_put('/devices/command',
                    {'path': 'acu.dish_management_controller.load_program_track',
                    'params': {'table_selector': ptrackA,
                                'load_mode': LOAD_TYPES[load_type],
                                'number_of_transmitted_program_track_table_entries': entries,
                                'time_0': t[0], 'time_1': t[1], 'time_2': t[2], 'time_3': t[3], 'time_4': t[4], 'time_5': t[5], 'time_6': t[6], 'time_7': t[7], 'time_8': t[8], 'time_9': t[9], 'time_10': t[10], 'time_11': t[11], 'time_12': t[12], 'time_13': t[13], 'time_14': t[14], 'time_15': t[15], 'time_16': t[16], 'time_17': t[17], 'time_18': t[18], 'time_19': t[19], 'time_20': t[20], 'time_21': t[21], 'time_22': t[22], 'time_23': t[23], 'time_24': t[24], 'time_25': t[25], 'time_26': t[26], 'time_27': t[27], 'time_28': t[28], 'time_29': t[29], 'time_30': t[30], 'time_31': t[31], 'time_32': t[32], 'time_33': t[33], 'time_34': t[34], 'time_35': t[35], 'time_36': t[36], 'time_37': t[37], 'time_38': t[38], 'time_39': t[39], 'time_40': t[40], 'time_41': t[41], 'time_42': t[42], 'time_43': t[43], 'time_44': t[44], 'time_45': t[45], 'time_46': t[46], 'time_47': t[47], 'time_48': t[48], 'time_49': t[49],
                                'azimuth_position_0': az[0], 'azimuth_position_1': az[1], 'azimuth_position_2': az[2], 'azimuth_position_3': az[3], 'azimuth_position_4': az[4], 'azimuth_position_5': az[5], 'azimuth_position_6': az[6], 'azimuth_position_7': az[7], 'azimuth_position_8': az[8], 'azimuth_position_9': az[9], 'azimuth_position_10': az[10], 'azimuth_position_11': az[11], 'azimuth_position_12': az[12], 'azimuth_position_13': az[13], 'azimuth_position_14': az[14], 'azimuth_position_15': az[15], 'azimuth_position_16': az[16], 'azimuth_position_17': az[17], 'azimuth_position_18': az[18], 'azimuth_position_19': az[19], 'azimuth_position_20': az[20], 'azimuth_position_21': az[21], 'azimuth_position_22': az[22], 'azimuth_position_23': az[23], 'azimuth_position_24': az[24], 'azimuth_position_25': az[25], 'azimuth_position_26': az[26], 'azimuth_position_27': az[27], 'azimuth_position_28': az[28], 'azimuth_position_29': az[29], 'azimuth_position_30': az[30], 'azimuth_position_31': az[31], 'azimuth_position_32': az[32], 'azimuth_position_33': az[33], 'azimuth_position_34': az[34], 'azimuth_position_35': az[35], 'azimuth_position_36': az[36], 'azimuth_position_37': az[37], 'azimuth_position_38': az[38], 'azimuth_position_39': az[39], 'azimuth_position_40': az[40], 'azimuth_position_41': az[41], 'azimuth_position_42': az[42], 'azimuth_position_43': az[43], 'azimuth_position_44': az[44], 'azimuth_position_45': az[45], 'azimuth_position_46': az[46], 'azimuth_position_47': az[47], 'azimuth_position_48': az[48], 'azimuth_position_49': az[49],
                                'elevation_position_0': el[0], 'elevation_position_1': el[1], 'elevation_position_2': el[2], 'elevation_position_3': el[3], 'elevation_position_4': el[4], 'elevation_position_5': el[5], 'elevation_position_6': el[6], 'elevation_position_7': el[7], 'elevation_position_8': el[8], 'elevation_position_9': el[9], 'elevation_position_10': el[10], 'elevation_position_11': el[11], 'elevation_position_12': el[12], 'elevation_position_13': el[13], 'elevation_position_14': el[14], 'elevation_position_15': el[15], 'elevation_position_16': el[16], 'elevation_position_17': el[17], 'elevation_position_18': el[18], 'elevation_position_19': el[19], 'elevation_position_20': el[20], 'elevation_position_21': el[21], 'elevation_position_22': el[22], 'elevation_position_23': el[23], 'elevation_position_24': el[24], 'elevation_position_25': el[25], 'elevation_position_26': el[26], 'elevation_position_27': el[27], 'elevation_position_28': el[28], 'elevation_position_29': el[29], 'elevation_position_30': el[30], 'elevation_position_31': el[31], 'elevation_position_32': el[32], 'elevation_position_33': el[33], 'elevation_position_34': el[34], 'elevation_position_35': el[35], 'elevation_position_36': el[36], 'elevation_position_37': el[37], 'elevation_position_38': el[38], 'elevation_position_39': el[39], 'elevation_position_40': el[40], 'elevation_position_41': el[41], 'elevation_position_42': el[42], 'elevation_position_43': el[43], 'elevation_position_44': el[44], 'elevation_position_45': el[45], 'elevation_position_46': el[46], 'elevation_position_47': el[47], 'elevation_position_48': el[48], 'elevation_position_49': el[49]}})



    # def start_program_track(self, start_time):
    #     """Start a previously loaded tracking table (Table A) using SPLINE interpolation and AZ EL tracking Mode

    #     Args:
    #         start_time (float): start time as MJD
    #     """
    #     ptrackA = 11
    #     #interpol_modes
    #     NEWTON = 0
    #     SPLINE = 1
    #     #start_track_modes
    #     AZ_EL = 1
    #     RA_DEC = 2
    #     RA_DEC_SC = 3  #shortcut
    #     self.scu_put('/devices/command',
    #                 {'path': 'acu.dish_management_controller.start_program_track',
    #                 'params' : {'table_selector': ptrackA,
    #                             'start_time_mjd': start_time,
    #                             'interpol_mode': SPLINE,
    #                             'track_mode': AZ_EL }})


    def run_track_table(self, t=None, az=None, el=None, df=None, columns=['time', 'az', 'el'], activate_logging=True, config_name='full_configuration'):
        """run a tracking tabel and block until complete
        stop_program_track()
        start_logger() only if needed
        upload_trac_table()
        wait_duration(dt)
        wait_for_pos(az[-1])
        wait_for_pos(el[-1])
        stop_logger() only if needed
        stop_program_track()
        wait_duration(5)
        return 

        Args:
            t (numpy array Nx1, optional): time vector for tracking table in mjd. Defaults to None.
            az (numpy array Nx1, optional): azimuth values for tracking table. Defaults to None.
            el (numpy array N x1, optional): elevation values for tracking table. Defaults to None.
            df (pd.DataFrame, optional): optional instead of az, el, t to pass a dataframe and use the columns defined in colums. Defaults to None.
            columns (list, optional): columns to use in the dataframe for t, az, el. Defaults to ['time', 'az', 'el'].
            activate_logging (bool, optional): whether or not to activate logging during running of this table. Defaults to True.
            config_name (str, optional): the logging configuration to use. Defaults to 'full_configuration'.
        """
        assert not (isinstance(t, pd.DataFrame) and az is None and el is None), 'Must pass a dataframe with the keyword argument df=...'
        if t is None and az is None and el is None and df is not None and columns is not None:
            t, az, el = [df[c].values for c in columns]
        
        
        self.stop_program_track()

        self.wait_duration(5)
        t_start, t_end = Time(t[0], format='mjd'), Time(t[-1], format='mjd')
        if activate_logging and self.logger_state() != 'STOPPED':
            log('WARNING, logger already recording - attempting to stop and start a fresh logger...', color=colors.WARNING)
            self.stop_logger()  
            self.wait_duration(2)
        
        dt_wait = self.upload_track_table(t, az, el, df, columns, wait_for_start=False)

        self.wait_until(t_start - 3*u.s)
        if activate_logging:
            # start logging for my testrun
            self.start_logger(config_name=config_name, stop_if_need=False)
        
        
        self.wait_until(t_start + 2*u.s)
        assert self.get_state().upper() == 'TRACK', 'SCU did not start tracking as requested!'

        # wait for track table to finish
        self.wait_until(t_end)
        self.wait_for_pos('az', az[-1], tolerance=0.05, timeout=20)
        self.wait_for_pos('el', el[-1], tolerance=0.05, timeout=20)
        if self.logger_state() != 'STOPPED':
            self.stop_logger()
        self.stop_program_track()
        self.wait_duration(5)



    def upload_track_table(self, t=None, az=None, el=None, df=None, columns=['time', 'az', 'el'], wait_for_start=False):
        """convenience funtion to wrap 
                scu.acu_ska_track(scu.format_body(t, az, el))
            in one call
        Args:
            Either:
                t (iterable of float): time as mjd
                az (iterable of float): azimuth in degree
                el (iterable of float): elevation (alt) in degree
            Or:
                df (pandas.DataFrame): with at least three columns giving time [mjd], az [deg], el[el]
                a (iterable of str): the columns to use in the dataframe. Default: ['time', 'az', 'el']
            wait_for_start (bool, optional): Whether or not to wait for the tracking table to start after upload. Defaults to False.
        """
        assert not (isinstance(t, pd.DataFrame) and az is None and el is None), 'Must pass a dataframe with the keyword argument df=...'
        if t is None and az is None and el is None and df is not None and columns is not None:
            t, az, el = [df[c].values for c in columns]
        

        is_mon_increasing = np.all(np.diff(t) > 0)
        if not is_mon_increasing:
            raise Exception('Time vector in tracking table is not monotonically increasing!')
        
        t_astro = Time(np.round(t, 12), format='mjd')
        t_end = t_astro[-1]
        dt = np.min(np.diff(t_astro.unix))
        assert dt >= 0.2, "ERROR, The ACU will only accept tracking tables with dt > 0.2s, but given was: dt_min={}".format(dt)
        log('Running Table ({}, {:5.3f}, {:5.3f}) --> ({}, {:5.3f}, {:5.3f}) T={:.2f} N={}, dt_min={:.12f}'.format(Time(t[0], format='mjd').datetime, az[0], el[0], Time(t[-1], format='mjd').datetime, az[-1], el[-1],  np.ptp(t_astro.unix), len(az), dt), color=colors.BOLD)
        
        # hack: Workaround. The SCU ignores tracking tables with <= 50 entries
        if len(t) <= 50:
            log(f'WARNING!: The given tracking table has only {len(t)} entries.', color=colors.WARNING)
            log(f'The SCU has a bug where tracking tables with <=50 samples are silently ignored.', color=colors.WARNING)
            log(f'appending until the tracking table has at least 51 entries', color=colors.WARNING)
            
            t, az, el = list(t), list(az), list(el)
            while len(t) <= 50:
                t.append(t[-1]+dt)
                az.append(az[-1])
                el.append(el[-1])
            t, az, el = np.array(t), np.array(az), np.array(el)


        rows_table = ["{:6.12f} {:3.8f} {:3.8f}".format(ti, azi, eli) for ti, azi, eli in zip(t, az, el)]
        self.acu_ska_track("\n".join(rows_table))
        if wait_for_start:
            self.wait_track_start(timeout=30)

        return t_end.unix - self.t_internal.unix


    def stop_program_track(self):
        """
        Stop loading program track table - presumably, stops a programmed track
        """

        log("Requesting stop program track")
        self.acu_ska_track_stoploadingtable()
        self.wait_duration(1)
        
        # See E-Mail from Arne, 2021/11/05
        self.scu_put("/devices/command", payload={"path": "acu.tracking_controller.reset_program_track",
                    "params": {"table_selector": "11", "load_mode": "3", "number_of_transmitted_program_track_table_entries": "0"}})

        self.wait_duration(1)


    def acu_ska_track(self, BODY):
        """Low level function. Use 'upload_track_table()' instead to upload a tracking table.
            This function uploads a programTrack (tracking table) in the internal SCU specific format, which is
                "{:6.12f} {:3.8f} {:3.8f}\n" for time[mjd] az[deg] el[deg]
            per row.
        

        Args:
            BODY (str): the string holing the tracking table in the internal SCU specific format.

        Returns:
            request.model.Response: response object from this call (useless for anything but ID and returncode checking)
        """
        log(f'uploading acu-ska-track with {len(BODY)} char size...')
        return self.scu_put('/acuska/programTrack', data = BODY)
        
    def acu_ska_track_stoploadingtable(self):
        """Low level function. Use 'stop_program_track()' instead 

        Returns:
            request.model.Response: response object from this call (useless for anything but ID and returncode checking)
        """
        log('acu ska track stop loading table')
        return self.scu_put('/acuska/stopLoadingTable')
        
    def format_tt_line(self, t, az,  el, capture_flag = 1, parallactic_angle = 0.0):
        """Low Level Function to format a single line within a tracking table in SCU native format.
        assumption is capture flag and parallactic angle will not be used.

        Args:
            t (float): time in MJD
            az (-270 <= float <= 270): azimuth position in deg
            el (15 <= float <= 90): elevation position in deg
            capture_flag (int, optional): ???. Defaults to 1.
            parallactic_angle (float, optional): ???. Defaults to 0.0.
        """
        f_str = '{:.12f} {:.6f} {:.6f} {:.0f} {:.6f}\n'.format(float(t), float(az), float(el), capture_flag, float(parallactic_angle))
        return(f_str)

    def format_body(self, t, az, el):
        """Low Level function to format a list of tracking table entries in SCU native format.

        Args:
            t (list of float): time in MJD
            az (list of float, -270 <= float <= 270): azimuth position in deg
            el (lost of float, 15 <= float <= 90): elevation position in deg
        Returns:
            str: The tracking table in SCU native format.
        """

        body = ''
        for i in range(len(t)):
            body += self.format_tt_line(t[i], az[i], el[i])
        return(body)        

    #status get functions goes here
    
    def status_Value(self, sensor):
        """Low Level function to get the 'value' field from the 
        status message fields a of given device.

        Args:
            sensor (str): path to the sensor to get
        """

        r = self.scu_get('/devices/statusValue', 
            {'path': sensor})
        data = r.json()['value']
        #log('value: ', data)
        return(data)

    def status_finalValue(self, sensor):
        """Low Level function to get the 'finalValue' field from the 
        status message fields a of given device.

        Args:
            sensor (str): path to the sensor to get
        """
        #log('get status finalValue: ', sensor)
        r = self.scu_get('/devices/statusValue', 
            {'path': sensor})
        data = r.json()['finalValue']
        #log('finalValue: ', data)
        return(data)



    def commandMessageFields(self, commandPath):
        """Low Level function to get complete list of all commands message 
        fields from a device given by device name or a single command by given path.

        Use the responses .json() method to access the returned data as a dictionary.

        Args:
            commandPath (str): The path of the command to get

        Returns:
            request.model.Response: response object from this call.
        """
        r = self.scu_get('/devices/commandMessageFields', 
            {'path': commandPath})
        return r

    def statusMessageField(self, statusPath):
        """Low Level function to get a complete list of all 
        status message fields (including the last known value) of given device.

        Use the responses .json() method to access the returned data as a dictionary.

        Args:
            statusPath (str): The path of the status to get

        Returns:
            request.model.Response: response object from this call.
        """
        r = self.scu_get('/devices/statusMessageFields', 
            {'deviceName': statusPath})
        return r
    
    #ppak added 1/10/2020 as debug for onsite SCU version
    #but only info about sensor, value itself is murky?
    def field(self, sensor):
        """Low Level function to get a specific status field.

        Args:
            sensor (str): path to the sensor to get
        """
        #old field method still used on site
        r = self.scu_get('/devices/field', 
            {'path': sensor})
        #data = r.json()['value']
        data = r.json()
        return(data)
    
    #logger functions goes here

    def create_logger(self, config_name, sensor_list):
        '''
        PUT create a config for logging
        Usage:
        create_logger('HN_INDEX_TEST', hn_feed_indexer_sensors)
        or 
        create_logger('HN_TILT_TEST', hn_tilt_sensors)
        '''
        log('create logger')
        r = self.scu_put('/datalogging/config', 
            {'name': config_name,
            'paths': sensor_list})
        return r

    '''unusual does not take json but params'''
    def start_logger(self, config_name='full_configuration', stop_if_need=True):
        """start logging with a given logging config.
        The logging config must have been registered prior. (see self.start() method)

        Args:
            config_name (str, optional): Config to use for logging. Defaults to 'normal'.
            stop_if_need (bool, optional): _description_. Defaults to True.
        """
            # Start data recording
        if stop_if_need and self.logger_state() != 'STOPPED':
            log('WARNING, logger already recording - attempting to stop and start a fresh logger...', color=colors.WARNING)
            self.stop_logger()  
            self.wait_duration(5)

        if self.logger_state() == 'STOPPED':
            log('Starting logger with config: {} ...'.format(config_name))
            r = self.scu_put('/datalogging/start', params='configName=' + config_name)
        else:
            raise Exception(f'Can not start logging, since logging state != "STOPPED" (actual state: "{self.logger_state()}"')

        return r

    def stop_logger(self):
        """stop logging, will raise HTTPError: 412 if logging is not running

        Returns:
            request.model.Response: response object from this call (useless for anything but ID and returncode checking)
        """
        log('stop logger')
        r = self.scu_put('/datalogging/stop')
        return r

    def logger_state(self):
        """get current logger state

        Returns:
            str: "RUNNING" or "STOPPED"
        """
#        log('logger state ')
        r = self.scu_get('/datalogging/currentState')
        #log(r.json()['state'])
        return(r.json()['state'])

    def logger_configs(self):
        """GET all config names
        """
        log('logger configs ')
        r = self.scu_get('/datalogging/configs')
        return(r.json())

    def last_session(self):
        '''
        GET last session
        '''
        log('Last sessions ')
        r = self.scu_get('/datalogging/lastSession')
        session = (r.json()['uuid'])
        return(session)
    
    def logger_sessions(self):
        '''
        GET all sessions
        '''
        warnings.warn(
            "Legacy Function: This is not maintained and might not work as intended",
            DeprecationWarning
        )
        log('logger sessions ')
        r = self.scu_get('/datalogging/sessions')
        return r.json()
    

    def session_query(self, id):
        '''
        GET specific session only - specified by id number
        Usage:
        session_query('16')
        '''
        warnings.warn(
            "Legacy Function: This is not maintained and might not work as intended",
            DeprecationWarning
        )

        log(f'logger session query id "{id}"')
        r = self.scu_get('/datalogging/session',
            {'id': id})
        return r.json()



    def export_session(self, id = 'last', interval_ms=100):
        '''
        LEGACY function: Do not use!

        EXPORT specific session - by id and with interval
        output r.text could be directed to be saved to file 
        Usage: 
        export_session('16',1000)
        or export_session('16',1000).text 
        '''
        log('export session ')
        if interval_ms is None and not hasattr(self, 'telescope'):
            interval_ms = 100

        if id == 'last':
            id = self.last_session()

        r = self.scu_get('/datalogging/exportSession',
            params = {'id': id, 
                'interval_ms' : interval_ms})
        return r

    #sorted_sessions not working yet

    def sorted_sessions(self, isDescending = 'True', startValue = '1', endValue = '25', sortBy = 'Name', filterType='indexSpan'):
        log('sorted sessions')
        r = self.scu_get('/datalogging/sortedSessions',
            {'isDescending': isDescending,
            'startValue': startValue,
            'endValue': endValue,
            'filterType': filterType, #STRING - indexSpan|timeSpan,
            'sortBy': sortBy})
        return r
    
    def get_session_as_text(self, interval_ms=100, session = 'last'):
        """Download and return a session log in original text form

        Args:
            interval_ms (int, optional): sampling interval in milliseconds. Defaults to 1000.
            session (str, optional): session id to save either string with number or 'last'. Defaults to 'last'.

        Returns:
            str: the raw text as downloaded from the SCU
        """

        log('Attempt export of session: {} at rate {} ms'.format(session, interval_ms))
        if session == 'last':
            #get all logger sessions, may be many
            # r = self.logger_sessions()
            #[-1] for end of list, and ['uuid'] to get id of last session in list
            session = self.last_session()
        log('Session id: {} '.format(session))
        file_txt = self.export_session(session, interval_ms).text
        return file_txt

    def get_session_as_df(self, interval_ms=100, session = 'last'):
        """Download and return a session log as pandas dataframe

        Args:
            interval_ms (int, optional): sampling interval in milliseconds. Defaults to 1000.
            session (str, optional): session id to save either string with number or 'last'. Defaults to 'last'.
        Raises:
            Exception: on unknown format returned by the SCU for the log file it will raise an generic exception

        Returns:
            pandas.DataFrame: a dataframe with the time column (datetime UTC) as index.
        """
        
        file_txt = self.get_session_as_text(interval_ms=interval_ms, session = session)

        buf = StringIO(file_txt)
        columns = None

        for i in range(100):
            linestart = buf.tell()
            s = buf.readline()
            if s.strip().startswith(';acu.') or s.strip().startswith('Date/Time;acu.'):
                columns = s
                buf.seek(linestart)
                break
        
        if columns is None: 
            raise Exception("The return format of the acu was not recognized. Here is the first 1000 chars:" + file_txt[:1000]) 

        # _log.trace('NSKIP', nskip)
        df = pd.read_csv(buf, sep=';', index_col=0)

        if 'Unnamed: 0' in df:
            df = df.set_index('Unnamed: 0')

        df.index = pd.to_datetime(df.index, errors='coerce')

        return df

                        
    # def save_session(self, path_to_save, interval_ms=1000, session = 'last'):
    #     """Download and save a session to the filesystem

    #     Args:
    #         path_to_save (str): path on local filesys to save the session to
    #         interval_ms (int, optional): sampling interval in milliseconds. Defaults to 1000.
    #         session (str, optional): session id to save either string with number or 'last'. Defaults to 'last'.
    #     """
        
        
    #     file_txt = self.get_session_as_text(interval_ms, session)

    #     folder = os.path.dirname(path_to_save)
    #     if os.path.exists(folder) == 0:
    #         log(folder + " does not exist. making new dir", color=colors.WARNING)
    #         os.mkdir(folder)
            
    #     log(f'Saving Session as log file to: "{path_to_save}"', color=colors.BOLD)    
    #     with open(path_to_save, 'a+') as f:
    #         f.write(file_txt)
        
        
    #Simplified one line commands particular to test section being peformed 


    #wait seconds, wait value, wait finalValue
    def wait_until(self, T, no_stout=False):
        """wait until a certain time has been reached

        Args:
            T (astropy.time.Time object): timestamp until which to wait
            no_stout (bool, optional): whether or not to give feedback in stdout. Defaults to False.
        """
        tnow = self.t_internal
        
        if T < tnow:
            log('T={} is in the past! returning without waiting!'.format(T.iso), color=colors.WARNING)

        else:
            # fun = lambda : self.t_internal >= T
            dt_wait = (T - tnow).to(u.s).value                
            return self.wait_duration(dt_wait)
        
            


    #wait seconds, wait value, wait finalValue
    def wait_duration(self, seconds, no_stout=False):
        """wait for a given amount of seconds

        Args:
            seconds (int): number of seconds to wait for
            no_stout (bool, optional): whether or not to give feedback in stdout. Defaults to False.
        """
        if not no_stout:
            log('wait for {:.1f}s'.format(seconds), color=colors.OKBLUE)
        time.sleep(seconds)
        # if not no_stout:
        #     log('  -> done', color=colors.OKBLUE)

    #Simplified track table functions
        
    def __point_toggle(self, action, select):
        self.scu_put("/devices/command", payload={"path": "acu.pointing_controller.pointing_correction_toggle",
                    "params": {"action": str(action), "select": str(select)}})
        

    def point_all_ON(self):
        self.__point_toggle(1, '1')

    def point_all_OFF(self):
        self.__point_toggle(0, '1')
    
    def point_tilt_ON(self):
        self.__point_toggle(1, '10')

    def point_tilt_OFF(self):
        self.__point_toggle(0, '10')

    def point_AT_ON(self):
        self.__point_toggle(1, '11')
    
    def point_AT_OFF(self):
        self.__point_toggle(0, '11')
    
    def point_refr_ON(self):
        self.__point_toggle(1, '12')
    
    def point_refr_OFF(self):
        self.__point_toggle(0, '12')
    
    def point_spem_ON(self):
        self.__point_toggle(1, '20')
    
    def point_spem_OFF(self):
        self.__point_toggle(0, '20')
    

    def point_spem_set(self, params:dict, band = 'all', activate = True, set_rest_zero=True, wait_for_set=False, no_stdout=False):
        """set new pointing model parameters to a specific band in ArcSec

        Args:
            params (list): list of parameters (must be of length 9 only contain numbers and in ArcSeconds)
            band (int, optional): the band to set these values to (1...7). Defaults to 1.
            activate (bool, optional): whether or not ton directly activate after setting (there seems to be an error currently). Defaults to False.
        """

        n_timouts = 0
        ready = False
        while not ready:
            try:
                fi_pos = self.get_state('acu.general_management_and_controller.feed_indexer_pos')
                params_old = self.point_spem_get()

                if band == 'all':
                    bands = bands_dc.values()
                else:
                    bands = [band]

                for i, b in enumerate(bands):
                    is_last = i+1 == len(bands)

                    if isinstance(b, str):
                        assert b in bands_dc, f'ERROR: Band "{b}" not in allowed bands: ' + str(bands_dc)
                        bandi = bands_dc[b]
                    else:
                        assert b in bands_dc_inv, f'ERROR: Band {b} not in allowed bands: ' + str(bands_dc_inv)
                        bandi = b

                    assert isinstance(params, dict), 'this version of the SCU lib does only accept dict parameters'
                    assert np.all([isinstance(k, str) for k in params.keys()]), 'dict keys must be strings in the form "P1"..."P9", but given was: ' + ', '.join(params.keys())
                    
                    params = {k.upper():v for k, v in params.items()}
                    param_name_map = self.spem_param_name_map

                    assert np.all([p in param_name_map for p in params.keys()]), 'only "P1 to P22 is allowed, but given was: ' + ', '.join(params.keys())

                    d = {param_name_map[k]:v for k, v in params.items()}
                    if set_rest_zero:
                        d = {**{k:0 for k in self.spem_keys}, **d}
                    else:
                        if band != 'all' and bands_dc_inv[bandi] != str(fi_pos) and len(d) != 18:
                            raise ValueError("can not set a partial pointing model for a feed indexer position which is currently not in focus! Need to position the Feed indexer first and then set the Pointing model or provide a full model!")
                        elif len(d) != 18:
                            params = {**params_old, **params}
                            dold = {param_name_map[k]:v for k, v in params_old.items()}
                            d = {**dold, **d}

                    
                        
                    d['band_information'] = str(bandi)

                    path = 'acu.pointing_controller.set_static_pointing_model_parameters'
                    payload = {'path': path, "params": d}
                    if self.debug:
                        log('setting pointing model with payload: ' + json.dumps(payload))

                    if is_last and not no_stdout:
                        log('setting pointing model to band "{}". Params: {}'.format(band, params), color=colors.OKBLUE)

                    self.scu_put('/devices/command', payload=payload)
                
                if wait_for_set:
                    if band != 'all' and bands_dc_inv[bandi] != str(fi_pos):
                        log('Can not wait for pointing model parameters to be set, because the feed indexer is in the wrong position. Will return without waiting! band_is = {} vs band_set = {}'.format(fi_pos, bandi), color=colors.WARNING)
                    else:
                        
                        for k, v in params.items():
                            delay = wait_for_set if not isinstance(wait_for_set, bool) and wait_for_set > 0 else 0.5
                            self.wait_for_status('acu.pointing.' + k.lower(), v, query_delay=delay, timeout=5, no_stout=no_stdout)
                        if not no_stdout:
                            log(f'Pointing model {params} has been set successfully!', color=colors.OKGREEN)

                if activate:
                    self.point_spem_ON()

                ready = True
            except TimeoutError as terr:
                n_timouts += 1
                if n_timouts > 3:
                    raise
            

    def point_spem_get(self):
        """get_device_status_value for the pointing model parameters"""
        param_keys = list(self.spem_param_name_map.keys())
        pathes = {k:f'acu.pointing.' + k.lower() for k in param_keys}
        return {k:self.get_device_status_value(p) for k, p in pathes.items()}
        


    def point_AT_set(self, p_at_azel, band = 'all', activate=False, wait_for_set=True):
        """Set new values to the ambient temperature correction values in arcseconds for a specific band

        Args:
            p_at_azel (ambient_temperature_factor_az, ambient_temperature_factor_el) (float): factors for temp correction in ArcSec/deg-C
            band (int|str, optional): the band to set these values to (1...7). Defaults to 0.
            activate (bool, optional): whether or not ton directly activate after setting (there seems to be an error currently). Defaults to False.
        """
        # TG 2023-09-07 seems to work with MKE
        # log('WARNING! setting an ambient temp correction model currently has errors in SCU and may not work as intended!', color=colors.WARNING)
        
        if band == 'all':
            bands = self.bands_possible.values()
        else:
            bands = [band]

        for bandi in bands:
            if isinstance(bandi, str):
                assert bandi in bands_dc, f'ERROR: Band "{bandi}" not in allowed bands: ' + str(bands_dc)
                bandi = bands_dc[bandi]
            else:
                assert bandi in bands_dc_inv, f'ERROR: Band {bandi} not in allowed bands: ' + str(bands_dc_inv)
                bandi = bandi

            assert int(bandi) in bands_dc_inv, "The given band was not pound in the possible bands for this scu. See scu.bands_possible for further info"

            d = {   'ambient_temperature_factor_az': p_at_azel[0],
                    'ambient_temperature_factor_el': p_at_azel[1],
                    'band_information': str(bandi)}
            
            path = 'acu.pointing_controller.ambient_temperature_correction_setup_values'
            self.scu_put('/devices/command', payload={'path': path, "params": d})
            
            if wait_for_set:
                fun = lambda: self.point_AT_get(band=bandi) == tuple(p_at_azel)
                delay = wait_for_set if not isinstance(wait_for_set, bool) and wait_for_set > 0 else 0.5
                self.wait_by_testfun(fun, query_delay=delay, timeout=10)
        
        if wait_for_set:
            log(f'AT correction model {p_at_azel} for band {band} has been set successfully!', color=colors.OKGREEN)

        if activate:
            self.point_AT_ON()

    def point_AT_get(self, band = 'current'):
        """get the ambient temperature correction coefficients for the band in question

        Args:
            band (str, optional): either 'all' or current, or a specific band name, sich as 'Band 5c'. Defaults to 'current'.

        Returns:
            if band == 'all' a dictionary of all coefficients, else a tuple with the two coefficients for az and el
        """

        channels = [
            'acu.ambient_temp_correction_config.ambient_factor_az_band_1',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_2',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_3',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_4',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_5a',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_5b',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_5c',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_8',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_9',
            'acu.ambient_temp_correction_config.ambient_factor_az_band_10',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_1',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_2',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_3',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_4',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_5a',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_5b',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_5c',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_8',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_9',
            'acu.ambient_temp_correction_config.ambient_factor_el_band_10'
            # 'acu.pointing.amb_temp_corr_val_az',
            # 'acu.pointing.amb_temp_corr_val_el',
            # 'acu.pointing.amb_temp_corr_filter_constant'
        ]

        vals = {p:self.get_device_status_value(p) for p in channels}
        if band == 'all':
            return vals
        elif band == 'current':
            b = self.band_in_focus
            assert b, 'Current Band is None or empty. This should not be for getting AT with the current band!'
            b = b.lower().replace(' ', '_')
            v = tuple([v for p, v in vals.items() if p.endswith(b)])
            return v[0], v[1]
        else:
            b = bands_dc_inv[band] if band in bands_dc_inv else band
            b = b.lower().replace(' ', '_')
            v = tuple([v for p, v in vals.items() if p.endswith(b)])
            return v[0], v[1]
        

        


    def get_from_scu_influx(self, tstart, tend, token, org = 'OHBDC', timeout=360_000, channels = None):
        if 'InfluxDBClient' not in locals():
            from influxdb_client import InfluxDBClient
        
        base_query= """
                from(bucket: "SCU")
                |> range(start: {}, stop: {})
                |> filter(fn: (r) => r["_measurement"] == "device_status")
                |> filter(fn: (r) => r["device"] == "acu")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["_time", {}])
                """
        mk_query = lambda tstart, tend, chans: base_query.format(tstart, tend, ', '.join(['"_time"'] + [f'"{s}"' for s in chans]))

        if isinstance(tstart, Time):
            tstart = make_zulustr(tstart.datetime, remove_ms=False)
        elif isinstance(tstart, datetime.datetime):
            tstart = make_zulustr(tstart, remove_ms=False)

        if isinstance(tend, Time):
            tend = make_zulustr(tend.datetime, remove_ms=False)
        elif isinstance(tstart, datetime.datetime):
            tend = make_zulustr(tend, remove_ms=False)

        url = f'http://{self.ip}:8086'
        client = InfluxDBClient(url, token, org=org, debug = False, timeout=timeout)

        if not channels:
            channels = self.get_channel_list()

        query = mk_query(tstart, tend, channels)
        
        df = client.query_api().query_data_frame(query)
        df = df.drop(columns=['result', 'table'])
        df = df.rename(columns={'_time':'time'})
        df = df.set_index('time')

        return df



        

    def start(self, az_start=None, el_start=None, band_start=None, az_speed=None, el_speed=None, send_default_configs=False):
        """getting command authority, unstow, activate and start the antenna for usage

        Args:
            az_start (-270 <= az_start <= 270, optional): start position for AZ axis in degree. Defaults to None.
            el_start (15 <= el_start <= 90, optional): start position for EL axis in degree. Defaults to None.
            band_start (str or int, optional): start position ('Band 1'... 'Band 5c' or 1...7) for the Feed Indexer Axis to move to. Defaults to None.
            az_speed (0 < az_speed <= 3.0, optional): azimuth speed to use for movement to inital position. None means as fast as possible. Defaults to None.
            el_speed (0 < el_speed <= 1.0, optional): elevation speed to use for movement to inital position None means as fast as possible. Defaults to None.
            send_default_configs (bool, optional): Whether or not to generate the default logging configs on the SCU on startup. Defaults to True.
        """
        log('=== INITIATING STARTUP ROUTINE ===', color=colors.BOLD)
        self.t_start = Time.now()
        self.get_command_authority()
        self.wait_duration(0.1)
        if self.dish_type == 'mke':
            self.deactivate_lowpowermode()
            self.wait_duration(0.1)
        self.reset_dmc()
        self.wait_duration(3)
        if self.get_state() == 'Stowed':
            self.unstow()

        if send_default_configs:
            configs_scu_dc = self.logger_configs()
            configs_scu = [c['name'] for c in configs_scu_dc]
            for k, v in configs_dc.items():
                if k not in configs_scu:
                    log(f'Creating Default Config: {k} with n={len(v)} channels')
                    self.create_logger(k, v)
        
        self.wait_duration(5)
        self.activate_dmc()
        self.wait_duration(5)
        self.activate_axes()
        self.wait_duration(5)

        if band_start is not None:
            self.move_to_band(band_start)

        if az_start is not None:
            self.abs_azimuth(az_start, az_speed)
        if el_start is not None:
            self.abs_elevation(el_start, el_speed)

        if az_start is not None or el_start is not None or band_start is not None:
            self.wait_settle()
            self.wait_duration(3)
        log('=== STARTUP ROUTINE COMPLETED ===', color=colors.BOLD)

    def shutdown(self):
        """Stow, deactivate, and release command authority for antenna in order to finish before handing back the antenna
        """
        log('=== INITIATING SHUTDOWN ROUTINE ===', color=colors.BOLD)
        if self.get_state() != 'Stowed':
            self.stow()
        self.wait_duration(5)
        self.deactivate_axes()
        self.wait_duration(5)
        self.deactivate_dmc()
        self.wait_duration(5)
        self.release_command_authority()
        self.wait_duration(5)

        log('=== SHUTDOWN ROUTINE COMPLETED ===', color=colors.BOLD)

if __name__ == '__main__':
    log("main")
