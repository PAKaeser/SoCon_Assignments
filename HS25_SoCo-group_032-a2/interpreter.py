import json
import pprint
import argparse
from typing import (
    Callable,
    Any,
)  # Reference for argparse: https://www.bitecode.dev/p/parameters-options-and-flags-for


def check_input_parameter_length(expected_parameter_length: int):
    """Nested decorator for validating the expected parameter length.
    1. Layer: check_input_parameter_length sets the  expected_parameter_length to the length number
    2. Layer: Defines the actual function
    3. Layer executes the function with the provided parameters
    Reference: https://www.geeksforgeeks.org/python/decorators-with-parameters-in-python/
    """

    def check_input_parameter_length_inner(func: Callable) -> Any:
        def wrapper_check_input_parameter_length_inner(*args, **kwargs) -> Any:
            if arguments.debug:
                print(f"arg length: {len(args[0])}, args: {args[0]}")
            assert len(args[0]) == expected_parameter_length
            result = func(*args, **kwargs)
            return result

        return wrapper_check_input_parameter_length_inner

    return check_input_parameter_length_inner


def add_tracing(func: Callable):
    """Decorator for adding the tracing functionality to a function. """
    def wrapper_function(*args, **kwargs):
        print_depth(func.__name__.replace("do_", ""))
        result = func(*args, **kwargs)
        reverse_depth()
        return result

    return wrapper_function


env = dict()
depth = ""


class Liste:
    # own arraylike object to differentiate lgl lists and python lists in interpreter
    def __init__(self, size):
        self.liste = [0] * size

    def __str__(self):
        return f"{self.liste}"

    def __repr__(self):
        return f"{self.liste}"

    def get_at(self, index):
        assert index < len(self.liste), "Index muss innerhalb der Liste sein"
        return self.liste[index]

    def set_at(self, index, value):
        assert index < len(self.liste), "Index muss innerhalb der Liste sein"
        self.liste[index] = value

    def einfuegen(self, value):
        self.liste.append(value)

    def entfernen(self, index):
        return self.liste.pop(index)

    def groesse(self):
        return len(self.liste)

    def verkette(self, other):
        return self.liste + other.liste
    
class Haufen():
# own setlike object to differentiate lgl sets and python sets in interpreter
    def __init__(self):
        self.haufen = set() 
    
    def __str__(self):
        return f"{self.haufen}"

    def __repr__(self):
        return f"{self.haufen}"
    
    def einfuegen(self, value):
        self.haufen = self.haufen | {value}

    def check_exist(self, value):
        return value in self.haufen
    
    def groesse(self):
        return len(self.haufen)
    
    def mische(self, other):
        return self.haufen | other.haufen


###### Helper functions for tracing ######

def print_depth(func_name):
    if not (arguments.trace or arguments.debug):
        return 
    global depth
    if "+--" in depth:
        depth = "|   " + depth
        print(depth, func_name)
    else:
        depth = "+--" + depth
        print(depth, func_name)


def reverse_depth():
    if not (arguments.trace or arguments.debug):
        return
    global depth
    depth = depth[4:]

##### End of helper functions for tracing ######


def do_set(args, envs):
    assert len(args) >= 2
    assert isinstance(args[0], str)
    var_name = args[0]
    var_value = do(args[1], envs)
    if len(args) > 2:
        index = do(args[2], envs)
        env_set(var_name, var_value, envs, index)
    else:
        env_set(var_name, var_value, envs)
    return var_value


def env_set(name, value, envs, index=None):
    assert isinstance(name, str)
    if index != None:
        envs[-1][name].set_at(index, value)
    else:
        envs[-1][name] = value


def do_get(args, envs):
    assert len(args) >= 1
    assert isinstance(args[0], str)
    var_name = args[0]
    var_value = env_get(var_name, envs)
    if len(args) >= 2:
        index = do(args[1], envs)
        return var_value.get_at(index)
    else:
        return var_value
    # assert args[0] in env, f"Unknown variable {args[0]}"
    # return env[args[0]]


def env_get(name, envs):
    assert isinstance(name, str)
    # envs = [{"same":["func",...]},{"num":3}]
    # we do dynamic scoping
    for env in reversed(envs):
        if name in env:
            return env[name]
    assert False, f"Unknown variable {name}"


def do_seq(args, env):
    # ["addieren", 2, 3], ["addieren", 4, 5]
    for each_ops in args:
        res = do(each_ops, env)
    return res



