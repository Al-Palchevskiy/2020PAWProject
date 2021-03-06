/* Automatically generated nanopb header */
/* Generated by nanopb-0.4.1 */

#ifndef PB_CARISPAWBUFFERS_PB_H_INCLUDED
#define PB_CARISPAWBUFFERS_PB_H_INCLUDED
#include <pb.h>

#if PB_PROTO_HEADER_VERSION != 40
#error Regenerate this file with the current version of nanopb generator.
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Enum definitions */
typedef enum _frameUnit_Sensor {
    frameUnit_Sensor_IMU_9 = 0,
    frameUnit_Sensor_IMU_6 = 1,
    frameUnit_Sensor_HALL = 3
} frameUnit_Sensor;

/* Struct definitions */
typedef struct _frameUnit {
    double time_stamp;
    frameUnit_Sensor sensorType;
    float acc_x;
    float acc_y;
    float acc_z;
    float angular_x;
    float angular_y;
    float angular_z;
    float hall;
    float mag_x;
    float mag_y;
    float mag_z;
    float heading;
    float pitch;
    float roll;
} frameUnit;

typedef struct _wheelUnit {
    float time_stamp;
    bool isStamp;
    float acc_x;
    float acc_y;
    float acc_z;
    float angular_x;
    float angular_y;
    float angular_z;
    float hall;
} wheelUnit;


/* Helper constants for enums */
#define _frameUnit_Sensor_MIN frameUnit_Sensor_IMU_9
#define _frameUnit_Sensor_MAX frameUnit_Sensor_HALL
#define _frameUnit_Sensor_ARRAYSIZE ((frameUnit_Sensor)(frameUnit_Sensor_HALL+1))


/* Initializer values for message structs */
#define frameUnit_init_default                   {0, _frameUnit_Sensor_MIN, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
#define wheelUnit_init_default                   {0, 0, 0, 0, 0, 0, 0, 0, 0}
#define frameUnit_init_zero                      {0, _frameUnit_Sensor_MIN, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
#define wheelUnit_init_zero                      {0, 0, 0, 0, 0, 0, 0, 0, 0}

/* Field tags (for use in manual encoding/decoding) */
#define frameUnit_time_stamp_tag                 1
#define frameUnit_sensorType_tag                 2
#define frameUnit_acc_x_tag                      3
#define frameUnit_acc_y_tag                      4
#define frameUnit_acc_z_tag                      5
#define frameUnit_angular_x_tag                  6
#define frameUnit_angular_y_tag                  7
#define frameUnit_angular_z_tag                  8
#define frameUnit_hall_tag                       9
#define frameUnit_mag_x_tag                      10
#define frameUnit_mag_y_tag                      11
#define frameUnit_mag_z_tag                      12
#define frameUnit_heading_tag                    13
#define frameUnit_pitch_tag                      14
#define frameUnit_roll_tag                       15
#define wheelUnit_time_stamp_tag                 1
#define wheelUnit_isStamp_tag                    2
#define wheelUnit_acc_x_tag                      3
#define wheelUnit_acc_y_tag                      4
#define wheelUnit_acc_z_tag                      5
#define wheelUnit_angular_x_tag                  6
#define wheelUnit_angular_y_tag                  7
#define wheelUnit_angular_z_tag                  8
#define wheelUnit_hall_tag                       9

/* Struct field encoding specification for nanopb */
#define frameUnit_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, DOUBLE,   time_stamp,        1) \
X(a, STATIC,   SINGULAR, UENUM,    sensorType,        2) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_x,             3) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_y,             4) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_z,             5) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_x,         6) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_y,         7) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_z,         8) \
X(a, STATIC,   SINGULAR, FLOAT,    hall,              9) \
X(a, STATIC,   SINGULAR, FLOAT,    mag_x,            10) \
X(a, STATIC,   SINGULAR, FLOAT,    mag_y,            11) \
X(a, STATIC,   SINGULAR, FLOAT,    mag_z,            12) \
X(a, STATIC,   SINGULAR, FLOAT,    heading,          13) \
X(a, STATIC,   SINGULAR, FLOAT,    pitch,            14) \
X(a, STATIC,   SINGULAR, FLOAT,    roll,             15)
#define frameUnit_CALLBACK NULL
#define frameUnit_DEFAULT NULL

#define wheelUnit_FIELDLIST(X, a) \
X(a, STATIC,   SINGULAR, FLOAT,    time_stamp,        1) \
X(a, STATIC,   SINGULAR, BOOL,     isStamp,           2) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_x,             3) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_y,             4) \
X(a, STATIC,   SINGULAR, FLOAT,    acc_z,             5) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_x,         6) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_y,         7) \
X(a, STATIC,   SINGULAR, FLOAT,    angular_z,         8) \
X(a, STATIC,   SINGULAR, FLOAT,    hall,              9)
#define wheelUnit_CALLBACK NULL
#define wheelUnit_DEFAULT NULL

extern const pb_msgdesc_t frameUnit_msg;
extern const pb_msgdesc_t wheelUnit_msg;

/* Defines for backwards compatibility with code written before nanopb-0.4.0 */
#define frameUnit_fields &frameUnit_msg
#define wheelUnit_fields &wheelUnit_msg

/* Maximum encoded size of messages (where known) */
#define frameUnit_size                           76
#define wheelUnit_size                           42

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif
