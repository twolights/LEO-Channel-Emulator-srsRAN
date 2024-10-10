# LEO Satellite Channel Emulator for srsRAN with ZeroMQ RF

This project is a part of the research work on the implementation of Doppler-tolerant PSS detection and CFO estimation for 5G NR-based non-terrestrial networks. The project aims to implement a LEO satellite channel emulator for srsRAN using ZeroMQ RF. The project is implemented on the srsRAN and GNURadio platforms.


# Prerequisites

- srsRAN 4G/5G compiled with ZeroMQ RF
- GNURadio
- Matplotlib

# Current Status (As of October 11th, 2024)

- This project is currently under development and for research purposes only.
- The simulator is implemented under the following assumptions:
  - The earth is a perfect sphere
  - The UE is stationary and the satellite is moving
  - The satellite is in a perfect circular orbit with a fixed altitude
  - The satellite is orbiting just right above the UE
  - The channel is LOS with no fading and noise (yet)
- The srsRAN gNB and UE are configured to connect to the ZeroMQ RF interface.
- IP addresses of srsRAN gNB and UE are hardcoded in the GNURadio flowgraph.

I have recorded a video of the current status of the project. You can watch it [here](https://youtu.be/pQOsAQG8Y0Q).

# Running

The simulator requires GNURadio-compiled Python script to run.
However the repository only contains the GNURadio flowgraph.
To run the simulator, you need to first compile the flowgraph using **grcc**.

```bash
grcc src/leo_channel.grc -o src/
```

The simulator can be started using the following command:
```bash
cd src/
python3 leo_channel.py --sat_init_pos=70 --sat_altitude=600 --dl_freq=2.6e9 --ul_freq=2.4e9 
```

To see what the command line options do:
```bash
python3 leo_channel.py --help
```

After running the simulator, start the srsRAN gNB and UE with proper configurations.

# TODOs

- [ ] Add command line options for srsRAN UE & gNB IP addresses
- [ ] Add noise and fading to the channel emulator
- [ ] Add channel models such as NTN-TDL-C
- [ ] Implement and test on real RF devices such as USRP
- [ ] Interactive GUI for the satellite & UE plot
