# Robin Cloud Relay

The cloud layer is a transport relay, not Robin's main brain.

## Contract

- Windows and Android authenticate with device-scoped credentials.
- Tasks use the same JSON contract as `core/companion_protocol.py`.
- The relay forwards tasks and task results without executing phone or Windows actions.
- Direct LAN transport remains preferred; cloud is the fallback for different networks.
- Production deployment must use TLS, short-lived credentials, revocation, expiry, rate limits, and device identity binding.

A concrete hosting provider can be selected later without changing the companion task protocol.
