
#Test on threading
"""
import threading
import time

def function1():
    while True:
        print('apple')
        time.sleep(0.05)        

def function2():
    while True:
        print('banana')
        time.sleep(0.05)

thread1 = threading.Thread(target=function1)
thread1.start()

thread2 = threading.Thread(target=function2)
thread2.start()"""

#It can work is there is a delay between both of them, where one can switch in from the other.
#This is actually very interesting.
#It only allows the thread to work when there is a delay and it is not forced to execute.

#Test on asyncio
import asyncio

async def ping_inactive_users_each_5_sec():
    while True:
        await asyncio.sleep(1)
        print("1 secs gone, ping the user!")


async def ping_paused_users_each_1_sec():
    while True:
        await asyncio.sleep(1)
        print("every 1 ping paused user!")


async def multi_thread_this():
    run_multiple_tasks_at_once = await asyncio.gather(ping_inactive_users_each_5_sec(), ping_paused_users_each_1_sec())


loop = asyncio.get_event_loop()
loop.run_until_complete(multi_thread_this())