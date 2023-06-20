import socket
import os

HOST = 'localhost'
PORT = 8000

Diretoriodestino = r'C:\\Users\\elias\\OneDrive\\Área de Trabalho\\Testepservidor'
Tipospermitidos = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.otf', '.txt', '.html']

def requisicao(request):
    # Analisa a solicitação HTTP para obter o caminho do arquivo solicitado
    request_lines = request.split('\r\n')

    if request_lines:
        first_line = request_lines[0]
        parts = first_line.split(' ')

        if len(parts) == 3:
            method, path, protocol = parts
        else:
            # Gera uma resposta para solicitação inválida
            response = 'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<h1>Solicitação inválida</h1>'
            return response
    if method == 'GET':
        if path == '/':
            # Obtém a lista de arquivos no diretório especificado
            entries = os.listdir(Diretoriodestino)

            # Cria uma lista de links para os arquivos permitidos
            file_links = []
            for entry in entries:
                entry_path = os.path.join(Diretoriodestino, entry)
                if os.path.isfile(entry_path):
                    extension = os.path.splitext(entry)[1].lower()
                    if extension in Tipospermitidos:
                        file_links.append(f'<li><a href="/download/{entry}">{entry}</a></li>')

            # Gera a resposta HTML com os links de download dos arquivos
            response_content = f'''
            <html>
            <body>
                <h1>Arquivos Disponíveis para Download</h1>
                <ul>
                    {''.join(file_links)}
                </ul>
            </body>
            </html>
            '''

            # Gera a resposta HTTP
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(response_content)}\r\n\r\n{response_content}'
        elif path.startswith('/download/'):
            # Obtém o nome do arquivo solicitado
            file_name = path.split('/')[-1]
            file_path = os.path.join(Diretoriodestino, file_name)

            # Verifica se o arquivo existe no diretório especificado
            if os.path.isfile(file_path):
                # Gera a resposta HTTP com o cabeçalho de download
                response = f'HTTP/1.1 200 OK\r\nContent-Disposition: attachment; filename={file_name}\r\n\r\n'
            else:
                # Gera uma resposta para arquivo não encontrado
                response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>Arquivo não encontrado</h1>'
        elif path == '/HEADER':
            # Gera a resposta HTTP com o cabeçalho da requisição
            headers = '\r\n'.join(request_lines[1:])
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{headers}'
        else:
            # Gera uma resposta para caminho inválido
            response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>Caminho inválido</h1>'
    else:
        # Gera uma resposta para outros métodos HTTP não suportados
        response = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n<h1>Método não permitido</h1>'

    return response

def run():
    # Cria um soquete de servidor TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Aumentamos o valor para aceitar múltiplas conexões
        print(f'Servidor rodando em http://{HOST}:{PORT}')

        conexoes = []  # Lista para armazenar as conexões estabelecidas

        while True:
            # Aguarda e aceita uma conexão do cliente
            client_socket, client_address = server_socket.accept()
            print(f'Conexão estabelecida: {client_address[0]}:{client_address[1]}')

            # Adiciona a conexão à lista de conexões estabelecidas
            conexoes.append(client_socket)

            # Recebe os dados da solicitação do cliente
            requisitar_dados = client_socket.recv(1024).decode('utf-8')
            print(f'Dados da solicitação:\n{requisitar_dados}')

            # Processa a solicitação e obtém a resposta
            response = requisicao(requisitar_dados)

            # Envia a resposta ao cliente
            client_socket.sendall(response.encode('utf-8'))

            # Se o caminho de download foi solicitado, envia o arquivo
            if response.startswith('HTTP/1.1 200 OK\r\nContent-Disposition: attachment; filename='):
                file_name = response.split('\r\n\r\n')[0].split('filename=')[1]
                file_path = os.path.join(Diretoriodestino, file_name)

                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        file_data = file.read()

                    client_socket.sendall(file_data)

            # Encerra a conexão com o cliente
            client_socket.close()

            # Remove a conexão da lista após encerrá-la
            conexoes.remove(client_socket)

        # Exibe as conexões ativas no terminal
        print(f'Conexões ativas: {len(conexoes)}')
        for connection in conexoes:
            print(f'Conexão: {connection.getpeername()[0]}:{connection.getpeername()[1]}')

run()
