# BasePack

---

[简体中文](../BasePack.md)|English

## Directories

+ [Introduction](# introduction)
+ [method (class) description](# method-class-description)
  + [1. bind_type](#1-bind_type)
  + [2. BaseAtomPack](#2-baseatompack)
  + [3. BaseAtomUnPack](#3-baseatomunpack)
  + [4. BasePack](#4-basepack)
  + [5. BaseUnPack](#5-baseunpack)

---

## Introduction

This is a relatively safe and extensible data persistence module base class module (security depends on extension), which has a more user-friendly way of operating.

This module has the following external classes:

> + **BaseAtomPack** A base class for packing atomic types
> + **BaseAtomUnPack** The base class that unpacks atomic types
> + **BasePack A base** class for packing all types
> + **BaseUnPack** The base class that unpacks all types

This module has the following external methods:

> + **bind_type** Type binding methods

Another module that comes with this module, 'ppack', uses this module to implement some (maybe not all) of the built-in data types. See the ppack source code for an example of use.

## Method (class) description

Let's get started with these methods:

### 1. bind_type

Function prototype:  
`def bind_type(type_: type, num: int = -1):`

Parameters:

| parameter name | type | description                              |
|----------------|------|------------------------------------------|
| type_          | type | to binding type                          | 
| num            | int  | reference array position (not mandatory) |

This method is used to bind types to class methods (for now, only one type per method is supported). This method should be used as a decorator with other classes

Examples:

```python
from PRPC.pack.BasePack import BaseAtomPack, bind_type


class MyPack(BaseAtomPack):

    @bind_type(int, 1)
    def pack_int(self, data):
        return data.to_bytes(data.bit_length() // 8 + 1, 'big', signed=True)


def main():
    print(MyPack.pack(1)) # output: b'\x01'
```

Let's move on to these classes

### 2. BaseAtomPack

**Features:**  
The base class from which atomic types are packed. All atomic packed classes must inherit from this class (or from BasePack, not recommended).

**Available:**  
`def pack(cls, data: Any) -> bytes:`

| parameter name | type | description                       |
|----------------|------|-----------------------------------|
| data           | Any  | to packaging data (must be bound) |

**Return value**
(bytes): The packed data (only the packed data and nothing else)


### 3. BaseAtomUnPack

**Features:**  
Base class for atomic types to unpack. All atomic unpack classes must inherit from this class (or from BaseUnPack, not recommended).

**Available:**  
`def unpack(cls, type_: type, data: bytes) -> Any:`

| parameter name | type | description                    |
|----------------|------|--------------------------------|
| type_          | type | data of the original type      | 
| data           | Any  | to unpack data (must be bound) |

**Return value**
(bytes): Unpacked data

### 4. BasePack

**Features:**  
The base class from which all types are packaged and from which all recursively typed packaged classes must inherit

**Available:**  
`def pack(cls, data, all_data: tuple[dict[int, type], dict[int, Any]] = None):`

| parameter name | type                                 | description                                                  |
|----------------|--------------------------------------|--------------------------------------------------------------|
| data           | Any                                  | to packaging data (must be bound)                            |
| all_data       | [dict [, int type], dict [int, Any]] | packaged in the middle of the data, users don't need to know |

**Return value**
(bytes): The packaged data

### 5. BaseUnPack

**Features:**  
The base class from which all types are unpacked and from which all recursively typed unpacked classes must inherit

**Available:**  
`def unpack(cls, id_: Union[bytes, int, ID], all_data: tuple[dict[int, type], dict[int, Any], dict[int, bool]] = None):`

| parameter name | type                                                            | description                                                  |
|----------------|-----------------------------------------------------------------|--------------------------------------------------------------|
| id_            | Union [bytes, int, ID]                                          | unpack the data of ID, the user need not know                |
| all_data       | tuple [dict [, int type], dict [int, Any], dict [int, Boolean]] | packaged in the middle of the data, users don't need to know |

**Return value**
(bytes): Unpacked data

---

## Instructions
The usage of this module is very simple.
If the data type you want to pack is atomic, then all you have to do is inherit from BaseAtomPack and use the bind_type method to bind the type.
If the data type you want to bundle is a recursive type, then all you have to do is inherit from BasePack and use the bind_type method to bind the type.
If the data type you want to unpack is atomic, then all you have to do is inherit from BaseAtomUnPack and use the bind_type method to bind the type.
If the data type you want to unpack is a recursive type, then all you have to do is inherit from BaseUnPack and use the bind_type method to bind the type.
See the ppack source code for an example.
Also, if you don't want your class to have only one method, then you can add your class to the main module after writing your class using the add_ppack method (directly into ppack is recommended).
Examples:

```python
from PRPC.pack import Pack, bind_type
from PRPC.pack.BasePack import BasePack


class MyPack(BasePack):

    @bind_type(tuple)
    def pack_tuple(self, data):
        # Your code
        return


Pack.add_ppack(MyPack)

```