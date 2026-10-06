import vsc

@vsc.randobj
class Cmd:
    def __init__(self):
        self.op = vsc.rand_uint8_t()
        self.size = vsc.rand_uint8_t()

    @vsc.constraint
    def c_op(self):
        self.op in vsc.rangelist(0, 1, 2, vsc.rng(4, 8))

    @vsc.constraint
    def c_ops(self):
        with vsc.if_then(self.op == 0): # NOP
            self.size == 0
        with vsc.else_if(self.op == 1): # READ
            self.size in vsc.rangelist(1, 4, 8)
        with vsc.else_then:
            self.size in vsc.rangelist(vsc.rng(32,64))

    @vsc.constraint
    def c_implies(self):
        with vsc.implies(self.op == 2): # WRITE→size>=1
            self.size >= 1
        
cmd = Cmd()

for _ in range(50):
    cmd.randomize()
    print(int(cmd.op), int(cmd.size))
