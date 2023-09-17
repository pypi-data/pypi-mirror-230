import base64
import zlib
import struct

def _decodeBytes(bytes:bytes) -> list:
    begin = bytes
    bytes = bytes[1:]
    result = []
    while len(bytes) > 0:
        if bytes[0] <= 0x3F: # int 0 to 63
            result.append(bytes[0])
            bytes = bytes[1:]
        elif bytes[0] <= 0x7F: # int -64 to -1
            result.append((bytes[0] - 0x3F) * -1)
            bytes = bytes[1:]
        elif bytes[0] <= 0x83: # unsigned int
            length = bytes[0]-0x7E
            result.append(int.from_bytes(bytes[1:(length)], 'little'))
            bytes = bytes[length:]
        elif bytes[0] <= 0x87: # signed int
            if bytes[0] == 0x84:
                result.append(struct.unpack('<h', bytes[1:3])[0])
                bytes = bytes[3:]
            if bytes[0] == 0x85:
                result.append(struct.unpack('<i', bytes[1:5])[0])
                bytes = bytes[5:]
            if bytes[0] == 0x86:
                result.append(struct.unpack('<l', bytes[1:7])[0])
                bytes = bytes[7:]
            if bytes[0] == 0x87:
                result.append(struct.unpack('<q', bytes[1:9])[0])
                bytes = bytes[9:]
        elif bytes[0] <= 0x89: # float
            if bytes[0] == 0x88:
                result.append(struct.unpack('<f', bytes[1:5])[0])
                bytes = bytes[5:]
            if bytes[0] == 0x89:
                result.append(struct.unpack('<d', bytes[1:9])[0])
                bytes = bytes[9:]
        elif bytes[0] <= 0x8C: # string
            if bytes[0] == 0x8a:
                length = bytes[1]*16**0
                result.append(bytes[2:(length+2)].decode('utf8'))
                bytes = bytes[length+2:]
            elif bytes[0] == 0x8b:
                length = bytes[1]*16**1+bytes[2]*16**0
                result.append(bytes[3:(length+3)].decode('utf8'))
                bytes = bytes[length+3:]
            elif bytes[0] == 0x8c:
                length = bytes[1]*16**3+bytes[2]*16**2+bytes[3]*16**1+bytes[4]*16**0
                result.append(bytes[5:(length+5)].decode('utf8'))
                bytes = bytes[length+5:]
        elif bytes[0] <= 0x8F: # bool / None
            if bytes[0] == 0x8D:
                result.append(True)
            elif bytes[0] == 0x8E:
                result.append(False)
            elif bytes[0] == 0x8F:
                result.append(None)
            bytes = bytes[1:]
        elif bytes[0] == 0x90: #start of an array
            decodedbytes = _decodeBytes(bytes)
            result.append(decodedbytes[0])
            bytes = bytes[decodedbytes[1]:]
        elif bytes[0] == 0x91: #end of an array
            bytes = bytes[1:]
            return (result, (len(begin)-len(bytes)))
        elif bytes[0] == 0x92: #start of a map
            decodedbytes = _decodeBytes(bytes)
            bytes = bytes[decodedbytes[1]:]
            decodedbytes = decodedbytes[0]
            if len(decodedbytes) % 2 == 1:
                raise ValueError ("Map {} has an odd number of objects".format(decodedbytes))
            obj_map = {}
            for i in range(0, len(decodedbytes), 2):
                obj_map[decodedbytes[i]] = decodedbytes[i+1]
            result.append(obj_map)
            del obj_map
        elif bytes[0] == 0x93: #end of a map
            bytes = bytes[1:]
            return (result, (len(begin)-len(bytes)))
        elif bytes[0] <= 0x96: #arbitrary bytes
            if bytes[0] == 0x94:
                length = bytes[1]*16**0
                result.append(bytes[2:(length+2)])
                bytes = bytes[length+2:]
            elif bytes[0] == 0x95:
                length = bytes[1]*16**1+bytes[2]*16**0
                result.append(bytes[3:(length+3)])
                bytes = bytes[length+3:]
            elif bytes[0] == 0x96:
                length = bytes[1]*16**3+bytes[2]*16**2+bytes[3]*16**1+bytes[4]*16**0
                result.append(bytes[5:(length+5)])
                bytes = bytes[length+5:]
        else:
            raise ValueError ("Can't decode byte "+str(bytes[0]))

