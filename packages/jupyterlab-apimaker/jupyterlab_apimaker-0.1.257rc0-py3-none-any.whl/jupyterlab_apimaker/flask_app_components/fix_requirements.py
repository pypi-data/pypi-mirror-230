import pkgutil

lines = []
with open('requirements.txt', 'r') as f:
    lines = f.readlines()


with open('requirements.txt', 'w') as f:
    for req in lines:
        if not pkgutil.find_loader(req.strip()):
            f.write(req)