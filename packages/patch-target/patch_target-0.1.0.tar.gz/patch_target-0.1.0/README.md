# Patch Target: A tiny library for creating valid unittest.mock.patch target arguments


The ability to monkey patch modules, functions, classes, and class instances is a powerful part of testing Python code; however, the unittest.mock.patch
function depends on the developer providing a precise module path AS A STRING to the
object to be patched.
If you refactor where your modules live or make other changes, you will find the annoying and hard-to-decipher-at-first
errors pointing to an invalid module path string.

This small library, consisting of a single exported function,
attempts to make using this function a more straightforward, reliably correct experience.

the `patch_target` function takes 2 arguments:
- a `host_module` of type `ModuleType`
- and an `object_to_be_patched`, a Union of `ModuleType | Callable[[Any], Any] | Type[Any]`

Since you're dealing with python objects instead of strings, you get more guarantees out of the box.
E.g. since you have to pass in a module instead of a string, that means you have to have successfully imported the module
into your test to begin with




example:

Given a src code file like this:
```python
# myapp.mymodule.mysubmodule

import datetime
from uuid import uuid4

def get_current_time():
    return datetime.datetime.now()

def generate_new_id():
    return uuid4()

```
You can patch the non-deterministic pieces (current time and uuid generation) like so:
```python

from unittest.mock import patch, Mock
from myapp.my_module import my_submodule  # noqa
import datetime

import uuid

from patch_target import patch_target


# using the patch decorator
@patch(patch_target(my_submodule, datetime))   # Using string paths the patch arg would be  "myapp.mymodule.my_submodule.datetime"
def test_get_current_time(mock_datetime: Mock) -> None:
    the_beginning_of_time = datetime.datetime(1970, 1, 1)
    mock_datetime.datetime.now.return_value = the_beginning_of_time
    
    actual = my_submodule.get_current_time()
    expected = the_beginning_of_time

    assert actual == expected


# using the patch context manager
def test_generate_new_id() -> None:
    fake_id = "my-super-cool-id"
    with patch(patch_target(my_submodule, uuid.uuid4)) as mock_uuid4: # Using string paths the patch arg would be  "myapp.mymodule.my_submodule.uuid.uuid4"
        mock_uuid4.return_value = fake_id
        
        actual = my_submodule.generate_new_id()
        expected = fake_id
        
        assert actual == expected
```
These are obviously trivial examples, the payoff becomes even more apparent with deeply nested module structures.



