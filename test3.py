import time

import world.original
import world.bitarray
import world.world64
import world.numpy

count = 100

# Now to correctly compare with the `world64`, the `width` must be a multiple of 16!
width, height = 256, 256

factory1 = world.original.WorldFactory(width, height)
factory2 = world.bitarray.WorldFactory(width, height)
factory3 = world.world64.WorldFactory(width, height)
factory4 = world.numpy.WorldFactory(width, height)

world1 = factory1.create_random_world()
array_ = factory1.pack_world_into_array(world1)

start_time = time.time()
for _ in range(count):
    _tmp = world1
    world1 = factory1.create_next_world(world1)
    # pack1 = factory1.pack_two_worlds_into_array(_tmp, world1)
print(f"original: {round((time.time() - start_time) * 1000 / count, 3)} ms")


world2 = factory2.create_world_from_array(array_)
start_time = time.time()
for _ in range(count):
    _old, world2 = world2, factory2.create_next_world(world2)
    # pack2 = factory2.pack_two_worlds_into_array(_old, world2)
print(f"bitarray: {round((time.time() - start_time) * 1000 / count, 3)} ms")

world3 = factory3.create_world_from_array(array_)
start_time = time.time()
for _ in range(count):
    _old, world3 = world3, factory3.create_next_world(world3)
    # pack3 = factory3.pack_two_worlds_into_array(_old, world3)
print(f"world64 : {round((time.time() - start_time) * 1000 / count, 3)} ms")

world4 = factory4.create_world_from_array(array_)
start_time = time.time()
for _ in range(count):
    _old, world4 = world4, factory4.create_next_world(world4)
    pack4 = factory4.pack_two_worlds_into_array(_old, world4)
print(f"numpy   : {round((time.time() - start_time) * 1000 / count, 3)} ms")

pack1 = factory1.pack_world_into_array(world1)
pack2 = factory2.pack_world_into_array(world2)
pack3 = factory3.pack_world_into_array(world3)
pack4 = factory4.pack_world_into_array(world4)

success = True

if pack2 != pack1:
    print("FAIL: next bitarray")
    success = False

if pack3 != pack1:
    print("FAIL: next world64")
    success = False

if pack4 != pack1:
    print("FAIL: next numpy")
    success = False

if not success:
    quit(1)
