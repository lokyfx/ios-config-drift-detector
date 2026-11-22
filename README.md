<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->



<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Cisco IOSv Configuration Drift Detector</h3>

  <p align="center">
    Lightweight Python NetDevOps tool to fetch Cisco IOSv running configurations over SSH and detect configuration drift against a golden baseline.
  </p>
</div>




<!-- ABOUT THE PROJECT -->
## About The Project

A lightweight **NetDevOps** utility in Python that connects to a simulated Cisco IOSv router (`R1`) over SSH, pulls its current `running-config`, and compares it against an approved golden baseline (`r1_golden.cfg`) to detect configuration drift.

Here's why it's built this way:
- **Readable over clever:** Uses straightforward list and loop comparisons instead of external diff abstractions, so every line of the drift check is easy to trace and tweak.
- **No `~/.ssh/config` clutter:** Registers legacy SHA-1 KEX algorithms (`diffie-hellman-group14-sha1`, `diffie-hellman-group1-sha1`) and `ssh-rsa` host keys directly on `paramiko.Transport` in Python for older IOSv images—and can be safely skipped or removed when targeting newer routers with modern SSH algorithms.
- **Sequential runner:** `run.py` orchestrates `get_config.py` and `drift_checker.py` as separate `subprocess.run()` steps, stopping early if config retrieval fails.

Project files at a glance:
- `get_config.py` — Connects over SSH via Netmiko and saves `r1_running_config.cfg`.
- `drift_checker.py` — Filters comments/dynamic lines and compares `r1_running_config.cfg` against `r1_golden.cfg`.
- `run.py` — Runs `get_config.py` followed by `drift_checker.py` in sequence.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

Built with Python and Netmiko (with Paramiko for SSH).

* [![Python][Python-badge]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Set up a virtual environment, add your router credentials, and capture a golden baseline before running drift checks.

### Prerequisites

- **Python 3.13+** (cross-platform: works on Linux, macOS, or Windows)
- **GNS3** (or a physical/virtual Cisco IOSv device) reachable over the network (e.g., `192.168.122.10`) with SSH enabled
- Python dependencies: `netmiko`, `paramiko`, `python-dotenv`

### Installation

1. Install **Python 3.13+** if you do not already have it installed
   - **Linux (Debian/Ubuntu/Kubuntu):**
     ```sh
     sudo apt update && sudo apt install -y python3 python3-venv python3-pip
     ```
   - **macOS (Homebrew):**
     ```sh
     brew install python
     ```
   - **Windows:** Download and run the installer from [python.org](https://www.python.org/downloads/) (check **Add python.exe to PATH** during setup).

   Verify your Python version:
   ```sh
   python3 --version  # On Windows: python --version
   
2. Clone the repo
   ```sh
   git clone https://github.com/lokyfx/ios-config-drift-detector.git
   cd ios-config-drift-detector
   ```
3. Create and activate a virtual environment (.venv) so packages stay isolated from your system Python
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. Upgrade pip and install the required packages (netmiko pulls in paramiko, and python-dotenv loads .env variables)
   ```sh
   pip install --upgrade pip
   pip install netmiko python-dotenv
   ```
5. Create a .env file in the project root with your router SSH password
   ```py
   SSH_KEY_R1=your_router_ssh_password
   ```
6. Verify SSH reachability to R1 and save your initial golden baseline configuration
   ```sh
   python3 get_config.py
   cp r1_running_config.cfg golden_config.cfg
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Before running the scripts, make sure the target Cisco IOSv device has IP reachability from your host and SSHv2 enabled with local authentication, then capture a golden baseline and run drift checks.

### 1.0 GNS3 Lab Setup (`R1` IOSv over `virbr0` NAT)

In GNS3, connect `R1`'s management/uplink interface (`GigabitEthernet0/0`) to a Cloud/NAT node bridged to `virbr0` (`192.168.122.0/24`), where the host/gateway is typically `192.168.122.1`.

Based on the lab `running-config` (`R1`), the core SSH and IP settings look like this:

```ios
hostname R1
ip domain name lab.local
!
username admin privilege 15 secret <your_password>
!
interface GigabitEthernet0/0
 ip address 192.168.122.10 255.255.255.0
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 192.168.122.1
ip ssh version 2
!
line vty 0 4
 login local
 transport input ssh
```

When setting up a fresh IOSv node, configure the interface IP and default route, set a domain name (ip domain name ...), generate an RSA key pair in global config mode (crypto key generate rsa modulus 2048), create a privilege-15 local account (username admin privilege 15 secret ...), and restrict VTY lines to transport input ssh with login local. Make sure the password matches SSH_KEY_R1 in .env.

### 1.1 Real-World / Production Router Usage
The same workflow applies to a physical or virtual router outside GNS3 (for example, a lab/branch IOSv or IOS device on a management VLAN

#### IMPORTANT
Review `legacy SSH compatibility`: The `Paramiko SHA-1` / `ssh-rsa` fallback in get_config.py is aimed at older IOSv images; if connecting to newer `IOS/IOS-XE` devices with modern KEX and host-key algorithms, you may not need it or can disable/remove it per your security policy.

### 2 Running the Full Drift Check (run.py)
Run both steps in order with a single command:

```sh
python3 run.py
```

### Running Scripts Individually
You can also run each stage on its own while debugging or testing config changes:

Pull the current running-config from R1 into r1_running_config.cfg
```sh
python3 get_config.py
```
Compare r1_running_config.cfg against golden_config.cfg
```sh
python3 drift_checker.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Example Output
When you run `python3 run.py`, it first retrieves the current configuration via `get_config.py` and then runs `drift_checker.py` against `golden_config.cfg`:

Changes were made to the DCHP - dns-server configuration for demo.

```sh
(.venv) user@system:~/ios-config-drift-detector$ python3 run.py
```
```sh
Config saved for R1.
REMOVED: Changes were modified/removed
REMOVED: - dns-server 1.1.1.1 
ADDED: changes were modified/added
ADDED: - dns-server 8.8.8.8
```

## Packet Capture via WireShark
Inspecting the raw SSH traffic helps verify that TCP reachability, protocol version exchange, and legacy algorithm negotiation behave as expected before troubleshooting Netmiko or Paramiko.

### 1. TCP 3-Way Handshake - (`SYN`, `SYN - ACK`, `ACK`) — Confirms IP routing and port 22 reachability between your host and R1 (`192.168.122.10`).
<img width="1600" height="57" alt="Screenshot_20261122_220113" src="https://github.com/user-attachments/assets/4e4c4374-9f40-4524-aada-e13293c0dfed" />


### 2. SSH-2.0 Banner Exchange — Both sides announce SSHv2 support + Key Exchange Both peers advertise supported key exchange (diffie-hellman-group14-sha1) and host key (ssh-rsa) algorithms.
<img width="1600" height="204" alt="Screenshot_20261122_220210" src="https://github.com/user-attachments/assets/16575c1f-2a85-46b3-b89f-3334dbf44926" />



<!-- LICENSE -->
## License

Distributed under the Unlicense License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Email - lokodiattila@gmail.com

Project Link: ([https://github.com/lokyfx/ios-config-drift-detector.git](https://github.com/lokyfx/ios-config-drift-detector.git))

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
