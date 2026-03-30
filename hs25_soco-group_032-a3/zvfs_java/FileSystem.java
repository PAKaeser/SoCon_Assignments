package zvfs_java;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Map;
import java.nio.charset.StandardCharsets;
import java.time.Instant;

public class FileSystem {
    String fileSystemName;
    String fileSystemOperation;
    String fileSystemArg;
    FileSystemHeader fileSystemHeader;
    FileHeader[] fileHeaders;
    ByteBuffer data;

    public FileSystem(String[] inputArgs) {
        this.fileSystemName = inputArgs[1];
        this.fileSystemOperation = inputArgs[0];
        System.out.println(String.format("fileSystemName: %s, operation: %s", fileSystemName, fileSystemOperation));
        if (inputArgs.length > 2) {
            this.fileSystemArg = inputArgs[2];
            System.out.println(String.format("fileSystemArg: %s", fileSystemArg));
        }

        // Dictionary in Python, operations can be called by operations.get(key).run()
        Map<String, Runnable> operations = Map.of(
                "mkfs", this::makeFileSystem,
                "addfs", this::addFileToFileSystem,
                "gifs", this::getInfoForFile,
                "getfs", this::extractFileFromFileSystem,
                "rmfs", this::removeFileFromFileSystem,
                "lsfs", this::listFilesInFileSystem,
                "catfs", this::printFileContents,
                "dfrgfs", this::defragmentFileSystem);

        if (fileSystemOperation.equals("mkfs")) {
            operations.get(fileSystemOperation).run();
        } else {
            loadFromBinary();
            operations.get(fileSystemOperation).run();
        }
        writeBinary();
    }

    public void loadFromBinary() {
        ByteBuffer buffer = null;
        FileSystemHeader dummyFSHeader = new FileSystemHeader();
        try (FileInputStream fis = new FileInputStream(fileSystemName);
                FileChannel fileChannel = fis.getChannel()) {
            buffer = ByteBuffer.allocate((int) fileChannel.size());
            fileChannel.read(buffer);
            buffer.flip();
        } catch (IOException e) {
            e.printStackTrace();
        }

        buffer.position(0).limit(dummyFSHeader.fileEntrySize);
        fileSystemHeader = new FileSystemHeader(buffer.slice());

        fileHeaders = new FileHeader[dummyFSHeader.fileCapacity];
        for (int i = 0; i < dummyFSHeader.fileCapacity; i++) {
            buffer.position(dummyFSHeader.fileTableOffset + i * dummyFSHeader.fileEntrySize)
                    .limit(dummyFSHeader.fileTableOffset + (i + 1) * dummyFSHeader.fileEntrySize);
            FileHeader tempFileHeader = new FileHeader(buffer.slice());
            tempFileHeader.setIndex(i);
            fileHeaders[i] = tempFileHeader;
        }
        buffer.position(dummyFSHeader.dataStartOffset).limit(buffer.capacity());

        this.data = ByteBuffer.allocate(buffer.remaining());
        this.data.put(buffer.slice());

    }

    public void writeBinary() {
        ByteBuffer bufferSysHeader = fileSystemHeader.getFileSystemHeaderBinary();

        ByteBuffer bufferFileHeaders = ByteBuffer.allocate(64 * 32);
        for (int i = 0; i < fileHeaders.length; i++) {
            bufferFileHeaders.put(fileHeaders[i].writeFileHeaderBinary());
        }
        bufferFileHeaders.position(0).limit(bufferFileHeaders.capacity());

        try (FileOutputStream fos = new FileOutputStream(fileSystemName);
                FileChannel fileChannel = fos.getChannel()) {
            fileChannel.write(bufferSysHeader);
            fileChannel.write(bufferFileHeaders);
            fileChannel.write(data.flip());
        } catch (IOException e) {
            e.printStackTrace();
        }
        /*
         * System.out.println("buffer header length");
         * System.out.println(bufferSysHeader.toString());
         * System.out.println(Arrays.toString(bufferSysHeader.array()));
         * System.out.println("buffer file header length");
         * System.out.println(bufferFileHeaders.toString());
         * System.out.println(Arrays.toString(bufferFileHeaders.array()));
         * System.out.println("buffer data length");
         * System.out.println(data.toString());
         * System.out.println(Arrays.toString(data.array()));
         */
    }

    public void makeFileSystem() {
        System.out.println(String.format(">> mkfs"));
        this.fileSystemHeader = new FileSystemHeader();

        this.fileHeaders = new FileHeader[32];
        for (int i = 0; i < fileHeaders.length; i++) {
            fileHeaders[i] = new FileHeader();
            this.data = ByteBuffer.allocate(0); // empty buffer, to make sure writeBinary works for all cases
        }

    }

