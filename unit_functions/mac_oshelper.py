def list_helper(dirs):
    viz = []
    for d in dirs:
        if not d[0] == '.':
            viz.append(d)
    return viz

def join_helper(dirs):
    if not d[0] == '.':
        return d
