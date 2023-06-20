import socket
import os
import threading

HOST = '172.18.185.44'
PORT = 8000

Diretoriodestino = r'C:\\Users\\elias\\OneDrive\\Área de Trabalho\\Testepservidor'
Tipospermitidos = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.otf', '.txt', '.html']

def requisicao(request):
    request_lines = request.split('\r\n')

    if request_lines:
        first_line = request_lines[0]
        parts = first_line.split(' ')

        if len(parts) == 3:
            metodo, path, protocolo = parts
        else:
            resposta = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<h1>Solicitação inválida</h1>'
            return resposta
    if metodo == 'GET':
        if path == '/':
            entries = os.listdir(Diretoriodestino)

            file_links = []
            for entry in entries:
                entry_path = os.path.join(Diretoriodestino, entry)
                if os.path.isfile(entry_path):
                    extension = os.path.splitext(entry)[1].lower()
                    if extension in Tipospermitidos:
                        file_links.append(f'<li><a href="/download/{entry}">{entry}</a></li>')

            conteudo_resposta = f'''
            <html>
            <body>
                <h1>Arquivos a Serem Visualizados</h1>
                <ul>
                    {''.join(file_links)}
                </ul>
            </body>
            </html>
            '''

            resposta = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(conteudo_resposta)}\r\n\r\n{conteudo_resposta}'
        elif path.startswith('/download/'):
            nome_arquivo = path.split('/')[-1]
            lista_links = os.path.join(Diretoriodestino, nome_arquivo)

            if os.path.isfile(lista_links):
                resposta = f'HTTP/1.1 200 OK\r\nContent-Disposition: attachment; filename={nome_arquivo}\r\n\r\n'
            else:
                resposta = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>Arquivo não encontrado</h1>'
        elif path == '/HEADER':
            cabecalhos = '\r\n'.join(request_lines[1:])
            resposta = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{cabecalhos}'
        else:
            resposta = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>path inválido</h1>'
    else:
        resposta = 'HTTP/1.1 405 metodo Not Allowed\r\nContent-Type: text/html\r\n\r\n<h1>Método não permitido</h1>'

    return resposta

def handle_client(client_socket, client_address):
    print(f'Conexão estabelecida: {client_address[0]}:{client_address[1]}')

    requisitar_dados = client_socket.recv(1024).decode('utf-8')
    print(f'Dados da solicitação:\n{requisitar_dados}')

    resposta = requisicao(requisitar_dados)

    client_socket.sendall(resposta.encode('utf-8'))

    if resposta.startswith('HTTP/1.1 200 OK\r\nContent-Disposition: attachment; filename='):
        nome_arquivo = resposta.split('\r\n\r\n')[0].split('filename=')[1]
        lista_links = os.path.join(Diretoriodestino, nome_arquivo)

        if os.path.isfile(lista_links):
            with open(lista_links, 'rb') as file:
                file_data = file.read()

            client_socket.sendall(file_data)

    client_socket.close()

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f'Servidor rodando em http://{HOST}:{PORT}')

        conexoes = []

        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

            conexoes.append(client_thread)

        for client_thread in conexoes:
            client_thread.join()

        print(f'Conexões ativas: {len(conexoes)}')
        for client_thread in conexoes:
            client_socket = client_thread.args[0]
            print(f'Conexão: {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}')

run()
