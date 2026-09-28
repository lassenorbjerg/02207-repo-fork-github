import vsc
from vsc.methods import RandState


@vsc.randobj
class Packet:
    def __init__(self):
        self.addr = vsc.rand_uint8_t()
        self.length = vsc.rand_uint8_t()

    @vsc.constraint
    def legal(self):
        self.length > 0
        self.addr % 4 == 0


def generate(packet, count):
    sequence = []
    for _ in range(count):
        packet.randomize()
        sequence.append((int(packet.addr), int(packet.length)))
    return sequence


packet = Packet()

packet.set_randstate(RandState.mkFromSeed(1234, "exp1"))
seq1 = generate(packet, 5)

# Re-create the initial state from the same seed to replay the stream.
packet.set_randstate(RandState.mkFromSeed(1234, "exp1"))
seq2 = generate(packet, 5)

assert seq1 == seq2
print("first: ", seq1)
print("replay:", seq2)
