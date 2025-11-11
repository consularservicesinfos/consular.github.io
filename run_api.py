import os
import sys
from App import app

def find_available_port(start_port=5000, max_port=5010):
    """Trouve un port disponible"""
    import socket
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port

if __name__ == '__main__':
    port = find_available_port(5000)
    print(f"🚀 Démarrage de l'API Consular Services sur le port {port}...")
    print(f"📧 URL de l'API: http://127.0.0.1:{port}")
    print(f"🔍 Health check: http://127.0.0.1:{port}/api/health")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Essayez de fermer les applications utilisant le port 5000-5010")