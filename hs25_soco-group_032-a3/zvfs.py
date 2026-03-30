import sys
import struct
from time import time

"""
Header offset keys explained:
using constants to reduce headspace while parsing header
using beginning + length of previous field as new offset, to make header dynamical changeable to help with debugging
binary[MAGIC:MAGIC_LENGTH] returns bytes at position 0 to 7 (inclusive) 
binary[DATA_START_OFFSET : DATA_START_OFFSET + DATA_START_OFFSET_LENGTH] returns the unsigned int at position of field of data start offset as binary
this means order has to be precisely like in assignment text
"""


class FileSystemHeader:
    def __init__(self, binary=None):
        self.total_header_length = 64
        self.header_format = "=8s1sc2x3H2x4IH26x"
        self.file_count_offset = 11
        self.next_free_offset = 28
        self.free_entry_offset = 32

        # If no FileSystem binary given: create new header binary
        if binary is None:
            self.magic = bytes("ZVFSDSK1", "ASCII")
            self.version = bytes("1", "ASCII")
            self.flags_value = bytes([0])
            self.file_count_value = 0
            self.file_capacity = 32
            self.file_entry_size = 64
            self.file_table_offset  = 64
            self.data_start_offset = 2112
            self.next_free_offset_value = 2112
            self.free_entry_offset_value = 64
            self.deleted_files_number = 0

        else:
            unpacked_file_system = struct.unpack(
                self.header_format, binary
            )
            self.magic = unpacked_file_system[0]
            self.version = unpacked_file_system[1]
            self.flags_value = unpacked_file_system[2]
            self.file_count_value = unpacked_file_system[3]
            self.file_capacity = unpacked_file_system[4]
            self.file_entry_size = unpacked_file_system[5]
            self.file_table_offset = unpacked_file_system[6]
            self.data_start_offset = unpacked_file_system[7]
            self.next_free_offset_value = unpacked_file_system[8]
            self.free_entry_offset_value = unpacked_file_system[9]
            self.deleted_files_number = unpacked_file_system[10]

        # if needed, new attributes can be named and extracted out of unpacked_file_system

    def create_filesystem_header_binary(self):
        binary = struct.pack("8s", self.magic)
        binary += struct.pack("s", self.version)
        binary += struct.pack("c", self.flags_value)
        binary += struct.pack("2x")  # reserved0
        binary += struct.pack("H", self.file_count_value)
        binary += struct.pack("H", self.file_capacity)
        binary += struct.pack("H", self.file_entry_size)
        binary += struct.pack("2x")  # reserved1
        binary += struct.pack("I", self.file_table_offset)
        binary += struct.pack("I", self.data_start_offset)
        binary += struct.pack("I", self.next_free_offset_value)
        binary += struct.pack("I", self.free_entry_offset_value)
        binary += struct.pack("H", self.deleted_files_number)
        binary += struct.pack("26x")  # reserved2
        assert len(binary) == self.total_header_length, "something went wrong in the binary generation of the Filesystem header"
        return binary


class FileHeader:
    def __init__(self, binary=None):
        self.header_format = "=32siic?2x1d12x"
        self.index = None

        if binary is None:
            self.name: str = ""
            self.start: int = 0
            self.length: int = 0
            self.type: str = bytes("0", "ASCII")
            self.flag: bool = False
            self.created = 0
            self.byte_length = 0

        else:
            unpacked_file_header = struct.unpack(
                self.header_format, binary
            )
            self.name = unpacked_file_header[0].decode("utf-8").rstrip("\x00")
            self.start = unpacked_file_header[1]
            self.length = unpacked_file_header[2]
            self.type = unpacked_file_header[3]
            self.flag = unpacked_file_header[4]
            self.created = unpacked_file_header[5]
            if self.length % 64 != 0:
                self.byte_length = self.length + 64 - (self.length % 64)
            else:
                self.byte_length = self.length

        # Static values
        self.reserved0: int = 2  # zero padding
        self.reserved1: int = 12  # zero padding

    def generate_file_header_bytes(self) -> bytes:
        binary = struct.pack("32s", bytes(self.name, "ASCII"))
        binary += struct.pack("1i", self.start)
        binary += struct.pack("1i", self.length)
        binary += struct.pack("1c", self.type)
        binary += struct.pack("?", self.flag)
        binary += struct.pack(f"{self.reserved0}x")
        binary += struct.pack("d", self.created)
        binary += struct.pack(f"{self.reserved1}x")
        return binary


