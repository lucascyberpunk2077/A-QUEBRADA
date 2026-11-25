import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave-secreta-projeto-peladas-a3'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'peladas.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    # Atualiza os hashes dos usuários de teste com hash real do Werkzeug (senha: 123456)
    senha_padrao = generate_password_hash('123456', method='pbkdf2:sha256')
    conn.execute('UPDATE USUARIO SET senha_hash = ?', (senha_padrao,))
    conn.commit()
    conn.close()


# Inicializa o banco automaticamente na primeira vez se ainda não existir
if not os.path.exists(DB_PATH):
    init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.after_request
def add_no_cache_headers(response):
    # Garante CT 09-06 (botão voltar após logout não reabre área logada)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# Rota utilitária para o Cypress resetar o banco antes dos testes
@app.route('/reset-db', methods=['POST', 'GET'])
def reset_db():
    init_db()
    session.clear()
    return jsonify({'status': 'ok', 'message': 'Banco resetado com sucesso'})


# ==========================================
# 1. AUTENTICAÇÃO E CADASTRO (CT 09-01 a CT 09-09)
# ==========================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('buscar'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        senha = request.form.get('senha') or ''

        if not email or not senha:
            erro = 'Preencha e-mail e senha.'
        else:
            conn = get_db()
            user = conn.execute('SELECT * FROM USUARIO WHERE lower(email) = ?', (email,)).fetchone()
            conn.close()

            if user and check_password_hash(user['senha_hash'], senha):
                session['user_id'] = user['id_usuario']
                session['user_nome'] = user['nome']
                return redirect(url_for('buscar'))
            else:
                erro = 'E-mail ou senha inválidos.'

    return render_template('login.html', erro=erro)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    erro = None
    if request.method == 'POST':
        nome = (request.form.get('nome') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        senha = request.form.get('senha') or ''
        telefone = (request.form.get('telefone') or '').strip()
        cidade = (request.form.get('cidade') or '').strip()
        posicao = (request.form.get('posicao_preferida') or '').strip()

        if not nome or not email or not senha:
            erro = 'Nome, e-mail e senha são obrigatórios.'
        else:
            conn = get_db()
            try:
                senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
                conn.execute(
                    '''INSERT INTO USUARIO (nome, email, senha_hash, telefone_whatsapp, cidade, posicao_preferida)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (nome, email, senha_hash, telefone, cidade, posicao)
                )
                conn.commit()
                conn.close()
                flash('Cadastro realizado com sucesso! Faça seu login.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                conn.close()
                erro = 'Este e-mail já está cadastrado.'

    return render_template('cadastro.html', erro=erro)


# ==========================================
# 2. BUSCA E DETALHES (CT 09-21 a CT 09-23)
# ==========================================

@app.route('/buscar')
@login_required
def buscar():
    local_filtro = (request.args.get('local') or '').strip()
    tipo_filtro = (request.args.get('tipo') or '').strip()
    valor_max = (request.args.get('valor_max') or '').strip()

    query = '''
        SELECT p.*, l.nome AS local_nome, l.bairro, l.cidade, l.tipo,
               (p.vagas_totais - (
                   SELECT COUNT(*) FROM SOLICITACAO s
                   WHERE s.id_pelada = p.id_pelada AND s.status = 'Aceita'
               )) AS vagas_livres
        FROM PELADA p
        JOIN LOCAL l ON p.id_local = l.id_local
        WHERE p.status IN ('Aberta', 'Lotada')
    '''
    params = []

    if local_filtro:
        query += ' AND (lower(l.bairro) LIKE ? OR lower(l.cidade) LIKE ? OR lower(l.nome) LIKE ?)'
        termo = f'%{local_filtro.lower()}%'
        params.extend([termo, termo, termo])

    if tipo_filtro:
        query += ' AND l.tipo = ?'
        params.append(tipo_filtro)

    if valor_max:
        try:
            query += ' AND p.valor_por_pessoa <= ?'
            params.append(float(valor_max))
        except ValueError:
            pass

    query += ' ORDER BY p.data_hora ASC'

    conn = get_db()
    peladas = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('buscar.html', peladas=peladas, local_filtro=local_filtro, tipo_filtro=tipo_filtro, valor_max=valor_max)


@app.route('/pelada/<int:id_pelada>')
@login_required
def detalhes_pelada(id_pelada):
    conn = get_db()
    pelada = conn.execute('''
        SELECT p.*, l.nome AS local_nome, l.endereco, l.bairro, l.cidade, l.tipo,
               u.nome AS organizador_nome, u.telefone_whatsapp AS organizador_whatsapp,
               (p.vagas_totais - (
                   SELECT COUNT(*) FROM SOLICITACAO s
                   WHERE s.id_pelada = p.id_pelada AND s.status = 'Aceita'
               )) AS vagas_livres
        FROM PELADA p
        JOIN LOCAL l ON p.id_local = l.id_local
        JOIN USUARIO u ON p.id_organizador = u.id_usuario
        WHERE p.id_pelada = ?
    ''', (id_pelada,)).fetchone()

    if not pelada:
        conn.close()
        return 'Pelada não encontrada', 404

    solicitacao = conn.execute(
        'SELECT * FROM SOLICITACAO WHERE id_pelada = ? AND id_usuario = ?',
        (id_pelada, session['user_id'])
    ).fetchone()
    conn.close()

    return render_template('detalhes.html', pelada=pelada, solicitacao=solicitacao)


# ==========================================
# 3. CRUD DE PELADA (CT 09-10 a CT 09-20)
# ==========================================

@app.route('/minhas-peladas')
@login_required
def minhas_peladas():
    conn = get_db()
    peladas = conn.execute('''
        SELECT p.*, l.nome AS local_nome,
               (p.vagas_totais - (
                   SELECT COUNT(*) FROM SOLICITACAO s
                   WHERE s.id_pelada = p.id_pelada AND s.status = 'Aceita'
               )) AS vagas_livres
        FROM PELADA p
        JOIN LOCAL l ON p.id_local = l.id_local
        WHERE p.id_organizador = ?
        ORDER BY p.data_hora ASC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('minhas_peladas.html', peladas=peladas)


@app.route('/pelada/nova', methods=['GET', 'POST'])
@login_required
def nova_pelada():
    conn = get_db()
    locais = conn.execute('SELECT * FROM LOCAL ORDER BY nome').fetchall()
    erro = None

    if request.method == 'POST':
        id_local = request.form.get('id_local')
        data = (request.form.get('data') or '').strip()
        hora = (request.form.get('hora') or '').strip()
        vagas = request.form.get('vagas_totais')
        valor = request.form.get('valor_por_pessoa')
        nivel = request.form.get('nivel') or 'Casual'
        descricao = (request.form.get('descricao') or '').strip()

        if not id_local or not data or not hora or not vagas or valor == '':
            erro = 'Todos os campos obrigatórios devem ser preenchidos.'
        else:
            try:
                vagas_int = int(vagas)
                valor_float = float(valor)
                data_hora_str = f'{data} {hora}'
                dt_pelada = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')

                if vagas_int <= 0:
                    erro = 'As vagas devem ser maiores que zero.'
                elif valor_float < 0:
                    erro = 'O valor não pode ser negativo.'
                elif dt_pelada <= datetime.now():
                    erro = 'Data inválida: a data da pelada deve ser no futuro.'
                else:
                    conn.execute('''
                        INSERT INTO PELADA (id_organizador, id_local, data_hora, vagas_totais, valor_por_pessoa, nivel, descricao, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Aberta')
                    ''', (session['user_id'], id_local, data_hora_str, vagas_int, valor_float, nivel, descricao))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('minhas_peladas'))
            except ValueError:
                erro = 'Valores inválidos informados.'
            except sqlite3.IntegrityError as e:
                erro = f'Erro no banco de dados: {e}'

    conn.close()
    return render_template('pelada_form.html', locais=locais, pelada=None, erro=erro)


@app.route('/pelada/<int:id_pelada>/editar', methods=['GET', 'POST'])
@login_required
def editar_pelada(id_pelada):
    conn = get_db()
    pelada = conn.execute('SELECT * FROM PELADA WHERE id_pelada = ?', (id_pelada,)).fetchone()

    # CT 09-20: Impede editar pelada de outro organizador
    if not pelada or pelada['id_organizador'] != session['user_id']:
        conn.close()
        return redirect(url_for('minhas_peladas'))

    locais = conn.execute('SELECT * FROM LOCAL ORDER BY nome').fetchall()
    erro = None

    if request.method == 'POST':
        id_local = request.form.get('id_local')
        data = (request.form.get('data') or '').strip()
        hora = (request.form.get('hora') or '').strip()
        vagas = request.form.get('vagas_totais')
        valor = request.form.get('valor_por_pessoa')
        nivel = request.form.get('nivel') or 'Casual'
        descricao = (request.form.get('descricao') or '').strip()

        if not id_local or not data or not hora or not vagas or valor == '':
            erro = 'Todos os campos obrigatórios devem ser preenchidos.'
        else:
            try:
                vagas_int = int(vagas)
                valor_float = float(valor)
                data_hora_str = f'{data} {hora}'

                aceitos = conn.execute(
                    "SELECT COUNT(*) FROM SOLICITACAO WHERE id_pelada = ? AND status = 'Aceita'",
                    (id_pelada,)
                ).fetchone()[0]

                if vagas_int <= 0 or vagas_int < aceitos:
                    erro = 'Número de vagas inválido.'
                elif valor_float < 0:
                    erro = 'O valor não pode ser negativo.'
                else:
                    novo_status = 'Lotada' if aceitos >= vagas_int else 'Aberta'
                    conn.execute('''
                        UPDATE PELADA
                        SET id_local = ?, data_hora = ?, vagas_totais = ?, valor_por_pessoa = ?,
                            nivel = ?, descricao = ?, status = ?
                        WHERE id_pelada = ?
                    ''', (id_local, data_hora_str, vagas_int, valor_float, nivel, descricao, novo_status, id_pelada))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('minhas_peladas'))
            except ValueError:
                erro = 'Valores inválidos.'

    conn.close()
    return render_template('pelada_form.html', locais=locais, pelada=pelada, erro=erro)


