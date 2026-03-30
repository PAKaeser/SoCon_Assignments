package zvfs_java;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class FileHeader {
    String name = "";
    int start = 0;
    int length = 0;
    String type = "0";
    byte flag = 0;
    byte[] reserved0 = new byte[2];
    long created = 0;
    byte[] reserved1 = new byte[12];

    int byteLength = 0;
    int namePadding = 32;

    private int index;

    public void setIndex(int currentIndex) {
        this.index = currentIndex;
    }

    public int getIndex(){
        return this.index;
    }

    public FileHeader(){} // initializes with predefined values

    public FileHeader(ByteBuffer buffer){ // initializes with buffer values
        // take name out of buffer, check where zero padding ends and save part without padding as string
        byte[] name = new byte[32];
        buffer.get(name);
        int nameLength = name.length;
        while (nameLength > 0 && name[nameLength-1] == 0){
            nameLength --;
        }
        this.name = new String(name, 0, nameLength, StandardCharsets.UTF_8);
        this.namePadding = 32 - nameLength;
        this.start = buffer.getInt();
        this.length = buffer.getInt();
        byte[] typeBinary = new byte[1];
        buffer.get(typeBinary);
        this.type = new String(typeBinary, StandardCharsets.US_ASCII);
        this.flag = buffer.get();
        buffer.get(reserved0);
        this.created = buffer.getLong();
        if (this.length % 64 != 0){
            this.byteLength = this.length + 64 -(this.length % 64);
        }
        else{
            this.byteLength = this.length;
        }
        buffer.get(reserved1);
    }
    public ByteBuffer writeFileHeaderBinary(){
        ByteBuffer buffer = ByteBuffer.allocate(64);
        if (name.length() > 32) {
            System.out.println("File name too long!");
            throw new AssertionError();
        }
        byte[] tempNamePadding = new byte[32 - name.length()];

        buffer.put(this.name.getBytes());
        buffer.put(tempNamePadding);
        buffer.putInt(this.start);
        buffer.putInt(this.length);
        buffer.put(this.type.getBytes(StandardCharsets.US_ASCII));
        buffer.put(this.flag);
        buffer.put(this.reserved0);
        buffer.putLong(this.created);
        buffer.put(this.reserved1);
        buffer.flip();
        return buffer;
    }
    
}
