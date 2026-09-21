from enum import IntEnum


class uvc_ssdt_type_enum(IntEnum):
    """ Type of driver: PRODUCER or CONSUMER """
    PRODUCER = 0
    CONSUMER = 1
