import sqlite3
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)


def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection_pymysql():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='98760bcv',
        database='siteescolar'
    )


def create_users_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT UNIQUE NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()


def create_aluno_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS aluno (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nomeAluno VARCHAR(255) NOT NULL,
                        nomeMaeAluno VARCHAR(255),
                        nomePaiAluno VARCHAR(255),
                        cpfAluno VARCHAR(14) UNIQUE NOT NULL,
                        dataNascimentoAluno DATE,
                        emailAluno VARCHAR(255),
                        serieAluno VARCHAR(10),
                        turmaAluno VARCHAR(10),
                        senhaAluno VARCHAR(255)
                    )''')
    connection.commit()
    cursor.close()
    connection.close()


create_users_table()
create_aluno_table()


def get_user_by_username_or_cpf(cpf, username):
    """Obter usuario por cpf ou username"""
    if not (cpf or username):
        return
    conn = get_db_connection()
    try:
        user = conn.execute(
            'SELECT * FROM users WHERE cpf = ? OR username = ?',
            (cpf, username)
        ).fetchone()
        return dict(user)
    finally:
        conn.close()


# Rota para a página de cadastro
@app.route('/register', methods=['POST'])
def cadastro():
    data = request.get_json()
    username = data['username']
    cpf = data['cpf']
    password = data['password']
    if not (cpf and password and username):
        return 'Campos inválidos', 400
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, cpf, password) VALUES (?, ?, ?)', (username, cpf, password))
        conn.commit()
        new_user = get_user_by_username_or_cpf(cpf, username)
        if not new_user:
            raise LookupError('Erro ao cadastrar usuário')
        new_user.pop('password', None)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()
    return jsonify(new_user), 201


@app.route('/users')
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users;').fetchall()
    conn.close()
    users_list = [dict(user) for user in users]
    return jsonify(users_list), 200


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        cpf = request.form['cpf']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE cpf = ? AND password = ?', (cpf, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Verifique seu CPF e senha.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f'Você está logado! ID do usuário: {session["user_id"]}'
    else:
        return redirect(url_for('login'))


# Função para criar um novo aluno
@app.route('/aluno', methods=['POST'])
def create_aluno():
    data = request.form
    nome1 = data['nomeAluno']
    nome_mae = data['nomeMaeAluno']
    nome_pai = data['nomePaiAluno']
    cpf1 = data['cpfAluno']
    data_nascimento1 = data['data-nascimento-aluno']
    email1 = data['emailAluno']
    serie = data['serieAluno']
    turma = data['turmaAluno']
    senha1 = data['senhaAluno']

    connection = get_db_connection_pymysql()
    cursor = connection.cursor()
    sql = f'insert into aluno(nomeAluno, nomeMaeAluno, nomePaiAluno, cpfAluno, dataNascimentoAluno, emailAluno, serieAluno, turmaAluno , senhaAluno ) values ("{nome1}", "{nome_mae}", "{nome_pai}", "{cpf1}", "{data_nascimento1}", "{email1}", "{serie}", "{turma}", "{senha1}" );'
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'Aluno cadastrado com sucesso!'})


# Função para listar todos os alunos
@app.route('/aluno', methods=['GET'])
def get_alunos():
    connection = get_db_connection_pymysql()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM aluno")
    alunos = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(alunos)


# Função para atualizar um aluno
@app.route('/aluno/<int:id>', methods=['PUT'])
def update_aluno(id):
    data = request.json
    nome = data['nome']
    cpf = data['cpf']
    serie = data['serie']
    turma = data['turma']

    connection = get_db_connection_pymysql()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE aluno SET nome = %s, cpf = %s, serie = %s, turma = %s
        WHERE id = %s
    """, (nome, cpf, serie, turma, id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'Aluno atualizado com sucesso!'})


# Função para deletar um aluno
@app.route('/aluno/<int:id>', methods=['DELETE'])
def delete_aluno(id):
    connection = get_db_connection_pymysql()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM aluno WHERE id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'Aluno deletado com sucesso!'})

# CRUD para Funcionário e Professor pode ser feito da mesma forma mudando apenas as tabelas


if __name__ == '__main__':
    app.run(debug=True)
