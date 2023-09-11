import ctypes

def kiwi(address,default=True,_=65536):
    if default:
        result = ""
        data = ctypes.string_at(address,_)
        with open(f"{address}.kiwi", "wb") as file:
            file.write(data)
        return data

    else:
        data = ctypes.string_at(address,_).hex()
        with open(f"{address}.kiwi", "w") as file:
            file.write(data)
        return data
