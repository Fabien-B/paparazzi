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

#define STR_(s) #s
#define STR(s) STR_(s)

#define RAD_TO_DEG 57.29577951308232

#define COORD_FACTOR ((1<<30)/180.)
#define ALT_FACTOR 10
#define TOD_FACTOR 128
#define MS_PER_DAY 86400000

union Data_item { //union to manage endianness
  int32_t i;
  uint32_t ui;
  char c[4];
};

struct uart_periph *dev;
uint8_t data[16];

void droneitgps_init() {
  dev = &(DRONEIT_DEV);
}


void droneitgps_periodic() {

  struct LlaCoor_f pos = *stateGetPositionLla_f();
  union Data_item lat, lon, alt, tod;

  lat.i = pos.lat * RAD_TO_DEG* COORD_FACTOR;
  lon.i = pos.lon * RAD_TO_DEG *COORD_FACTOR;
  alt.i = pos.alt * ALT_FACTOR;
  tod.ui = ((gps.tow % MS_PER_DAY)*TOD_FACTOR)/1000;    //GPS Time of Week in ms

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

  uart_put_buffer(dev, 0, data, 16);
}


