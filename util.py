import os
def safe_name(path):
    if not os.path.exists(path):
        return path

    dir = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))

    i = 1
    while True:
        new_path = os.path.join(dir, name + " - " + str(i) + ext)
        if not os.path.exists(new_path):
            return new_path
        i += 1
