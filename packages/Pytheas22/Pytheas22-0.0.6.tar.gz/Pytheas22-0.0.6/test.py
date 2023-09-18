data = [('192.168.0.1', ["53: Domain Name System (DNS). Translates an internet address into an address consisting of numbers \nThis is the website: ''Server:  UnKnown\\r' of this IP"]), ('192.168.0.2', ['62078: Lightning Connector Apple Device']), ('192.168.0.66', ['62078: Lightning Connector Apple Device']), ('192.168.0.233', ['62078: Lightning Connector Apple Device']), ('192.168.0.249', ['8001: Streaming \nThere might be a website: http://192.168.0.249:8001', '8002: Cisco Systems Unified Call Manager Intercluster\nThere might be a website: http://192.168.0.249:8002', '8080: HTTP alternativ\nThere might be a website: http://192.168.0.249:8080', '9080: Microsoft Groove Software', '9999: Communication'])]
idx = 0
for ip, port_lst in data:
    idx += 1
    print("".join("_" for _ in range(50)))
    print(f"[{idx}] {ip} open ports\n")
    for checking, each in enumerate(port_lst):
        print(each)
        if checking != port_lst.index(port_lst[-1]):
            print()
    print("".join("_" for _ in range(50)))
    print(f"\n\n")
