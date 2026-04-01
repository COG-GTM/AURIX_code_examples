<img src="./Images/IFX_LOGO_600.gif" align="right" width="150" />  

# iLLD_TC4D7_LK_ADS_Bluetooth_RFCOMM
**Demonstrate the download of an application firmware to Infineon's CYW20819 device family by applying the AIROC(TM) HCI UART Control Protocol on AURIX(TM)**  

## Device  
The device used in this example is AURIX&trade; TC4D7XP_A-Step_CC_COM   

## Board  
The board used for testing is the AURIX&trade; TC4D7LITE (KIT_A3G_TC4D7_LITE)  
Beside the AURIX&trade; evaluation kit, also a CYW920819EVB-02 evaluation kit is needed

## Scope of work   
The example enables the extension of AURIX&trade; devices with the BLE (Bluetooth Low Energy) and classic bluetooth capability which is provided by Infineon's CYW20819 device. The application firmware binary which is distributed within this example implements a RFCOMM (Radio Frequency Communication) bluetooth classic profile for the CYW20819 device. This application binary is downloaded by AURIX&trade; to the CYW20819 device. During execution of the application binary, the data received/transmitted on the RFCOMM bluetooth interface by the CYW20819 device is bridged to a UART (Universal Asynchronous Receiver Transmitter), which is connected to AURIX&trade; and processed on AURIX&trade; within a shell. A shell is a user interface for parsing commands and accessing services. By this, a RFCOMM bluetooth application on a remote device (i.e. smartphone) can be used as a terminal application to communicate with AURIX&trade;.

## Introduction  
Inside this example, the AURIX&trade; TC4D7 Lite Kit is connected to the CYW920819EVB-02 evaluation kit. The CYW20819 device comes with two UART interfaces. These interfaces are the HCI (Host Controller interface) UART interface, which is used to download application firmware and the PUART (Peripheral UART) interface, which can be used for general application purpose.

* The ASCLIN (Asynchronous/Synchronous Interface) instance number 2 (called ASCLIN2 throughout the further description) of AURIX&trade; (P02.10/RX and P02.9/TX on S2G1 connector) is configured for UART communication and connected to HCI UART interface of the CYW20819 device. This connection is used to download the application firmware from AURIX&trade; to CYW20819.  

* The ASCLIN instance number 3 (called ASCLIN3 throughout the further description) of AURIX&trade; (P20.3/RX and P20.0/TX on S2G2 connector) is configured for UART communication and connected to PUART of CYW20819 device. The RFCOMM application binary executed on the CYW20819 device is forwarding the bi-directional traffic of the RFCOMM bluetooth profile to its PUART. On AURIX&trade; side a shell application is executed on ASCLIN3.

During startup, before the shell is executed on AURIX&trade;, first it is confirmed the correct application firmware is programmed into CYW20819.

The RFCOMM terminal can be connected from remote to the bluetooth RFCOMM profile of the CYW20819 and interact with the shell, which is executed on AURIX&trade;.

To download the application binary, an Infineon vendor specific AIROC&trade; HCI firmware download protocol is used.

As of writing, this protocol is valid for the following chip families:
CYW20706, CYW20719, CYW20721, CYW20735, CYW20819, CYW20820, CYW20835, or CYW43012.  

So even this example is demonstrated on CYW920819EVB-02 evaluation kit within the example here, the scope of this example is broader. 

## Hardware setup  
This code example is developed for the board AURIX&trade; TC4D7 Lite Kit (KIT_A3G_TC4D7_LITE)  

The AURIX&trade; TC4D7 Lite Kit is connected to the PC through a USB port to support download and debug.  
The CYW920819EVB-02 evaluation kit needs to be powered by another USB port or a USB power supply.  

Make sure, the UART interfaces of both kits are interconnected as shown in the following table.  
The jumpers of the CYW920819EVB-02 kit needs to be placed as indicated to support 3.3V operation mode:  

<table>
    <tbody>
        <tr>
            <td>&emsp;<b>AURIX&trade; TC4D7 Lite Kit</b></td>
            <td>&emsp;<b>CYW920819EVB-02 Kit</b></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(0,0,0)">GND</span></td>
            <td>&emsp;<span style="color:rgb(0,0,0)">GND</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(0,112,192)">P02.9 ASCLIN2/TX (S2G1)</span></td>
            <td>&emsp;<span style="color:rgb(0,112,192)">HCI UART/RX</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(255,192,0)">P02.10 ASCLIN2/RX (S2G1)</span></td>
            <td>&emsp;<span style="color:rgb(255,192,0)">HCI UART/TX</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(146,208,80)">P32.2 RTS</span></td>
            <td>&emsp;<span style="color:rgb(146,208,80)">HCI UART/CTS</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(227,0,52)">P23.4 CTS</span></td>
            <td>&emsp;<span style="color:rgb(227,0,52)">HCI UART/RTS</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(255,192,0)">P20.3 ASCLIN3/RX (S2G2)</span></td>
            <td>&emsp;<span style="color:rgb(255,192,0)">PUART/TX</span></td>
        </tr>
        <tr>
            <td>&emsp;<span style="color:rgb(0,112,192)">P20.0 ASCLIN3/TX (S2G2)</span></td>
            <td>&emsp;<span style="color:rgb(0,112,192)">PUART/RX</span></td>
        </tr>
    </tbody>
</table>

