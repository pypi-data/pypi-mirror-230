def have_extension(path, ext) :
    """
    returns True if path is ends with ext, False otherwise.
    """
    
    return (path[len(path)-len(ext):len(path)] == ext)

def append_extension_if_missing(path, ext) : 
    """
    add ext to path if path doesnt already ends with ext
    """
    
    if have_extension(path, ext) : 
        return path
    else :
        return path+ext

def remove_extension_if_existing(path, ext) : 
    """
    add ext to path if path doesnt already ends with ext
    """
    
    if have_extension(path, ext) : 
        return path[0:len(path)-len(ext)]
    else :
        return path