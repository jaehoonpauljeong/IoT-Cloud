package cpslab.iotcloud.utils;

public class DebugManager implements CompactDebug{
    public static boolean isProperDebug(int targetLevel){
        return targetLevel >= CURRENT_DEBUG_LEVEL;
    }

    public static void debugPrintln(int targetLevel, String msg){
        if(isProperDebug(targetLevel)){
            System.out.println(msg);
        }
    }

    public static void debugPrint(int targetLevel, String msg){
        if(isProperDebug(targetLevel)){
            System.out.print(msg);
        }
    }
}
