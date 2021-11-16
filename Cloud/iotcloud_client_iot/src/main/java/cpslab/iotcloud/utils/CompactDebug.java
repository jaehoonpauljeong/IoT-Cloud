package cpslab.iotcloud.utils;

public interface CompactDebug {
    public static final int DEBUG_LEVEL_ALL = 0x00;
    public static final int DEBUG_LEVEL_VERBOSE = 0x10;
    public static final int DEBUG_LEVEL_DEBUG = 0x20;
    public static final int DEBUG_LEVEL_INFO = 0x30;
    public static final int DEBUG_LEVEL_WARNING = 0x40;
    public static final int DEBUG_LEVEL_ERR = 0x50;
    public static final int DEBUG_LEVEL_NONE = 0xff;

    /*
        change value for use
        Set none for deploy state
     */
    public static final int CURRENT_DEBUG_LEVEL = DEBUG_LEVEL_ALL;

}
