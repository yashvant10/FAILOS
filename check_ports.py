import socket

def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        try:
            s.connect((host, port))
            print(f"Port {port} is OPEN")
        except Exception as e:
            print(f"Port {port} is CLOSED or UNREACHABLE: {e}")

host = "db.nbsehwzthsezdswyttzq.supabase.co"
check_port(host, 6543)
check_port(host, 5432)
