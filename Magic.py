from bitstring import BitArray

class CryptoMagic(object):
    def __init__(self, key, sbox, permutation) -> None:
        super().__init__()
        self.permutation = permutation
        self.sbox = sbox
        self.keys = []
        for i in range(5):
            self.keys.append(key[(i * 16):((i + 1) * 16)])

    def encrypt(self, plain_text, rounds=4) -> BitArray:
        self.state = plain_text
        for i in range(3):
            self.state ^= self.keys[i]
            self.state = CryptoMagic.run_substitution(self.state, self.sbox)
            self.state = self.run_permutation(self.state, self.permutation)
        self.state ^= self.keys[3]
        if rounds == 4:
            self.state = CryptoMagic.run_substitution(self.state, self.sbox)
            self.state ^= self.keys[4]
        return self.state

    @staticmethod
    def run_permutation(state, permutation):
        result = state
        for index, bit in enumerate(state):
            result[permutation[index]] = bit
        return result

    @staticmethod
    def run_substitution(state, sbox):
        for j in range(4):
            decimal = state[(j * 4):((j + 1) * 4)].int
            substitution = CryptoMagic.one_substitution(decimal, sbox)
            state.overwrite(substitution, j * 4)
        return state

    @staticmethod
    def one_substitution(four_bits, sbox):
        substitution = BitArray(length=4, uint=sbox[four_bits])
        return substitution
