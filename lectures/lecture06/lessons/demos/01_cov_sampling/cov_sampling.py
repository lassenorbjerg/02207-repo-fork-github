import vsc

@vsc.covergroup
class my_covergroup(object):
     def __init__(self):
         self.with_sample(
             a=vsc.bit_t(4)
             )
         self.cp1 = vsc.coverpoint(self.a, bins={
             "a" : vsc.bin(1, 2, 4),
             "b" : vsc.bin(8, [12,15])
             })

cg = my_covergroup()
cg.sample(1)
cg.sample(7)

print("Type=%f" % (
  cg.get_coverage()
))

cg.sample(12)

print("Type=%f" % (
  cg.get_coverage()
))
