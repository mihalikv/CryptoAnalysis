import random

import time
from bitstring import BitArray
from prettytable import PrettyTable

from Magic import CryptoMagic


class LinearCrypto(object):
    def __init__(self, magic, inputs: list, outputs: list, alternative_inputs: list, alternative_outputs: list) -> None:
        super().__init__()
        self.magic = magic
        self.inputs = [inputs, alternative_inputs, inputs]
        self.outputs = [outputs, alternative_outputs, outputs]

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
                    result_four_bits = CryptoMagic.one_substitution(input_four_bits.uint, self.magic.sbox)
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

    def get_stat(self):
        filename0 = '{}_lin.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        file = open(filename0, 'a')
        stop = 10000
        step = 100
        total_equals = [0, 0, 0]
        for i in range(stop):
            random_input = random.SystemRandom().randint(0, 65535)
            random_output = random.SystemRandom().randint(0, 65535)  # for third stat
            random_input_bits = BitArray(length=16, uint=random_input)
            random_output_bits = BitArray(length=16, uint=random_output)  # for third stat
            encrypted = self.magic.encrypt(random_input_bits)
            result = False
            for stat_index in range(3):
                for input in self.inputs[stat_index]:
                    result ^= random_input_bits[input - 1]
                for output in self.outputs[stat_index]:
                    if stat_index == 2:
                        result ^= random_output_bits[output - 1]
                    else:
                        result ^= encrypted[output - 1]
                if not result:
                    total_equals[stat_index] += 1
            if i % step == 0 and i != 0:
                file.write("{}, {}, {}, {}\n".format(float((total_equals[0] - (i / 2)) / i),
                                                     float((total_equals[1] - (i / 2)) / i),
                                                     float((total_equals[2] - (i / 2)) / i), i))
        file.close()


class DifferentialCrypto(object):
    def __init__(self, magic,
                 delta_p: BitArray,
                 delta_u: BitArray,
                 delta_p_alt: BitArray,
                 delta_u_alt: BitArray) -> None:

        super().__init__()
        self.magic = magic
        self.delta_p = [delta_p, delta_p_alt]
        self.delta_u = [delta_u, delta_u_alt]

    def get_stat(self):
        filename0 = '{}_diff.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        file = open(filename0, 'a')
        stop = 10000
        step = 100
        total_equals = [0, 0, 0]
        for i in range(stop):
            for stat_index in range(3):
                if stat_index == 2:
                    x = random.SystemRandom().randint(0, 65535)
                    y = random.SystemRandom().randint(0, 65535)
                    if x ^ y == self.delta_u[0].uint:
                        total_equals[stat_index] += 1
                else:
                    x = random.SystemRandom().randint(0, 65535)
                    x_bits = BitArray(length=16, uint=x)
                    y = self.magic.encrypt(x_bits, 3)
                    x_1 = BitArray(length=16, uint=(x ^ self.delta_p[stat_index].uint))
                    y_1 = self.magic.encrypt(x_1, 3)
                    if y.uint ^ y_1.uint == self.delta_u[stat_index].uint:
                        total_equals[stat_index] += 1
            if i % step == 0 and i != 0:
                file.write("{}, {}, {}, {}\n".format(float((total_equals[0] - (i / 2)) / i),
                                                     float((total_equals[1] - (i / 2)) / i),
                                                     float((total_equals[2] - (i / 2)) / i), i))
                total_equals = [0, 0, 0]
        file.close()


def main():
    plain_text = BitArray('0b0000101100000000')
    sbox = [7, 0, 13, 3, 12, 15, 5, 4, 11, 2, 1, 14, 9, 10, 6, 8]
    permutation = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    key = BitArray(length=80, uint=0)
    crypto_magic = CryptoMagic(key, sbox, permutation)
    linear_crypto = LinearCrypto(crypto_magic, [2, 3, 4], [5, 6, 9, 10, 13, 14], [4], [10, 12])
    linear_crypto.get_stat()

    differential_crypto = DifferentialCrypto(
        crypto_magic,
        BitArray('0b0000101100000000'),
        BitArray('0b0000011000000110'),
        BitArray('0b0000101100000000'),
        BitArray('0b0000100100000000'),
    )
    differential_crypto.get_stat()


if __name__ == "__main__":
    main()
