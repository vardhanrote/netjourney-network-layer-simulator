"""NetJourney - Interactive Network Layer Simulator (educational simulation only)."""
import random
import plotly.graph_objects as go
import streamlit as st
from core import *

st.set_page_config(page_title="NetJourney", page_icon="🌐", layout="wide")
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#0a1428 0%,#0d1f3c 100%);color:#e6f1ff}
[data-testid=stSidebar]{background:#081022;border-right:1px solid #16315a}
h1,h2,h3{color:#e6f1ff!important}
.brand{font-size:2.6rem;font-weight:800;background:linear-gradient(90deg,#22d3ee,#14b8a6,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{letter-spacing:.25em;color:#22d3ee;font-size:.8rem;font-weight:600}
.card{background:#0f2447;border:1px solid #1e4079;border-radius:16px;padding:18px 20px;margin-bottom:12px}
.card h4{color:#22d3ee;margin:0 0 6px 0}.card p{color:#b8c9e6;margin:0;font-size:.93rem}
.note{background:#0b2a3a;border-left:4px solid #14b8a6;border-radius:8px;padding:10px 14px;color:#cfe8f3;margin:8px 0;font-size:.9rem}
.warn{background:#2a2410;border-left:4px solid #f59e0b;border-radius:8px;padding:10px 14px;color:#f7e6bd;margin:8px 0;font-size:.9rem}
[data-testid=stMetric]{background:#0f2447;border:1px solid #1e4079;border-radius:14px;padding:10px 14px}
.step{display:inline-block;background:#0f2447;border:1px solid #22d3ee;border-radius:12px;padding:8px 12px;margin:4px;color:#e6f1ff;font-size:.88rem}
.bad{border-color:#f87171}
</style>""", unsafe_allow_html=True)


def card(t, p): st.markdown(f"<div class='card'><h4>{t}</h4><p>{p}</p></div>", unsafe_allow_html=True)
def note(t): st.markdown(f"<div class='note'>ℹ️ {t}</div>", unsafe_allow_html=True)
def warn(t): st.markdown(f"<div class='warn'>⚠️ {t}</div>", unsafe_allow_html=True)
def header(t, s): st.markdown(f"<div class='sub'>NETWORK LAYER · UNIT 4</div><h1>{t}</h1><p style='color:#9db4d6'>{s}</p>", unsafe_allow_html=True)


def fig_graph(costs, path=(), current=None, visited=(), height=430):
    pe = {frozenset(e) for e in zip(path, path[1:])}
    f = go.Figure()
    for (a, b), c in costs.items():
        hot = frozenset((a, b)) in pe
        f.add_trace(go.Scatter(x=[POS[a][0], POS[b][0]], y=[POS[a][1], POS[b][1]], mode="lines", hoverinfo="skip",
                               line=dict(width=6 if hot else 2, color="#22d3ee" if hot else "#35568f"), showlegend=False))
    f.add_trace(go.Scatter(x=[(POS[a][0] + POS[b][0]) / 2 for a, b in costs], y=[(POS[a][1] + POS[b][1]) / 2 for a, b in costs],
                           mode="text", text=[f"<b>{c}</b>" for c in costs.values()], textfont=dict(color="#fbbf24", size=14), hoverinfo="skip", showlegend=False))
    col = ["#f59e0b" if n == current else "#14b8a6" if n in visited else "#3b82f6" if n.startswith("R") else "#8b5cf6" for n in NODES]
    f.add_trace(go.Scatter(x=[POS[n][0] for n in NODES], y=[POS[n][1] for n in NODES], mode="markers+text", text=NODES, textposition="bottom center",
                           textfont=dict(color="#e6f1ff", size=13), marker=dict(size=[44 if n == current else 34 for n in NODES], color=col, line=dict(width=2, color="#e6f1ff")),
                           hovertext=[f"{n}<br>{NODE_IPS[n]}" for n in NODES], hoverinfo="text", showlegend=False))
    f.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(visible=False, range=[-0.5, 5.5]), yaxis=dict(visible=False, range=[-0.7, 2.6]))
    return f


# ---------- sidebar ----------
PAGES = ["🏠 Home", "A · Packet Journey", "B · IP Packet Explorer", "C · Routing Lab", "D · IPv4/IPv6 Lab", "E · ICMP & Troubleshooting", "F · Quiz", "G · Reference"]
st.sidebar.markdown("<div class='brand' style='font-size:1.6rem'>NetJourney</div><div class='sub'>NETWORK LAYER · UNIT 4</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", PAGES, key="nav")
with st.sidebar.expander("⚙️ Link costs (shared by Modules A & C)"):
    costs = {}
    for (a, b), d in DEFAULT_COSTS.items():
        costs[(a, b)] = st.number_input(f"{a} ↔ {b}", 1, 20, d, key=f"cost_{a}_{b}")
    st.caption("Costs are illustrative units, not measured delay.")
st.sidebar.caption("All demonstrations are simulated. No real packets are sent.")


def pick_pair(key):
    c1, c2 = st.columns(2)
    s = c1.selectbox("Source", NODES, 0, key=f"s{key}")
    d = c2.selectbox("Destination", NODES, len(NODES) - 1, key=f"d{key}")
    return s, d


# ---------- HOME ----------
if page == PAGES[0]:
    st.markdown("<div class='sub'>NETWORK LAYER · UNIT 4</div><div class='brand'>NetJourney</div>", unsafe_allow_html=True)
    st.markdown("#### Follow a packet from source to destination, hop by hop.")
    st.write("The **network layer** (Layer 3) moves packets across many networks. It gives hosts logical (IP) addresses, "
             "**forwards** each packet at every router using its destination address, and uses **routing** algorithms to fill the forwarding tables. "
             "IP is *best-effort*: it does not guarantee delivery, ordering, or timing.")
    warn("Everything here is an educational simulation. It does not capture real packets, read real routing tables, or implement full OSPF, RIP or BGP.")
    mods = [("A · Packet Journey", "Step a packet along the least-cost path through routers."), ("B · IP Packet Explorer", "Build and explain an IPv4 header with a real checksum."),
            ("C · Routing Lab", "Dijkstra vs Bellman-Ford on an adjustable network."), ("D · IPv4/IPv6 Lab", "Validate addresses; see binary and expanded forms."),
            ("E · ICMP & Troubleshooting", "Simulated TTL expiry and unreachable scenarios."), ("F · Quiz", "9 questions with scoring and explanations."),
            ("G · Reference", "Concise notes and glossary.")]
    cols = st.columns(3)
    for i, (t, d) in enumerate(mods):
        with cols[i % 3]: card(t, d)
    st.info("Use the sidebar on the left to open any module.")

# ---------- A ----------
elif page == PAGES[1]:
    header("Interactive Packet Journey", "Least-cost path and step-by-step forwarding (simulated).")
    src, dst = pick_pair("A")
    if src == dst:
        st.warning("Choose different source and destination."); st.stop()
    path, total = dijkstra(costs, src, dst)
    hops = len(path) - 1
    step = st.slider("Journey step", 0, hops, 0, key="stepA")
    cur = path[step]
    routers_passed = sum(1 for n in path[1:step + 1] if n.startswith("R"))
    ttl = 64 - routers_passed
    status = ("Created at source" if step == 0 else "Delivered to destination" if step == hops else f"In transit - being forwarded by {cur}")
    st.plotly_chart(fig_graph(costs, path, cur, path[:step]), use_container_width=True)
    m = st.columns(5)
    m[0].metric("Current node", cur); m[1].metric("Hop", f"{step} / {hops}"); m[2].metric("Hops remaining", hops - step)
    m[3].metric("Route cost", total); m[4].metric("Simulated TTL", ttl)
    st.success(f"**Status:** {status}")
    st.markdown("**Route:** " + " → ".join(f"**{n}**" if n == cur else n for n in path))
    if step == 0:
        st.write(f"**Source ({cur}, {NODE_IPS[cur]})** builds an IP packet with destination address {NODE_IPS[dst]} and hands it to its next hop, {path[1]}.")
    elif step == hops:
        st.write(f"**Destination ({cur})** sees that the destination address is its own, accepts the packet and passes the payload up to the transport layer.")
    else:
        st.write(f"**Router {cur}** receives the packet, decrements TTL, looks up destination {NODE_IPS[dst]} in its forwarding table and sends it to next hop **{path[step + 1]}**.")
    note("Link costs are illustrative units chosen for teaching. They are not measured Internet latency. Change them in the sidebar and the path updates.")
    note("Real routers forward using longest-prefix match on the destination IP address; this simulation shows only the resulting next hop.")

# ---------- B ----------
elif page == PAGES[2]:
    header("IP Packet Explorer", "Build an illustrative IPv4 header (no packet is sent).")
    c1, c2 = st.columns(2)
    src = c1.text_input("Source IPv4", "192.168.1.10"); dst = c2.text_input("Destination IPv4", "129.11.11.239")
    c3, c4, c5 = st.columns(3)
    ttl = c3.number_input("TTL", 0, 255, 64); proto = c4.selectbox("Protocol", list(PROTO)); size = c5.number_input("Total packet size (bytes)", 20, 65535, 1500)
    try:
        h = build_header(src, dst, int(ttl), proto, int(size))
    except ValueError as e:
        st.error(str(e)); st.stop()
    rows = [("Version", h["version"], "IP version; 4 for IPv4."),
            ("Header length (IHL)", f"{h['ihl']} words = {h['header_bytes']} bytes", "Header length in 32-bit words. No options are used here, so the minimum of 5."),
            ("Total length", f"{h['total_len']} bytes", f"Header + payload; payload here = {h['payload']} bytes."),
            ("Identification", f"0x{h['ident']:04X} (illustrative)", "Identifies fragments of one datagram. Fixed example value."),
            ("Flags / Fragment offset", "DF set / 0", "Don't Fragment; no fragmentation in this example."),
            ("TTL", h["ttl"], "Decremented by each forwarding router; packet dropped at 0. (IPv6 calls it Hop Limit.)"),
            ("Protocol", f"{h['proto_name']} ({h['proto_num']})", "Tells the receiver which upper-layer protocol is in the payload."),
            ("Header checksum", f"0x{h['checksum']:04X}", "Computed with the real one's-complement algorithm over the 20-byte header. Routers recompute it after changing TTL."),
            ("Source address", h["src"], "Sender's IPv4 address."), ("Destination address", h["dst"], "Used by routers for forwarding decisions.")]
    st.dataframe([{"Field": a, "Value": str(b), "Meaning": c} for a, b, c in rows], use_container_width=True, hide_index=True)
    st.code(h["hex"], language="text")
    note("The hex above is a header built for illustration. Type of service, options and real fragmentation are not simulated; nothing is transmitted.")

# ---------- C ----------
elif page == PAGES[3]:
    header("Routing Algorithms Lab", "Dijkstra and Bellman-Ford on the sample network (change costs in the sidebar).")
    src, dst = pick_pair("C")
    if src == dst:
        st.warning("Choose different source and destination."); st.stop()
    dp, dc = dijkstra(costs, src, dst)
    dist, prev, rounds = bellman_ford(costs, src)
    bp = bf_path(prev, src, dst)
    a, b = st.columns(2)
    a.markdown("##### Dijkstra (link-state style)"); a.plotly_chart(fig_graph(costs, dp, height=330), use_container_width=True, key="fd")
    a.write(f"Path: {' → '.join(dp)}  |  **Cost: {dc}**")
    b.markdown("##### Bellman-Ford (distance-vector style)"); b.plotly_chart(fig_graph(costs, bp, height=330), use_container_width=True, key="fb")
    b.write(f"Path: {' → '.join(bp)}  |  **Cost: {dist[dst]}**")
    (st.success if dc == dist[dst] else st.error)("Both algorithms give the same least cost." if dc == dist[dst] else "Costs differ (unexpected).")
    if dp != bp: note("Equal-cost ties can give different but equally good paths.")
    t1, t2 = st.tabs(["Dijkstra steps", "Bellman-Ford rounds"])
    t1.dataframe(dijkstra_trace(costs, src), use_container_width=True, hide_index=True)
    t2.dataframe([{"Round": i, **{n: ("∞" if r[n] == float("inf") else r[n]) for n in NODES}} for i, r in enumerate(rounds)], use_container_width=True, hide_index=True)
    warn("The Bellman-Ford here is a centralised, simplified mathematical demonstration. It is NOT an implementation of RIP: real RIP routers exchange distance vectors with neighbours periodically, with hop-count metric (max 15), timers and split-horizon.")
    st.markdown("""**Link-state vs distance-vector**
- **Link-state:** every router learns the whole topology (flooded link-state advertisements) and runs a shortest-path algorithm such as Dijkstra. **OSPF** is a link-state protocol.
- **Distance-vector:** each router knows only its neighbours and the distances they advertise, and updates its table iteratively (Bellman-Ford equation). **RIP** is a distance-vector protocol.""")

# ---------- D ----------
elif page == PAGES[4]:
    header("IPv4 and IPv6 Address Lab", "Validate and inspect addresses using Python's ipaddress module.")
    ex = st.selectbox("Examples", ["192.168.1.10", "129.11.11.239", "2001:db8::1", "(type your own)"])
    txt = st.text_input("Address", "" if ex.startswith("(") else ex, key=f"addr_{ex}")
    if txt:
        r = analyse_address(txt)
        if "error" in r: st.error(r["error"])
        elif r["version"] == 4:
            st.success("Valid IPv4 address"); st.write(f"Length: **32 bits** · 4 octets · type: {r['kind']}")
            st.write("Octets: " + " . ".join(map(str, r["octets"]))); st.code(r["binary"], language="text")
        else:
            st.success("Valid IPv6 address"); st.write(f"Length: **128 bits** · type: {r['kind']}")
            st.write("Expanded:"); st.code(r["exploded"], language="text"); st.write("Compressed:"); st.code(r["compressed"], language="text")
    st.markdown("##### IPv4 vs IPv6")
    st.dataframe([{"": "Address length", "IPv4": "32 bits", "IPv6": "128 bits"}, {"": "Notation", "IPv4": "Dotted decimal (192.168.1.10)", "IPv6": "Colon-hex, :: compresses zeros (2001:db8::1)"},
                  {"": "Address space", "IPv4": "~4.3 billion", "IPv6": "~3.4 × 10^38"}, {"": "TTL field", "IPv4": "Time to Live", "IPv6": "Hop Limit"},
                  {"": "Header checksum", "IPv4": "Yes", "IPv6": "No (removed)"}, {"": "Router fragmentation", "IPv4": "Allowed", "IPv6": "Not allowed (source only)"}], use_container_width=True, hide_index=True)

# ---------- E ----------
elif page == PAGES[5]:
    header("ICMP and Network Troubleshooting", "Simulated scenarios. No real traffic is sent.")
    name = st.selectbox("Scenario", list(SCENARIOS)); sc = SCENARIOS[name]
    st.markdown("".join(f"<span class='step {'bad' if (i == len(sc['steps']) - 1 and not sc['ok']) else ''}'>{i + 1}. {s}</span> →" for i, s in enumerate(sc["steps"]))[:-1], unsafe_allow_html=True)
    st.markdown("##### What happens at the network layer"); st.write(sc["explain"])
    st.markdown("##### ICMP"); st.write(sc["icmp"])
    st.markdown("##### Real-world connection"); st.write(sc["real"])
    warn("ICMP errors are not guaranteed: routers and firewalls may filter or rate-limit them, so the source may never see one. This page only simulates the events.")

# ---------- F ----------
elif page == PAGES[6]:
    header("Knowledge Quiz", f"{len(QUIZ)} multiple-choice questions.")
    st.session_state.setdefault("qround", 0)
    r = st.session_state.qround
    if f"order{r}" not in st.session_state:
        rng = random.Random(); st.session_state[f"order{r}"] = [rng.sample(range(len(q[1])), len(q[1])) for q in QUIZ]
    order = st.session_state[f"order{r}"]
    with st.form(f"quiz{r}"):
        picks = [st.radio(f"**Q{i + 1}. {q[0]}**", [q[1][j] for j in order[i]], index=None, key=f"q{r}_{i}") for i, q in enumerate(QUIZ)]
        done = st.form_submit_button("Submit answers")
    if done:
        score = 0
        for i, (q, p) in enumerate(zip(QUIZ, picks)):
            ok = p == q[1][q[2]]; score += ok
            (st.success if ok else st.error)(f"Q{i + 1}: {'Correct' if ok else 'Incorrect' if p else 'Unanswered'}. Answer: {q[1][q[2]]}. {q[3]}")
        st.markdown(f"### Score: {score} / {len(QUIZ)} ({100 * score // len(QUIZ)}%)")
        st.write("Excellent!" if score >= 8 else "Good work - review the reference page." if score >= 5 else "Keep practising - see Module G.")
        st.button("Retry quiz", on_click=lambda: st.session_state.update(qround=r + 1))

# ---------- G ----------
else:
    header("Network Layer Reference", "Concise notes for undergraduate students.")
    topics = [("Datagram networks", "Each packet is routed independently using its full destination address; routers keep no per-connection state. The Internet's IP works this way."),
              ("Virtual-circuit networks", "A path is set up before data flows; packets carry a circuit identifier and routers keep per-connection state (e.g. ATM, MPLS-style labels)."),
              ("IP", "Best-effort, connectionless delivery with logical addressing and forwarding. No guarantee of delivery, order or timing."),
              ("IPv4 and IPv6", "IPv4: 32-bit addresses, header checksum, TTL. IPv6: 128-bit addresses, simpler fixed header, Hop Limit, no router fragmentation."),
              ("ICMP", "Carries error reports and diagnostics (Echo, Time Exceeded, Destination Unreachable) used by ping and traceroute. Messages can be filtered."),
              ("Link-state routing", "Routers flood link information, build a full map and run Dijkstra to compute least-cost paths."),
              ("Distance-vector routing", "Routers share distance tables with neighbours and update iteratively using the Bellman-Ford equation."),
              ("RIP", "Distance-vector protocol using hop count (max 15) for small networks."),
              ("OSPF", "Link-state interior gateway protocol; routers run SPF (Dijkstra) over a link-state database, using areas for scalability."),
              ("BGP", "Path-vector, policy-based protocol that exchanges reachability between autonomous systems across the Internet.")]
    cols = st.columns(2)
    for i, (t, d) in enumerate(topics):
        with cols[i % 2]: card(t, d)
    st.markdown("##### Glossary")
    st.dataframe([{"Term": a, "Meaning": b} for a, b in [("Forwarding", "Moving a packet from an input port to the correct output port using the forwarding table."),
        ("Routing", "Computing the paths that populate forwarding tables."), ("TTL / Hop Limit", "Counter decremented per router hop to stop endless loops."),
        ("Autonomous System (AS)", "A network under one administrative control, identified by an AS number."), ("Next hop", "The adjacent router a packet is sent to next."),
        ("Link cost / metric", "Number a routing algorithm minimises (hops, bandwidth-based, etc.)."), ("MTU", "Largest packet a link can carry without fragmentation.")]], use_container_width=True, hide_index=True)
    st.markdown("##### Key takeaways\n- Forwarding is per-router and local; routing is the global computation behind it.\n- IP is best-effort; reliability comes from higher layers like TCP.\n- OSPF = link-state, RIP = distance-vector, BGP = between autonomous systems.")
