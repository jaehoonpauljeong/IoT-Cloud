package cpslab.iotcloud.utils;

public class DebugExample implements CompactDebug {
    private int test;

    DebugExample(int test) {
        this.test = test;
    }

    public static void main(String[] args) {
        DebugExample example = new DebugExample(123);


        DebugManager.debugPrintln(DEBUG_LEVEL_DEBUG, "디버그 레벨 디버그, DebugExample 객체 생성됨");
        DebugManager.debugPrintln(DEBUG_LEVEL_INFO, "인포 레벨 디버그, " + "New DebugExample with test value" +
                example.test + " generated"); // 디버그 레벨은 알아서 적절히 선택


        if (DebugManager.isProperDebug(DEBUG_LEVEL_WARNING) && // 조건에 isProperDebug를 할지는 취사선택
                example.test > 50) {
            DebugManager.debugPrintln(DEBUG_LEVEL_WARNING, "에러 레벨 디버그, " +
                    "DebugExample 객체의 test 값이 50을 초과함" +
                    "해당 값: " + example.test);
        }

        if (example.test > 100) {
            DebugManager.debugPrintln(DEBUG_LEVEL_ERR, "에러 레벨 디버그, " +
                    "DebugExample 객체의 test 변수값이 100을 초과함" +
                    "해당 값: " + example.test);
        }


    }
}
