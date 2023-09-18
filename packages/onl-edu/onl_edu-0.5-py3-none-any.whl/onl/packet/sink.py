from collections import defaultdict as dd

from ..sim import Store, Environment
from ..device import Device


class PacketSink(Device):
    """A PacketSink is designed to record both arrival times and waiting times from the incoming
    packets. By default, it records absolute arrival times, but it can also be initialized to record
    inter-arrival times.

    """

    def __init__(
        self,
        env: Environment,
        rec_arrivals: bool = True,
        absolute_arrivals: bool = True,
        rec_waits: bool = True,
        rec_flow_ids: bool = True,
        debug: bool = False,
    ):
        self.store = Store(env)
        self.env = env
        # if True, the waiting times experienced by the packets are recorded
        self.rec_waits = rec_waits
        # if True, the flow IDs that the packets are used as the index for recording;
        # otherwise, the 'src' field in the packets are used
        self.rec_flow_ids = rec_flow_ids
        # if True, arrivals will be recorded
        self.rec_arrivals = rec_arrivals
        # if True absolute arrival times will be recorded, otherwise the time between
        # consecutive arrivals is recorded.
        self.absolute_arrivals = absolute_arrivals
        self.waits = dd(list)
        self.arrivals = dd(list)
        self.packets_received = dd(lambda: 0)
        self.bytes_received = dd(lambda: 0)
        self.packet_sizes = dd(list)
        self.packet_times = dd(list)
        self.perhop_times = dd(list)

        self.first_arrival = dd(lambda: 0.0)
        self.last_arrival = dd(lambda: 0.0)

        self.debug = debug

    def put(self, packet):
        """Sends a packet to this element."""
        now = self.env.now

        if self.rec_flow_ids:
            rec_index = packet.flow_id
        else:
            rec_index = packet.src

        if self.rec_waits:
            self.waits[rec_index].append(self.env.now - packet.time)
            self.packet_sizes[rec_index].append(packet.size)
            self.packet_times[rec_index].append(packet.time)
            self.perhop_times[rec_index].append(packet.perhop_time)

        if self.rec_arrivals:
            self.arrivals[rec_index].append(now)
            if len(self.arrivals[rec_index]) == 1:
                self.first_arrival[rec_index] = now

            if not self.absolute_arrivals:
                self.arrivals[rec_index][-1] = now - self.last_arrival[rec_index]

            self.last_arrival[rec_index] = now

        if self.debug:
            print("At time {:.1f}, packet {:d} arrived.".format(now, packet.packet_id))
            if self.rec_waits and len(self.packet_sizes[rec_index]) >= 10:
                bytes_received = sum(self.packet_sizes[rec_index][-9:])
                time_elapsed = self.env.now - (
                    self.packet_times[rec_index][-10] + self.waits[rec_index][-10]
                )
                print(
                    "Average throughput (last 10 packets): {:.2f} bytes/second.".format(
                        float(bytes_received) / time_elapsed
                    )
                )

        self.packets_received[rec_index] += 1
        self.bytes_received[rec_index] += packet.size
