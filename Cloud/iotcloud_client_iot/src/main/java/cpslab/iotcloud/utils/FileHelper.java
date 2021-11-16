package cpslab.iotcloud.utils;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

public class FileHelper {
    /**
     * Read file
     * @param folder folder path
     * @param filename file name
     * @return string
     */
    public String readJsonFile(String folder, String filename) throws IOException {
        InputStream inputStream =  getClass().getResourceAsStream(folder+ "/" + filename);
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "Searching");
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        StringBuffer result = new StringBuffer();
        String tmp = reader.readLine();

        while (tmp != null) {
            result.append(tmp + "\n");
            tmp = reader.readLine();
        }
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "read result = " + result);
        return result.toString();
    }

    public String readFileinRasp(String folder, String fileName) throws IOException {

        File file = new File(folder + "/" + fileName);

        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
        StringBuffer result = new StringBuffer();
        String tmp = reader.readLine();

        while (tmp != null) {
            result.append(tmp + "\n");
            tmp = reader.readLine();
        }

        return result.toString();
    }

    public File readImageFile(String folder, String fileName) throws IOException {
        InputStream inputStream = getClass().getResourceAsStream(folder + "/" + fileName);
        File tempFile = File.createTempFile(String.valueOf(inputStream.hashCode()), ".tmp");
        tempFile.deleteOnExit();

        try(FileOutputStream outputStream = new FileOutputStream(tempFile)) {
            int read; byte[] bytes = new byte[4096];
            while((read = inputStream.read(bytes)) != -1) {
                outputStream.write(bytes, 0, read);
            }
        }
        return tempFile;
    }

    public boolean saveFile(String folderName, String fileName, String target) throws IOException {
        OutputStream outputStream = new FileOutputStream(folderName + "/" + fileName);
        byte[] bytes = target.getBytes(StandardCharsets.UTF_8);
        outputStream.write(bytes);

        return true;
    }
}
