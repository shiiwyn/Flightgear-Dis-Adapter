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
start udpsocket.py
start flightgear, select Model (should exist in the mapping file)
in flightgear launcher select settings -> paste "--multiplay=out,10,ip,flightgear_mp_port_out --multiplay=in,10,ip,flightgear_mp_port_in" at the bottom in additional Settings, use the ip and port used in the configuration file (listening_ip, flightgear_mp_port_out, flightgear_mp_port_in)
press on flight in launcher

There can be an error if the adapter receives pdu packages before flightgear is online, for that case try starting flightgear before the python code

Add Plane & Model
Follow same steps from start & use 
then copy the name printed by python code into the mapping file to allocate the desired entitytype for the model
also copy the model path into the mapping file 


