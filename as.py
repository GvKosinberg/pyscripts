import random

def get_random_state(fmt):
    state = random.randint(0,1)
    defas = {"OC": ["OPEN", "CLOSED"],
             "OO": ["ON", "OFF"],
             "HL": ["HIGH", "LOW"]}
    out = defas[fmt][state]
    return out

if __name__ == "__main__":
    print(get_random_state("OO"))
