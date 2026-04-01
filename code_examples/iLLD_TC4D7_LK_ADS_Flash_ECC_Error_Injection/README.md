<img src="./Images/IFX_LOGO_600.gif" align="right" width="150" />  

# iLLD_TC4D7_LK_ADS_Flash_ECC_Error_Injection
**Inject an ECC (Error Correction Code) error into the Program or Data Flash**  

## Device  
The device used in this example is AURIX&trade; TC4D7XP_A-Step_CC_COM 

## Board  
The board used for testing is the AURIX&trade; TC4D7XP_A-Step_CC_COM (KIT_A3G_TC4D7_LITE) 

## Scope of work   
Inject an ECC error in one of the valid pages of the PFlash and DFlash

## Introduction  
- For the PFlash it is possible to inject a Single, Double or Multiple Bit Error (SBE, DBE, MBE) 
- For the DFlash it is possible to inject a Single, Double, Triple or Multiple Bit Error (SBE, DBE, TBE, MBE)
- A page is an aligned group of data double words plus an ECC extension
- Program Flash page consists of 32 bytes
- Data Flash page consists of 8 bytes

## Hardware setup  
This code example has been developed for the board TC4D7XP_A-Step_CC_COM (KIT_A3G_TC4D7_LITE)
 
<img src="./Images/Kit Image Front.PNG" width="1024" />  
  
  
## Implementation  
The SW is capable to insert ECC errors in the PFlash and DFlash. The API *injectFlashECCError* must be called and two parameters shall be passed to it. First, the absolute address where to inject the ECC error and second, the error type (SBE, DBE, TBE or MBE). The absolute address must be page-aligned and the target page must not have any ECC error. Also, in case of PFlash error injection, only addresses belonging to Segment 10 (non-cached area) will be accepted.
The error types are defined in the *Flash_ECCErrorType* enumeration.

Depending on where the target address is pointing, one of the APIs called *checkPFlashAddress* and *checkDFlashAddress* is used to check if the target address is valid. If all the checks are passed, one of the APIs *injectPFlash* and *injectDFlash* will be called to really inject the ECC error in the PFlash or in the DFlash. All these APIs return an error code which is in the end saved in the variable *injectionResult*.

On AURIX&trade; TC4xx the protection scheme using the "safety_endinit" functions has been replaced by the PROT/APU mechanism, therefore "safety_endinit" functions are not needed for flash write operations. The watchdog timer management uses the IfxWtu API instead of the IfxScuWdt API used on TC3xx.

**Configure and control the LEDs**  

Two LEDs are configured using methods from the iLLD header *IfxPort.h*.  

The port pins to which the LEDs are connected are configured as push-pull output using the function *IfxPort_setPinModeOutput()*.  

To toggle the LEDs, the function *IfxPort_togglePin()* is used.  

## Compiling and programming
Before testing this code example:  
- Power the board through the dedicated power connector 
- Connect the board to the PC through the USB interface
- Build the project using the dedicated Build button <img src="./Images/build_activeproj.gif" /> or by right-clicking the project name and selecting "Build Project"
- To flash the device and immediately run the program, click on the dedicated Flash button <img src="./Images/micro.png" />  

## Run and Test   
After code compilation and flashing the device, one of these LEDs can be observed
- If ECC error injection is completed with no errors, LED1 will be blinking
- If ECC error injection is completed with an error, LED2 will be blinking
- If before the ECC error injection a Bus Error Trap occurs while reading from the flash, LED2 will be switched on

When ECC error injection fails, the value of the variable *injectionResult* can be checked in order to establish the root cause.
Below are the possible errors:

- <code>*INVALID_ECC_ERROR_TYPE*</code>: target ECC error type is not valid
- <code>*INVALID_ADDRESS*</code>: target address is not valid and generates a bus error
- <code>*INVALID_PFLASH_ADDRESS*</code>: target address is not inside the PFlash memory map
- <code>*NOT_ALIGNED_PFLASH_ADDRESS*</code>: target address is not aligned to PFlash page 
- <code>*ERRORED_PFLASH_ADDRESS*</code>: target PFlash page has already an ECC error
- <code>*FAILED_PFLASH_ERROR_INJECTION*</code>: error injection in the PFlash failed
- <code>*INVALID_DFLASH_ADDRESS*</code>: target address is not inside the DFlash memory map
- <code>*NOT_ALIGNED_DFLASH_ADDRESS*</code>: target address is not aligned to DFlash page
- <code>*ERRORED_DFLASH_ADDRESS*</code>: target DFlash page has already an ECC error
- <code>*FAILED_DFLASH_ERROR_INJECTION*</code>: error injection in the DFlash failed
- <code>*ERROR_INJECTION_NOT_POSSIBLE*</code>: desired ECC error injection is not possible

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
