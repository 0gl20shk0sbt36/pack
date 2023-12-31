from .BasePack import BaseAtomPack, BaseAtomUnPack, BasePack, BaseUnPack, bind_type, ID, uint_to_bytes, uint_from_bytes


class AtomPack(BaseAtomPack):

    @bind_type(int)
    def pack_int(self, data: int):
        return data.to_bytes(data.bit_length() // 8 + 1, 'big', signed=True)

    @bind_type(bool)
    def pack_bool(self, data: bool):
        return self.pack_int(int(data))

    @bind_type(str)
    def pack_str(self, data: str):
        return data.encode('utf-8')

    @bind_type(type(None))
    def pack_none(self, data):
        return b'\x00'

    @bind_type(bytes)
    def pack_bytes(self, data: bytes):
        return data


class AtomUnPack(BaseAtomUnPack):

    @bind_type(int)
    def unpack_int(self, data: bytes) -> int:
        return int.from_bytes(data, 'big', signed=True)

    @bind_type(bool)
    def unpack_bool(self, data: bytes) -> bool:
        return bool(self.unpack_int(data))

    @bind_type(str)
    def unpack_str(self, data: bytes) -> str:
        return data.decode('utf-8')

    @bind_type(type(None))
    def unpack_none(self, data: bytes) -> None:
        return None

    @bind_type(bytes)
    def unpack_bytes(self, data: bytes) -> bytes:
        return data


class Pack(BasePack):
    atom_pack = AtomPack

    @bind_type(list)
    def pack_list(self, data: list, all_data) -> tuple[bytes, list[ID]]:
        data_ = []
        self.login(data_, ID(data), all_data)
        for i in data:
            data_.append(ID(i))
            self.pack(i, all_data)
        return b'', data_

    @bind_type(dict)
    def pack_dict(self, data: dict, all_data) -> tuple[bytes, list[ID]]:
        data_ = []
        keys = []
        values = []
        self.login(data_, ID(data), all_data)
        for k, v in data.items():
            keys.append(ID(k))
            values.append(ID(v))
            self.pack(k, all_data)
            self.pack(v, all_data)
        data_.extend(keys)
        data_.extend(values)
        head = uint_to_bytes(len(keys))
        print(head)
        return head, data_


class UnPack(BaseUnPack):
    atom_unpack = AtomUnPack

    @bind_type(list)
    def unpack_list(self, data: tuple[bytes, list[ID]], id_: ID, all_data):
        data = data[1]
        data_ = []
        self.login(data_, id_, all_data)
        for i in data:
            data_.append(self.unpack(i, all_data))
        return data_

    @bind_type(dict)
    def unpack_dict(self, data: tuple[bytes, list[ID]], id_: ID, all_data):
        head, data = data
        head = uint_from_bytes(head)[0]
        keys = data[:head]
        values = data[head:]
        data_ = {}
        self.login(data_, id_, all_data)
        for k, v in zip(keys, values):
            data_[self.unpack(k, all_data)] = self.unpack(v, all_data)
        return data_
