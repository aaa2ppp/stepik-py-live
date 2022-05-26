# https://wiki.python.org/moin/BitArrays
# A bit array demo - written for Python 3.0
import array
from random import randint


def makeBitArray(bitSize, fill=0, random=False):
    intSize = (bitSize + 31) >> 5  # number of 32-bit integers

    if fill == 1:
        fill = 4294967295  # all bits set
    else:
        fill = 0  # all bits cleared

    bitArray = array.array('L')  # 'L' = unsigned 32-bit integer

    if random:
        for _ in range(intSize):
            bitArray.append(randint(0, 0xFFFFFFFF))
    else:
        bitArray.extend((fill,) * intSize)

    bitArray[-1] &= (0xFFFFFFFF >> (32 - bitSize & 31))  # to correctly compare arrays, clear the unused tail

    return bitArray


# testBit() returns a nonzero result, 2**offset, if the bit at 'bit_num' is set to 1.
def testBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = 1 << offset
    return array_name[record] & mask


# getOneBit() returns 1 if bit is set or 0 otherwise.
def getBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    return (array_name[record] >> offset) & 1


# getTwoBit() returns value of 2 bit
# NOTE: Here bits are not shifted between records!
def getTwoBits(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    return (array_name[record] >> offset) & 3


# getFourBit() returns value of 4 bit
# NOTE: Here bits are not shifted between records!
def getFourBits(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    return (array_name[record] >> offset) & 15


# setBit() returns an integer with the bit at 'bit_num' set to 1.
def setBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = 1 << offset
    array_name[record] |= mask
    return array_name[record]


# clearBit() returns an integer with the bit at 'bit_num' cleared.
def clearBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = ~(1 << offset)
    array_name[record] &= mask
    return array_name[record]


# toggleBit() returns an integer with the bit at 'bit_num' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
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
