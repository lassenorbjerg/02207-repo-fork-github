import vsc

@vsc.randobj
class Packet:
    def __init__(self):
        self.addr = vsc.rand_uint8_t()    # 0..255
        self.length  = vsc.rand_uint8_t() # 0..255
        self.is_read = vsc.rand_bit_t(1)  # 0/1

    @vsc.constraint
    def legal(self):
        self.length > 0    # No zero‑length
        self.addr % 4 == 0 # 4‑byte alignment
        
p = Packet()

for _ in range(3):
    p.randomize()
    print(int(p.addr), int(p.length), int(p.is_read))
