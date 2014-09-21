#!/bin/bash

#Create our OpenFlow "devices"
echo "Creating OVS bridges..."
ovs-vsctl add-br of-router1
ovs-ofctl del-flows of-router1
ovs-vsctl add-br of-router2
ovs-ofctl del-flows of-router2

#Create our namespaces
echo "Creating IP namespaces..."
ip netns add 10_20_30_0
ip netns add 30_20_10_0

#Create veth interfaces to link the OVS bridges together
echo "Creating veth pairs..."
ip link add veth0 type veth peer name veth1
ip link add host1 type veth peer name veth3
ip link add host2 type veth peer name veth5

# Connect our routers
echo "Connecting OVS bridges..."
ovs-vsctl add-port of-router1 veth0
ovs-vsctl add-port of-router2 veth1

# Connect our "hosts" to the routers
ovs-vsctl add-port of-router1 veth3
ovs-vsctl add-port of-router2 veth5

# Address our "hosts"
echo "Configuring IP namespaces..."
ip link set host1 netns 10_20_30_0
ip netns exec 10_20_30_0 ifconfig host1 10.20.30.2/24 up
ifconfig of-router1 10.20.30.1/24 up
ifconfig veth3 up
ip netns exec 10_20_30_0 ip route add default via 10.20.30.1
ip link set host2 netns 30_20_10_0
ip netns exec 30_20_10_0 ifconfig host2 30.20.10.2/24 up
ifconfig of-router2 30.20.10.1/24 up
ifconfig veth5 up
ip netns exec 30_20_10_0 ip route add default via 30.20.10.1

ip link set veth0 up
ip link set veth1 up

#Get the OpenFlow port numbers and MAC addresses
ROUTER1_INFRA_PORT=`ovs-ofctl show of-router1 | grep veth0 | cut -f 1 -d '(' | sed 's/[[:space:]]//g'`
ROUTER1_INFRA_MAC=`ovs-ofctl show of-router1 | grep veth0 | awk -F'addr:' '{print $2}'`
ROUTER1_GW_MAC=`ovs-ofctl show of-router1 | grep of-router1 | awk -F'addr:' '{print $2}'`
ROUTER2_INFRA_PORT=`ovs-ofctl show of-router2 | grep veth1 | cut -f 1 -d '(' | sed 's/[[:space:]]//g'`
ROUTER2_INFRA_MAC=`ovs-ofctl show of-router2 | grep veth1 | awk -F'addr:' '{print $2}'`
ROUTER2_GW_MAC=`ovs-ofctl show of-router2 | grep of-router2 | awk -F'addr:' '{print $2}'`
ROUTER1_HOST_MAC=`ovs-ofctl show of-router1 | grep veth3 | awk -F'addr:' '{print $2}'`
ROUTER1_HOST_PORT=`ovs-ofctl show of-router1 | grep veth3 | cut -f 1 -d '(' | sed 's/[[:space:]]//g'`
ROUTER2_HOST_MAC=`ovs-ofctl show of-router2 | grep veth5 | awk -F'addr:' '{print $2}'`
ROUTER2_HOST_PORT=`ovs-ofctl show of-router2 | grep veth5 | cut -f 1 -d '(' | sed 's/[[:space:]]//g'`
HOST1_MAC=`ip netns exec 10_20_30_0 ifconfig host1 | grep HWaddr | cut -f 10 -d ' '`
HOST2_MAC=`ip netns exec 30_20_10_0 ifconfig host2 | grep HWaddr | cut -f 10 -d ' '`

echo "Installing of-router1 rules..."
ovs-ofctl add-flow of-router1 priority=0,actions=drop
ovs-ofctl add-flow of-router1 priority=1000,dl_type=0x0806,nw_dst=10.20.30.1,actions=output:LOCAL
ovs-ofctl add-flow of-router1 priority=1000,dl_type=0x0806,dl_src=$ROUTER1_GW_MAC,nw_dst=10.20.30.0/24,actions=output:$ROUTER1_HOST_PORT
ovs-ofctl add-flow of-router1 priority=2000,dl_type=0x0800,nw_dst=10.20.30.0/24,actions=mod_dl_src:$ROUTER1_HOST_MAC,mod_dl_dst:$HOST1_MAC,dec_ttl,output:$ROUTER1_HOST_PORT
ovs-ofctl add-flow of-router1 priority=2500,dl_type=0x0800,nw_dst=10.20.30.1,actions=output:LOCAL
ovs-ofctl add-flow of-router1 priority=2500,dl_type=0x0800,nw_src=10.20.30.1,nw_dst=10.20.30.0/24,actions=output:$ROUTER1_HOST_PORT
ovs-ofctl add-flow of-router1 priority=3000,dl_type=0x0800,nw_dst=30.20.10.0/24,actions=mod_dl_src:$ROUTER1_INFRA_MAC,mod_dl_dst:$ROUTER2_INFRA_MAC,dec_ttl,output:$ROUTER1_INFRA_PORT

echo "Installing of-router2 rules"
ovs-ofctl add-flow of-router2 priority=0,actions=drop
ovs-ofctl add-flow of-router2 priority=1000,dl_type=0x0806,nw_dst=30.20.10.1,actions=output:LOCAL
ovs-ofctl add-flow of-router2 priority=1000,dl_type=0x0806,dl_src=$ROUTER2_GW_MAC,nw_dst=30.20.10.0/24,actions=output:$ROUTER2_HOST_PORT
ovs-ofctl add-flow of-router2 priority=2000,dl_type=0x0800,nw_dst=30.20.10.0/24,actions=mod_dl_src:$ROUTER2_HOST_MAC,mod_dl_dst:$HOST2_MAC,dec_ttl,output:$ROUTER2_HOST_PORT
ovs-ofctl add-flow of-router2 priority=2500,dl_type=0x0800,nw_dst=30.20.10.1,actions=output:LOCAL
ovs-ofctl add-flow of-router2 priority=2500,dl_type=0x0800,nw_src=30.20.10.1,nw_dst=30.20.10.0/24,actions=output:$ROUTER2_HOST_PORT
ovs-ofctl add-flow of-router2 priority=3000,dl_type=0x0800,nw_dst=10.20.30.0/24,actions=mod_dl_src:$ROUTER2_INFRA_MAC,mod_dl_dst:$ROUTER1_INFRA_MAC,dec_ttl,output:$ROUTER2_INFRA_PORT
