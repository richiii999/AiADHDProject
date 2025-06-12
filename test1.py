from subprocess import Popen, PIPE, STDOUT
import time

p = Popen(['./test2.py'], stdout=PIPE, stdin=PIPE)

p.stdin.write('Hello world\n'.encode())
p.stdin.flush()
print(p.stdout.readline().decode()[:-1])

time.sleep(1)

p.stdin.write('bonne journeé\n'.encode())
p.stdin.flush()
print(p.stdout.readline().decode()[:-1])

time.sleep(1)

p.stdin.write('goodbye world\n'.encode())
p.stdin.flush()
print(p.stdout.readline().decode()[:-1])