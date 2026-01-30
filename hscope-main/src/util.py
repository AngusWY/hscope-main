
class SimpleEnum:
    def __init__(self, args):
        self._members = {}
        self._reverse_lookup = {}
        if isinstance(args, list):
            # Initialization from list
            for i, name in enumerate(args):
                self._members[name] = i
                self._reverse_lookup[i] = name
                setattr(self, name, i)
        elif isinstance(args, dict):
            # Initialization from dictionary
            for name, value in args.items():
                self._members[name] = value
                self._reverse_lookup[value] = name  # Assuming the values are unique and hashable
                setattr(self, name, value)

    def __getitem__(self, value):
        return self._reverse_lookup[value]

    def reverse(self, value):
        return self._reverse_lookup[value]

    def __getattr__(self, item):
        return self._members[item]

    def __contains__(self, name):
        return name in self._reverse_lookup

    def __iter__(self):
        return iter(self._reverse_lookup)

    def __repr__(self):
        return f"SimpleEnum({self._members})"

    def map(self, name):
        return self._members[name]
def get_unit_id(unit_info):
    if not unit_info:
        return -1
    return unit_info.module_id

def get_unit_name(unit_info):
    if not unit_info:
        return None
    return unit_info.symbol_name

def hex_to_decimal(hex_str):
    try:
        # base=16 
        decimal_num = int(hex_str, 16)
        return decimal_num
    except ValueError:
        # 
        return hex_str