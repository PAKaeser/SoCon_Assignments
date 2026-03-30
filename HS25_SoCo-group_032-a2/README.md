
## Additional concept: Decorator

In our code we use decorators to reduce redundant code and in general to make the code more readable. 

The following decorators are used:

- check_input_parameter_length
  - A configurable decorator which checks the length of the input arguments.
  - Uses 3 wrapped functions: 
    - Most outer: For the definition of the length.
    - Inner function: Wraps the function which should be checked.
    - The most inner function: Validates the length of the arguments.
- add_tracing
  - A wrapper to trace the provided function. It executes the print `printdepth` function before executing the function and the end of the execution `reverse_depth`.

  For a more comprehensive description of how decorators work, the following article explains it: (https://www.geeksforgeeks.org/python/decorators-with-parameters-in-python/)[https://www.geeksforgeeks.org/python/decorators-with-parameters-in-python/]

# Assignment walkthrough

## Step 1

In step 1 the operators for arithmetic, comparison and boolean are implemented in the fist step. To test it the `extensions.lgl` demonstrate all the operations. 

### Arithmetic Operations

- multiplizieren (multiplication): Multiplies the input numbers with each other.
- dividieren(division): The first argument gets divided by the second argument.
- potenzieren (power): The first argument is the base number on which the power, second argument, gets applied. 
- modulo (modulo - remainder operation): Applies the modulo operator to the input arguments. The first argument is the value which gets divided by the second one. 

### Comparison Operations
The comparison operations take two variables as input and compare them with the selected operation. Not all data types are supported for all the operations. The result of the operations are always a binary result: 0 for False and 1 for True. 
- kleiner (less than): Compares two numeric values, either float or integer, if the first provided number is smaller than the second.
- groesser (greater than): Compares two numeric values, either float or integer, if the first provided number is greater than the second.
- kleiner_gleich (less than or equal): Compares two numeric values, either float or integer, if the first provided number is smaller or equal than the second.
- groesser_gleich (greater than or equal): Compares two numeric values, either float or integer, if the first provided number is greater or equal than the second.
- gleich (equal): Compares any given two values if those are equal.
- nicht_gleich (not equal): Compares any given two values if those are not equal.

### Boolean Operations
In terms of the boolean operations, those take `only` boolean values as input! This means, integer either `1` for `True` or `0` for `False`. 
- und (AND): Compares two boolean values and returns if both of them are `True`. 
- oder (OR): Compares two boolean values and returns the or operation between the input boolean values. 
- nicht (NOT): Returns the not boolean value of the input. E.g. 0 gets to 1 and vice-versa. 

### Do while loop

The do while loop `schleife_kondition` executes the provided function until the provided condition is met. This is done by recursively calling the `schleife_kondition` until the stop condition has the boolean operator `True`. Thus, the condition should should return a boolean value! For this the boolean operations implemented in the interpreter can be used. \ 
Example of the loop: \ 
Loops until the target variable `a` is larger than the value `d`. The variable `a` gets increased with the value of variable `c` in each iteration.

```json
[
  ["set", "a", 10],
  ["set", "c", 5],
  ["set", "d", 500],
    ["schleife_kondition", ["groesser", ["get", "a"], ["get", "d"]], ["set", "a", ["addieren", ["get", "a"], ["get", "c"]]]]
]

```

## Step 2
### Arrays: "Listen"
- Creating a new `Liste` with size n:
  The function `do_liste()` takes a list of arguments of size 1 (as asserted in the decorator), executes the argument to make sure that an evaluation can be an expression, then creates a Liste object with the computed size n.
  The Liste object saves an array with n zeros.
  Example in lgl: `["set", "l", ["liste", 5]] `
- To read an element at index i, the function `do_get` can be called the same way as with any other value.
  To actually get to the value at index i, the `do_get` function distinguishes between the two different argument lengths. If there is an additional argument, it executes the expression for the length and calls the method `get_at` on the object with the index as an argument, that then returns the value at index in the Liste.
  Example in lgl: `["get", "l", 3]`
- To set an element at index i, `do_set` is called in the same manner as the `do_get` on a List, with the difference that the method `set_at` is called on the object with the index and the new value as arguments.
  Example in lgl: `["set", "l", 4, 3]`
- To get the size of a Liste, the function `do_groesse` is called, that gets the Liste (or "Haufen") object from the environment and calls the method `groesse` on it.
  Example in lgl: `["groesse", "l"]` 
- To concatenate two Listen, the `do_verkette` function is called with two Liste names. The objects are retrieved from the environment and named liste1 and liste2. The method `verkette(liste2)` is called on liste1, being the front part of the new array. 
  Example in lgl: `["verkette", ["get", "l1"],["get", "l2"]]`
- Finally, helper functions `do_einfuegen()` and `do_entfernen()` were added for implementing `do_filtere()` and `do_reduziere` respectively (the `filter` and `reduce` operations from step 3).

### Sets: "Haufen"
- Creating a Haufen object by calling `do_haufen` will initialize a Haufen object, that stores an empty set.
  Example in lgl: `["set", "h", ["haufen"]]`
- To insert a new element into an existing Haufen, the function `do_einfuegen` should be used. This function gets the Haufen object from the environment and executes the expression given as the value. Then the method `einfuegen` is called on the Haufen object. This method merges two python sets with the pipe operator, one being the set that is stored inside the object, the other one is a new set with only the new value. Using python sets, we don't have to check if multiple identical values are in the Haufen, since python only includes a new element, if it is not existing in the set already. 
  Example in lgl: `["einfuegen", "h", 2]`
-  The function `do_existenz` checks if a value as second argument is in a Haufen (first argument). It evaluates both expression first, to enable creating a Haufen inside the arguments. Then returns a boolean directly using pythons keyword `in` to check if the value is in the objects set.
  Example in lgl: `["existenz", ["get", "h"], 3]` 
- Since there is polymorphism between the two classes Haufen and Liste, the same function `do_groesse` as described in the section *Arrays: "Listen"* can be called for Haufen as well.
  Example in lgl: `["groesse", "h"]`
- To merge two sets, the function `do_mische` needs to be called. It takes two arguments, executes them to enable creating Haufen in the arguments, and uses the method `mische` on the first Haufen with the second Haufen as argument. The method uses the pipe operator to merge the two Haufen. Since Haufen object stores a Python set, we don't have to check if multiple identical elements are in one set, python does that for us.
  Example in lgl: `["mische", ["get", "h1"], ["get", "h2"]]`

## Step 3
### Map
- The function `do_mappe()` loops through all elements of the input array (`liste`, the first input argument) and maps them to their corresponding elements after applying the specified function (`funktion_name`, the second input argument). 
- It returns the modified array after applying the mapping to all elements. 
- The `modified` array is returned instead of creating a new array and returning that one, since it is sensible that a `mapping` operation transforms the input after making it go through the mapping process. For the `filter` operations, the same logic is applied.

### Reduce
- The function `do_reduziere()` takes an array and a function as inputs like with the map operation. 
- Additionally, it checks that no empty array can be reduced (and includes an assertion message if such an array gets passed), and trivially returns the first (and only) element of an array with size 1. 
- Then, it keeps track of the first two elements (`element1` and `element2`) (after checking if the array contains 0 or 1 elements, it must contain at least 2 elements).
- These two elements get called with the specified function and the result (which is a single value (`neues_element`), a crucial step of the reducing process).
- This single value is then placed at the `second position` of the array (where `element2` was).
- The element at the `first position` then gets removed from the array (another step that ensures reduction).
- We finally use recursion by returning `do_reduziere()` with the arguments and the environments. This lets us recursively iterate on the previously described steps so that ultimately a final, reduced array gets returned.

### Filter
- The function `do_filtere()` also takes an array and a function as inputs. 
- It iterates over the input array and inserts in a new, initially empty, array (`neue_liste`) only the elements from the input array that return the boolean value `1` after applying the specified function to those elements. If they returned 1, it means they were evaluated as `true`.
- The new array with the filtered elements gets returned.

## Step 4 - Tracing
The flag `--trace` is parsed by the module argparse, which takes one positional argument `file` and two flags. (`--debug` is used by us while completing the assignment and prints not only the tracing, but also all the called programs by `do()`.) Since there is only one positional argument and flags do not interfere with positioning, it does not matter whether `--trace` is the first or second argument (defined by argparse).

The tracing is built with three-character-long blocks. Depending on the depth of function calls, it either adds only `+--` which is the right-most depth indicator. For each function call one depth down, only `|   `  is added to the left of the string. This pushes the tracing one block to the right and the tracing depth is complete. This builtup is managed by the function `print_depth(func_name)`. It also prints the depth string and the function name. 

After a function is traced, the function `reverse_depth()` is called and the depth string is reduced by a block of four characters, removing those to the left and automatically reduces the depth.

Those two function calls are managed by the decorator `add_tracing(func)`. It catches the function calls, calls `print_depth` with the function name first, executes the function call itself then and afterwards calls `reverse_depth()` . This decorator is called independent of the flag. Whether the function is called with the `--trace` or `--debug` flag is checked inside the functions `print_depth(func_name)` and `reverse_depth()`. 

The variable `depth`, that stores the depth string, is a global variable and therefore can be accessed by both depth functions.

We considered adding the tracing inside the `env_get()` function, checking how deep the array nesting is, but decided not to tamper with a function for a specific task or the environment. Also, using the decorator gives us the ability to easily add and remove tracing to individual functions by adding/removing one line above the definition. Additionally, the decorator and global variable provide more readability than adding additional functionalities to existing functions.


# Example files
## extensions.lgl
In the `extensions.lgl` all the implemented functions, which were required for the step 1 of the assignment, are tested in this script. The structure of this script follows the following ideas: We have `4 numeric variables: a,b,c and d`. Each function gets tested by executing the operation and than using the boolean operators to check if the test has passed. \
Then the result of the test is printed. If the test returns 1, it means that it passed the test. If 0 is printed, this indicates, that the test has failed. 

## data_structures.lgl
We use a big int for separating different parts of the execution of our lgl file. 
- In the first part, two Listen are created. Then values from 1 to 4 are added to the increasing index of Liste 1. For the fifth value, we show that an expression, for example `["addieren", 2, 3]`  can be an argument for a value. After line 9, the Liste in the environment looks like this: `[1, 2, 3, 4, 5]`. Then, the second Liste gets its values, showing in line 11, that also for the index, an expression can be an argument. We show in this part, that `verkette` works, by printing the concatenated Liste of Liste1 and Liste2, printing `[1, 2, 3, 4, 5, 9, 10]`
- In the second part, we show the functionality of `get` for a Liste by calling  `get` with two arguments: Liste1 and 3 as index. 
  Also, we show that `groesse` works for Listen by calling `groesse` on Liste1.
- In the third part, we show that a Haufen is initialized with an empty set. Then we show `einfuegen` by adding 5 and 2 to our Haufen1. 
  After inserting two different values to Haufen1, we show that `groesse` also works on Haufen.
  Then, we show that calling `einfuegen` with an already existing value changes nothing, by adding 2 again and calling `groesse` again.
- In the fourth part, we initialize a new Haufen and insert 1, and 2. By calling `mische`, we show that merging two Haufen with one shared value generates a Haufen with only unique values.
- For the last part, we check if 3 is in the Haufen2. Since Haufen2 is `{1, 2}`, calling `existenz` with value 3 returns `False`.

## functional.lgl
We use a big int number (lots of ones) to separate between different parts.
- In the first part, we showcase the functionality of the `mappe` operation by first defining a new fuction `quadrieren()`. Then a Liste named `a` of size 4 gets created, in which the example values 1 through 4 get inserted. The `mappe` operation with the Liste and defined function gets called, and in the terminal we can see the Liste before and after going though `mappe` with `quadrieren`, for comparison and checking purposes. Printing of Liste before and after also happens for the other two parts.
- In the second part, the `reduziere` operation gets applied on a Liste named `b` with same size and elements as Liste `a`. The operation and Liste get called with the `addieren()` function that was already defined in `interpreter.py`. The result is a the input Liste `b` reduced to a single element, which value was computed by adding all elements of Liste `b` together.
- In the third part, the `filtere` operation gets called with an example Liste named `c` and with the function `groesser_als_zehn`. `c` contains elements `under` the value `10`, as well as `over` it and `equal` to it to check if values under or equal to 10 get correctly filtered out and only values over it get returned, matching the expected behaviour of `>`.

## tracing.lgl
In this file, we show that nested tracing works. To see the output described here, `--trace` has to be added as an argument when called this file.

On line 2 and 3, we show that minor functions like setting or getting variables are not traced. 

On line 4, we show that bigger functions like `addieren` is traced, but the expression in the argument is a get function so this inner function is not traced.

On line 6, a function is defined. Since this works with a set, nothing is traced. 

On line 7, a print function is traced, but it has a larger expressions as an argument. It calls the self-defined function, showing that nesting on one level deeper works fine and also, tracing for self defined functions with their function name works too. 

The function that is called has in its body two `addieren` functions, that are called. This shows, that one level deeper, nesting still works and also, that sequenced tracing works. `addieren` is on the same nested level one after the other executed and tracing captures that.

Then, we see the actual print output. This is the evaluated value after executing all those nested functions.

On line 8, we show that removing the tracing works too by starting at the outermost level and start nesting with `print` and `kleiner_gleich` again. 

# Declaration of use of generative AI
No one in our team has used generative AI to complete this assignment.  