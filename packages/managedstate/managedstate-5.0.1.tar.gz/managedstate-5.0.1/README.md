# managedstate

###### State management inspired by Redux

## Quickstart

### Setup

```python
from managedstate import State

initial_state = {
    "first_key": [
        {
            "id": 1,
            "second_key": True
        },
        {
            "id": 2,
            "second_key": False
        }
    ]
}

state = State(initial_state=initial_state)
```

### Getting the state

- The full state object
```python
>>> state.get()
{'first_key': [{'id': 1, 'second_key': True}, {'id': 2, 'second_key': False}]}
```

- A sub-state object
```python
>>> state.get(["first_key", 0, "second_key"], defaults=[[], {}, False])
True
```

- A sub-state object, using a query function
```python
def id_is_1_query(first_key_list):
    for index, obj in enumerate(first_key_list):
        if obj["id"] == 1:
            return index
```
```python
>>> state.get(["first_key", KeyQuery(id_is_1_query), "second_key"], defaults=[[], {}, False])
True
```

### Setting the state
- The full state object
```python
>>> state.set({'first_key': [{'id': 3, 'second_key': True}, {'id': 4, 'second_key': False}]})
>>> state.get()
{'first_key': [{'id': 3, 'second_key': True}, {'id': 4, 'second_key': False}]}
```

- A sub-state object, using a query function
```python
def get_id_key_query(target_id):  # This will dynamically create the query we need, when we need it
    def id_query(substate):
        for index, obj in enumerate(substate):
            if obj["id"] == target_id:
                return index
    return KeyQuery(id_query)
```
```python
>>> state.set(False, ['first_key', get_id_key_query(3), 'second_key'], defaults=[[], {}])
>>> state.get()
{'first_key': [{'id': 3, 'second_key': False}, {'id': 4, 'second_key': False}]}
```


## Functionality

### Dependencies

