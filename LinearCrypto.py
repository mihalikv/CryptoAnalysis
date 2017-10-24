from bitstring import BitArray
from prettytable import PrettyTable

class CryptoMagic(object):
    def __init__(self, plain_text, key, sbox, permutation) -> None:
        super().__init__()
        self.state = plain_text
        self.permutation = permutation
        self.sbox = sbox
        self.keys = []
        for i in range(5):
            self.keys.append(key[(i * 16):((i + 1) * 16)])

    def encrypt(self):
        for i in range(3):
            self.state ^= self.keys[i]
            self.state = CryptoMagic.run_substitution(self.state, self.sbox)
            self.state = self.run_permutation(self.state, self.permutation)
        self.state ^= self.keys[3]
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
        for j in state:
            decimal = state[(j * 4):((j + 1) * 4)].int
            substitution = CryptoMagic.one_substitution(decimal, sbox)
            state.overwrite(substitution, j * 4)
        return state

    @staticmethod
    def one_substitution(four_bits, sbox):
        substitution = BitArray(length=4, uint=sbox[four_bits])
        return substitution


class LinearCrypto(object):
    def __init__(self, sbox) -> None:
        super().__init__()
        self.sbox = sbox

    def generate_table(self):
        raise NotImplementedError


def main():
    plain_text = BitArray('0b0000000011111111')
    sbox = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
    permutation = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    key = BitArray(length=80, uint=0)
    # crypto_magic = CryptoMagic(plain_text, key, sbox, permutation)
    # print(crypto_magic.encrypt().bin)

    header = [" "]
    header += list(range(16))
    t = PrettyTable(header)
    for input in range(16):
        out = [input]
        for output in range(16):
            positive = 0
            for i in range(16):
                input_four_bits = BitArray(length=4, uint=i)
                result_four_bits = CryptoMagic.one_substitution(input_four_bits.int, sbox)
                sum = False
                for index, bit in enumerate(BitArray(length=4, uint=input)):
                    if bit:
                        sum ^= input_four_bits[index]
                for index, bit in enumerate(BitArray(length=4, uint=output)):
                    if bit:
                        sum ^= result_four_bits[index]
                if not sum:
                    positive += 1
            out.append(positive-8)
        t.add_row(out)
    print(t)


if __name__ == "__main__":
    main()
