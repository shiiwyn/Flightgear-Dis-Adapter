# Flightgear-Dis-Adapter
Creates a Socket to which Flightgear Multiplayer connects 
collects the xdr package from flightgear and fills in a pdu from dis with the package it receives and a mapping file for the plane model, then it sends this pdu over multicast or singlecast

comming: receiving pdu packages and transforming into a xdr package to send to flightgear to see other planes in the same simulation

## Installation
Clone the repository and install dependencies:
git clone https://github.com/shiiwyn/Flightgear-Dis-Adapter.git
cd your-repository-name
pip install -r requirements.txt

## Usage
fill in configuration & mapping file
start python code
start flightgear, select Model (should exist in the mapping file)
in flightgear launcher select settings -> paste "--multiplay=out,10,ip,port" at the bottom in additional Settings, use the ip and port used in the configuration file (listening_ip, listening_port)
press on flight in launcher

Add Plane & Model
Follow same steps from usage 
then copy the name printed by python code into the mapping file to allocate the desired entitytype for the model
then close everything and start the Usage step again
