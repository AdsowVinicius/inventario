"""
Servidor de produção para SPA (Single Page Application)
Redireciona todas as rotas para index.html para que o React Router funcione
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent / "dist"


class SPAHandler(http.server.SimpleHTTPRequestHandler):
    """Handler que serve arquivos estáticos e redireciona rotas para index.html"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_GET(self):
        # Caminho do arquivo requisitado
        path = self.path.split('?')[0]  # Remove query string
        file_path = DIRECTORY / path.lstrip('/')
        
        # Se o arquivo existe, serve normalmente
        if file_path.exists() and file_path.is_file():
            return super().do_GET()
        
        # Se é um diretório com index.html, serve o index
        if file_path.is_dir() and (file_path / 'index.html').exists():
            return super().do_GET()
        
        # Caso contrário, serve o index.html principal (SPA fallback)
        self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        # Adicionar headers CORS para desenvolvimento
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()


def main():
    # Verificar se o diretório dist existe
    if not DIRECTORY.exists():
        print(f"❌ Erro: Diretório '{DIRECTORY}' não encontrado!")
        print("   Execute 'npm run build' primeiro para gerar os arquivos de produção.")
        return
    
    # Verificar se index.html existe
    index_file = DIRECTORY / 'index.html'
    if not index_file.exists():
        print(f"❌ Erro: Arquivo '{index_file}' não encontrado!")
        print("   Execute 'npm run build' primeiro.")
        return
    
    print(f"📂 Servindo arquivos de: {DIRECTORY}")
    print(f"🌐 Frontend disponível em: http://0.0.0.0:{PORT}")
    print(f"   Acesse: http://localhost:{PORT}")
    print(f"   Ou na rede: http://<SEU_IP>:{PORT}")
    print()
    print("ℹ️  Todas as rotas serão redirecionadas para index.html (SPA mode)")
    print("   Pressione Ctrl+C para parar o servidor")
    print()
    
    with socketserver.TCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor encerrado.")


if __name__ == "__main__":
    main()
