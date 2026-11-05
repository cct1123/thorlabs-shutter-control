# KEH3 direct Ethernet: blocked contract

SRC-003 (DOC-103012 Rev E, section 4.3/Figure 17) establishes one hub address and
ports 40303 management, 40304 left, 40305 middle, 40306 right, 40307 external USB.
USB IN must be disconnected in Ethernet mode. These are physical route facts,
not proof that an unwrapped APT stream works on those ports.

The retrieved manual explains vendor-application discovery and configuration but
does not establish the direct management identity exchange, wire framing,
handshake, route-specific APT addresses, supported firmware or external USB-route
contract. QMI does not establish KEH3 support. Previous Kinesis LAN successes do
not qualify a new wire implementation.

All `keh3` routes are parsed and validated but unavailable before socket access.
Hub serial, firmware, IPv4 address, selected bay and expected controller serial
are separate configuration fields. No management-port scan, guessed rack address,
raw-TCP fallback, hub reset or persistent configuration is attempted.

Request the manufacturer developer contract for these exact items:

1. TCP/UDP connection type, per-port framing, initialization and idle/reconnect semantics.
2. Read-only hub serial/model/firmware query and responses; no configuration side effects.
3. Controller identity/routing exchange for occupied/empty/swapped bays and firmware variants.
4. External USB OUT supported devices/topologies and concurrent USB/Ethernet restrictions.
5. Delayed reply ordering, unsolicited messages, faults and recovery guarantees.

After clarification, implement a separate hub transport with one owner/receive
path per documented connection, invalidate all observations on hub loss, and run
TEST-208. Required bench cases include wrong hub, empty/swapped bays, multiple
same-model cubes, route loss, shared hub loss and no ON replay after reconnect.
No Ethernet or FTDI-avoidance acceptance result is currently PASS.

5 November follow-up: [offline commissioning support](keh3-offline-validation.md)
adds a bounded TCP candidate identity probe and hardware-free capture analyzer.
These diagnostics are separate from operational routes, preserve unverified hub
identity, require an explicit candidate address, and cannot unlock control.
The reference and the inspected manufacturer documents do not yet resolve the
wire contract. No live probe was performed.
