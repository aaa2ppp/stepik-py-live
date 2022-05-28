import time
import world

count = 100

# Now to correctly compare with the `world64`, the `width` must be a multiple of 16!
width, height = 256, 256

factory1 = world.OrigWorldFactory(width, height)
factory2 = world.BitArrayWorldFactory(width, height)
factory3 = world.World64Factory(width, height)

world1 = factory1._create_random_world()
array_ = factory1.pack_world_to_array(world1)

world2 = factory2.next_from_array(array_)
if factory2.pack_world_to_array(world2) != array_:
    print("FAIL: create (or pack) bitarray world")
    quit(1)

world3 = factory3.next_from_array(array_)
if factory3.pack_world_to_array(world3) != array_:
    print("FAIL: create (or pack) world64")
    quit(1)

time1, time2, time3 = 0.0, 0.0, 0.0

for _ in range(count):
    start_time = time.time()
    _old_world = world1
    world1 = factory1._create_next_world(world1)
    pack1 = factory1._pack_two_worlds_to_array(_old_world, world1)
    time1 += time.time() - start_time

    start_time = time.time()
    _old_world = world2
    world2 = factory2._create_next_world(world2)
    pack2 = factory2._pack_two_worlds_to_array(_old_world, world2)
    time2 += time.time() - start_time

    start_time = time.time()
    _old_world = world3
    world3 = factory3._create_next_world(world3)
    pack3 = factory3._pack_two_worlds_to_array(_old_world, world3)
    time3 += time.time() - start_time

    if pack2 != pack1:
        print("FAIL: next bitarray")
        quit(1)

    if pack3 != pack1:
        print("FAIL: next world64")
        quit(1)

print("SUCCESS")
print(f"original time: {time1} ms")
print(f"bitarray time: {time2} ms")
print(f"world64 time : {time3} ms")
