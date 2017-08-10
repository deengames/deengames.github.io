# requires Python 3.4+
from importlib import util
spec = util.find_spec('PIL')

if spec is not None:
    import src.builder
    src.builder.Builder().build()
else:
    raise "Please install the 'pillow' library (pip install pillow)."
