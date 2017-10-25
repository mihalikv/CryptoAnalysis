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
        filename0 = '{}_0.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        filename1 = '{}_1.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        filename2 = '{}_2.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        files = [open(filename0, 'a'), open(filename1, 'a'), open(filename2, 'a')]
        start, stop = 1000, 10000
        step = int(stop / start)
        for j in range(step):
            total_equals = [0, 0, 0]
            total = start * (j + 1)
            for i in range(total):
                random_input = random.SystemRandom().randint(0, 65535)
                random_output = random.SystemRandom().randint(0, 65535)  # for third stat
                random_input_bits = BitArray(length=16, uint=random_input)
                random_output_bits = BitArray(length=16, uint=random_output)  # for third stat
                encrypted = self.magic.encrypt(random_input_bits, 3)
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
            for stat_index in range(3):
                files[stat_index].write("{}, {}\n".format(float(total_equals[stat_index] / total), total))
        map(lambda f: f.close(), files)


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
        filename0 = '{}_0.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        filename1 = '{}_1.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
        files = [open(filename0, 'a'), open(filename1, 'a')]
        start, stop = 1000, 10000
        step = int(stop / start)
        for j in range(step):
            total_equals = [0, 0]
            total = start * (j + 1)
            for i in range(total):
                for stat_index in range(1):
                    x = random.SystemRandom().randint(0, 65535)
                    x_bits = BitArray(length=16, uint=x)
                    y = self.magic.encrypt(x_bits, 3)
                    x_1 = BitArray(length=16, uint=(x ^ self.delta_p[stat_index].uint))
                    y_1 = self.magic.encrypt(x_1, 3)
                    if y.uint ^ y_1.uint == self.delta_u[stat_index].uint:
                        total_equals[stat_index] += 1
            for stat_index in range(1):
                files[stat_index].write("{}, {}\n".format(float(total_equals[stat_index] / total), total))
        map(lambda f: f.close(), files)


def main():
    plain_text = BitArray('0b0000101100000000')
    sbox = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
    permutation = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
    key = BitArray(length=80, uint=0)
    crypto_magic = CryptoMagic(key, sbox, permutation)
    # print(crypto_magic.encrypt(plain_text, 4).bin)
    # linear_crypto = LinearCrypto(crypto_magic, [5, 7, 8], [6, 8, 14, 16], [6, 7, 8], [6, 8, 13, 16])
    # linear_crypto.generate_table()
    # linear_crypto.get_stat()

    differential_crypto = DifferentialCrypto(
        crypto_magic,
        BitArray('0b0000101100000000'),
        BitArray('0b0000011000000110'),
        BitArray('0b0000010000000000'),
        BitArray('0b0000100100000000'),
    )
    differential_crypto.get_stat()


if __name__ == "__main__":
    main()
