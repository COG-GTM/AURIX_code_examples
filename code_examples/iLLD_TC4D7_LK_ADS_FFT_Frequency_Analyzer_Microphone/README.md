<img src="./Images/IFX_LOGO_600.gif" align="right" width="150" />  

# iLLD_TC4D7_LK_ADS_FFT_Frequency_Analyzer_Microphone
**CPU0 sets the analog input channel and reads the output of a microphone using STM Timer generated interrupts. Once the buffer is filled CPU1 computes the Fast Fourier Transform (FFT).**

## Device  
The device used in this example is AURIX&trade; TC4D7XP_A-Step_MC_COM

## Board  
The board used for testing is the AURIX&trade; TC4D7 lite Kit (KIT_A3G_TC4D7_LITE)

## Scope of work
This code example explains how to connect a microphone type KY-038 to the evaluation board, to collect analog sample and to apply a FFT to the data collected.
The microphone type KY-038 is connected to the board with GND, 3.3 V and Analog Out pins.
STM Timer is used to generate a timed interrupt (replacing CCU6 from the TC3xx version).
The Triggered Modular Analog-to-Digital Converter (TMADC) is used to read a value on channel 0. The reading is performed by the interrupt routine triggered by the STM Timer.
Each analog reading is stored in a buffer, once it is filled, a flag is set and the FFT is performed.
 
## Introduction  
- The Triggered Modular Analog-to-Digital Converter (TMADC) provides analog inputs to acquire signals 
- A microphone type KY-038 is connected to GND, 3.3 V and an analog input channel
- STM Timer is used to generate interrupts with a fixed timebase and inside the interrupt service routine analog channel readings are performed
- Radix-2 FFT algorithm, provided by Infineon Low Level Drivers (iLLDs), is performed once the buffer is filled with analog samples

## Hardware setup  
This code example has been developed for the AURIX&trade; TC4D7 Lite Kit (KIT_A3G_TC4D7_LITE). 
In this example, an analog input pin is connected to the analog output of KY-038 microphone. GND and 3.3 V pins of the board are connected to microphone power supply inputs. 
The board should be connected to the PC via USB to allow flashing and debugging.

## Implementation  
**Configure the project**  
This project needs: 
- STM Timer configuration to create interrupts with fixed frequency (20 kHz sampling rate),
- TMADC configuration to read the output of the microphone,
- A buffer to store the readings from analog input.

**Configuration of the STM Timer module**  
Configuration of the STM Timer is done in the <i>`init_STM_Timer()`</i> function by initializing an instance of the <i>*IfxStm_Timer_Config*</i> structure, which contains the following fields:
- <i>*base.frequency*</i> - sets the interrupt frequency in Hz (20 kHz for audio sampling)
- <i>*base.isrPriority*</i> - sets the interrupt priority
- <i>*base.isrProvider*</i> - sets the interrupt service provider (CPU0)
- <i>*comparator*</i> - selects which STM comparator to use

The functions used for STM Timer configuration are:
- <i>`IfxStm_Timer_initConfig()`</i> - fills the configuration structure with default values 
- <i>`IfxStm_Timer_init()`</i> - initializes the timer module with the user configuration
- <i>`IfxStm_Timer_run()`</i> - starts the timer
- <i>`IfxStm_Timer_acknowledgeTimerIrq()`</i> - acknowledges the timer interrupt and sets the next compare value

The above functions can be found in the iLLD header <i>*IfxStm_Timer.h*</i>

**Configuration of the TMADC**  
The configuration of the TMADC is done in the <i>`init_TMADC()`</i> function in two different steps:
- Configuration of the TMADC module
- Configuration of the TMADC channel

When both the STM Timer and TMADC modules are configured, the STM Timer periodically triggers an interrupt where the ADC reading is performed.
All the functions used for configuring the TMADC module and channel can be found in the iLLD header <i>*IfxAdc_Tmadc.h*</i>.

**Configuration of the TMADC module**  
The functions used for configuring the TMADC module are:
- <i>`IfxAdc_enableModule()`</i> - enables the global ADC module clock
- <i>`IfxAdc_Tmadc_initModuleConfig()`</i> - initializes the TMADC module configuration structure with the default values
- <i>`IfxAdc_Tmadc_initModule()`</i> - initializes the TMADC module with the user configuration

**The creation of the buffer and the call of FFT function**  
To perform a meaningful FFT a buffer needs to be filled with samples taken at a known sampling frequency keeping in mind Nyquist-Shannon sampling theorem. In this case only a part of audible spectrum (about 30 to 16 kHz) is analyzed so the sample rate is set to 20 kHz.
The function used to compute the FFT transform is <i>`Ifx_FftF32_radix2()`</i> that can be found in the iLLD header <i>*Ifx_FftF32.h*</i>, its input parameters are:
- <i>*R*</i> pointer to <i>*cfloat32*</i> array that contains the result of FFT
- <i>*X*</i> pointer to <i>*cfloat32*</i> array that contains measures
- <i>*nX*</i> size of array, which defines also the frequency resolution of FFT (fc/nX), must be power of 2 

To allow calculation and inspection of result a few variables are defined:
- <i>*g_AnalogSamplesBuffer*</i> containing measurements
- <i>*g_AnalogSamplesFFT*</i> containing result of transform, size of array must be power of 2;
- <i>*g_FFTAmplitude*</i> containing amplitude of frequency components (sqrt(Re^2+Im^2));

## Compiling and programming
Before testing this code example:
- Power the board through the dedicated power connector
- Connect the board to the PC through the USB interface
- Build the project using the dedicated Build button <img src="./Images/build_activeproj.gif" /> or by right-clicking the project name and selecting "Build Project"
- To flash the device and immediately run the program, click on the dedicated Flash button <img src="./Images/micro.png" />  

## Run and Test  
Start a debug session and resume execution of all cores, samples coming from analog port connected to the microphone are stored in <i>*g_AnalogSamplesBuffer*</i> array until it is filled, at this point a flag is raised and the FFT computation starts.
After FFT calculation flag is reset and process begins again. 
To inspect result of calculation, add variables <i>*g_AnalogSamplesFFT*</i> and <i>*g_FFTAmplitude*</i> by dragging and dropping them in the Expression view.
Suspend the execution and read the results.
<i>*FFT_RESOLUTION*</i> must be a power of 2 and can be used to increase or decrease the FFT resolution. To validate result you can place a breakpoint in <i>*FFT_CCU6.c*</i> after the FFT computation, start execution, copy buffers <i>*g_AnalogSamplesBuffer*</i> and <i>*g_AnalogSamplesFFT*</i> content and compare calculation with an external FFT calculation tool (e.g. Excel or Matlab)

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
