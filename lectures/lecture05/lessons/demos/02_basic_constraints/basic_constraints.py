import vsc

@vsc.randobj
class Arith:
    def __init__(self):
        self.a = vsc.rand_uint8_t()
        self.b = vsc.rand_uint8_t()
        
    @vsc.constraint
    def c_rel(self):
        self.a < self.b
        self.a in vsc.rangelist(1, 2, vsc.rng(4, 8))
        self.b.inside(vsc.rangelist(vsc.rng(2,20)))
        
arith = Arith()

for _ in range(3):
    arith.randomize()
    print(int(arith.a), int(arith.b))
