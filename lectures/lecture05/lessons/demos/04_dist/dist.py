import vsc

@vsc.randobj
class Biased:
    def __init__(self):
        self.length = vsc.rand_uint8_t()

    @vsc.constraint
    def c_len_dist(self):
        vsc.dist(self.length, [
            vsc.weight(1, 50), # single‑beat favored
            vsc.weight(2, 20),
            vsc.weight((3,8),30)
        ])

dist = Biased()

distcnt = [0, 0, 0, 0, 0, 0, 0, 0]

for _ in range(10):
    dist.randomize()
    distcnt[dist.length-1] = distcnt[dist.length-1] + 1

    print(int(dist.length))

print(distcnt)

distcntp = list(map(lambda x: 100 * x / sum(distcnt), distcnt))

print(distcntp)
