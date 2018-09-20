/*
 * Copyright (C) Fabien-B
 *
 * This file is part of paparazzi
 *
 * paparazzi is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * paparazzi is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with paparazzi; see the file COPYING.  If not, see
 * <http://www.gnu.org/licenses/>.
 */
/**
 * @file "modules/droneitgps/droneitgps.c"
 * @author Fabien-B
 * Send periodicaly GPS position on UART, formated as needed by DroneIt.
 */

#include "modules/droneitgps/droneitgps.h"
#include "state.h"
#include "math/pprz_geodetic_float.h"
#include "mcu_periph/uart.h"
#include "subsystems/gps.h"
#include "generated/airframe.h"
#include "bdm_crc.h"

#define STR_(s) #s
#define STR(s) STR_(s)

#define RAD_TO_DEG 57.29577951308232

#define COORD_FACTOR ((1<<30)/180.)
#define ALT_FACTOR 100
#define TOD_FACTOR 128
#define S_PER_DAY 86400
#define LEAP_SECONDS 18

union Data_item { //union to manage endianness
  int32_t i;
  uint32_t ui;
  Bdm_crc16_t bdm_crc;
  char c[4];
};

struct uart_periph *dev;
uint8_t data[18];

void droneitgps_init() {
  dev = &(DRONEIT_DEV);
}


void droneitgps_periodic() {
  
  if(!gps.fix) {
    return;
  }
  union Data_item crc;
  crc.bdm_crc = Bdm_crc16_init();  

  struct LlaCoor_f pos = *stateGetPositionLla_f();
  union Data_item lat, lon, alt, tod;

  lat.i = pos.lat * RAD_TO_DEG* COORD_FACTOR;
  lon.i = pos.lon * RAD_TO_DEG *COORD_FACTOR;
  alt.i = gps.hmsl / ALT_FACTOR;
  tod.ui = (((gps.tow/1000) - LEAP_SECONDS) % S_PER_DAY)*TOD_FACTOR;    //TODO: What happen sunday between 00:00:00 and 00:00:18 ?

// The CAT129 data should be in big endian, but we use little endian

  data[0] = lat.c[3];  
  data[1] = lat.c[2];  
  data[2] = lat.c[1];  
  data[3] = lat.c[0];

  data[4] = lon.c[3];  
  data[5] = lon.c[2];  
  data[6] = lon.c[1];  
  data[7] = lon.c[0];

  data[8] = alt.c[2];  
  data[9] = alt.c[1];  
  data[10] = alt.c[0];  

  data[11] = tod.c[2];
  data[12] = tod.c[1];
  data[13] = tod.c[0];

  data[14] = 0;
  data[15] = 0;

  crc.bdm_crc = Bdm_crc16_update(crc.bdm_crc, data, 16);
  data[16] = crc.c[1];
  data[17] = crc.c[0];

  uart_put_buffer(dev, 0, data, 18);
}


