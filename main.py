from flask import Flask , render_template, request, flash, redirect, url_for, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'OI'

host = 'localhost'
database = r'C:\Users\Aluno\Documents\PY-Banco-de-Dado\1-09.FDB'
user = 'SYSDBA'
password = 'sysdba'

con = fdb.connect(host=host, database=database,user=user, password=password)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT p.ID_PESSOA, p.NOME, p.EMAIL FROM PESSOA p")
    usuarios = cursor.fetchall()

    cursor.close()

    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/cadatrar')
def cadastrar():
    return render_template('cadastro.html', titulo="Cadastro")

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor = con.cursor()

        try:
            cursor.execute('Select 1 from PESSOA p where p.EMAIL = ?', (email,))
            if cursor.fetchone(): #se existir algum usuario com o email passado
                flash("Erro: Email já cadastrado", 'error')
                return redirect(url_for('login'))

            senha_cryptografada = generate_password_hash(senha).decode('utf-8')
            cursor.execute('INSERT INTO PESSOA ( NOME, EMAIL, SENHA)VALUES (?,?, ?)', (nome, email, senha_cryptografada))
            con.commit()
        finally:
            cursor.close()
        flash('Usuario cadastrado com sucesso', 'success')
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html', titulo="Login")

@app.route('/logar', methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute("SELECT p.email, p.senha,p.id_pessoa FROM PESSOA p WHERE p.email = ?", (email,))
        usuario = cursor.fetchone()
        if usuario :
           if check_password_hash(usuario[1], senha):
                session['id_pessoa'] = usuario[2]
                flash("Login realizado com sucesso")
                return redirect(url_for('livros'))

    finally:
        cursor.close
    flash("Senha ou email incorreto")
    return redirect(url_for('login'))

app.route('/logout')
def logout():
    session.pop('id_pessoa', None)
    flash("Logout realizado com sucesso")
    return redirect(url_for('login'))

@app.route('/editarusuario')
def editarusuario():
    return render_template('editarusuario.html', titulo="Editar Usuario")

@app.route('/usuarioedit/<int:id>', methods=['GET', 'POST'])
def usuarioedit(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_PESSOA , NOME, EMAIL, SENHA FROM pessoa WHERE id_pessoa = ?", (id,))
    usuarios = cursor.fetchone()

    if not usuarios:
        cursor.close()
        flash('Usuario não encontrado')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        cursor.execute('update pessoa set nome = ?, email = ?, senha= ? where id_pessoa = ?',
                       (nome, email, senha, id))

        con.commit()
        flash('Usuario atulizado com sucesso')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editarusuario.html', usuario=usuarios, titulo='Editar Usuario')

@app.route('/delete2/<int:id>', methods=['POST'])
def delete2(id):
    cursor = con.cursor()  # Abre o cursor
    try:
        cursor.execute('delete from pessoa where id_pessoa = ?', (id,))
        con.commit()
        flash('Usuario removido com sucesso')

    except Exception as e:
        con.rollback()
        flash('Erro ao delete o usuario')
    finally:
        cursor.close()
        return redirect(url_for('index'))

@app.route('/livros')
def livros():
    cursor = con.cursor()
    cursor.execute("SELECT l.ID_LIVRO, l.TITULO, l.AUTOR, l.ANO_PUBLICADO FROM LIVRO l")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)

@app.route("/novo")
def novo():
    return render_template('novo.html', titulo="Novo Livro")

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM LIVRO l WHERE l.TITULO = ?', (titulo,))
        if cursor.fetchone(): #se existir algum livro com o titulo passado
            flash("Erro: Livro já cadastrado", 'error')
            return redirect(url_for('novo'))

        cursor.execute(''' INSERT INTO LIVRO (TITULO, AUTOR, ANO_PUBLICADO)
                           VALUES (?, ?, ?)''', (titulo, autor, ano_publicacao))

        con.commit()
    finally:
        cursor.close()
    flash('Livro cradastrado com sucesso', 'success')
    return  redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    if "id_pessoa" not in session:
        flash("Você precisa estar logado para acessar essa página.", "error")
        return redirect(url_for('login'))
    return render_template('editar.html', titulo="Editar Livro")

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if "id_pessoa" not in session:
        flash("Você precisa estar logado para acessar essa página.", "error")
        return redirect(url_for('login'))
    cursor=con.cursor() # abre cursor
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicado FROM LIVRO where id_livro = ?',(id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash('Livro não encontrado')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicacao']

        cursor.execute('update livro set titulo = ?, autor = ?, ano_publicado= ? where id_livro = ?',
                       (titulo, autor, ano_publicado, id))

        con.commit()
        flash('Livro atualizado com sucesso')
        return redirect(url_for('livros'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    if request.method == 'POST':
        if "id_pessoa" not in session:
            flash("Você precisa estar logado para acessar essa página.", "error")
            return redirect(url_for('login'))
    cursor = con.cursor()  # Abre o cursor
    try:
        cursor.execute('delete from livro where id_livro = ?', (id,))
        con.commit()
        flash('Livro removido com sucesso')

    except Exception as e:
        con.rollback()
        flash('Erro ao delete o livro')
    finally:
        cursor.close()
        return redirect(url_for('livros'))

if __name__ == '__main__':
    app.run(debug=True)