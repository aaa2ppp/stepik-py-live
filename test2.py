import time
import world

count = 100
width, height = 256, 256  # `width` must be a multiple of 16!

wf_bi = world.BitArrayWorldFactory(width, height)
wf_or = world.OriginalWorldFactory(width, height)
wf_64 = world.World64Factory(width, height)

bitarray_world = wf_bi.create_random_world()
orig_world = wf_or.create_world_from_bitarray(bitarray_world)
world64 = wf_64.create_world_from_bitarray(bitarray_world)

# print("bitarray:", bitarray_world)
# print("original:", wf_or.convert_world_to_bitarray(orig_world))
# print("world64 :", wf_64.convert_world_to_bitarray(world64))

if bitarray_world != wf_or.convert_world_to_bitarray(orig_world):
    print("FAIL: can't convert orig_world")
    quit(1)

if bitarray_world != wf_64.convert_world_to_bitarray(world64):
    print("FAIL: can't convert world64")
    quit(1)

orig_time, bitarr_time, world64_time = 0.0, 0.0, 0.0

for _ in range(count):
    start_time = time.time()
    bitarray_world = wf_bi.create_next_world(bitarray_world)
    bitarr_time += time.time() - start_time

    start_time = time.time()
    orig_world = wf_or.create_next_world(orig_world)
    orig_time += time.time() - start_time

    start_time = time.time()
    world64 = wf_64.create_next_world(world64)
    world64_time += time.time() - start_time

    if bitarray_world != wf_or.convert_world_to_bitarray(orig_world):
        print("FAIL: orig_world")
        quit(1)

    if bitarray_world != wf_64.convert_world_to_bitarray(world64):
        print("FAIL: world64")
        quit(1)

print("SUCCESS")
print(f"original time: {orig_time} ms")
print(f"bitarray time: {bitarr_time} ms")
print(f"world64 time: {world64_time} ms")