def decodeString(inputString:str, /, configMessageEnabled:bool=False) -> list:
    '''
    Decodes a blueprint string <inputString> and returns a list 
    containing the data of the decoded string
    '''
    inputBytes = inputString.encode("ascii")
    decodedBytes = base64.decodebytes(inputBytes)
    decompressedBytes = zlib.decompress(decodedBytes, -15)
    output = _decodeBytes(decompressedBytes)[0]
    if configMessageEnabled:
        for i in range(len(output[3])):
            command = output[3][i]
            if command[0] == 1:
                output[3][i][1] = _decodeBytes(command[1])[0]
    return output

def _encodeBytes(datalist:list, /, float_precision:str="single") -> bytes:
    output = b'\x90'
    for data in datalist:
        if type(data) == int:
            if data == 0:
                output += b'\x00'
            elif data > 0:
                if data < 64:
                    output += data.to_bytes(1, "little")
                elif data <= 0xFF:
                    output += b'\x80'
                    output += data.to_bytes(1, "little")
                elif data <= 0xFFFF:
                    output += b'\x81'
                    output += data.to_bytes(2, "little")
                elif data <= 0xFFFFFF:
                    output += b'\x82'
                    output += data.to_bytes(3, "little")
                elif data <= 0xFFFFFFFF:
                    output += b'\x83'
                    output += data.to_bytes(4, "little")
                else:
                    raise OverflowError ("Unsigned Int: {} too big to represent (greater than {})".format(data, 0xFFFFFFFF))
            elif data < 0:
                if data >= -64:
                    data = data * (-1) + 0x3f
                    output += data.to_bytes(1, "little")
                elif data >= -0x7FFF:
                    output += b'\x84'
                    output += struct.pack("<h", data)
                elif data >= -0x7FFFFF:
                    output += b'\x85'
                    output += struct.pack("<i", data)
                elif data >= -0x7FFFFFFF:
                    output += b'\x86'
                    output += struct.pack("<l", data)
                elif data >= -0x7FFFFFFFFF:
                    output += b'\x87'
                    output += struct.pack("<q", data)
                else:
                    raise OverflowError ("Negative Signed Int: {} too small to represent (smaller than {})".format(data, -0x7FFFFFFFFF))
        elif type(data) == str:
            length = len(data)
            if length <= 0xFF:
                output += b'\x8a'
                output += length.to_bytes(1, "little")
            elif length <= 0xFFFF:
                output += b'\x8b'
                output += length.to_bytes(2, "little")
            elif length <= 0xFFFFFFFF:
                output += b'\x8c'
                output += length.to_bytes(4, "little")
            else:
                raise OverflowError ("String ["+data+"] too long to represent (length>0xFFFFFFFF)")
            output += data.encode('utf8')
        elif type(data) == list:
            output += _encodeBytes(data)
        elif type(data) == float:
            if float_precision == "single":
                output += b'\x88'
                output += struct.pack("<f", data)
            elif float_precision == "double":
                output += b'\x89'
                output += struct.pack("<d", data)
            else:
                raise RuntimeError ("float_precision must be 'single' or 'double'")
        elif type(data) == bytes:
            length = len(data)
            if length <= 0xFF:
                output += b'\x94'
                output += length.to_bytes(1, "little")
            elif length <= 0xFFFF:
                output += b'\x95'
                output += length.to_bytes(2, "little")
            elif length <= 0xFFFFFFFF:
                output += b'\x96'
                output += length.to_bytes(4, "little")
            else:
                raise OverflowError ("Bytes "+str(data)+" too long to be represented")
            output += data
        elif type(data) == bool:
            if data == True:
                output += b'\x8D'
            elif data == False:
                output += b'\x8E'
        elif data == None:
            output += b'\x8F'
        elif type(data) == dict:
            output += b'\x92'
            temp = []
            for key in data:
                temp.append(key)
                temp.append(data[key])
            output += _encodeBytes(temp)[1:-1]
            del temp
            output += b'\x93'
        else:
            raise NotImplementedError (str(type(data))+" byte encoding isn't implemented yet")
    return output + b'\x91'

def encodeList(inputList:list, /, configMessageEnabled:bool=False, floatPrecision:str='single') -> str:
    '''
    Encodes a list <inputList> and returns a blueprint string
    '''
    if not floatPrecision in {"single", "double"}:
        raise RuntimeError ("floatPrecision must be single or double, floatPrecision is", floatPrecision)
    if configMessageEnabled:
        for i in range(len(inputList[3])):
            command = inputList[3][i]
            if command[0] == 1:
                commandbytes = _encodeBytes(command[1])#[1:-1]
                inputList[3][i][1] = commandbytes

    inputbytes = _encodeBytes(inputList, float_precision=floatPrecision)
    #print(inputbytes)
    compressedBytes = zlib.compress(inputbytes)[2:-4]

    encodedBytes = base64.encodebytes(compressedBytes)

    output = encodedBytes.decode('ascii').replace("\n", "")

    return output