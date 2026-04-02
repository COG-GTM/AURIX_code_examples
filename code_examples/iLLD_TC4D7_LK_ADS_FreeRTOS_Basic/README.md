<img src="./Images/IFX_LOGO_600.gif" align="right" width="150" />  

# iLLD_TC4D7_LK_ADS_FreeRTOS_Basic

**This example shows how to get started with using the AURIX&trade; FreeRTOS port on TC4xx**

## Device  
The device used in this example is AURIX&trade; TC4D7XP_A-Step_CC_COM

## Board  
The board used for testing is the AURIX&trade; TC4D7XP_A-Step_CC_COM (KIT_A3G_TC4D7_LITE)

## Scope of work
This example explores FreeRTOS usage on AURIX&trade; TC4D7 using two simple tasks and one interrupt

## Introduction  
- One task toggles LED1 every 250ms
- LED2 is toggled when a BUTTON1 is pressed
    - A task waits indefinitely for a notification and then toggles LED2
    - BUTTON1 triggers an interrupt and the corresponding ISR then notifies the task

## Hardware setup  
This code example has been developed for the board KIT_TC4D7 Lite KIT (AURIX&trade; TC4D7 Lite KIT Board)

<img src="./Images/Kit_front_TC4D7.jpg" width="800" />    

The button (BUTTON1) is connected to P03.11. To trigger an external interrupt via the ERU module, `P33.7` is configured as the ERU input source (`IfxScu_REQ4A_P33_7_IN`). On the board, connect the button signal to `P33.7` so that BUTTON1 presses can generate an ERU interrupt.

For more details about ERU configuration, please refer to the **AURIX&trade; User Manual** or the ERU interrupt code examples; the corresponding links are provided in the *References* section.

## Implementation
**Startup software:**
- The code initializes the device through the Startup software libraries provided by the iLLDs (Infineon Low Level Driver)
- Core0 executes this code example, including FreeRTOS and the tasks for the "*app*" for each LED
- Core1 through Core5 are then running into an empty infinite while loop

**The example works as follows...**

- The following FreeRTOS tasks and interrupts are used:
    1. **APP LED1**  
            - Task function: `task_app_led1(..)` in `App_Led1.c`  
            - The `app_init(..)` function is called before the task enters its infinite loop. Initialization of P03.9 as an output for driving LED1 is done here
            - Inside the infinite loop, LED1 is toggled once every 250ms
    2. **APP LED2**  
            - Task function: `task_app_led2` in `App_Led2.c`  
            - The `app_init(..)` function is called before the task enters its infinite loop. Initialization of P03.10 as an output for driving the LED2 is done here. Additionally, the initialization of an ERU interrupt for input P33.7 is also configured here. Only falling edge detection is enabled, so the interrupt will be triggered only when BUTTON1 is pressed (release has no effect)  
            - Inside the infinite loop, waits indefinitely for a task notification from the ERU ISR
    3. **ERU Int0 ISR**  
            - `SCUERU_Int0_Handler` in `App_Led2.c`  
            - Triggered when BUTTON1 is pressed. Sends a task notification to the "APP LED2" task then yields from the ISR

## Compiling and programming

Before testing this code example:  
- Power the board through the dedicated power connector 
- Connect the board to the PC through the USB interface
- Build the project using the dedicated Build button <img src="./Images/build_activeproj.gif" /> or by right-clicking the project name and selecting "Build Project"
- To flash the device and immediately run the program, click on the dedicated Flash button <img src="./Images/micro.png" /> 

## Run and Test   
After code compilation and flashing the device, LED1 (P03.9) should start blinking with a period of 250ms and pressing BUTTON1 should toggle the state of LED2 (P03.10).

## References  

AURIX&trade; Development Studio is available online:  
- <https://www.infineon.com/aurixdevelopmentstudio>  
- Use the "Import..." function to get access to more code examples  

FreeRTOS Quick Start Guide:
- <https://www.freertos.org/FreeRTOS-quick-start-guide.html>

More code examples can be found on the GIT repository:  
- <https://github.com/Infineon/AURIX_code_examples>  

For additional trainings, visit our webpage:  
- <https://www.infineon.com/aurix-expert-training>  

For questions and support, use the AURIX&trade; Forum:  
- <https://community.infineon.com/t5/AURIX/bd-p/AURIX>      
