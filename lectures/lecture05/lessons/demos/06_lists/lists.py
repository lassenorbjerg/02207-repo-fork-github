import vsc


@vsc.randobj
class Burst:
    def __init__(self):
        self.nbeats = vsc.rand_uint8_t()
        # A randomizable list with a fixed size of 16.
        self.data = vsc.rand_list_t(vsc.uint8_t(), 16)

    @vsc.constraint
    def c_shape(self):
        self.nbeats in vsc.rangelist(vsc.rng(1, 16))
        with vsc.foreach(self.data, idx=True) as i:
            # Entries after the active beats must be zero.
            with vsc.implies(i >= self.nbeats):
                self.data[i] == 0


burst = Burst()

for _ in range(20):
    burst.randomize()
    nbeats = int(burst.nbeats)
    data = [int(value) for value in burst.data]
    assert len(data) == 16
    assert all(value == 0 for value in data[nbeats:])
    print(nbeats, data)
