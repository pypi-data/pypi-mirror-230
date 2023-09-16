text=""
with open("/Users/ansoncar/Desktop/MyProject/pyday/requirements.txt") as f:
    for line in f.readlines():
        text+= f"'{line[:-1]}',\n"
print(text)