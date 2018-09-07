/**
 * \file bdm_crc.h
 * Functions and types for CRC checks.
 *
 * Generated on Tue Jun 28 15:35:34 2016,
 * by pycrc v0.8.2, http://www.tty1.net/pycrc/
 * using the configuration:
 *    Width        = 16
 *    Poly         = 0x8005
 *    XorIn        = 0x0000
 *    ReflectIn    = True
 *    XorOut       = 0x0000
 *    ReflectOut   = True
 *    Algorithm    = table-driven
 *****************************************************************************/
#ifndef __BDM_CRC_H__
#define __BDM_CRC_H__

#include <stdlib.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif


/**
 * The definition of the used algorithm.
 *
 * This is not used anywhere in the generated code, but it may be used by the
 * application code to call algoritm-specific code, is desired.
 *****************************************************************************/
#define CRC_ALGO_TABLE_DRIVEN 1


/**
 * The type of the CRC values.
 *
 * This type must be big enough to contain at least 16 bits.
 *****************************************************************************/
typedef uint16_t Bdm_crc16_t;


/**
 * Reflect all bits of a \a data word of \a data_len bytes.
 *
 * \param data         The data word to be reflected.
 * \param data_len     The width of \a data expressed in number of bits.
 * \return             The reflected data.
 *****************************************************************************/
Bdm_crc16_t Bdm_crc16_reflect(Bdm_crc16_t data, size_t data_len);


/**
 * Calculate the initial crc value.
 *
 * \return     The initial crc value.
 *****************************************************************************/
static inline Bdm_crc16_t Bdm_crc16_init(void)
{
    return 0x0000;
}


/**
 * Update the crc value with new data.
 *
 * \param crc      The current crc value.
 * \param data     Pointer to a buffer of \a data_len bytes.
 * \param data_len Number of bytes in the \a data buffer.
 * \return         The updated crc value.
 *****************************************************************************/
Bdm_crc16_t Bdm_crc16_update(Bdm_crc16_t crc, const unsigned char *data, size_t data_len);


/**
 * Calculate the final crc value.
 *
 * \param crc  The current crc value.
 * \return     The final crc value.
 *****************************************************************************/
static inline Bdm_crc16_t Bdm_crc16_finalize(Bdm_crc16_t crc)
{
    return crc ^ 0x0000;
}


#ifdef __cplusplus
}           /* closing brace for extern "C" */
#endif

#endif      /* __BDM_CRC_H__ */
