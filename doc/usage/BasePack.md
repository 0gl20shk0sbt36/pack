# BasePack

---

简体中文|[English](./English/BasePack.md)

## 目录

+ [简介](#简介)
+ [方法（类）说明](#方法类说明)
  + [1. bind_type](#1-bind_type)
  + [2. BaseAtomPack](#2-baseatompack)
  + [3. BaseAtomUnPack](#3-baseatomunpack)
  + [4. BasePack](#4-basepack)
  + [5. BaseUnPack](#5-baseunpack)

---

## 简介

这是一个相对安全且可扩展的数据持久化模块基类模块（安全性取决于扩展），它具有对使用者更加友好的操作方式。

本模块对外具有以下几个类：

> + BaseAtomPack 对于原子类型进行打包的基类
> + BaseAtomUnPack 对于原子类型进行解包的基类
> + BasePack 对所有类型进行打包的基类
> + BaseUnPack 对所有类型进行解包的基类

本模块对外具有以下几个方法：

> + bind_type 类型绑定方法

与本模块一起的另一个模块 `ppack`使用本模块完成了对部分内置数据类型的实现（可能不全）。使用示例请查看ppack源代码。

## 方法（类）说明

下面开始讲解以上几个方法：

### 1. bind_type

函数原型：  
`def bind_type(type_: type, num: int = -1):`  

参数：

| 参数名   | 类型   | 说明            |
|-------|------|---------------|
| type_ | type | 要绑定的类型        |
| num   | int  | 参考排列位置（不是强制的） |

本方法用于为类方法绑定类型（暂时一个方法只支持一个类型）,本方法需要作为装饰器配合其他类使用

示例：

```python
from PRPC.pack.BasePack import BaseAtomPack, bind_type


class MyPack(BaseAtomPack):

    @bind_type(int, 1)
    def pack_int(self, data):
        return data.to_bytes(data.bit_length() // 8 + 1, 'big', signed=True)


def main():
    print(MyPack.pack(1))  # 输出：b'\x01'
```

下面开始讲解上面几个类

### 2. BaseAtomPack

**功能：**  
原子类型进行打包的基类，所有原子类型打包类必须继承于此类（或继承于BasePack，不建议）

**可用方法：**  
`def pack(cls, data: Any) -> bytes:`

| 参数   | 类型  | 说明             |
|------|-----|----------------|
| data | Any | 要打包的数据（必须被绑定过） |

**返回值**
(bytes): 打包好的数据（只有打包后的数据，其他的都没有）

### 3. BaseAtomUnPack

**功能：**
原子类型进行解包的基类，所有原子类型解包类必须继承于此类（或继承于BaseUnPack，不建议）

**可用方法：**  
`def unpack(cls, type_: type, data: bytes) -> Any:`

| 参数    | 类型   | 说明             |
|-------|------|----------------|
| type_ | type | 数据的原类型         |
| data  | Any  | 要解包的数据（必须被绑定过） |

**返回值**
(bytes): 解包后的数据

### 4. BasePack

**功能：**
所有类型进行打包的基类，所有可递归类型打包类必须继承于此类

**可用方法：**  
`def pack(cls, data, all_data: tuple[dict[int, type], dict[int, Any]] = None):`

| 参数       | 类型                                | 说明              |
|----------|-----------------------------------|-----------------|
| data     | Any                               | 要打包的数据（必须被绑定过）  |
| all_data | [dict[int, type], dict[int, Any]] | 打包的中间数据，使用者无需知晓 |

**返回值**
(bytes): 打包后的数据

### 5. BaseUnPack

**功能：**
所有类型进行解包的基类，所有可递归类型解包类必须继承于此类

**可用方法：**
`def unpack(cls, id_: Union[bytes, int, ID], all_data: tuple[dict[int, type], dict[int, Any], dict[int, bool]] = None):`

| 参数       | 类型                                                      | 说明              |
|----------|---------------------------------------------------------|-----------------|
| id_      | Union[bytes, int, ID]                                   | 解包的数据ID，使用者无需了解 |
| all_data | tuple[dict[int, type], dict[int, Any], dict[int, bool]] | 打包的中间数据，使用者无需知晓 |

**返回值**
(bytes): 解包后的数据

---

## 使用说明
本模块的使用方法非常简单，  
如果你希望进行打包的数据类型是原子类型，那么你只需要继承BaseAtomPack类，然后使用bind_type方法绑定类型即可，  
如果你希望进行打包的数据类型是可递归类型，那么你只需要继承BasePack类，然后使用bind_type方法绑定类型即可，  
如果你希望进行解包的数据类型是原子类型，那么你只需要继承BaseAtomUnPack类，然后使用bind_type方法绑定类型即可，  
如果你希望进行解包的数据类型是可递归类型，那么你只需要继承BaseUnPack类，然后使用bind_type方法绑定类型即可。  
具体例子请查看ppack源代码。
同时，如果你不希望你所写的类只有一个方法，那么你可以在写完你的类后，使用add_ppack方法将你的类添加到主模块中（建议直接并到ppack中）。
示例：

```python
from PRPC.pack import Pack, bind_type
from PRPC.pack.BasePack import BasePack


class MyPack(BasePack):

    @bind_type(tuple)
    def pack_tuple(self, data):
        # 你的代码
        return 

    
Pack.add_ppack(MyPack)

```