    public void getInfoForFile() {
        System.out.println(String.format(">> gifs"));
        if (this.fileSystemArg != null) {
            throw new AssertionError("gifs takes no arguments");
        }
        int activeFiles = this.fileSystemHeader.fileCount;
        int deletedFiles = this.fileSystemHeader.deletedFiles;
        int freeEntries = this.fileSystemHeader.fileCapacity - (activeFiles + deletedFiles);
        int headerSize = this.fileSystemHeader.totalHeaderLength;
        int tableSize = this.fileSystemHeader.fileCapacity * this.fileSystemHeader.fileEntrySize;
        int dataSize = this.data.capacity();
        int totalSize = headerSize + tableSize + dataSize;

        System.out.println(String.format("File name: %s", this.fileSystemName));
        System.out.println(String.format("Number of files present (non deleted): %d", activeFiles));
        System.out.println(String.format("Remaining free entries for new files (excluding deleted files): %d", freeEntries));
        System.out.println(String.format("Number of files marked as deleted: %d", deletedFiles));
        System.out.println(String.format("Total size of the file: %d", totalSize));
    }

    public void addFileToFileSystem() {
        System.out.println(String.format(">> addfs"));
        int fileHeaderIndex = 0;
        if (this.fileSystemHeader.freeEntryOffset != 0) {
            fileHeaderIndex = (this.fileSystemHeader.freeEntryOffset - this.fileSystemHeader.fileTableOffset)
                    / this.fileSystemHeader.fileEntrySize;
            fileHeaderIndex += 1;
        }
        ;

        for (int i = 0; i < fileHeaders.length; i++) {
            if (fileHeaders[i].name.equals(this.fileSystemArg)) {
                throw new AssertionError("This file already exists in the file system: " + this.fileSystemArg);
            }
            ;
        }
        ByteBuffer fileBuffer = null;
        int fileLength = 0;

        try (FileInputStream fis = new FileInputStream(this.fileSystemArg);
                FileChannel fileChannel = fis.getChannel()) {
            fileBuffer = ByteBuffer.allocate((int) fileChannel.size());
            fileChannel.read(fileBuffer);
            fileLength = (int) fileChannel.size();
            fileBuffer = fileBuffer.flip();

        } catch (IOException e) {
            e.printStackTrace();
            return;
        }

        int fileZeroPadding = 0;
        if (fileLength % 64 != 0) {
            fileZeroPadding = 64 - (fileLength % 64);
        }

        FileHeader newFileHeader = new FileHeader();
        newFileHeader.name = this.fileSystemArg;
        newFileHeader.created = Instant.now().getEpochSecond();
        newFileHeader.start = this.fileSystemHeader.nextFreeOffset;
        newFileHeader.length = fileLength;
        if (fileLength % 64 != 0) {
            newFileHeader.byteLength = fileLength + fileZeroPadding;
        } else {
            newFileHeader.byteLength = fileLength;
        }

        this.fileHeaders[fileHeaderIndex] = newFileHeader;
        this.fileSystemHeader.freeEntryOffset = this.fileSystemHeader.fileTableOffset
                + fileHeaderIndex * this.fileSystemHeader.fileEntrySize;

        this.fileSystemHeader.nextFreeOffset += newFileHeader.length;

        this.data.flip();
        ByteBuffer updatedByteBuffer = ByteBuffer.allocate(this.data.remaining() + newFileHeader.byteLength);
        updatedByteBuffer.put(this.data);
        updatedByteBuffer.put(fileBuffer);
        if (fileZeroPadding != 0) {
            byte[] zeroPadding = new byte[fileZeroPadding];
            updatedByteBuffer.put(zeroPadding);
        }
        this.data = updatedByteBuffer;
        this.fileSystemHeader.fileCount++;
    }

