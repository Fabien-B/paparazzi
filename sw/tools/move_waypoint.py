#!/usr/bin/env python3

import sys
import argparse
from os import path, getenv
from typing import List, Optional
import time
from math import degrees

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_HOME + "/var/lib/python")
sys.path.append(PPRZ_HOME + "/sw/lib/python")
from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage
import pprz_connect
import flight_plan
from pprz_math import geodetic


class WaypointMover:
    def __init__(self, ivy_bus, waypoint, id):
        self.waypoint = waypoint
        self.ref = None     # type: Optional[geodetic.LtpDef_d]
        self.datum_diff = 0
        self.ivy = IvyMessagesInterface("WaypointMover", ivy_bus=ivy_bus)
        self.connect = pprz_connect.PprzConnect(notify=self.new_ac, ivy=self.ivy)
        self.ivy.subscribe(self.waypoint_update, PprzMessage('datalink', 'REMOTE_GPS_LOCAL'))
        self.ivy.subscribe(self.ref_update, PprzMessage('telemetry', 'INS_REF'))
        self.acs_wp = []        # type: List[(int, int)]        ## [(ac_id, wp_id), ...]
        self.id = id

    def new_ac(self, conf: pprz_connect.PprzConfig):
        fp = flight_plan.FlightPlan()
        fp.parse(conf.flight_plan)
        try:
            wp_no = fp.get_waypoint_no(self.waypoint)
            self.acs_wp.append((conf.id, wp_no))
            print(self.acs_wp)
        except ValueError:
            print("No waypoint named {} in AC {}!".format(self.waypoint, conf.name))

    def ref_update(self, sender, rmsg):
        self.datum_diff = (int(rmsg.alt0) - int(rmsg.hmsl0)) / 1000
        ref_ecef = geodetic.EcefCoor_d(float(rmsg.ecef_x0)/100, float(rmsg.ecef_y0)/100, float(rmsg.ecef_z0)/100)
        self.ref = ref_ecef.to_ltp_def()
        print("new ref: ", self.ref)

    def waypoint_update(self, sender, rmsg):
        if rmsg.ac_id == self.id and self.ref is not None:
            pos_enu = geodetic.EnuCoor_d(float(rmsg.enu_x), float(rmsg.enu_y), float(rmsg.enu_z))
            print("enu: ", pos_enu)
            pos_ecef = pos_enu.to_ecef(self.ref)    # type: geodetic.EcefCoor_d
            pos_lla = pos_ecef.to_lla()             # type: geodetic.LlaCoor_d
            print("lla: ", pos_lla, pos_lla.lat, pos_lla.lon, pos_lla.alt)

            for (ac_id, wp_id) in self.acs_wp:
                tmsg = PprzMessage("ground", "MOVE_WAYPOINT")
                tmsg['ac_id'] = ac_id
                tmsg['wp_id'] = wp_id
                tmsg['lat'] = degrees(pos_lla.lat)
                tmsg['long'] = degrees(pos_lla.lon)
                tmsg['alt'] = pos_lla.alt - self.datum_diff
                self.ivy.send(tmsg)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("going to a stop!")
        self.connect.shutdown()


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w', '--waypoint', dest='waypoint', help="Waypoint that will be moved", required=True)
    parser.add_argument('-b', '--ivy_bus', dest='ivy_bus', help="Ivy bus address and port")
    parser.add_argument('-id', '--id', dest='id', help="ac_id representing the waypoint", required=True)
    # parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="display debug messages")
    args = parser.parse_args()

    if args.waypoint is None:
        print("A waypoint must be specified")
        exit(-1)

    with WaypointMover(args.ivy_bus, args.waypoint, args.id):
        while True:
            time.sleep(1)

