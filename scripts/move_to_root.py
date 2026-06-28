import shutil
import os

source = "/Users/chad/business/allcitypros/public"
dest = "/Users/chad/business/allcitypros"

for item in os.listdir(source):
    s = os.path.join(source, item)
    d = os.path.join(dest, item)
    if os.path.isdir(s):
        shutil.move(s, d)

print("Moved public files to root.")
