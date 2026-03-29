import socket

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"Port {port} is OPEN on {host}")
    else:
        print(f"Port {port} is CLOSED on {host} (Error: {result})")
    sock.close()

check_port("db.nbsehwzthsezdswyttzq.supabase.co", 5432)
check_port("db.nbsehwzthsezdswyttzq.supabase.co", 6543)
