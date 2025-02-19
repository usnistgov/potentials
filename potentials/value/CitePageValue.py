from yabadaba.value.StrValue import StrValue

class CitePageValue(StrValue):

    def set_value_mod(self, val):
        
        # Call StrValue's mod
        val = super().set_value_mod(val)
        
        # Pass None values through
        if val is None:
            return None
        
        # Modify str values
        return val.replace('--', '-')