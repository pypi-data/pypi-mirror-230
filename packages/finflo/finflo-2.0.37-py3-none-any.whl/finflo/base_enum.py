from enum import Enum 



""" default enum values cannot be deleted from admin """ 
""" hint : can be modified """
class Values(Enum):
    DRAFT = "DRAFT"
    RETURN = "RETURN"
    INITIAL_SIGN = "initial sign"
    AWAITING_SIGN_A = "Awaiting Sign A"
    AWAITING_SIGN_B = "Awaiting Sign B"
    AWAITING_SIGN_C = "Awaiting Sign C"
    SIGN_A  = "sign a"
    SIGN_B = "sign b"
    SIGN_C = "sign c"

    
    def __repr__(self):
        return f"{self.value}"
    
    def __str__(self):
        return f"{self.value}"

    def __eq__(self, other):
        return self.value == other if isinstance(other, str) else super().__eq__(other)

    




# IMP_NOTE:  THE DRAFT IS DEFAULT VALUE FOR A TRANSITION STARTED PACK 