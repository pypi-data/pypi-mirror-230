CLASS_DOCUMENTATION_TEMPLATE = """
## `ClassName`

#### Description:
This class represents [a specific entity or concept] and provides functionalities for [specific purposes].

#### Attributes:
- `attribute1` (`Type`): Description of the purpose and use of attribute1. Default: `default_value` (if applicable).
- `attribute2` (`Type`): Description of the purpose and use of attribute2. Default: `default_value` (if applicable).
- ...
- it could have no Attributes at all.

#### Usage Cases:

```python
# Sample code to demonstrate a common use case of instantiating and using the class
instance = ClassName(arg1, arg2)
# The rest of the example
```

#### How it Works:

Brief explanation or description of the internal workings of the class or the logic behind its main functionalities.

#### Dependencies:
- `DependencyName`: Brief description of the dependency and its role.
- Another dependency (if applicable): Description...
[In case of no dependencies display] This class does not have any dependencies.
"""
#_______________________________________________________________________________
#_______________________________________________________________________________
FUNCTION_DOCUMENTATION_TEMPLATE = """
## `function_name(argument1: Type, argument2: Type) -> ReturnType`

#### Description:
This function performs [specific action] and is typically used for [purpose].

#### Arguments:
- `argument1` (`Type`): Description of the purpose and use of argument1.
- `argument2` (`Type`): Description of the purpose and use of argument2.

#### Returns:
- `ReturnType`: Description of what the return value represents.

#### Exceptions:
- `ExceptionName`: Circumstances under which this exception is thrown.

#### Usage Cases:

```python
# Sample code to demonstrate a common use case
result_case1 = function_name(value1, value2)
print(result_case1)

# Another use case (if applicable)
result_case2 = function_name(valueA, valueB)
print(result_case2)
```

#### How it Works:

Explanation or description of the internal workings of the function or the logic behind it.

#### Dependencies:
- `DependencyName`: Brief description of the dependency and its role.
- Another dependency (if applicable): Description...
[In case of no dependencies display] This function does not have any dependencies.
"""
#_______________________________________________________________________________
#_______________________________________________________________________________
METHOD_DOCUMENTATION_TEMPLATE = """
## `method_name(parameter1: Type, parameter2: Type) -> ReturnType`

#### Description:
This method performs [specific action] and is used for [purpose]. This method belongs to the class [class name].

#### Parameters:
- `parameter1` (`Type`): Description of the purpose and use of parameter1.
- `parameterN` (`Type`): Description of the purpose and use of parameterN.

#### Returns:
- `ReturnType`: Description of what the return value represents.

#### Exceptions:
- `ExceptionName`: Circumstances under which this exception is thrown.

#### Usage Cases:

```python
# Sample code to demonstrate a common use case
result_case1 = method_name(value1, value2)
print(result_case1)

# Another use case (if applicable)
result_case2 = method_name(valueA, valueB)
print(result_case2)
```

#### How it Works:

Explanation or description of the internal workings of the method or the logic behind it.

#### Dependencies:
- `DependencyName`: Brief description of the dependency and its role.
- Another dependency (if applicable): Description...
[In case of no dependencies display] This method does not have any dependencies.
"""