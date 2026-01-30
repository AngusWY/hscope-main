
def static_vars(**kwargs):
    """
    [rn]
    
    """
    def decorate(func):
        for k, v in kwargs.items():
            # setset
            value = v() if callable(v) else v
            setattr(func,k,value) 
        return func
    return decorate