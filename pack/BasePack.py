from typing import TypeVar, Any, Union


class _BindData:

    def __init__(self, type_, fun, num=None):
        self.type_ = type_
        self.fun = fun
        self.num = num

    def __call__(self, *args, **kwargs):
        return self.fun(*args, **kwargs)


T = TypeVar('T')


class BasePPack:
    bind_fun = {}
    obj = None

    def __init_subclass__(cls, **kwargs):
        for name, fun in cls.__dict__.items():
            if isinstance(fun, _BindData):
                setattr(cls, name, fun.fun)
                cls.bind_fun[fun.type_] = fun

    @classmethod
    def copy_ppack(cls: T, cls_name, *, args_=None) -> T:
        if args_ is None:
            args_ = {}
        args = {'bind_fun': cls.bind_fun.copy()}
        args.update({fun.fun.__name__: fun for fun in cls.bind_fun.values()})
        args.update(args_)
        return type(cls_name, (cls.__bases__[0],), args)

    @classmethod
    def add_ppack(cls: T, other: T):
        if not issubclass(other, BasePPack):
            raise TypeError()
        base = cls.__bases__[0]
        if other.__bases__[0] != base:
            raise TypeError()
        cls.bind_fun.update(other.bind_fun)
        for fun in other.bind_fun.values():
            if isinstance(fun, _BindData):
                setattr(cls, fun.__name__, fun)


class BaseAtomPack(BasePPack):
    bind_fun: dict[type, _BindData] = {}

    @classmethod
    def pack(cls, data) -> bytes:
        if cls.obj is None:
            cls.obj = cls()
        return cls.bind_fun[type(data)](cls.obj, data)


class BaseAtomUnPack(BasePPack):
    bind_fun: dict[type, _BindData] = {}

    @classmethod
    def unpack(cls, type_: type, data: bytes):
        if cls.obj is None:
            cls.obj = cls()
        return cls.bind_fun[type_](cls.obj, data)


def bind_type(type_, num=-1):
    def _bind_(fun: T) -> T:
        return _BindData(type_, fun, num)

    return _bind_


class _ID:

    def __init__(self):
        self.data = {}

    def __get__(self, instance, owner):
        return self.data[instance._id]

    def __set__(self, instance, value):
        if instance._id in instance.ids:
            del instance.ids[instance._id]
        instance.ids[value] = instance
        self.data[instance._id] = value


class ID:
    ids = {}
    id_ = _ID()

    def __new__(cls, data=None, id_=None):
        if id_ is None:
            id_ = id(data)
        if id_ in cls.ids:
            return cls.ids[id_]
        id_o = super().__new__(cls)
        id_o._id = id(data)
        id_o.id_ = id(data)
        cls.ids[id_] = id_o
        return id_o

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, o):
        if isinstance(o, ID):
            return self.id_ == o.id_
        if isinstance(o, int):
            return self.id_ == o
        return False

    def __str__(self):
        return str(self.id_)

    def __repr__(self):
        return str(self.id_)


