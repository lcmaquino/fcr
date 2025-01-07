## Description

The Fenix Reballing Controller (FCR) software controls the temperature of two heating devices for preheating electronic boards or reballing BGA components. Examples of heating devices include an electric grill or an electric resistor. Due to the high electrical current required to power these devices, they should be activated via a mechanical relay or a solid-state relay.

The FCR consists of an electronic circuit with the [Raspberry Pi Pico](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico) microcontroller and a set of codes written for [MicroPython](https://www.micropython.org/).

## Assembly and Installation

  - Assemble the electronic circuit according to the schematic diagram: [fenix-controlador-de-ressolda.pdf](https://github.com/lcmaquino/fcr/tree/main/pcb/fenix-controlador-de-ressolda.pdf). Also, see the [simple wiring diagram](assets/fcr-simple-wiring.png);
  - Connect the relay input pins to the connectors indicated in the diagram by `OUT1` and `OUT2`;
  - Connect the relay output pins to the heating devices;
  - Connect the HD44780 LCD 16×02, MAX6675, and Keyes_AD_Key modules to their respective connectors indicated in the diagram;
  - Install the [MicroPython firmware](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3) on the Raspberry Pi Pico;
  - Use your preferred IDE to copy all files from the [`src`](https://github.com/lcmaquino/fcr/tree/main/src) directory to the Raspberry Pi Pico. (For example, you can use [Thonny](https://thonny.org/) or [Visual Studio Code](https://code.visualstudio.com/));
  - Power the electronic circuit with a 5V DC power supply with at least 500mA;

  The Keyes_AD_Key module has five tactile switches labeled SW1, SW2, SW3, SW4, and SW5. The FCR maps these switches for menu navigation such that:

  - SW1 - moves the menu to the left;
  - SW2 - increases the value of the currently displayed option;
  - SW3 - decreases the value of the currently displayed option;
  - SW4 - moves the menu to the right;
  - SW5 - selects the current menu;

## Usage

  The FCR has three modes:
  - Preheater - for preheating an electronic board;
  - Reballing - for reballing BGA components;
  - Auto Tuning - to automatically calculate the coefficients used in the [PID](https://en.wikipedia.org/wiki/Proportional-integral-derivative_controller) control;

  All modes have a menu containing specific and general options.

  The general options are:
  - `Kp` - proportional coefficient of the PID control;
  - `Ki` - integral coefficient of the PID control;
  - `Kd` - derivative coefficient of the PID control;
  - `ap` - actuation period is the period (in seconds) at which the PID control is updated;
  - `Run` - execute the mode functions;
  - `Home` - return to the initial mode selection screen;

  See below the specific options for each mode.

### Preheater Mode

  The Preheater mode controls only one heating device that should be placed below the electronic board.

  In Preheater mode, the specific options are:
  - `SV` - Setpoint Variable is the temperature (in degrees Celsius) that the heating element should reach;
  - `d` - duration is the duration (in seconds) the mode should run;

### Reballing Mode

  The Reballing mode controls two heating devices, one of which should be placed below the electronic board and the other above it.

  In Reballing mode, the specific options are:
  - `PTN` - pattern is the temperature pattern (in degrees Celsius) that the heating devices should follow. Each pattern consists of up to five parts, each containing the `r`, `L`, and `d` options explained below;
  - `r` - rate is the rate of temperature change (in degrees Celsius per second);
  - `L` - limit is the temperature limit (in degrees Celsius) that should be reached;
  - `d` - duration is the duration (in seconds) that the temperature should remain at its limit `L`;

  Up to 10 temperature patterns can be configured. Here is an example configuration:
```
  PTN1
  | - r1: 0.86
  | - L1: 120.0
  | - d1: 60
  | - r2: 0.57
  | - L2: 180.0
  | - d2: 60
  | - r3: 0.29
  | - L3: 210.0
  | - d3: 60
  | - r4: 0.19
  | - L4: 227.0
  | - d4: 60
  | - r5: 0.0
  | - L5: 0.0
  | - d5: 0
```

  Note that in this example, the PTN1 pattern will have four active parts. The fifth part is all zeros and will be ignored by the FCR. The figure below represents this pattern.

  ![Image of the graph representing the PTN1 pattern](https://github.com/lcmaquino/fcr/blob/main/assets/plot_ptn1.svg)

  In the first part of the pattern, the temperature should rise at a rate of `r1 = 0.86`°C/s until it reaches `L1 = 120`°C, staying at this temperature for `d1 = 60`s. In the second part, the temperature should rise at a rate of `r2 = 0.57`°C/s until it reaches `L2 = 180`°C, staying at this temperature for `d2 = 60`s. In the third part, the temperature should rise at a rate of `r3 = 0.29`°C/s until it reaches `L3 = 210`°C, staying at this temperature for `d3 = 60`s. Finally, in the fourth part, the temperature should rise at a rate of `r4 = 0.19`°C/s until it reaches `L4 = 227`°C, staying at this temperature for `d4 = 60`s.

### Auto Tuning

  The Auto Tuning mode analyzes the temperature data of the heating device below the electronic board to approximately calculate the `Kp`, `Ki`, and `Kd` coefficients of the PID controller.

  In Auto Tuning mode, the specific options are:
  - `SV` - Setpoint Variable is the temperature (in degrees Celsius) that the heating element should reach;
  - `d` - duration is the duration (in seconds) the mode should run;

## License

FCR is open-sourced software licensed under the [GPL v3.0 or later](https://github.com/lcmaquino/ccolab/blob/main/LICENSE).
