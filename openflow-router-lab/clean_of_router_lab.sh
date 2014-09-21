#!/bin/bash

ip netns del 10_20_30_0
ip netns del 30_20_10_0

ovs-vsctl del-br of-router1
ovs-vsctl del-br of-router2

ip link del veth0


