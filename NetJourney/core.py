"""NetJourney core logic (no Streamlit imports, so it can be tested on its own).
Everything here is an EDUCATIONAL SIMULATION, not real networking."""
import ipaddress
import networkx as nx

NODES = ["PC-A", "R1", "R2", "R3", "R4", "PC-B"]
POS = {"PC-A": (0, 1), "R1": (1.5, 2), "R2": (1.5, 0), "R3": (3.5, 2), "R4": (3.5, 0), "PC-B": (5, 1)}
DEFAULT_COSTS = {("PC-A", "R1"): 2, ("PC-A", "R2"): 5, ("R1", "R2"): 2, ("R1", "R3"): 6,
                 ("R2", "R3"): 3, ("R2", "R4"): 6, ("R3", "R4"): 2, ("R3", "PC-B"): 5, ("R4", "PC-B"): 2}
NODE_IPS = {"PC-A": "192.168.1.10", "R1": "10.0.1.1", "R2": "10.0.2.1", "R3": "10.0.3.1",
            "R4": "10.0.4.1", "PC-B": "172.16.5.20"}


def build_graph(costs):
    g = nx.Graph()
    g.add_nodes_from(NODES)
    for (a, b), c in costs.items():
        g.add_edge(a, b, weight=c)
    return g


def dijkstra(costs, src, dst):
    """Least-cost path via NetworkX Dijkstra. Returns (path, cost)."""
    g = build_graph(costs)
    return nx.dijkstra_path(g, src, dst, weight="weight"), nx.dijkstra_path_length(g, src, dst, weight="weight")


def dijkstra_trace(costs, src):
    """Hand-written Dijkstra that records each step (for the lab table)."""
    adj = {n: {} for n in NODES}
    for (a, b), c in costs.items():
        adj[a][b] = c; adj[b][a] = c
    dist = {n: float("inf") for n in NODES}; dist[src] = 0
    done, steps = set(), []
    while len(done) < len(NODES):
        u = min((n for n in NODES if n not in done), key=lambda n: dist[n])
        if dist[u] == float("inf"):
            break
        done.add(u)
        for v, c in adj[u].items():
            if dist[u] + c < dist[v]:
                dist[v] = dist[u] + c
        steps.append({"Settled node": u, **{n: ("∞" if dist[n] == float("inf") else dist[n]) for n in NODES}})
    return steps


def bellman_ford(costs, src):
    """Round-by-round Bellman-Ford relaxation (centralised, simplified).
    Returns (dist, prev, rounds) where rounds is a list of distance snapshots."""
    dist = {n: float("inf") for n in NODES}; dist[src] = 0
    prev = {n: None for n in NODES}
    rounds = [dict(dist)]
    edges = [(a, b, c) for (a, b), c in costs.items()] + [(b, a, c) for (a, b), c in costs.items()]
    for _ in range(len(NODES) - 1):
        changed = False
        for u, v, c in edges:
            if dist[u] + c < dist[v]:
                dist[v] = dist[u] + c; prev[v] = u; changed = True
        rounds.append(dict(dist))
        if not changed:
            break
    return dist, prev, rounds


def bf_path(prev, src, dst):
    path, n = [], dst
    while n is not None:
        path.append(n); n = prev[n]
    path.reverse()
    return path if path and path[0] == src else []


def path_cost(costs, path):
    tot = 0
    for a, b in zip(path, path[1:]):
        tot += costs.get((a, b), costs.get((b, a)))
    return tot


# ---------------- IPv4 header ----------------
def ipv4_checksum(header: bytes) -> int:
    s = 0
    for i in range(0, len(header), 2):
        s += (header[i] << 8) + header[i + 1]
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


PROTO = {"TCP": 6, "UDP": 17, "ICMP": 1}


def build_header(src, dst, ttl, proto, total_len, ident=0x1C46):
    """Validate inputs and build an ILLUSTRATIVE 20-byte IPv4 header (no options). Raises ValueError."""
    try:
        s = ipaddress.IPv4Address(src.strip()); d = ipaddress.IPv4Address(dst.strip())
    except ValueError as e:
        raise ValueError(f"Invalid IPv4 address: {e}")
    if not 0 <= ttl <= 255:
        raise ValueError("TTL must be between 0 and 255.")
    if proto not in PROTO:
        raise ValueError("Protocol must be TCP, UDP or ICMP.")
    if not 20 <= total_len <= 65535:
        raise ValueError("Total length must be between 20 (header only) and 65535 bytes.")
    raw = bytearray(20)
    raw[0] = (4 << 4) | 5
    raw[2:4] = total_len.to_bytes(2, "big"); raw[4:6] = ident.to_bytes(2, "big")
    raw[6:8] = (0x4000).to_bytes(2, "big")  # DF flag set, fragment offset 0
    raw[8] = ttl; raw[9] = PROTO[proto]
    raw[12:16] = s.packed; raw[16:20] = d.packed
    ck = ipv4_checksum(bytes(raw)); raw[10:12] = ck.to_bytes(2, "big")
    assert ipv4_checksum(bytes(raw)) == 0
    return {"version": 4, "ihl": 5, "header_bytes": 20, "total_len": total_len, "payload": total_len - 20,
            "ident": ident, "ttl": ttl, "proto_name": proto, "proto_num": PROTO[proto], "checksum": ck,
            "src": str(s), "dst": str(d), "hex": bytes(raw).hex(" ").upper()}


