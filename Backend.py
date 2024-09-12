from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS
from datetime import date
import random
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

def conexao():
    try:
        con_BD = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Gr@n0300',
            database='Plataforma_de_vendas_de_jogos_online'
        )
        if con_BD.is_connected():
            print("A conexão foi um sucesso!")
            return con_BD
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None
    


#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Jogo
#-----------------------------------------------------------------------------------------------------------------------------
#Adiciona o jogo ao banco

# Defina o caminho para o diretório de uploads
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verifique se o diretório existe, e se não existir, crie-o
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_game', methods=['POST'])
def add_game():
    if 'capa' not in request.files:
        return jsonify({"message": "Nenhum arquivo de capa enviado!"}), 400
    
    file = request.files['capa']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        capa_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        data = request.form
        db = conexao()
        if db:
            try:
                cursor = db.cursor()
                query = """INSERT INTO Jogo (idJogo, Descrição, Titulo, Categoria, Data_Lancamento, Capa, Processador, Memoria_RAM, Placa_de_Vídeo, Armazenamento)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (random.randint(1, 10000), data['descricao'], data['titulo'], data['categoria'], data['dataLancamento'], capa_url, data['processador'], data['memoriaRAM'], data['placaVideo'], data['armazenamento'])
                cursor.execute(query, values)

                db.commit()
                return jsonify({"message": "Jogo adicionado com sucesso!"}), 201
            except Error as e:
                db.rollback()
                return jsonify({"message": f"Falha ao adicionar jogo: {e}"}), 500
            finally:
                cursor.close()
                db.close()
        else:
            return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

#Faz a leitura dos jogos no sistema
@app.route('/get_games', methods=['GET'])
def get_games():
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT idJogo, Titulo, Descrição FROM jogo")  # Ajuste os nomes das colunas conforme sua tabela
            games = cursor.fetchall()
            game_list = [{"id": game[0], "title": game[1], "description": game[2]} for game in games]
            return jsonify(game_list), 200
        except Error as e:
            return jsonify({"message": f"Falha ao listar jogos: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

#Garante que  jogo se conecte ao usuario que acabou de pegar ele
@app.route('/buy_game', methods=['POST'])
def buy_game():
    db = conexao()
    if db:
        try:
            data = request.json
            user_id = data['user_id']
            game_id = data['game_id']
            
            cursor = db.cursor()
            print(f"Usuário: {user_id}, Jogo: {game_id}")  # Verifica se os dados estão corretos

            query = "INSERT INTO usuário_possui_jogo (ID_Usuário, ID_Jogo) VALUES (%s, %s)"
            cursor.execute(query, (user_id, game_id))
            db.commit()
            
            return jsonify({"message": "Compra registrada com sucesso!"}), 200
        except Error as e:
            return jsonify({"message": f"Falha ao registrar compra: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

#Procura os jogos do usuário
@app.route('/get_user_games/<int:user_id>', methods=['GET'])
def get_user_games(user_id):
    db = conexao()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT Jogo.idJogo, Jogo.Titulo, Jogo.Descrição
                FROM usuário_possui_jogo
                JOIN Jogo ON usuário_possui_jogo.ID_Jogo = Jogo.idJogo
                WHERE usuário_possui_jogo.ID_Usuário = %s
            """
            cursor.execute(query, (user_id,))
            user_games = cursor.fetchall()
            
            return jsonify(user_games), 200
        except Error as e:
            return jsonify({"message": f"Falha ao buscar jogos do usuário: {e}"}), 500
        finally:
            cursor.close()
            db.close()
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

#Serv para remover o jogo so sistema   
def deletar_jogo(db, idJogo): 
    try:
        cursor = db.cursor()
        sql = """
        DELETE FROM jogo
        WHERE idJogo = %s
        """
        cursor.execute(sql, (idJogo,))
        db.commit()
        print("Jogo deletado com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar jogo: {e}")
    finally:
        db.close()

#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Biblioteca_de_Jogos
#-----------------------------------------------------------------------------------------------------------------------------

def inserir_biblioteca_jg(db, idBiblioteca_de_Jogos, Status_Instalação, Data_de_Adição):
    try:
        cursor = db.cursor()
        
        sql = """
        INSERT INTO biblioteca_de_jogos (idBiblioteca_de_Jogos, Status_Instalação, Data_de_Adição)
        VALUES (%s, %s, %s)
        """
        valores = (idBiblioteca_de_Jogos, Status_Instalação, Data_de_Adição)
        cursor.execute(sql, valores)
        db.commit()
        print("Biblioteca de jogos feita com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao fazer a biblioteca de jogos: {e}")
    finally:
        cursor.close()

