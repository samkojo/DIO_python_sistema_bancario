from usingversion import getattr_with_version

__getattr__ = getattr_with_version("sistema_bancario", __file__, __name__)