    public void extractFileFromFileSystem() {
        System.out.println(String.format(">> getfs"));
        if (this.fileSystemArg == null) {
            throw new AssertionError("getfs requires one filename argument");
        }
        String fileName = this.fileSystemArg;
        boolean foundFileName = false;
        FileHeader correctHeaderObj = null;
        for (int i = 0; i < this.fileHeaders.length; i++) {
            if (this.fileHeaders[i].name.equals(fileName)) {
                foundFileName = true;
                correctHeaderObj = this.fileHeaders[i];
                break;
            }
        }
        if (!foundFileName) {
            throw new AssertionError("File not found!");
        }
        if (correctHeaderObj.flag == 1) {
            throw new AssertionError("File was previously deleted!");
        }
        int startInData = correctHeaderObj.start - this.fileSystemHeader.dataStartOffset;
        int length = correctHeaderObj.length;
        ByteBuffer readBuffer = this.data.duplicate();
        readBuffer.flip();
        readBuffer.position(startInData);
        byte[] fileContent = new byte[length];
        readBuffer.get(fileContent);

        try (FileOutputStream fos = new FileOutputStream(fileName)) {
            fos.write(fileContent);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void removeFileFromFileSystem() {
        System.out.println(String.format(">> rmfs"));
        boolean removedFile = false;
        for (int i = 0; i < fileHeaders.length; i++) {
            if (fileHeaders[i].name.equals(this.fileSystemArg)) {
                if (fileHeaders[i].flag == 1){
                    System.out.println(this.fileSystemArg + " allready deleted.");
                }
                else{
                    fileHeaders[i].flag = 1;
                    removedFile = true;
                    this.fileSystemHeader.deletedFiles += 1;
                    this.fileSystemHeader.fileCount -= 1;
                }
            }
            ;

        }
        if (removedFile == true) {
            System.out.println("Flagged file " + this.fileSystemArg + " for removal.");
        } else {
            System.out.println("No file was flagged for removal.");
        }
    }

    public void listFilesInFileSystem() {
        System.out.println(String.format(">> lsfs"));
        if (this.fileSystemArg != null) {
            throw new AssertionError("lsfs takes no arguments");
        }
        for (int i = 0; i < this.fileHeaders.length; i++) {
            FileHeader header = this.fileHeaders[i];
            boolean isSlotUsed = header.name != null && !header.name.isEmpty();
            boolean isNotDeleted = header.flag != 1;
            if (isSlotUsed && isNotDeleted) {
                System.out.println(String.format("Name: %s, size (in bytes): %d, creation time: %d", header.name, header.length, header.created));
            }
        }
    }

    public void printFileContents() {
        System.out.println(String.format(">> catfs"));
        if (this.fileSystemArg == null) {
            throw new AssertionError("catfs requires one filename argument");
        }
        String fileName = this.fileSystemArg;
        boolean foundFileName = false;
        FileHeader correctHeaderObj = null;
        for (int i = 0; i < this.fileHeaders.length; i++) {
            if (this.fileHeaders[i].name.equals(fileName)) {
                foundFileName = true;
                correctHeaderObj = this.fileHeaders[i];
                break;
            }
        }
        if (!foundFileName) {
            throw new AssertionError("File not found!");
        }
        if (correctHeaderObj.flag == 1) {
            throw new AssertionError("File was previously deleted!");
        }
        int startInData = correctHeaderObj.start - this.fileSystemHeader.dataStartOffset;
        int length = correctHeaderObj.length;
        ByteBuffer readBuffer = this.data.duplicate();
        readBuffer.flip();
        readBuffer.position(startInData);
        byte[] fileContent = new byte[length];
        readBuffer.get(fileContent);

        System.out.println(new String(fileContent, StandardCharsets.UTF_8));
    }

    public void defragmentFileSystem() {
        int filesDefragmented = 0;
        int bytesFreed = 0;
        for (int index = this.fileHeaders.length -1; index > -1; index--){
            int binaryDataOffset = fileHeaders[index].start - fileSystemHeader.dataStartOffset;
            if (fileHeaders[index].flag == 1){
                int removedLength = fileHeaders[index].byteLength;

                fileSystemHeader.freeEntryOffset -= fileSystemHeader.fileEntrySize;
                fileSystemHeader.nextFreeOffset -= removedLength;

                ByteBuffer newData = ByteBuffer.allocate(data.capacity()- fileHeaders[index].byteLength);
                data.position(0).limit(binaryDataOffset);
                newData.put(data);
                data.limit(data.capacity()).position(binaryDataOffset + fileHeaders[index].byteLength);
                newData.put(data);
                data = newData;

                for (int i = index + 1; i < fileHeaders.length; i++){
                    fileHeaders[i].start -= removedLength;
                }
                
                FileHeader[] FileHeadersCopy = new FileHeader[fileSystemHeader.fileCapacity];
                for (int i = 0; i < fileHeaders.length-1; i++){
                    int x;
                    if (i < index){x = i;}
                    else {x = i+1;}
                    FileHeadersCopy[i] = fileHeaders[x];
                }
                FileHeadersCopy[FileHeadersCopy.length-1] = new FileHeader();
                fileHeaders = FileHeadersCopy;
                filesDefragmented++;
                bytesFreed += removedLength;
            }
        
        }   
        fileSystemHeader.deletedFiles = 0;
        System.out.println(String.format("Files defragmented: %d", filesDefragmented));
        System.out.println(String.format("Bytes freed: %d", bytesFreed));
    }   
}