def deletar_biblioteca_jg(db, idBiblioteca_de_Jogos): 
    try:
        cursor = db.cursor()
        sql = "DELETE FROM biblioteca_de_jogos WHERE idBiblioteca_de_Jogos = %s"
        cursor.execute(sql, (idBiblioteca_de_Jogos,))
        db.commit()
        print("Biblioteca deletada com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar a biblioteca: {e}")
    finally:
        cursor.close()
#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Perfil_Usuário
#-----------------------------------------------------------------------------------------------------------------------------

def inserir_perfil_usuario(db, idPerfil_Usuário, caminho_foto_perfil, Biografia, Localização):
    try:
        cursor = db.cursor()
        
        Foto_perfil = None
        
        if isinstance(caminho_foto_perfil, str) and caminho_foto_perfil.strip():
            try:
                with open(caminho_foto_perfil, 'rb') as file:
                    Foto_perfil = file.read()
            except (FileNotFoundError, OSError):
                print(f"Arquivo de imagem não encontrado ou erro ao abrir o arquivo: {caminho_foto_perfil}. Inserindo valor None para Foto_perfil.")
        else:
            print("Caminho da foto de perfil inválido ou não fornecido. Inserindo valor None para Foto_perfil.")
        
        sql = """
        INSERT INTO perfil_usuário (idPerfil_Usuário, Foto_perfil, Biografia, Localização)
        VALUES (%s, %s, %s, %s)
        """
        valores = (idPerfil_Usuário, Foto_perfil, Biografia, Localização)
        cursor.execute(sql, valores)
        db.commit()
        print("Perfil do usuário inserido com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao inserir perfil do usuário: {e}")
    finally:
        cursor.close()

def deletar_perfil_usuario(db, idPerfil_Usuário):
    try:
        cursor = db.cursor()
        sql = "DELETE FROM perfil_usuário WHERE idPerfil_Usuário = %s"
        cursor.execute(sql, (idPerfil_Usuário,))
        db.commit()
        print("Perfil do usuário deletado com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar perfil do usuário: {e}")
    finally:
        cursor.close()
    
#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Loja
#-----------------------------------------------------------------------------------------------------------------------------

def inserir_loja(db, idLoja, Preço, ID_Jogo):
    try:
        cursor = db.cursor()
        
        sql = """
        INSERT INTO loja (idLoja, Preço, ID_Jogo)
        VALUES (%s, %s, %s)
        """
        valores = (idLoja, Preço, ID_Jogo)
        cursor.execute(sql, valores)
        db.commit()
        print("Loja inserido com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao inserir loja: {e}")
    finally:
        cursor.close()

def deletar_loja(db, idLoja):
    try:
        cursor = db.cursor()
        
        sql = "DELETE FROM loja WHERE idLoja = %s"
        valores = (idLoja,)
        cursor.execute(sql, valores)
        db.commit()
        print("Loja deletada com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar loja: {e}")
    finally:
        cursor.close()

#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Carrinho_de_Compras
#-----------------------------------------------------------------------------------------------------------------------------

def inserir_carrinho_compras(db, idCarrinho_de_Compras, Data_de_Adição, Quantidade, ID_Loja):
    try:
        cursor = db.cursor()
        
        id_jogo_random = random.randint(1,5)
        inserir_loja(db, ID_Loja, 'R$0,00', id_jogo_random)
        
        sql = """
        INSERT INTO carrinho_de_compras (idCarrinho_de_Compras, Data_de_Adição, Quantidade, ID_Loja)
        VALUES (%s, %s, %s, %s)
        """
        valores = (idCarrinho_de_Compras, Data_de_Adição, Quantidade, ID_Loja)
        cursor.execute(sql, valores)
        db.commit()
        print("Carrinho inserido com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao inserir carrinho: {e}")
    finally:
        cursor.close()

def deletar_carrinho(db, idCarrinho_de_Compras): 
    try:
        cursor = db.cursor()
        
        # Seleciona o ID_Loja do carrinho de compras
        cursor.execute("SELECT ID_Loja FROM carrinho_de_compras WHERE idCarrinho_de_Compras = %s", (idCarrinho_de_Compras,))
        id_loja = cursor.fetchone()[0]
        
        # Deleta a loja correspondente
        deletar_loja(db, id_loja)
        
        # Deleta o carrinho de compras
        sql = "DELETE FROM carrinho_de_compras WHERE idCarrinho_de_Compras = %s"
        cursor.execute(sql, (idCarrinho_de_Compras,))
        db.commit()
        print("Carrinho deletado com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar o carrinho: {e}")
    finally:
        cursor.close()