@app.route('/pelada/<int:id_pelada>/excluir', methods=['POST'])
@login_required
def excluir_pelada(id_pelada):
    conn = get_db()
    pelada = conn.execute('SELECT * FROM PELADA WHERE id_pelada = ?', (id_pelada,)).fetchone()
    if pelada and pelada['id_organizador'] == session['user_id']:
        conn.execute('DELETE FROM PELADA WHERE id_pelada = ?', (id_pelada,))
        conn.commit()
    conn.close()
    return redirect(url_for('minhas_peladas'))


# ==========================================
# 4. SOLICITAÇÕES, ACEITE, RECUSA E AVALIAÇÃO
# ==========================================

@app.route('/pelada/<int:id_pelada>/solicitar', methods=['POST'])
@login_required
def solicitar_vaga(id_pelada):
    mensagem = (request.form.get('mensagem') or 'Quero jogar!').strip()
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO SOLICITACAO (id_pelada, id_usuario, mensagem, status) VALUES (?, ?, ?, ?)',
            (id_pelada, session['user_id'], mensagem, 'Pendente')
        )
        conn.commit()
        flash('Solicitação enviada com sucesso!')
    except sqlite3.IntegrityError as e:
        msg_erro = str(e)
        if 'Organizador' in msg_erro:
            flash('O organizador não pode solicitar vaga na própria pelada.')
        elif 'Pelada lotada' in msg_erro:
            flash('Pelada lotada ou indisponível.')
        else:
            flash('Você já possui uma solicitação para esta pelada.')
    finally:
        conn.close()

    return redirect(url_for('detalhes_pelada', id_pelada=id_pelada))


