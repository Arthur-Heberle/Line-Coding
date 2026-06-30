PREFIX = "T"
line = PREFIX + "1-110-11"
line.strip()
print(line)
line = line.removeprefix(PREFIX)
print(line)
j = ""
list = []
for i in line:
    print(i)
    j += i  
    if i in ["1", "0"]:
        list.append(int(j))
        j = ""
      

print (list)