def uint_to_bytes(int_: int) -> bytes:
    """
    The function `uint_to_bytes` converts an unsigned integer into a byte array.
    
    :param int_: The `int_` parameter is an integer value that we want to convert to bytes
    :type int_: int
    :return: The function `uint_to_bytes` returns a `bytes` object.
    """
    data = bytearray()
    for i in range((int_.bit_length() - 1) // 7, 0, -1):
        data.append((int_ >> (7 * i)) & 0b1111111)
    data.append(int_ & 0b1111111 | 0b10000000)
    return bytes(data)


def uint_from_bytes(data: bytes, start: int = 0) -> tuple[int, int]:
    """
    The function `uint_from_bytes` converts a variable-length encoded integer from a byte array to an
    unsigned integer and returns the integer value along with the index of the next byte in the array.
    
    :param data: The `data` parameter is a `bytes` object, which represents a sequence of bytes. It is
    the input from which we want to extract an unsigned integer
    :type data: bytes
    :param start: The `start` parameter is the index in the `data` bytes where the decoding of the
    unsigned integer should start. It is set to 0 by default, which means the decoding will start from
    the beginning of the `data` bytes, defaults to 0
    :type start: int (optional)
    :return: The function `uint_from_bytes` returns a tuple containing two values: an integer (`int_`)
    and an integer (`start`).
    """
    int_ = 0
    while True:
        int_ <<= 7
        int_ += data[start] & 0b1111111
        if data[start] & 0b10000000:
            break
        start += 1
    start += 1
    return int_, start


# region _Placeholder
# class _Placeholder:

#     ids = {}
#     id_ = _ID()

#     def __new__(cls, data=None, id_=None):
#         if id_ is None:
#             id_ = id(data)
#         if id_ in cls.ids:
#             return cls.ids[id_]
#         id_o = super().__new__(cls)
#         id_o._id = id(data)
#         id_o.id_ = id(data)
#         cls.ids[id_] = id_o
#         return id_o

#     def __hash__(self):
#         return hash(self._id)

#     def __eq__(self, o):
#         if isinstance(o, ID):
#             return self.id_ == o.id_
#         if isinstance(o, int):
#             return self.id_ == o
#         return False
# endregion


class BasePack(BasePPack):
    """打包类的基类

    Raises:
        TypeError: 未定义这个类型
    """
    bind_fun = {}
    _bind_types = ()
    atom_pack = None
    _atom_bind_types = ()
    pack_num = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.init()

    @classmethod
    def copy_ppack(cls: T, cls_name, *, args_=None) -> T:
        return super().copy_ppack(cls_name, args_={'atom_pack': cls.atom_pack})

    @classmethod
    def init(cls):
        """初始化(在修改了atom_unpack后需要调用)
        """
        pack_num: dict[int, list[type]] = {}
        bind_types = []
        for atom_pack in cls.atom_pack.bind_fun.values():
            pack_num.setdefault(atom_pack.num, []).append(atom_pack.type_)
            bind_types.append(atom_pack.type_)
        cls._atom_bind_types = tuple(bind_types)
        bind_types = []
        for atom_pack in cls.bind_fun.values():
            pack_num.setdefault(atom_pack.num, []).append(atom_pack.type_)
            bind_types.append(atom_pack.type_)
        cls._bind_types = bind_types
        num = 0
        cls_pack_num = {}
        for num_ in sorted(pack_num.keys()):
            if num_ == -1:
                continue
            for pack_fun in pack_num[num_]:
                cls_pack_num[pack_fun] = num
                num += 1
        for pack_fun in pack_num.get(-1, []):
            cls_pack_num[pack_fun] = num
            num += 1
        cls.pack_num = cls_pack_num

    @classmethod
    def integrate(cls, start_id: ID, all_data: tuple[dict[int, type], dict[int, Any]]):
        """组装

        Args:
            start_id (ID): 起始对象的ID
            all_data (tuple[dict[int, type], dict[int, Any]]): 所有数据.

        Returns:
            bytes: 组装好的数据
        """
        id_num = 0
        for id_ in all_data[0]:
            id_.id_ = id_num
            id_num += 1
        head = bytearray()
        head.extend(uint_to_bytes(start_id.id_))
        types = bytearray()
        datas = bytearray()
        for id_ in range(id_num):
            id_ = ID(id_=id_)
            types.extend(uint_to_bytes(all_data[0][id_]))
            data = all_data[1][id_]
            if isinstance(data, bytes):
                datas.extend(uint_to_bytes(len(data) + 1))
                datas.append(0)
                datas.extend(data)
            elif isinstance(data, tuple):
                data_ = bytearray()
                data_.append(1)
                data_.extend(uint_to_bytes(len(data[0])))
                data_.extend(data[0])
                for i in data[1]:
                    data_.extend(uint_to_bytes(i.id_))
                datas.extend(uint_to_bytes(len(data_)))
                datas.extend(data_)
        head.extend(uint_to_bytes(len(types)))
        head.extend(uint_to_bytes(len(datas)))
        return bytes(head + types + datas)

    @staticmethod
    def login(data, id_, all_data: tuple[dict[int, type], dict[int, Any]]):
        """注册返回值(用于解决循环引用)

        Args:
            data (Any): 注册的返回值
            id_ (ID): 注册的ID
            all_data (tuple[dict[int, type], dict[int, Any]]): 所有过程数据.
        """
        all_data[1][id_] = data

    @classmethod
    def pack(cls, data, all_data: tuple[dict[int, type], dict[int, Any]] = None):
        """打包

        Args:
            data (Any): 要打包的对象
            all_data (tuple[dict[int, type], dict[int, Any]], optional): 打包过程数据,使用者不用管.

        Raises:
            TypeError: 未定义这个类型

        Returns:
            bytes or None: 打包好的数据
        """
        if all_data is None:
            all_data = {}, {}
            integrate = True
        else:
            integrate = False
        if cls.obj is None:
            cls.obj = cls()
        if ID(data) not in all_data[1]:
            type_data = type(data)
            if type_data in cls._bind_types:
                all_data[1][ID(data)] = cls.bind_fun[type(data)](cls.obj, data, all_data)
                all_data[0][ID(data)] = cls.pack_num[type(data)]
            elif type_data in cls._atom_bind_types:
                all_data[1][ID(data)] = cls.atom_pack.pack(data)
                all_data[0][ID(data)] = cls.pack_num[type(data)]
            else:
                raise TypeError()
        if integrate:
            return cls.integrate(ID(data), all_data)


class BaseUnPack(BasePPack):
    """解包类的基类

    Raises:
        TypeError: 未定义这个类型
    """
    bind_fun = {}
    _bind_types = ()
    atom_unpack = None
    _atom_bind_types = ()
    pack_num = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.init()

    @classmethod
    def copy_ppack(cls: T, cls_name, *, args_=None) -> T:
        return super().copy_ppack(cls_name, args_={'atom_unpack': cls.atom_unpack.copy()})

    @classmethod
    def init(cls):
        """初始化(在修改了atom_unpack后需要调用)
        """
        pack_num: dict[int, list[type]] = {}
        bind_types = []
        for atom_unpack in cls.atom_unpack.bind_fun.values():
            pack_num.setdefault(atom_unpack.num, []).append(atom_unpack.type_)
            bind_types.append(atom_unpack.type_)
        cls._atom_bind_types = tuple(bind_types)
        bind_types = []
        for atom_unpack in cls.bind_fun.values():
            pack_num.setdefault(atom_unpack.num, []).append(atom_unpack.type_)
            bind_types.append(atom_unpack.type_)
        cls._bind_types = bind_types
        num = 0
        cls_pack_num = {}
        for num_ in sorted(pack_num.keys()):
            if num_ == -1:
                continue
            for pack_fun in pack_num[num_]:
                cls_pack_num[num] = pack_fun
                num += 1
        for pack_fun in pack_num.get(-1, []):
            cls_pack_num[num] = pack_fun
            num += 1
        cls.pack_num = cls_pack_num

    @classmethod
    def __get_head(cls, data: bytes):
        index = 0
        start_id, index = uint_from_bytes(data, index)
        types_len, index = uint_from_bytes(data, index)
        datas_len, index = uint_from_bytes(data, index)
        types_bytes = data[index: index + types_len]
        datas_bytes = data[index + types_len: index + types_len + datas_len]
        return start_id, types_bytes, datas_bytes

    @classmethod
    def __get_body(cls, types_bytes, datas_bytes):
        all_type = {}
        all_data = {}
        num = 0
        types_index = 0
        data_index = 0
        len_types = len(types_bytes)
        while types_index < len_types:
            type_, types_index = uint_from_bytes(types_bytes, types_index)
            all_type[ID(id_=num)] = type_
            data_len, data_index = uint_from_bytes(datas_bytes, data_index)
            data = datas_bytes[data_index: data_index + data_len]
            # print(num, data)
            if data[0] == 0:
                all_data[ID(id_=num)] = data[1:]
            else:
                data_ = []
                i = 1
                head_len, i = uint_from_bytes(data, i)
                head_data = data[i: i + head_len]
                i += head_len
                len_data = len(data)
                while i < len_data:
                    d, i = uint_from_bytes(data, i)
                    data_.append(d)
                all_data[ID(id_=num)] = head_data, data_
            data_index += data_len
            num += 1
        return all_type, all_data, {key: False for key in all_type}

    @classmethod
    def split(cls, data: bytes) -> tuple[ID, tuple[dict[int, type], dict[int, Any], dict[int, bool]]]:
        """分解打包的数据

        Args:
            data (bytes): 打包后的数据

        Returns:
            tuple[ID, tuple[dict[int, type], dict[int, Any], dict[int, bool]]]: 返回ID,以及包含三个字典
            (所有类型,所有数据,是否完成解包)的元组
        """
        start_id, types_bytes, datas_bytes = cls.__get_head(data)
        return ID(id_=start_id), cls.__get_body(types_bytes, datas_bytes)

    @staticmethod
    def login(data, id_, all_data: tuple[dict[int, type], dict[int, Any]]):
        """注册返回值(用于解决循环引用)

        Args:
            data (Any): 注册的返回值
            id_ (ID): 注册的ID
            all_data (tuple[dict[int, type], dict[int, Any]]): 所有过程数据.
        """
        all_data[1][id_] = data
        all_data[2][id_] = True

    @classmethod
    def unpack(cls, id_: Union[bytes, int, ID],
               all_data: tuple[dict[int, type], dict[int, Any], dict[int, bool]] = None):
        """解包

        Args:
            id_ (Union[bytes, int, ID]): 解包ID或解包数据(使用解包数据时无需提供第二个参数)
            all_data (tuple[dict[int, type], dict[int, Any], dict[int, bool]], optional): 
            解包过程数据. Defaults to None.

        Raises:
            TypeError: 未注册该类型

        Returns:
            Any: 解包后的数据
        """
        if cls.obj is None:
            cls.obj = cls()
        if isinstance(id_, bytes):
            id_, all_data = cls.split(id_)
        if isinstance(id_, int):
            id_ = ID(id_=id_)
        if all_data[2][id_]:
            return all_data[1][id_]
        type_ = cls.pack_num[all_data[0][id_]]
        data = all_data[1][id_]
        if type_ in cls._bind_types:
            all_data[1][id_] = cls.bind_fun[type_](cls.obj, data, id_, all_data)
        elif type_ in cls._atom_bind_types:
            all_data[1][id_] = cls.atom_unpack.unpack(type_, data)
        else:
            raise TypeError()
        all_data[2][id_] = True
        return all_data[1][id_]
