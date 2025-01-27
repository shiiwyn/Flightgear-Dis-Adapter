# Flightgear-Dis-Adapter
Creates a Socket to which Flightgear connects over the Multiplayer 

## Installation
Clone the repository and install dependencies:
git clone https://github.com/shiiwyn/Flightgear-Dis-Adapter.git
cd your-repository-name
pip install -r requirements.txt

Start & use
fill in configuration & mapping file
start python code
start flightgear, select Model
in flightgear launcher select settings -> --multiplay=out,10,127.0.0.1,5005 use the ip and port used in the configuration file (listening_ip, listening_port)
press on flight in launcher

Add Plane & Model
Follow same steps from start & use 
then copy the name printed by python code into the mapping file to allocate the desired entitytype for the model
