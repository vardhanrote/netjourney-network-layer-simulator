# NetJourney - Interactive Network Layer Simulator (NETWORK LAYER · UNIT 4)

An educational web app (Streamlit) that shows how packets travel through routers. **All demonstrations are simulated**: it does not capture real packets, read real routing tables, send ICMP, or implement complete OSPF/RIP/BGP.

## Features
- **A - Packet Journey:** network graph, source/destination choice, least-cost path, step slider, hop/cost/TTL/status, adjustable link costs
- **B - IP Packet Explorer:** validated IPv4 header with real checksum computation, field explanations
- **C - Routing Lab:** Dijkstra vs Bellman-Ford with step tables and highlighted paths
- **D - IPv4/IPv6 Lab:** validation with Python `ipaddress`, binary/expanded/compressed forms
- **E - ICMP & Troubleshooting:** 4 simulated scenarios
- **F - Quiz:** 9 questions, scoring, explanations, retry
- **G - Reference:** summary, glossary, takeaways

## Tech stack
Python 3.11 or 3.13, Streamlit, NetworkX, Plotly (+ standard library). Works offline after installing dependencies.

## Folder structure
```
NetJourney/
  app.py            # Streamlit interface
  core.py           # networking logic (routing, IPv4 header, quiz data)
  test_core.py      # logic tests (no Streamlit needed)
  requirements.txt
  README.md
  .gitignore
```

## Windows setup (PowerShell, in the extracted NetJourney folder)
1. Right-click `NetJourney.zip` > Extract All. Open VS Code > File > Open Folder > select `NetJourney`. Open a terminal (Ctrl+`).
2. Create a virtual environment:
   - Python 3.11: `py -3.11 -m venv .venv`
   - Python 3.13: `py -3.13 -m venv .venv`
3. Install dependencies: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
4. Run: `.\.venv\Scripts\python.exe -m streamlit run app.py`

The browser opens at http://localhost:8501. Stop with Ctrl+C.
Optional logic tests: `.\.venv\Scripts\python.exe test_core.py`

## Troubleshooting
- **Scripts disabled / activation error:** you do not need to activate; use the full `.\.venv\Scripts\python.exe` commands above.
- **`py` not recognised:** install Python from python.org and tick "Add to PATH", or use `python -m venv .venv`.
- **Version not found:** run `py -0` to list installed versions and use one of them (3.11 or 3.13).
- **Port in use:** add `--server.port 8502`.
- **Pinned package fails to install:** upgrade pip (`.\.venv\Scripts\python.exe -m pip install --upgrade pip`) and retry.
- **Browser does not open:** visit http://localhost:8501 manually.

## Upload to GitHub
```
git init
git add .
git commit -m "NetJourney network layer simulator"
git branch -M main
git remote add origin https://github.com/<your-username>/NetJourney.git
git push -u origin main
```
(Create the empty repository on github.com first. `.gitignore` already excludes `.venv` and caches.)

## Screenshots for your report
Open each module in the sidebar and press **Win + Shift + S** to capture the page. Suggested shots: Home, Packet Journey at step 0 / middle / end, IP header table, Routing Lab, Address Lab, ICMP scenario, Quiz result.

## Educational limitations
- Link costs are illustrative units, not measured latency.
- The Bellman-Ford demo is a centralised calculation, not RIP (no timers, neighbour exchange, split horizon).
- Dijkstra here is a shortest-path calculation, not full OSPF (no LSAs, areas, adjacencies).
- BGP is only described, not simulated.
- IPv4 headers are built for illustration (no options, fixed identification); nothing is transmitted.
- ICMP scenarios are scripted; in real networks ICMP errors may be filtered or rate-limited.
