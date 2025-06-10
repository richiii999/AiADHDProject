# main.py
# Manages the sensors talking to the LLM via subprocesses

import subprocess

import time


faceTracker = subprocess.Popen(['python','-u', './Sensors/PythonFaceTracker/main.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
llm = subprocess.Popen("ollama run llama3.2", stdin=subprocess.PIPE, shell=True)

# while True:
time.sleep(5)
print("time 1")
time.sleep(5)
print("time 2")
out = faceTracker.stdout.readline()
# faceTracker.stdout.close()
print(str(out))
llm.stdin.write(out)
llm.stdin.flush()
time.sleep(5)
print("exit")


# todo: turn off subprocess from this file


# T1                        # T2
# print("test1!")           # print("test2!")
# var = 7                   # var = input()
# print(var)                # print(f"Test2: var = {var}")
t1 = subprocess.Popen(['python', './test1.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
t2 = subprocess.Popen(['python', './test2.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
print(str(t1.stdout.readline()), end="") # Test1!
print(str(t2.stdout.readline()), end="") # Test2!
t2.stdin.write(str(t1.stdout.readline())) # T1 prints '7', send that to T2
t2.stdin.close()                          # close is required to end the input() function
print(str(t2.stdout.readline()), end="")  # Test2: var = 7