@app.route('/meus-pedidos')
@login_required
def meus_pedidos():
    conn = get_db()
    pedidos = conn.execute('''
        SELECT s.*, p.data_hora, p.id_organizador, l.nome AS local_nome,
               u.nome AS organizador_nome, u.telefone_whatsapp AS organizador_whatsapp
        FROM SOLICITACAO s
        JOIN PELADA p ON s.id_pelada = p.id_pelada
        JOIN LOCAL l ON p.id_local = l.id_local
        JOIN USUARIO u ON p.id_organizador = u.id_usuario
        WHERE s.id_usuario = ?
        ORDER BY s.data_solicitacao DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('meus_pedidos.html', pedidos=pedidos)


@app.route('/solicitacao/<int:id_solicitacao>/cancelar', methods=['POST'])
@login_required
def cancelar_solicitacao(id_solicitacao):
    conn = get_db()
    sol = conn.execute('SELECT * FROM SOLICITACAO WHERE id_solicitacao = ?', (id_solicitacao,)).fetchone()
    if sol and sol['id_usuario'] == session['user_id'] and sol['status'] in ('Pendente', 'Aceita'):
        conn.execute(
            "UPDATE SOLICITACAO SET status = 'Cancelada', data_resposta = CURRENT_TIMESTAMP WHERE id_solicitacao = ?",
            (id_solicitacao,)
        )
        conn.commit()
    conn.close()
    return redirect(url_for('meus_pedidos'))


@app.route('/solicitacoes')
@login_required
def solicitacoes_recebidas():
    pelada_id = request.args.get('pelada_id')
    conn = get_db()
    minhas = conn.execute(
        'SELECT p.*, l.nome AS local_nome FROM PELADA p JOIN LOCAL l ON p.id_local = l.id_local WHERE p.id_organizador = ?',
        (session['user_id'],)
    ).fetchall()

    if not pelada_id and minhas:
        pelada_id = str(minhas[0]['id_pelada'])

    pelada_selecionada = None
    lista_solicitacoes = []
    vagas_livres = 0
    jogo_aconteceu = False

    if pelada_id:
        pelada_selecionada = conn.execute(
            'SELECT p.*, l.nome AS local_nome FROM PELADA p JOIN LOCAL l ON p.id_local = l.id_local WHERE p.id_pelada = ? AND p.id_organizador = ?',
            (pelada_id, session['user_id'])
        ).fetchone()

        if pelada_selecionada:
            aceitos = conn.execute(
                "SELECT COUNT(*) FROM SOLICITACAO WHERE id_pelada = ? AND status = 'Aceita'",
                (pelada_id,)
            ).fetchone()[0]
            vagas_livres = pelada_selecionada['vagas_totais'] - aceitos
            jogo_aconteceu = pelada_selecionada['data_hora'] <= datetime.now().strftime('%Y-%m-%d %H:%M')

            lista_solicitacoes = conn.execute('''
                SELECT s.*, u.nome AS jogador_nome,
                       r.percentual_presenca, r.jogos_marcados, r.nota_media
                FROM SOLICITACAO s
                JOIN USUARIO u ON s.id_usuario = u.id_usuario
                LEFT JOIN vw_reputacao_jogador r ON r.id_usuario = s.id_usuario
                WHERE s.id_pelada = ?
                ORDER BY s.data_solicitacao ASC
            ''', (pelada_id,)).fetchall()

    conn.close()
    return render_template(
        'solicitacoes.html',
        minhas=minhas,
        pelada_selecionada=pelada_selecionada,
        vagas_livres=vagas_livres,
        solicitacoes=lista_solicitacoes,
        jogo_aconteceu=jogo_aconteceu
    )


@app.route('/solicitacao/<int:id_solicitacao>/responder', methods=['POST'])
@login_required
def responder_solicitacao(id_solicitacao):
    acao = request.form.get('acao')  # 'Aceita' ou 'Recusada'
    conn = get_db()
    sol = conn.execute('''
        SELECT s.*, p.id_organizador
        FROM SOLICITACAO s
        JOIN PELADA p ON s.id_pelada = p.id_pelada
        WHERE s.id_solicitacao = ?
    ''', (id_solicitacao,)).fetchone()

    pelada_id = sol['id_pelada'] if sol else ''

    if sol and sol['id_organizador'] == session['user_id'] and sol['status'] == 'Pendente':
        if acao in ('Aceita', 'Recusada'):
            try:
                conn.execute(
                    'UPDATE SOLICITACAO SET status = ?, data_resposta = CURRENT_TIMESTAMP WHERE id_solicitacao = ?',
                    (acao, id_solicitacao)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                flash('Sem vagas livres: o aceite foi rejeitado.')

    conn.close()
    return redirect(url_for('solicitacoes_recebidas', pelada_id=pelada_id))


@app.route('/solicitacao/<int:id_solicitacao>/presenca', methods=['POST'])
@login_required
def marcar_presenca(id_solicitacao):
    valor = request.form.get('compareceu')  # '1' = compareceu, '0' = faltou
    conn = get_db()
    sol = conn.execute('''
        SELECT s.*, p.id_organizador
        FROM SOLICITACAO s
        JOIN PELADA p ON s.id_pelada = p.id_pelada
        WHERE s.id_solicitacao = ?
    ''', (id_solicitacao,)).fetchone()

    pelada_id = sol['id_pelada'] if sol else ''

    if sol and sol['id_organizador'] == session['user_id'] and valor in ('0', '1'):
        try:
            conn.execute(
                'UPDATE SOLICITACAO SET compareceu = ? WHERE id_solicitacao = ?',
                (int(valor), id_solicitacao)
            )
            conn.commit()
            flash('Presença registrada.')
        except sqlite3.IntegrityError as erro:
            flash(str(erro))

    conn.close()
    return redirect(url_for('solicitacoes_recebidas', pelada_id=pelada_id))


@app.route('/avaliar/<int:id_pelada>', methods=['GET', 'POST'])
@login_required
def avaliar_participante(id_pelada):
    conn = get_db()
    pelada = conn.execute('SELECT * FROM PELADA WHERE id_pelada = ?', (id_pelada,)).fetchone()

    # Lista todos os participantes da pelada (organizador + aceitos)
    participantes = conn.execute('''
        SELECT id_usuario, nome FROM USUARIO
        WHERE id_usuario = ?
           OR id_usuario IN (
               SELECT id_usuario FROM SOLICITACAO WHERE id_pelada = ? AND status = 'Aceita'
           )
    ''', (pelada['id_organizador'], id_pelada)).fetchall()

    erro = None
    if request.method == 'POST':
        id_avaliado = request.form.get('id_avaliado')
        nota = request.form.get('nota')
        comentario = (request.form.get('comentario') or '').strip()

        try:
            id_avaliado_int = int(id_avaliado)
            nota_int = int(nota)

            if id_avaliado_int == session['user_id']:
                erro = 'Você não pode avaliar a si mesmo.'
            elif nota_int < 1 or nota_int > 5:
                erro = 'A nota deve estar entre 1 e 5.'
            else:
                conn.execute('''
                    INSERT INTO AVALIACAO (id_pelada, id_avaliador, id_avaliado, nota, comentario)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id_pelada, session['user_id'], id_avaliado_int, nota_int, comentario))
                conn.commit()
                conn.close()
                flash('Avaliação registrada com sucesso!')
                return redirect(url_for('meus_pedidos'))
        except (ValueError, TypeError):
            erro = 'Dados inválidos.'
        except sqlite3.IntegrityError:
            erro = 'Não foi possível registrar a avaliação (duplicada ou inválida).'

    conn.close()
    return render_template('avaliar.html', pelada=pelada, participantes=participantes, erro=erro)


if __name__ == '__main__':
    app.run(debug=True, port=5001)