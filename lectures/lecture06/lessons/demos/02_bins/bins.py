import vsc

@vsc.covergroup
class my_covergroup(object):
    def __init__(self):
        self.with_sample(
            a=vsc.bit_t(4),
            b=vsc.bit_t(4)
         )
         
        self.cp1 = vsc.coverpoint(self.a, bins={
            "b0" : vsc.bin(1, 2, 4),
            "b1" : vsc.bin(8, [12,15])
            })

        self.cp2 = vsc.coverpoint(self.b, bins={
            "b0" : vsc.bin_array([], 1, 2, 4),
            "b1" : vsc.bin_array([4], [8,15])
            })


cg = my_covergroup()
cg.sample(1, 0)
cg.sample(7, 0)

vsc.report_coverage(details=True)

cg.sample(12, 0)

vsc.report_coverage(details=True)

cg.sample(0, 2)
cg.sample(0, 8)
cg.sample(0, 10)
cg.sample(0, 10)

vsc.report_coverage(details=True)
