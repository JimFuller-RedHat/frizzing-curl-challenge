import socket

# A dumb server that sends garbage to try and confuse curl

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8080))
s.listen(1)

print("Malicious server listening...")

while True:
    conn, addr = s.accept()

    # Send infinite stream of 'A's to try and overflow something
    try:
        conn.send(b"HTTP/1.1 200 OK\r\nContent-Length: 999999\r\n\r\n")
        conn.send(b"A" * 1000000)
    except:
        pass
    finally:
        conn.close()