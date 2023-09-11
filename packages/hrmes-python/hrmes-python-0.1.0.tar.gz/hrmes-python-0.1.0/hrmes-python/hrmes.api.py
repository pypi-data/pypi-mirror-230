from ctypes import *
from pathlib import Path


# Load the shared library into ctypes
#libname = Path().absolute() / "liblibhrmes.so"
libname = "/home/yechan.kim/CLionProjects/mec-storage/sqlitecpp/cmake-build-debug-gcc-12/liblibhrmes.so"
c_lib = CDLL(libname)

# define the types of the arguments and return
# create_section
c_lib.create_section.argtypes = (c_char_p, c_uint, POINTER(c_char_p), c_size_t)
c_lib.create_section.restype = c_uint

# read_data
c_lib.read_data.argtypes = (c_uint, c_char_p, c_char_p)

# write_data
c_lib.write_data.argtypes = (c_uint, c_char_p, c_char_p)
c_lib.write_data.restype = c_bool

# commit
c_lib.commit.argtypes = (c_uint, )

# finalize
c_lib.finalize.argtypes = (c_uint, )
c_lib.finalize.restype = c_uint

def test(url):
    # Convert Python strings to C-style strings (bytes)
    return c_lib.test(url.encode('utf-8'))
def create_section(url, port, keys):
    # Convert Python strings to C-style strings (bytes)
    c_keys = [c_char_p(string.encode('utf-8')) for string in keys]
    size = len(keys)

    return c_lib.create_section(url.encode('utf-8'),
                                port,
                                (c_char_p * (size + 1))(*c_keys),
                                size)
def read_data(section_handler_id, key):
    value = create_string_buffer(100)
    c_lib.read_data(section_handler_id, key.encode('utf-8'), value)
    return value.value
def write_data(section_handler_id, key, value):
    return c_lib.write_data(section_handler_id, key.encode('utf-8'), value.encode('utf-8'))
def commit(section_handler_id):
    c_lib.commit(section_handler_id)
    return
def finalize(section_handler_id):
    return c_lib.finalize(section_handler_id);

if __name__ == "__main__":
    # create a section
    print("[Connection]")
    id = create_section("0.0.0.0", 1337, ["A-Key", "B-Key"])
    print(id)

    # Read data
    print("[Read]")
    value = read_data(0, "A-Key")
    print("Read value : ")
    print(value)

    # write data
    print("[Write]")
    written = write_data(id, "A-Key", "A-new-value-test_write")
    print(written)

    print("[Read]")
    value = read_data(0, "A-Key")
    print("Written value : ")
    print(value)

    # commit
    print("[Commit]")
    commit(id)

    # finalize
    finalize(id)

