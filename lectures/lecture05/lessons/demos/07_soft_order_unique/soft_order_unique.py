import vsc


@vsc.randobj
class Fancy:
    def __init__(self):
        self.a = vsc.rand_uint8_t()
        self.b = vsc.rand_uint8_t()
        self.c = vsc.rand_uint8_t()

    @vsc.constraint
    def c_misc(self):
        # Prefer a=0 unless another constraint conflicts.
        vsc.soft(self.a == 0)

        # Choose a before choosing b.
        vsc.solve_order(self.a, self.b)

        # All three values must differ.
        vsc.unique(self.a, self.b, self.c)

        self.a < self.b

fancy = Fancy()

for _ in range(3):
    fancy.randomize()
    values = [int(fancy.a), int(fancy.b), int(fancy.c)]
    assert fancy.a == 0
    assert len(set(values)) == 3
    print(*values)

# A hard inline constraint overrides the soft default.
with fancy.randomize_with() as it:
    it.a == 10

assert fancy.a == 10
assert len({int(fancy.a), int(fancy.b), int(fancy.c)}) == 3
print("soft overridden:", int(fancy.a), int(fancy.b), int(fancy.c))
