import glob

file_list = glob.glob("tmp*.txt")
for f in file_list:
    with open(f, "r", encoding="utf-8") as infile:
        text = infile.read()
    if ("Your search did not match any articles" in text) or ("result" in text):
        pass
    else:
        print("Fail:", f)