The State class and the extensions in this package implement Extendable and Extension respectively, from [objectextensions](https://github.com/immijimmi/objectextensions).
As such, applying extensions is done by calling the class method `State.with_extensions()` and passing in the extension classes to be applied.

Example code:
```python
from managedstate import State
from managedstate.extensions import Registrar

state = State.with_extensions(Registrar)()
```

### Extensions

*extensions*.**Registrar**  
&nbsp;&nbsp;&nbsp;&nbsp;Allows specific get and set operations to be registered under a shorthand label for ease of use later.  
&nbsp;

*extensions*.**Listeners**  
&nbsp;&nbsp;&nbsp;&nbsp;Provides an easy way to attach observer methods that will be called immediately after `set()` and/or `get()`.  
&nbsp;

### Data Classes

**AttributeName**(*self, attribute_name: str*)  
&nbsp;&nbsp;&nbsp;&nbsp;An instance of this class should be provided as a path key when getting or setting the state,  
&nbsp;&nbsp;&nbsp;&nbsp;to indicate that the next nesting level of the state should be accessed via an object attribute.  

*Note: As this class is used indirectly to determine the method of access into the state,*  
&nbsp;&nbsp;&nbsp;&nbsp;*it should never be stored directly as a key within that state.*  
&nbsp;

**KeyQuery**(*self, path_key_getter: Callable[[Any], Any]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Instances of this class can be provided as path keys when getting or setting the state,  
&nbsp;&nbsp;&nbsp;&nbsp;to indicate that the next nesting level of the state should be accessed via the path key returned  
&nbsp;&nbsp;&nbsp;&nbsp;from its stored function.  
&nbsp;&nbsp;&nbsp;&nbsp;The function will receive a copy of the state object at the current level of nesting  
&nbsp;&nbsp;&nbsp;&nbsp;in order to determine what key to return.  
&nbsp;

*extensions*.**PartialQuery**(*self, path_key_getter: Callable[[Any], Any]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Instances of this class can be provided as path keys only in `Registrar.register_path()`.  
&nbsp;&nbsp;&nbsp;&nbsp;When `registered_get()`/`registered_set()` is called with the relevant path label, the function provided below  
&nbsp;&nbsp;&nbsp;&nbsp;will be called and passed one value from the custom query args list;  
&nbsp;&nbsp;&nbsp;&nbsp;a valid path key or KeyQuery should be returned.  
&nbsp;

### Properties

*extensions*.Registrar.**registered_paths**  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a copy of the current path registry.  
&nbsp;

### Methods

State.**get**(*self, path_keys: Iterable[Any] = (), defaults: Iterable[Any] = ()*)  
&nbsp;&nbsp;&nbsp;&nbsp;Drills into the state object using the provided path keys in sequence.  
&nbsp;&nbsp;&nbsp;&nbsp;Any time progressing further into the state object fails, a copy of the default value at the relevant index  
&nbsp;&nbsp;&nbsp;&nbsp;of defaults is substituted in.  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a copy of the drilled-down state object.  
&nbsp;&nbsp;&nbsp;&nbsp;  
&nbsp;&nbsp;&nbsp;&nbsp;The `defaults` param may be provided any number of default values, and they will only be used as necessary.  
&nbsp;

State.**set**(*self, value: Any, path_keys: Iterable[Any] = (), defaults: Iterable[Any] = ()*)  
&nbsp;&nbsp;&nbsp;&nbsp;Drills into the state object using the provided path keys in sequence.  
&nbsp;&nbsp;&nbsp;&nbsp;Any time progressing further into the state object fails, a copy of the default value at the relevant index  
&nbsp;&nbsp;&nbsp;&nbsp;of defaults is substituted in.  
&nbsp;&nbsp;&nbsp;&nbsp;The final path key is used as the index to store a copy of the provided value at  
&nbsp;&nbsp;&nbsp;&nbsp;inside the drilled-down state object.  
&nbsp;&nbsp;&nbsp;&nbsp;  
&nbsp;&nbsp;&nbsp;&nbsp;The `defaults` param may be provided any number of default values, and they will only be used as necessary.  
&nbsp;

*extensions*.Registrar.**register_path**(*self, registered_path_label: str, path_keys: Iterable[Any], defaults: Iterable[Any] = ()*)  
&nbsp;&nbsp;&nbsp;&nbsp;Saves the provided path keys and defaults under the provided label, so that a custom get or set can be  
&nbsp;&nbsp;&nbsp;&nbsp;carried out at later times simply by providing the label again in a call to `registered_get()` or `registered_set()`.  
&nbsp;

*extensions*.Registrar.**get_shape**(*self, initial_state: Any = None*)  
&nbsp;&nbsp;&nbsp;&nbsp;Generates a default shape for the state, using the current registered paths.  
&nbsp;&nbsp;&nbsp;&nbsp;  
&nbsp;&nbsp;&nbsp;&nbsp;Any registered paths containing PartialQuery objects are truncated for this purpose, as it is not possible  
&nbsp;&nbsp;&nbsp;&nbsp;to determine what kind of value a PartialQuery object would provide to drill further into the state.  
&nbsp;

*extensions*.Registrar.**registered_get**(*self, registered_path_label: str, custom_query_args: Iterable[Any] = ()*)  
&nbsp;&nbsp;&nbsp;&nbsp;Calls `get()`, passing in the path keys and defaults previously provided in `register()`.  
&nbsp;&nbsp;&nbsp;&nbsp;If any of these path keys are instances of PartialQuery, each will be called and passed one value from  
&nbsp;&nbsp;&nbsp;&nbsp;the custom query args list and is expected to return a valid path key or KeyQuery.  
&nbsp;

*extensions*.Registrar.**registered_set**(*self, value: Any, registered_path_label: str, custom_query_args: Iterable[Any] = ()*)  
&nbsp;&nbsp;&nbsp;&nbsp;Calls `set()`, passing in the path keys and defaults previously provided in `register()`.  
&nbsp;&nbsp;&nbsp;&nbsp;If any of these path keys are instances of PartialQuery, each will be called and passed one value from  
&nbsp;&nbsp;&nbsp;&nbsp;the custom query args list and is expected to return a valid path key or KeyQuery.  
&nbsp;

*extensions*.Listeners.**add_listener**(*self, method_name: str, listener: Callable[[dict], None]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Adds the provided listener to a set of callbacks for the specified method.  
&nbsp;&nbsp;&nbsp;&nbsp;These callbacks will receive copies of the method return value and its arguments  
&nbsp;&nbsp;&nbsp;&nbsp;in the form `result, self, *args, **kwargs`.  
&nbsp;

*extensions*.Listeners.**remove_listener**(*self, method_name: str, listener: Callable[[dict], None]*)  
&nbsp;&nbsp;&nbsp;&nbsp;Removes the provided listener from the set of callbacks for the specified method.  
&nbsp;

### Additional Info

- KeyQuery instances provided as path keys can return any valid path key, *except* another KeyQuery or a PartialQuery
- Similarly, PartialQuery instances can return any valid path key except for another PartialQuery (they can however return a KeyQuery)
- The data classes provided in this package are not designed to be stored inside the state object themselves. Doing so may result in unintended behaviour
