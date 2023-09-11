import sys, os

def reroute(directory_names):
    found_paths = []
    for directory_name in directory_names:
        path = os.getcwd()
        previous_path = None
        found = False
        count = 0
        while True:
            if directory_name in os.listdir(path):
                previous_path = path
                path = os.path.join(path, directory_name)
                found = True
                break
            new_path = os.path.abspath(os.path.join(str(path), str(os.pardir)))
            if new_path == path or count >= 5:
                break
            path = new_path
            count += 1
        if not found:
            print(f"Directory '{directory_name}' not found")
            continue
        found_paths.append(path)
    for path in found_paths:
        try:
            os.chdir(path)
            sys.path.append(os.getcwd())
        except OSError:
            print("Can't change the Current Working Directory")