#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Relação do usuário com o jogo
#-----------------------------------------------------------------------------------------------------------------------------

def deletar_relacao_usu_jogo(db, idUsuario): 
    try:
        cursor = db.cursor()
        sql = "DELETE FROM usuário_possui_jogo WHERE ID_Usuário = %s"
        cursor.execute(sql, (idUsuario,))
        db.commit()
        print("Relação de usuário com jogos deletada com sucesso.")
    except Error as e:
        db.rollback()
        print(f"Erro ao deletar a relação de usuário com jogos: {e}")
    finally:
        cursor.close()


#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Usuário
#-----------------------------------------------------------------------------------------------------------------------------

# Rota para adicionar usuário
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    db = conexao()
    if db:
        try:
            cursor = db.cursor()

            id_biblioteca = random.randint(1, 10000)
            id_perfil_usuario = random.randint(1, 10000)
            id_carrinho_compras = random.randint(1, 10000)
            id_loja_random = random.randint(1, 10000)
            data_cadastro = date.today()
            inserir_biblioteca_jg(db, id_biblioteca, 0, data_cadastro)
            inserir_perfil_usuario(db, id_perfil_usuario, "None", "Biografia", "Localização")
            inserir_carrinho_compras(db, id_carrinho_compras, data_cadastro, 1, id_loja_random)

            cursor.execute("INSERT INTO usuário (idUsuario, Data_Nascimento, Nome, Data_Cadastro, Email, Telefone, ID_Biblioteca, ID_Perfil_Usuário, ID_Carrinho_de_Compras) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (data['id'], data['birthdate'], data['name'], data_cadastro, data['email'], data['phone'], id_biblioteca, id_perfil_usuario, id_carrinho_compras))
            db.commit()
            print("Usuário adicionado com sucesso.")
            return jsonify({"message": "Usuário adicionado com sucesso!"}), 201
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao adicionar usuário: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500
    
# Rota para listar usuários
@app.route('/get_users', methods=['GET'])
def get_users():
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT idUsuario, Nome, Email, Data_Nascimento, Telefone FROM usuário")
            users = cursor.fetchall()
            users_list = [{"id": user[0], "name": user[1], "email": user[2], "birthdate": user[3], "phone": user[4]} for user in users]
            return jsonify(users_list), 200
        except Error as e:
            return jsonify({"message": f"Falha ao listar usuários: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

# Rota para editar usuário
@app.route('/edit_user/<int:id>', methods=['PUT'])
def edit_user(id):
    data = request.get_json()
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("UPDATE usuário SET Nome = %s, Email = %s, Data_Nascimento = %s, Telefone = %s WHERE idUsuario = %s", 
                           (data['name'], data['email'], data['birthdate'], data['phone'], id))
            db.commit()
            return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao atualizar usuário: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500


# Rota para deletar usuário
@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT ID_Biblioteca, ID_Perfil_Usuário, ID_Carrinho_de_Compras FROM usuário WHERE idUsuario = %s", (id,))
            result = cursor.fetchone()

            if result:
                id_biblioteca, id_perfil_usuario, id_carrinho_compras = result

                deletar_relacao_usu_jogo(db, id)

                # Deletar o usuário primeiro
                cursor.execute("DELETE FROM usuário WHERE idUsuario = %s", (id,))
                db.commit()

                # Deletar as chaves estrangeiras associadas
                deletar_biblioteca_jg(db, id_biblioteca)
                deletar_perfil_usuario(db, id_perfil_usuario)
                deletar_carrinho(db, id_carrinho_compras)
                

                return jsonify({"message": "Usuário deletado com sucesso!"}), 200
            else:
                return jsonify({"message": "Usuário não encontrado."}), 404
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao deletar usuário: {e}"}), 500
        finally:
            cursor.close()
            db.close()
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Desenvolvedor
#-----------------------------------------------------------------------------------------------------------------------------

# Rota para adicionar desenvolvedor
@app.route('/add_developer', methods=['POST'])
def add_developer():
    data = request.get_json()
    db = conexao()
    if db:
        try:
            cursor = db.cursor()

            id_perfil_desenvolvedor = random.randint(1,100000)
            inserir_perfil_usuario(db, id_perfil_desenvolvedor, "None", "Biografia", "Localização")

            cursor.execute(
                "INSERT INTO Desenvolvedor (idDesenvolvedor, Nome, Telefone, Email, ID_Perfil_Usuário) VALUES (%s, %s, %s, %s, %s)",
                (data['id'], data['name'], data['phone'], data['email'], id_perfil_desenvolvedor)
            )
            db.commit()
            print("Desenvolvedor adicionado com sucesso.")
            return jsonify({"message": "Desenvolvedor adicionado com sucesso!"}), 201
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao adicionar desenvolvedor: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500


# Rota para listar desenvolvedores
@app.route('/get_developers', methods=['GET'])
def get_developers():
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT idDesenvolvedor, Nome, Telefone, Email FROM Desenvolvedor")
            developers = cursor.fetchall()
            developers_list = [{"idDesenvolvedor": dev[0], "Nome": dev[1], "Telefone": dev[2], "Email": dev[3]} for dev in developers]
            return jsonify(developers_list), 200
        except Error as e:
            return jsonify({"message": f"Falha ao listar desenvolvedores: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

# Rota para editar desenvolvedor
@app.route('/edit_developer/<int:id>', methods=['PUT'])
def edit_developer(id):
    data = request.get_json()
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE Desenvolvedor SET Nome = %s, Telefone = %s, Email = %s WHERE idDesenvolvedor = %s",
                (data['name'], data['phone'], data['email'], id)
            )
            db.commit()
            return jsonify({"message": "Desenvolvedor atualizado com sucesso!"}), 200
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao atualizar desenvolvedor: {e}"}), 500
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500

@app.route('/delete_developer_game/<int:developer_id>', methods=['DELETE'])
def delete_developer_game(developer_id):
    db = conexao()  # Função que faz a conexão com o banco de dados
    if db:
        try:
            cursor = db.cursor()
            sql = "DELETE FROM Deselvolvedor_possui_Jogo WHERE ID_Desenvolvedor = %s"
            cursor.execute(sql, (developer_id,))
            db.commit()
            print("Relação de desenvolvedor com jogos deletada com sucesso.")
            return jsonify({"message": "Relação de desenvolvedor com jogos deletada com sucesso."}), 200
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Erro ao deletar a relação de desenvolvedor com jogos: {e}"}), 500
        finally:
            cursor.close()
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500


# Rota para deletar desenvolvedor
@app.route('/delete_developer/<int:id>', methods=['DELETE'])
def delete_developer(id):
    db = conexao()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT ID_Perfil_Usuário FROM Desenvolvedor WHERE idDesenvolvedor = %s", (id,))
            result = cursor.fetchone()

            if result:
                id_perfil_usuario = result[0]

                delete_developer_game(db, id)

                cursor.execute("DELETE FROM Desenvolvedor WHERE idDesenvolvedor = %s", (id,))
                db.commit()

                deletar_perfil_usuario(db, id_perfil_usuario)

                return jsonify({"message": "Desenvolvedor deletado com sucesso!"}), 200
            else:
                return jsonify({"message": "Desenvolvedor não encontrado."}), 404
        except Error as e:
            db.rollback()
            return jsonify({"message": f"Falha ao deletar desenvolvedor: {e}"}), 500
        finally:
            cursor.close()
            db.close()
    else:
        return jsonify({"message": "Falha na conexão com o banco de dados."}), 500


#-----------------------------------------------------------------------------------------------------------------------------
# Códigos Relação do desenvolvedor com o jogo
#-----------------------------------------------------------------------------------------------------------------------------



@app.route('/add_developer_game', methods=['POST'])
def add_developer_game():
    data = request.get_json()
    developer_id = data.get('developer_id')
    game_id = data.get('game_id')

    if not developer_id or not game_id:
        return jsonify({"error": "Missing developer_id or game_id"}), 400

    conn = conexao()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Desenvolvedor_possui_Jogo (ID_Desenvolvedor, ID_Jogo) VALUES (%s, %s)",
            (developer_id, game_id)
        )
        conn.commit()
        return jsonify({"message": "Developer and game associated successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/getDeveloperGames/<int:developer_id>', methods=['GET'])
def get_developer_games(developer_id):
    conn = conexao()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT Jogo.* FROM Jogo "
            "JOIN Desenvolvedor_possui_Jogo ON Jogo.idJogo = Desenvolvedor_possui_Jogo.ID_Jogo "
            "WHERE Desenvolvedor_possui_Jogo.ID_Desenvolvedor = %s",
            (developer_id,)
        )
        games = cursor.fetchall()
        return jsonify(games), 200
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
