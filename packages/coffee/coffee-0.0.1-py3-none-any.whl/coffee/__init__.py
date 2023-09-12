from typing import Any, List, Callable


def get_cls_repr(obj: Any, attrs: List[str] = None) -> str:
    attrs = attrs or list()
    attr_string = ", ".join([
        f'{attr}={getattr(obj, attr)}'
        for attr in attrs
    ])
    return f'{obj.__class__.__name__}({attr_string})'


def model(original_class):
    orig_init = original_class.__init__
    orig_setattr = original_class.__setattr__

    setters = dict()
    for k, v in original_class.__dict__.items():
        if isinstance(v, field):
            if v.setfn is not None:
                setters[k] = v.setfn

    def __init__(self, *args, **kws):
        print(original_class.__annotations__)
        self.__dict__.update(kws)
        orig_init(self, *args)

    def __repr__(self):
        return get_cls_repr(self, list(original_class.__annotations__.keys()))

    def __setattr__(self, attr, value):
        if attr in setters:
            orig_setattr(self, attr, setters[attr](self, value))
        else:
            orig_setattr(self, attr, value)

    original_class.__init__ = __init__ 
    original_class.__repr__ = __repr__ 
    original_class.__setattr__ = __setattr__
    return original_class


class Field:

    def __init__(self):
        self.setfn: Callable = None

    def setter(self, fn):
        self.setfn = fn

def field() -> Field: return Field()

@model
class Apple:
    color: str = field()

    @color.setter
    def set_color(self, color):
        print('here is the setter')

    def set_color(self, color: str) -> None:
        if color not in ['red', 'green']:
            raise ValueError(f'Not a valid apple color: {color}')
        self.color = color
