

# intra-agent messaging on the same channel

# scenario where agent sends message to channel
# and a message gets sent in reply distributed by the channel


# use N pingpong agents

# agents are on the same channel

# set RT ticks to be sent to all agents in pool every second

# each agent to send a "ping" to the channel every
# 10 seconds (every 10th tick)

# upon receiving a ping, send a pong in reply to the ping to all agents
# on the channel, so each agent receives N pongs
# an agent can differentiate between the pong received in reply to their
# ping vs pongs triggered by other agents



