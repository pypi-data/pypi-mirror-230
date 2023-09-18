from enum import IntFlag


class MessageTypes(IntFlag):

    CAN_DataFrame = 0x00000001
    CAN_RemoteFrame = 0x00000002
    CAN_ErrorFrame = 0x00000004
    LIN_Frame = 0x00000010

    pass
