"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatReceiver] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            receiver = cls(cls.__private_key, connection, local_logger)
            return True, receiver
        except (OSError, mavutil.mavlink.MAVError) as e:
            local_logger.error(f"Failed to create Heartbeat receiver object: {e}")
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self.connection = connection
        self.local_logger = local_logger
        self.last_5_heartbeats = [False, False, False, False, False]

    def run(self) -> None:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        try:
            msg = self.connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1.1)

            # Remove oldest heartbeat record
            self.last_5_heartbeats.pop(0)

            # If no heartbeat received in 1.1 seconds
            if not msg:
                self.last_5_heartbeats.append(False)
                self.local_logger.warning("Did not receive heartbeat from drone")

                # Check if there is no record of the drone being connected in last 5 checks
                if True not in self.last_5_heartbeats:
                    return (True, "Disconnected")
                return (True, "Connected")

            # If heartbeat received
            self.last_5_heartbeats.append(True)
            self.local_logger.info("Received heartbeat from drone")
            return (True, "Connected")

        except (OSError, mavutil.mavlink.MAVError) as e:
            self.local_logger.error(f"heartbeat_receiver.py failed to receive heartbeat: {e}")
            return (False, None)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
