from typing import Callable, List

# Define a type alias for clarity: a function that takes a number and returns a number
F = Callable[[int], int]

def compose(functions: List[F]) -> F:
    def inner(x: int) -> int:
        result = x
        for fn in reversed(functions):  # go from last to first
            result = fn(result)
        return result
    return inner

# Example usage
fn = compose([lambda x: x + 1, lambda x: 2 * x])
print(fn(4))  # Output: 9