############################################
# Step 03: Functional Programming Elements #
############################################


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_mappe(args, envs):
    liste = env_get(args[0], envs)
    funktion_name = args[1]
    assert isinstance(liste, Liste)
    assert isinstance(funktion_name, str)

    for index in range(liste.groesse()):
        element = liste.get_at(index)
        neues_element = do(["call", funktion_name, element], envs)
        liste.set_at(index, neues_element)

    return liste


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_reduziere(args, envs):
    liste = env_get(args[0], envs)
    funktion_name = args[1]
    assert isinstance(liste, Liste)
    assert isinstance(funktion_name, str)

    if liste.groesse() == 0:
        assert False, "Cannot reduce an empty array"
    if liste.groesse() == 1:
        return liste.get_at(0)

    element1 = liste.get_at(0)
    element2 = liste.get_at(1)
    neues_element = do(["call", funktion_name, element1, element2], envs)
    liste.set_at(1, neues_element)
    liste.entfernen(0)

    return do_reduziere(args, envs)


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_filtere(args, envs):
    liste = env_get(args[0], envs)
    funktion_name = args[1]
    assert isinstance(liste, Liste)
    assert isinstance(funktion_name, str)

    neue_liste = do(["liste", 0], envs)

    for index in range(liste.groesse()):
        element = liste.get_at(index)
        if do(["call", funktion_name, element], envs) == 1:
            neue_liste.einfuegen(element)

    env_set(args[0], neue_liste, envs)
    
    return neue_liste



###################################
# Step 02: Arrays and Sets in LGL #
###################################


@check_input_parameter_length(expected_parameter_length=1)
def do_liste(args, envs):
    length = do(args[0], envs)
    return Liste(length)


@check_input_parameter_length(expected_parameter_length=0)
def do_haufen(args, envs):
    return Haufen()


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_mische(args, envs):
    haufen1 = do(args[0], envs)
    haufen2 = do(args[1], envs)
    assert isinstance(haufen1, Haufen)
    assert isinstance(haufen2, Haufen)
    return haufen1.mische(haufen2)


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_einfuegen(args, envs):
    haufen1 = env_get(args[0], envs)
    var_value = do(args[1], envs)
    assert isinstance(haufen1, Haufen)
    haufen1.einfuegen(var_value)


@check_input_parameter_length(expected_parameter_length=2)   # check if value (arg[1]) is in haufen (arg[0])
@add_tracing
def do_existenz(args, envs):
    haufen = do(args[0], envs)
    value = do(args[1], envs)
    return value in haufen.haufen


@check_input_parameter_length(expected_parameter_length=1)
@add_tracing
def do_groesse(args, envs):
    assert isinstance(args[0], str)
    sammlung = env_get(args[0], envs)
    assert isinstance(sammlung, Liste) or isinstance(sammlung, Haufen)
    return sammlung.groesse()


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_verkette(args, envs):
    liste1 = do(args[0], envs)
    liste2 = do(args[1], envs)
    assert isinstance(liste1, Liste)
    assert isinstance(liste2, Liste)
    return liste1.verkette(liste2)



######################################################################################################
# Step 01: Mathematical operations, boolean expressions and operations, and do ... until loop in LGL #
######################################################################################################


### Arithmetic Operations ###

@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_addieren(args, env):
    left = do(args[0], env)
    right = do(args[1], env)
    return left + right


@check_input_parameter_length(expected_parameter_length=1)
@add_tracing
def do_absolutwert(args, env):
    value = do(args[0], env)
    if value >= 0:
        return value
    return -value


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_subtrahieren(args, envs):
    left = do(args[0], envs)
    right = do(args[1], envs)
    return left - right


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_multiplizieren(args, envs):
    left = do(args[0], envs)
    right = do(args[1], envs)
    return left * right


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_dividieren(args, envs):
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert right != 0, "Cannot divide by 0"
    return left / right


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_potenzieren(args, envs):
    left = do(args[0], envs)
    right = do(args[1], envs)
    return left ** right


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_modulo(args, envs):
    left = do(args[0], envs)
    right = do(args[1], envs)
    return left % right


### Boolean Operations ###

@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_und(args, envs) -> int:
    """This function acts as an 'AND' gate. The expected input consists of two integers that must be elements of the list [0, 1]
    (two boolean values), otherwise raises an 'AssertionError'.
    Params:
        args (list): List of input arguments with two integers that are boolean values
        envs (dict): Current environments
    """

    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, int), "Left part of 'AND' must be an interger"
    assert isinstance(right, int), "Right part of 'AND' must be an interger"
    assert left in [0, 1], "Left part of 'AND' must be either 0 or 1"
    assert right in [0, 1], "Right part of 'AND' must be either 0 or 1"
    if left and right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_oder(args, envs) -> int:
    """This function acts as an 'OR' gate. The expected input consists of two integers that must be elements of the list [0, 1]
    (two boolean values), otherwise raises an 'AssertionError'.
    Params:
        args (list): List of input arguments with two integers that are boolean values
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, int), "Left part of 'OR' must be an interger"
    assert isinstance(right, int), "Right part of 'OR' must be an interger"
    assert left == 0 or left == 1, "Left part of 'OR' must be either 0 or 1"
    assert right == 0 or right == 1, "Right part of '0R' must be either 0 or 1"
    if left or right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=1)
def do_nicht(args, envs) -> int:
    """This function acts as a 'NOT' gate. The expected input consists of two integers that must be elements of the list [0, 1]
    (two boolean values), otherwise raises an 'AssertionError'.
    Params:
        args (list): List of input arguments with one integer that is a boolean value
        envs (dict): Current environments
    """
    value = do(args[0], envs)
    assert isinstance(value, int), "Input of 'NOT' must be an integer"
    assert value in [0, 1], "Input of 'NOT' must be either 0 or 1"
    if value:
        return 0
    return 1


### Comparison Operations ###

@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_kleiner(args, envs) -> int:
    """This function acts as a < (less than) operator for two numeric values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two numeric parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, float | int)
    assert isinstance(right, float | int)
    if left < right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_groesser(args, envs) -> int:
    """This function acts as a > (greater than) operator for two numeric values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two numeric parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, float | int)
    assert isinstance(right, float | int)
    if left > right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_kleiner_gleich(args, envs) -> int:
    """This function acts as a >= (less equal than) operator for two numeric values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two numeric parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, float | int)
    assert isinstance(right, float | int)
    if left <= right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_groesser_gleich(args, envs) -> int:
    """This function acts as a >= (greater equal than) operator for two numeric values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two numeric parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    assert isinstance(left, float | int)
    assert isinstance(right, float | int)
    if left >= right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_gleich(args, envs) -> int:
    """This function acts as a == (equal) operator for two values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    if left == right:
        return 1
    return 0