To make sure, CYW920819EVB-02 is in a well pre-defined state, execute the following sequence before programming the kit for the very first time:
1. Supply the kit with power
2. Push Recovery Button (SW1) for at least one second
3. While still keeping pushed the Recovery Button (SW1), also push the Reset Button (SW2) for at least one second
4. Release Reset Button (SW2) and after one second later the Recovery Button (SW1)
5. Execute a power cycle of the kit  

## Implementation  
**Overview - Source files and structure**  
This examples comes with the following software modules:
- BT_HCI_Protocol_Download.c/BT_HCI_Protocol_Download.h 
    - Within these files an API is implemented to configure and use the ASCLIN2 peripheral of AURIX&trade; to interconnect with the HCI UART peripheral of CYW20819. It implements the sending of commands and receiving of events of the AIROC&trade; HCI firmware download protocol. By using this API, the application binaries can be programmed into CYW20819.
- BT_Minidriver_Binary.c/BT_Minidriver_Binary.h 
    - These files provide the binary data of the minidriver for the CYW20819 device. The minidriver needs to be downloaded to RAM and its execution has to be started, before the subsequent download of the application binary to the flash can follow.
- BT_RFCOMM_Binary.c/BT_RFCOMM_Binary.h 
    - These files provide the binary data of the RFCOMM application executable for the CYW20819 device. Thereby the CYW20819 is enabled as a bluetooth classic device supporting the implementation of RFCOMM profile and it is functioning as a bridge of this profile to its PUART interface.
- BT_Shell.c/BT_Shell.h
    - Within these files the shell application executed on top the ASCLIN3 peripheral of AURIX&trade; is implemented. Incoming shell commands are parsed, executed and responded.
    
**Details - Software modules and structure**  

**Initialize the ASCLIN2 peripheral for HCI UART communication**  
The function *void init_hci_protocol_UART(void)* inside file *BT_HCI_Protocol_Download.c* implements the configuration of the ASCLIN2 peripheral.  
The ASCLIN2 peripheral uses pins P02.10/RX and P02.9/TX on the S2G1 connector of the TC4D7 Lite Kit.

The interrupt-handlers *asc2_tx_ISR(...)*, *asc2_rx_ISR(...)* and *asc2_err_ISR(...)* are implemented inside *BT_HCI_Protocol_Download.c*.

RTS/CTS is operated under software control using GPIO pins P32.2 (RTS) and P23.4 (CTS), because CYW20819 requires CTS to be driven high during reset to enable firmware download through HCI UART.

**Initialize the ASCLIN3 peripheral to communicate with PUART on CYW20819**  
The function *void init_shell_UART(void)* inside file *BT_Shell.c* implements the configuration of the ASCLIN3 peripheral using pins P20.3/RX and P20.0/TX on the S2G2 connector.

**Initialize the shell**  
The function *void init_shell(void)* initializes the shell functionality including ASCLIN3, LEDs (LED1 at P03.9, LED2 at P03.10), and the shell command parser.

Three shell commands are supported: *info*, *toggle [0/1/2]*, and *help*.

**Example core0_main implementation**  
1. Standard initialization: *IfxCpu_enableInterrupts(...)*, *IfxWtu_disableCpuWatchdog(...)*, *IfxWtu_disableSystemWatchdog(...)*, *IfxCpu_emitEvent(...)* and *IfxCpu_waitEvent(...)*
2. Configure ASCLIN2 for HCI UART by calling *init_hci_protocol_UART(...)*
3. Download firmware to CYW20819 using the AIROC&trade; HCI protocol
4. Configure ASCLIN3 and shell by calling *init_shell(...)*
5. Run shell in infinite loop by calling *run_shell(...)*

## Compiling and programming
 
Before testing this code example: 
- Connect the board to the PC through the USB interface
- Build the project using the dedicated Build button <img src="./Images/build_activeproj.gif" /> or by right-clicking the project name and selecting "Build Project"
- To flash the device and immediately run the program, click on the dedicated Flash button <img src="./Images/micro.png" /> 

## Run and Test  
For this example, a remote device (like a smartphone) running a RFCOMM-profile bluetooth classic serial terminal is required. As of today, iOS does not support RFCOMM profile in general, while for Android devices several apps are available within Google Play Store.

1. Install "Serial Bluetooth Terminal" App on your remote device  
2. Setup hardware as described above. Also supply CYW920819EVB-02 kit with power via USB and consider executing recovery sequence
3. Compile, download and start execution of this example on AURIX&trade; TC4D7 Lite Kit  
4. AURIX&trade; will wait for a reset-cycle of CYW920819EVB-02 Kit, before downloading the binary. Push SW2 reset button on CYW920819EVB-02 Kit
5. Open the Serial Bluetooth Terminal App on your smartphone  
6. Open the App menu and select "Devices" to scan for available bluetooth devices
7. Connect to device "spp test" inside Bluetooth Classic tab
8. Once the device is connected, the info screen will show up
9. Enter command "toggle 1"/"toggle 2" and confirm toggling of LED1(P03.9)/LED2(P03.10) on AURIX&trade; TC4D7 Lite Kit

## References  

AURIX&trade; Development Studio is available online:  
- <https://www.infineon.com/aurixdevelopmentstudio>  
- Use the "Import..." function to get access to more code examples  

More code examples can be found on the GIT repository:  
- <https://github.com/Infineon/AURIX_code_examples>  

For additional trainings, visit our webpage:  
- <https://www.infineon.com/aurix-expert-training>  

For questions and support, use the AURIX&trade; Forum:  
- <https://community.infineon.com/t5/AURIX/bd-p/AURIX>  
