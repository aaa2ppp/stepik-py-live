# https://wiki.python.org/moin/BitArrays
# A bit array demo - written for Python 3.0
import array
from random import randint


def makeBitArray(bitSize, fill=0, random=False):
    intSize = (bitSize + 63) >> 6  # number of 64 bit integers

    if fill == 1:
        fill = 0xFFFFFFFF_FFFFFFFF  # all bits set
    else:
        fill = 0  # all bits cleared

    bitArray = array.array('Q')  # 'L' = unsigned 64-bit integer

    if random:
        for _ in range(intSize):
            bitArray.append(randint(0, 0xFFFFFFFF_FFFFFFFF))
    else:
        bitArray.extend((fill,) * intSize)

    bitArray[-1] &= (0xFFFFFFFF_FFFFFFFF >> (64 - bitSize & 63))  # to correctly compare arrays, clear the unused tail

    return bitArray


# testBit() returns 1 if bit is set, or 0 otherwise.
def testBit(array_name, bit_num):
    record = bit_num >> 6
    offset = bit_num & 63
    return (array_name[record] >> offset) & 1


# testBit() returns value of 2 bit (bit_num, bit_num + 1). bit_num must be even!
def getTwoBit(array_name, bit_num):
    record = bit_num >> 6
    offset = bit_num & 63
    return (array_name[record] >> offset) & 3


# setBit() returns an integer with the bit at 'bit_num' set to 1.
def setBit(array_name, bit_num):
    record = bit_num >> 6
    offset = bit_num & 63
    mask = 1 << offset
    array_name[record] |= mask
    return array_name[record]


# clearBit() returns an integer with the bit at 'bit_num' cleared.
def clearBit(array_name, bit_num):
    record = bit_num >> 6
    offset = bit_num & 63
    mask = ~(1 << offset)
    array_name[record] &= mask
    return array_name[record]


# toggleBit() returns an integer with the bit at 'bit_num' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(array_name, bit_num):
    record = bit_num >> 6
    offset = bit_num & 63
    mask = 1 << offset
    array_name[record] ^= mask
    return array_name[record]

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# bits = 65536                     # change these numbers to
#
# ini = 1                          # test the function
#
# myArray = makeBitArray(bits, ini)
#
# # array info: input bits; final length; excess bits; fill pattern
# print(bits, len(myArray), (len(myArray) * 32) - bits, bin(myArray[0]))
