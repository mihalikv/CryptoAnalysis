import random

import time
from bitstring import BitArray
from prettytable import PrettyTable

from Magic import CryptoMagic


class LinearCrypto(object):
    def __init__(self, magic, inputs, outputs) -> None:
        super().__init__()
        self.magic = magic
        self.inputs = inputs
        self.outputs = outputs

    def generate_table(self):
        header = [" "]
        header += list(range(16))
        t = PrettyTable(header)
        for input in range(16):
            out = [input]
            for output in range(16):
                positive = 0
                for i in range(16):
                    input_four_bits = BitArray(length=4, uint=i)
                    result_four_bits = CryptoMagic.one_substitution(input_four_bits.int, self.magic.sbox)
                    sum = False
                    for index, bit in enumerate(BitArray(length=4, uint=input)):
                        if bit:
                            sum ^= input_four_bits[index]
                    for index, bit in enumerate(BitArray(length=4, uint=output)):
                        if bit:
                            sum ^= result_four_bits[index]
                    if not sum:
                        positive += 1
                out.append(positive - 8)
            t.add_row(out)
        print(t)

    def get_first_stat(self):
        filename = '{}.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        start, stop = 1000, 10000
        step = int(stop/start)
        with open(filename, 'a') as f:
            for j in range(step):
                total_equals = 0
                total = start*(j+1)
                for i in range(total):
                    random_input = random.SystemRandom().randint(0, 65535)
                    encrypted = self.magic.encrypt(BitArray(length=16, uint=random_input))
                    result = False
                    for input in self.inputs:
                        result ^= encrypted[input-1]
                    for output in self.outputs:
                        result ^= encrypted[output-1]
                    if not result:
                        total_equals += 1
                f.write("{}, {}\n".format(float(total_equals/total), total))
            f.close()


def main():
    plain_text = BitArray('0b0000000011111111')
    sbox = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
    permutation = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    key = BitArray(length=80, uint=0)
    crypto_magic = CryptoMagic(key, sbox, permutation)

    linear_crypto = LinearCrypto(crypto_magic, [5, 7, 8], [6, 8, 14, 16])
    linear_crypto.generate_table()
    linear_crypto.get_first_stat()

if __name__ == "__main__":
    main()
