# main.py
# Manages the sensors talking to the LLM via subprocesses

import subprocess

import time


faceTracker = subprocess.Popen(['python', './Sensors/PythonFaceTracker/main.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
llm = subprocess.Popen("ollama run llama3.2", stdin=subprocess.PIPE, shell=True)

time.sleep(10)
print("time 1")
time.sleep(5)
print("time 2")
out = faceTracker.stdout.readline()
print('3') # Bug, does not reach here
faceTracker.stdout.close()
print('4')
print(str(out))
print('5')
llm.stdin.write(out)
llm.stdin.close()
time.sleep(5)





# T1                        # T2
# print("test1! one")       # print("test2!")
# var = 7                   # var = input()
#                           # print(f"Test2: var = {var}")
# t1 = subprocess.Popen(['python', './test1.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
# t2 = subprocess.Popen(['python', './test2.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
# print(str(t1.stdout.readline()), end="") # Test1!
# print(str(t2.stdout.readline()), end="") # Test2!
# t2.stdin.write(str(t1.stdout.readline())) # T1 prints '7', send that to T2
# t2.stdin.close()                          # close is required to end the input() function
# print(str(t2.stdout.readline()), end="")  # Test2: var = 7
