# PHAL plugin - Network Manager

Provides the network manager interface for NetworkManager based plugins. This plugin utilizes nmcli for all communications with network manager. The dbus interface for this plugin is a work in progress.

# Requires
This plugin has the following requirements:
- nmcli

# Install

`pip install ovos-PHAL-plugin-network-manager`

# Event Details:

##### Backend Selection

This plugin provides two different backends: nmcli and dbus, the following event allows for setting the backend at runtime for every operation

```python

# Backend:
# ovos.phal.nm.set.backend
# - type: Request
# - description: Allows client to use a specific backend

# ovos.phal.nm.backend.not.supported
# - type: Response
# - description: Emitted when plugin does not support the
# specific backend

```

##### Scanning

This plugin provides scanning operations for Network Manager to scan for available nearby networks, the following event can be used to initialize the scan.

```python
# Scanning: 
# ovos.phal.nm.scan
# - type: Request
# - description: Allows client to request for a network scan
#
# ovos.phal.nm.scan.complete
# - type: Response
# - description: Emited when the requested scan is completed
# with a network list
```

##### Connecting

This plugin provides handling of connection operations for Network Manager, the following events can be used to connect a network, disconnect a network using the network manager interface.

```python

# Connecting:
# ovos.phal.nm.connect
# - type: Request
# - description: Allows clients to connect to a given network
#
# ovos.phal.nm.connection.successful
# - type: Response
# - description: Emitted when a connection is successfully established
#
# ovos.phal.nm.connection.failure
# - type: Response
# - description: Emitted when a connection fails to establish
#
# Disconnecting:
# ovos.phal.nm.disconnect
# - type: Request
# - description: Allows clients to disconnect from a network
#
# ovos.phal.nm.disconnection.successful
# - type: Response
# - description: Emitted when a connection successfully disconnects
#
# ovos.phal.nm.disconnection.failure
# - type: Response
# - description: Emitted when a connection fails to disconnect
```

##### Forget Networks

The plugin also provides a interface to forget already connected networks, The following events can be used to forget a network

```python
# Forgetting:
# ovos.phal.nm.forget
# - type: Request
# - description: Allows a client to forget a network
#
# ovos.phal.nm.forget.successful
# - type: Response
# - description: Emitted when a connection successfully is forgetten
#
# ovos.phal.nm.forget.failure
# - type: Response
# - description: Emitted when a connection fails to forget
```
