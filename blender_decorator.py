classes = []

def register_class(cls):
    classes.append(cls)
    return cls

menus = []

def register_menu(menu):
    def apply(entry):
        menus.append((menu, entry))
    return apply
