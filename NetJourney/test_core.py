"""Run with:  python test_core.py"""
import networkx as nx
from core import *

def main():
    c = DEFAULT_COSTS
    for s in NODES:
        for d in NODES:
            if s == d: continue
            p, cost = dijkstra(c, s, d)
            dist, prev, _ = bellman_ford(c, s)
            bp = bf_path(prev, s, d)
            assert dist[d] == cost, (s, d)
            assert path_cost(c, p) == cost and path_cost(c, bp) == cost
            assert nx.dijkstra_path_length(build_graph(c), s, d) == cost
    assert dijkstra(c, "PC-A", "PC-B") == (["PC-A", "R1", "R2", "R3", "R4", "PC-B"], 11)
    assert dijkstra_trace(c, "PC-A")[-1]["PC-B"] == 11
    h = build_header("192.168.1.10", "129.11.11.239", 64, "TCP", 1500)
    assert h["ihl"] == 5 and h["total_len"] >= h["header_bytes"] and h["payload"] == 1480
    for bad in [("300.1.1.1", "1.1.1.1", 64, "TCP", 100), ("1.1.1.1", "2.2.2.2", 256, "UDP", 100),
                ("1.1.1.1", "2.2.2.2", 64, "UDP", 19), ("1.1.1.1", "2.2.2.2", 64, "UDP", 70000), ("1.1.1.1", "2.2.2.2", 64, "XYZ", 100)]:
        try: build_header(*bad); raise SystemExit(f"should fail: {bad}")
        except ValueError: pass
    assert analyse_address("192.168.1.10")["binary"] == "11000000.10101000.00000001.00001010"
    assert analyse_address("2001:db8::1")["exploded"] == "2001:0db8:0000:0000:0000:0000:0000:0001"
    assert "error" in analyse_address("999.1.1.1") and "error" in analyse_address("hello")
    assert all(0 <= q[2] < len(q[1]) for q in QUIZ) and len(QUIZ) >= 5
    print("All core tests passed.")
main()