class FileSystem:

    def __init__(
        self,
        file_system_name: str,
        file_system_operation: str,
        file_system_args: list = [],
    ):
        self.file_system_name: str = file_system_name
        self.file_system_operation: str = file_system_operation
        self.file_system_args: list = file_system_args
        available_functions = {
            "addfs": self.add_file_to_file_system,
            "mkfs": self.make_file_system,
            "rmfs": self.remove_file_from_file_system,
            "catfs": self.print_file_contents,
            "dfrgfs": self.defragment_file_system,
            "getfs": self.extract_file_from_file_system,
            "lsfs": self.list_files_in_file_system,
            "gifs": self.get_info_for_file,
        }

        if self.file_system_operation == "mkfs":
           self.make_file_system()
        
        else:
            self.load_from_binary()
            available_functions[self.file_system_operation]()

        self.write_binary()

    def load_from_binary(self):
        dummy_FSheader = FileSystemHeader() # to use the saved value of total_header_length (reducing bugs if this value should be changed in init)

        with open(self.file_system_name, "rb") as file:
            binary = file.read()

        self.file_system_header = FileSystemHeader(binary[:dummy_FSheader.total_header_length])

        self.file_headers = []
        for i in range(self.file_system_header.file_table_offset, self.file_system_header.data_start_offset, self.file_system_header.file_entry_size): # range from first file entry, to begin of data, in file entry size steps
            new_Fileheader = FileHeader(binary[i:i+self.file_system_header.file_entry_size]) # slice for each file entry alone
            self.file_headers.append(new_Fileheader) # new FileHeader obj. to list of all file entries for this file system
            new_Fileheader.index = int((i - self.file_system_header.file_table_offset) / self.file_system_header.file_entry_size)

        self.data = binary[self.file_system_header.data_start_offset:]

    def write_binary(self):
        assert self.file_system_header is not None, "missing filesystem header"
        assert self.file_headers != [], "missing file headers"

        binary = self.file_system_header.create_filesystem_header_binary()
        for obj in self.file_headers:
            binary += obj.generate_file_header_bytes()
        binary += self.data

        with open(self.file_system_name, "wb") as fs:
            fs.write(binary)

    def make_file_system(self):
        """Creates an empty filesystem."""
        self.file_system_header = FileSystemHeader()       # makes "empty" header
        self.file_headers = [FileHeader()] * self.file_system_header.file_capacity
        self.data = b""

    def get_info_for_file(self):
        """Gets information for a specified file system file."""
        assert len(self.file_system_args) == 0, "gifs takes no arguments"
        active_files = self.file_system_header.file_count_value
        deleted_files = self.file_system_header.deleted_files_number
        free_entries = self.file_system_header.file_capacity - (active_files + deleted_files)
        header_size = self.file_system_header.total_header_length
        table_size = self.file_system_header.file_capacity * self.file_system_header.file_entry_size
        data_size = len(self.data)
        total_size = header_size + table_size + data_size
        
        print(f"File name: {self.file_system_name}")
        print(f"Number of files present (non deleted): {active_files}")
        print(f"Remaining free entries for new files (excluding deleted files): {free_entries}")
        print(f"Number of files marked as deleted: {deleted_files}")
        print(f"Total size of the file: {total_size}")

    def add_file_to_file_system(self):
        """Adds a file to the given file system. It also updated the header entries."""
        assert len(self.file_system_args) == 1, "addfs only takes one argument, which is the target file name"

        assert self.file_system_header.free_entry_offset_value != 0, (
            "The file system has no free space! Please try to defragment."
        )
        assert self.file_system_header.file_count_value < 32, "The file system reached its limit of 32 entries!"

        file_name = self.file_system_args[0]
        assert len(bytes(file_name, "ASCII")) <= 32, "name must be at most 32 characters"
        
        # check if a file with that name exists:
        for file_header in self.file_headers:
            assert file_name != file_header.name ,"file with this name exists already, please rename!"

        with open(file_name, "rb") as file:
            file_content = file.read()

        file_header = FileHeader() # create new empty FileHeader obj
        file_header.created = time()  # adjust attributes of FileHeader
        file_header.name = self.file_system_args[0]
        file_header.start = self.file_system_header.next_free_offset_value
        file_header.length = len(file_content)
        file_header.type = bytes([0])
        file_header.flag = False
        if file_header.length % 64 != 0:
            file_header.byte_length = file_header.length + 64 - (file_header.length % 64)
        else: 
            file_header.byte_length = file_header.length
        # calculate correct index in list of file header obj of file system obj
        file_header.index = int((self.file_system_header.free_entry_offset_value - self.file_system_header.file_table_offset) / self.file_system_header.file_entry_size)
        # put obj at right place in list of FileHeader obj.
        self.file_headers[file_header.index] = file_header

        # calc zero padding size
        if len(file_content) % 64 == 0:
            padding_len = 0
        else:
            padding_len = 64 - (len(file_content) % 64)
        
        # adding file content and zero padding to binary
        self.data += file_content 
        self.data += b"\x00" * padding_len

        # adjusting the info in file system header where to append data
        self.file_system_header.next_free_offset_value += len(file_content) + padding_len

        # adjusting the info in the file system header, where next file to append
        self.file_system_header.free_entry_offset_value += self.file_system_header.file_entry_size
        # check if files full
        if self.file_system_header.free_entry_offset_value >= self.file_system_header.data_start_offset: 
            self.file_system_header.free_entry_offset_value = 0
            print("Last entry filled, please defragment!")

        # adjust info in file system header for active entries
        self.file_system_header.file_count_value += 1

    def extract_file_from_file_system(self):
        """getfs: Extracts a file from the file system to the disk. The requested file is produced as the output."""
        assert len(self.file_system_args) == 1, "Only one file can be extracted at a time"
        file_name = self.file_system_args[0]
        found_file_name: bool = False
        for file_header in self.file_headers:
            if file_name == file_header.name:
                found_file_name = True
                correct_header_obj = file_header
                break

        assert found_file_name, "File not found!"
        assert correct_header_obj.flag != 1, "File was previously deleted!"
        start_in_data = correct_header_obj.start - self.file_system_header.data_start_offset
        file_content = self.data[start_in_data: start_in_data + correct_header_obj.length]

        with open(file_name, "wb") as f:
            f.write(file_content)

    def remove_file_from_file_system(self):
        """Removes the file from the file system by setting the flag attribute to 1. This signals, that the file is deleted."""
        assert len(self.file_system_args) == 1, "Only one file can be deleted at a time"
        file_name = self.file_system_args[0]
        found_file_name: bool = False
        for file_header in self.file_headers:
            if file_name == file_header.name:
                assert file_header.flag != 1, "File is already deleted!"
                file_header.flag = 1
                found_file_name = True
                self.file_system_header.deleted_files_number += 1
                self.file_system_header.file_count_value -= 1
                break
        assert found_file_name, (
            f"No file {file_name} found in file system! No data was deleted."
        )

    def list_files_in_file_system(self):
        """Lists all the files in the provided filesystem."""
        assert len(self.file_system_args) == 0, "lsfs takes no arguments"
        for file_header in self.file_headers:
            if file_header.name and file_header.flag != 1:
                print(f"Name: {file_header.name}, size (in bytes): {file_header.length}, creation time: {file_header.created}")

    def print_file_contents(self):
        assert len(self.file_system_args) == 1, "catfs requires one filename argument"
        file_name = self.file_system_args[0]
        found_file_name: bool = False
        for file_header in self.file_headers:
            if file_name == file_header.name:
                found_file_name = True
                correct_header_obj = file_header
                break

        assert found_file_name, "File not found!"
        assert correct_header_obj.flag != 1, "File was previously deleted!"
        start_in_data = correct_header_obj.start - self.file_system_header.data_start_offset
        file_content = self.data[start_in_data: start_in_data + correct_header_obj.length]

        print(file_content)

    def defragment_file_system(self):
        files_defragmented = 0
        bytes_freed = 0

        for index in range(self.file_system_header.file_capacity - 1, -1, -1):
            binary_data_offset = self.file_headers[index].start - self.file_system_header.data_start_offset
            # print(f"name of visited header: {self.file_headers[index].name}")

            if self.file_headers[index].flag == 1:
                # print(f"found del file at {index}")

                removed_length = self.file_headers[index].byte_length
                removed_start = self.file_headers[index].start

                self.file_system_header.free_entry_offset_value -= self.file_system_header.file_entry_size
                self.file_system_header.next_free_offset_value -= removed_length

                self.new_data = self.data[:binary_data_offset] + self.data[binary_data_offset + self.file_headers[index].byte_length:]
                self.data = self.new_data
                del self.new_data

                for header in self.file_headers:
                    if header.start > removed_start:
                        header.start -= removed_length

                self.file_headers.pop(index)
                self.file_headers.append(FileHeader())
                files_defragmented += 1
                bytes_freed += removed_length

            # print(f"file count: {self.file_system_header.file_count_value}")
            # print(f"file offset: {self.file_system_header.free_entry_offset_value - self.file_system_header.file_table_offset}")
        
        self.file_system_header.deleted_files_number = 0
        print(f"Files defragmented: {files_defragmented}")
        print(f"Bytes freed: {bytes_freed}")
        

if __name__ == "__main__":
    fs = FileSystem(
        file_system_name=sys.argv[2],
        file_system_operation=sys.argv[1],
        file_system_args=sys.argv[3:],
    )

