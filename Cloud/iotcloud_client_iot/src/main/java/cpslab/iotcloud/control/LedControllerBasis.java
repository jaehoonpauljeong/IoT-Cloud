package cpslab.iotcloud.control;

import cpslab.iotcloud.structure.data.CommandStructure;
import cpslab.iotcloud.structure.data.StatusStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

/**
 * Abstract class of led
 * @author IoT Controller & Relay Team /
 */
public abstract class LedControllerBasis {
    static final String GPIO_OUT = "out";
    static String[] GpioChannels = { "17" };

    private static void control(String gpio) {
        FileWriter[] commandChannels;
        try {
            // Open file handles to GPIO port unexport and export controls
            FileWriter unexportFile =
                    new FileWriter("/sys/class/gpio/unexport");
            FileWriter exportFile =
                    new FileWriter("/sys/class/gpio/export");

            // Loop through all ports if more than 1
            for (String gpioChannel : GpioChannels) {
                System.out.println(gpioChannel);

                // Reset the port, if needed
                File exportFileCheck =
                        new File("/sys/class/gpio/gpio"+gpioChannel);
                if (exportFileCheck.exists()) {
                    unexportFile.write(gpioChannel);
                    unexportFile.flush();
                }

                // Set the port for use
                exportFile.write(gpioChannel);
                exportFile.flush();

                // Open file handle to port input/output control
                FileWriter directionFile =
                        new FileWriter("/sys/class/gpio/gpio" + gpioChannel +
                                "/direction");

                // Set port for output
                directionFile.write(GPIO_OUT);
                directionFile.flush();
            }
            // Set up a GPIO port as a command channel
            FileWriter commandChannel = new
                    FileWriter("/sys/class/gpio/gpio" +
                    GpioChannels[0] + "/value");
            commandChannel.write(gpio);
            commandChannel.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    private static void turnOn(String gpio) {
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "turning on led...");
        control(gpio);
    }
    private static void turnOff(String gpio) {
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "turning off led...");
        control(gpio);
    }

    public static StatusStructure LedControl(CommandStructure command, StatusStructure myStatus) {
        for (Map.Entry<String, String> commandToken : command.commands.entrySet()) {
            if (commandToken.getValue().equals("on")) {
                turnOn("1");
                myStatus.status.put(commandToken.getKey(), "on");

            }else if(commandToken.getValue().equals("off")) {
                turnOff("0");
                myStatus.status.put(commandToken.getKey(), "off");
            }
        }
        return myStatus;
    }
}
