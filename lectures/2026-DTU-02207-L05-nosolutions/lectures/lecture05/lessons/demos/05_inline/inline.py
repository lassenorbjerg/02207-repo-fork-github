import vsc


@vsc.randobj
class Packet:
    def __init__(self):
        self.addr = vsc.rand_uint8_t()
        self.length = vsc.rand_uint8_t()

    @vsc.constraint
    def legal(self):
        self.length > 0
        self.addr % 4 == 0


pkt = Packet()

# Ordinary randomization respects the class constraints.
pkt.randomize()
print("ordinary:", int(pkt.addr), int(pkt.length))

# Add one-off constraints for this randomization only.
with pkt.randomize_with() as it:
    it.length == 64
    it.addr % 64 == 0

assert pkt.length == 64
assert pkt.addr % 64 == 0
print("inline:  ", int(pkt.addr), int(pkt.length))

# Inline constraints can also be applied to standalone random variables.
a = vsc.rand_uint8_t()
b = vsc.rand_uint8_t()
with vsc.randomize_with(a, b):
    a < b

assert a < b
print("scalars: ", a.val, b.val)
