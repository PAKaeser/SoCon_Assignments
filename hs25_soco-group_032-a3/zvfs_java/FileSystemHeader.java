package zvfs_java;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class FileSystemHeader {
    int totalHeaderLength = 64;
    String magicString = "ZVFSDSK1";
    byte versionString = 1;
    byte flags = 0;
    byte[] reserved0 = new byte[2];
    short fileCount = 0;
    short fileCapacity = 32;
    short fileEntrySize = 64;
    byte[] reserved1 = new byte[2];
    int fileTableOffset = 64;
    int dataStartOffset = 2112;
    int nextFreeOffset = 2112;
    int freeEntryOffset = 0;
    short deletedFiles = 0;
    byte[] reserved2 = new byte[26];

    // empty constructor for no given input stores default values
    public FileSystemHeader() {
    }

    // constructor with binary input to load and store values out of binary
    public FileSystemHeader(ByteBuffer buffer) {
        byte[] arrayMagic = new byte[8];
        buffer.get(arrayMagic);
        this.magicString = new String(arrayMagic, StandardCharsets.US_ASCII);
        this.versionString = buffer.get();
        this.flags = buffer.get();
        buffer.get(this.reserved0);
        this.fileCount = buffer.getShort();
        this.fileCapacity = buffer.getShort();
        this.fileEntrySize = buffer.getShort();
        buffer.get(this.reserved1);
        this.fileTableOffset = buffer.getInt();
        this.dataStartOffset = buffer.getInt();
        this.nextFreeOffset = buffer.getInt();
        this.freeEntryOffset = buffer.getInt();
        this.deletedFiles = buffer.getShort();
        buffer.get(this.reserved2);
    }

    public ByteBuffer getFileSystemHeaderBinary() {
        int fileSystemHeaderSize = 64;

        // Allocate the file system size
        ByteBuffer buffer = ByteBuffer.allocate(fileSystemHeaderSize); // 4 bytes for int, 4 bytes for float, 8 bytes
                                                                       // for double
        // Put the values into the buffer
        buffer.put(this.magicString.getBytes());
        buffer.put(this.versionString);
        buffer.put(this.flags);
        buffer.put(this.reserved0);
        buffer.putShort(this.fileCount);
        buffer.putShort(this.fileCapacity);
        buffer.putShort(this.fileEntrySize);
        buffer.put(this.reserved1);
        buffer.putInt(this.fileTableOffset);
        buffer.putInt(this.dataStartOffset);
        buffer.putInt(this.nextFreeOffset);
        buffer.putInt(this.freeEntryOffset);
        buffer.putShort(this.deletedFiles);
        buffer.put(this.reserved2);
        // System.out.println(buffer.toString());

        buffer.flip();

        return buffer;
    }
}
