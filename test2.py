import time

import world.original
import world.bitarray
import world.world64

count = 100

# Now to correctly compare with the `world64`, the `width` must be a multiple of 16!
width, height = 256, 256

factory1 = world.original.WorldFactory(width, height)
factory2 = world.bitarray.WorldFactory(width, height)
factory3 = world.world64.WorldFactory(width, height)

world1 = factory1.create_random_world()
array_ = factory1.pack_world_into_array(world1)

world2 = factory2.create_world_from_array(array_)
if factory2.pack_world_into_array(world2) != array_:
    print("FAIL: create (or pack) bitarray world")
    quit(1)

world3 = factory3.create_world_from_array(array_)
if factory3.pack_world_into_array(world3) != array_:
    print("FAIL: create (or pack) world64")
    quit(1)

time1, time2, time3 = 0.0, 0.0, 0.0
success = True

for _ in range(count):
    start_time = time.time()
    _old_world = world1
    world1 = factory1.create_next_world(world1)
    pack1 = factory1.pack_two_worlds_into_array(_old_world, world1)
    time1 += time.time() - start_time

    start_time = time.time()
    _old_world = world2
    world2 = factory2.create_next_world(world2)
    pack2 = factory2.pack_two_worlds_into_array(_old_world, world2)
    time2 += time.time() - start_time

    start_time = time.time()
    _old_world = world3
    world3 = factory3.create_next_world(world3)
    pack3 = factory3.pack_two_worlds_into_array(_old_world, world3)
    time3 += time.time() - start_time

    if pack2 != pack1:
        print("FAIL: next bitarray")
        success = False

    if pack3 != pack1:
        print("FAIL: next world64")
        success = False

    if not success:
        quit(1)

print("SUCCESS")
print(f"original time: {time1} ms")
print(f"bitarray time: {time2} ms")
print(f"world64 time : {time3} ms")

print(f"world64 factory3 _count2/_count1: {factory3._count2 / factory3._count1}")
print(f"world64 factory3 _count2/_count1: {factory3._count3 / factory3._count1}")