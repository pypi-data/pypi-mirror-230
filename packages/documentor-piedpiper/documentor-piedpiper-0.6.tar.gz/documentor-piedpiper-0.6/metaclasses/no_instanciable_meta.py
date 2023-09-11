class NoInstanciable(type):
    def __call__(cls, *args, **kwargs):
        raise TypeError(f"Class '{cls.__name__}' is not instanciable.")