# ---------------- Address lab ----------------
def analyse_address(text):
    """Return a dict describing an IPv4/IPv6 address, or {'error': msg}."""
    text = text.strip()
    try:
        a = ipaddress.ip_address(text)
    except ValueError:
        return {"error": f"'{text}' is not a valid IPv4 or IPv6 address."}
    kind = "private" if a.is_private else "global/public"
    if a.is_loopback: kind = "loopback"
    elif a.is_link_local: kind = "link-local"
    elif a.is_multicast: kind = "multicast"
    if a.version == 4:
        octs = [int(x) for x in str(a).split(".")]
        return {"version": 4, "bits": 32, "octets": octs, "binary": ".".join(f"{o:08b}" for o in octs),
                "dotted": str(a), "kind": kind}
    return {"version": 6, "bits": 128, "exploded": a.exploded, "compressed": a.compressed, "kind": kind}


# ---------------- Quiz ----------------
QUIZ = [
 ("Which is a core responsibility of the network layer?", ["Logical addressing and routing packets between networks", "Encoding bits on a wire", "Providing reliable byte streams", "Rendering web pages"], 0,
  "The network layer provides logical (IP) addressing and moves packets hop by hop across networks via forwarding and routing."),
 ("What does a router do when a packet arrives?", ["Looks up the destination IP address in its forwarding table and sends it to the next hop", "Rewrites the application data", "Guarantees delivery by retransmitting", "Broadcasts it to every port"], 0,
  "Forwarding means matching the destination address against the forwarding table to pick an output link. IP itself is best-effort."),
 ("How long is an IPv6 address compared with IPv4?", ["128 bits vs 32 bits", "64 bits vs 32 bits", "256 bits vs 128 bits", "48 bits vs 32 bits"], 0,
  "IPv4 uses 32-bit addresses; IPv6 uses 128-bit addresses written in hexadecimal."),
 ("Who decrements the IPv4 TTL field?", ["Each router that forwards the packet", "Only the sender", "Only the receiver", "The DNS server"], 0,
  "Each forwarding router decrements TTL by at least 1; at 0 the packet is discarded. (IPv6 calls this field Hop Limit.)"),
 ("Which protocol carries error and diagnostic messages such as 'Time Exceeded'?", ["ICMP", "UDP", "ARP", "BGP"], 0,
  "ICMP reports problems and supports tools like ping and traceroute. ICMP errors may be filtered or rate-limited."),
 ("Dijkstra's algorithm computes:", ["Least-cost paths from one source using full-topology knowledge", "Paths using only neighbours' tables, with no topology map", "The MAC address of a host", "Packet checksums"], 0,
  "Dijkstra needs the whole weighted graph, which is what link-state protocols such as OSPF flood to every router."),
 ("Which pairing is correct?", ["OSPF = link-state, RIP = distance-vector", "OSPF = distance-vector, RIP = link-state", "Both are path-vector", "Both are link-state"], 0,
  "OSPF is link-state (each router runs SPF/Dijkstra); RIP is distance-vector (routers exchange distance tables with neighbours)."),
 ("What is BGP used for?", ["Routing between autonomous systems on the Internet", "Routing inside a single LAN switch", "Assigning IP addresses by DHCP", "Encrypting traffic"], 0,
  "BGP is the inter-domain (path-vector) protocol exchanging reachability between autonomous systems, driven by policy."),
 ("In a virtual-circuit network, compared with a datagram network:", ["A path is set up first and packets carry a circuit identifier", "Every packet is routed independently by full destination address", "No router keeps any state", "Packets never share links"], 0,
  "Virtual circuits set up a path and keep per-connection state in routers. Datagram networks (like IP) route each packet independently."),
]

# ---------------- ICMP scenarios ----------------
SCENARIOS = {
 "1. Successful delivery": dict(steps=["PC-A sends packet (TTL 64)", "R1 forwards (TTL 63)", "R2 forwards (TTL 62)", "PC-B receives packet"], ok=True,
   explain="Each router looked up the destination and forwarded the packet, decrementing TTL. IP does not guarantee delivery, but here it worked.",
   icmp="No ICMP error. With ping, the destination would answer with an ICMP Echo Reply (type 0).",
   real="This is the normal case behind a successful `ping`."),
 "2. TTL reaches zero": dict(steps=["PC-A sends packet (TTL 2)", "R1 forwards (TTL 1)", "R2 decrements TTL to 0 and drops it", "R2 may send ICMP Time Exceeded (type 11) to PC-A"], ok=False,
   explain="A router that decrements TTL to 0 must discard the packet. This stops packets from looping forever.",
   icmp="ICMP Time Exceeded (type 11, code 0). The error is not guaranteed to arrive: it may be filtered or rate-limited.",
   real="`tracert`/`traceroute` sends probes with TTL 1, 2, 3... and uses the Time Exceeded replies to discover each hop."),
 "3. Destination unreachable": dict(steps=["PC-A sends packet to PC-B", "R1, R2 forward it", "R3 cannot deliver to the destination subnet", "R3 may send ICMP Destination Unreachable (type 3) to PC-A"], ok=False,
   explain="The packet reached the right region, but the final router or host could not deliver it (for example host down or port unreachable).",
   icmp="ICMP Destination Unreachable (type 3) with a code such as host unreachable (1) or port unreachable (3). May be suppressed by firewalls.",
   real="`ping` may print 'Destination host unreachable' when such a message is received."),
 "4. No usable route": dict(steps=["PC-A sends packet to an unknown network", "R1 searches its forwarding table: no matching route, no default route", "R1 drops the packet", "R1 may send ICMP Destination Unreachable (network unreachable, code 0)"], ok=False,
   explain="With no matching entry and no default route, the router cannot choose a next hop and discards the packet.",
   icmp="ICMP Destination Unreachable, code 0 (network unreachable). Delivery of this message is not guaranteed.",
   real="Typical when a route is missing or a link failure removed the only path; check `route print` / `ip route`."),
}