@check_input_parameter_length(expected_parameter_length=2)
@add_tracing
def do_nicht_gleich(args, envs) -> int:
    """This function acts as a != (not equal) operator for two values and returns either 1 for or 0 false.
    Params:
        args (list): List of input arguments which must contain two parameters to be compared
        envs (dict): Current environments
    """
    left = do(args[0], envs)
    right = do(args[1], envs)
    if left != right:
        return 1
    return 0


### Loop ###

def do_schleife_kondition(args, envs):
    """Is a do until loop with recursive loop function calls until the condition is met.
    Params:
        args (list): first the condition is expected, which returns a bool
                     value and the function which should be called until the condition is met.
        envs (dict): Current environments

    """
    condition = args[0]
    input_arguments = args[1]

    assert isinstance(condition, list)
    assert isinstance(input_arguments, list)

    condition_result = do(condition, envs)
    if not condition_result:
        do(input_arguments, envs)
        do_schleife_kondition([condition, input_arguments], envs)


@add_tracing
def do_print(args, env):
    if len(args) > 0 and isinstance(args[0], str) and args[0] in OPS:  # ["get", "a"]
        result = do(args, env)
        print(result)
    else:
        args = [do(a, env) for a in args]
        print(*args)
    return None


@check_input_parameter_length(expected_parameter_length=2)
def do_func(args, env):
    params = args[0]
    body = args[1]
    return ["func", params, body]


def do_call(args, envs):  # ["call", "same", 3]
    assert len(args) >= 1
    assert isinstance(args[0], str)
    print_depth(args[0])
    name_func = args[0]  # same
    values = [do(a, envs) for a in args[1:]]  # [3]

    func = env_get(name_func, envs)  # ["func",["num"],["get","num"]]
    assert isinstance(func, list) and (func[0] == "func")
    params = func[1]
    body = func[2]
    assert len(values) == len(params), (
        f"You passed {len(values)} parameters instead of {len(params)}"
    )

    local_env = dict()
    # params = ["num","num2"]
    # values = [3,4]
    # {"num":3, "num2":4}
    for index, param_name in enumerate(params):
        local_env[param_name] = values[index]
    envs.append(local_env)
    result = do(body, envs)  # ["get","num"]
    envs.pop()
    reverse_depth()
    return result


OPS = {
    name.replace("do_", ""): func  # {"addieren":do_addieren,
    for (name, func) in globals().items()  #  "absolutewert":do_absolutewert,
    if name.startswith("do_")  #  "set":do_set, ... }
}

# OPS_EASY = {}
# for (name,func) in globals().items():
#     if name.startswith("do_"): #do_addieren
#         operation_name = name.replace("do_","") # addieren
#         OPS_EASY[operation_name] = func # "addieren" : do_addieren


def do(program, envs):  # ["addieren",1,2]
    if isinstance(program, int):
        return program
    if isinstance(program, str):
        return env_get(program, envs)
    if isinstance(program, Liste):
        return program
    if isinstance(program, Haufen):
        return program
    if arguments.debug:
        print("executing", program[0])

    operation_name = program[0]
    args = program[1:]
    
    if operation_name == "call":
        func_name = args[0]
        if isinstance(func_name, str) and func_name in OPS:
            operation_name = func_name
            args = args[1:]
    
    assert operation_name in OPS, f"Unkown operation {operation_name}"
    func = OPS[operation_name]
    return func(args, envs)


def main():
    global arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", type=str, help="The little german language file to interpret"
    )
    parser.add_argument(
        "--trace", action="store_true", help="Add tracing for function calls"
    )
    parser.add_argument("--debug", action="store_true", help="Add debugging for function calls")
    arguments = parser.parse_args()
    filename = arguments.file
    with open(filename, "r") as f:
        if arguments.trace: print("main")
        program = json.load(f)
        envs = [dict()]
        result = do(program, envs)
    print(">>>", result)
    # pprint.pprint(envs)


if __name__ == "__main__":
    main()
