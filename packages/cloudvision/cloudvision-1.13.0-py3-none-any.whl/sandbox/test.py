storagePath = ["a", "b", "c", "d", "e"]
# Generate the list of path pointer notifs that lead to the
for i, pathElem in enumerate(storagePath):
    if i == 0:
        continue
    print(f"currentPath = {storagePath[:i]}")
    print(f"{pathElem} : {storagePath[:i+1]}")
