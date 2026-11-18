import os

os.makedirs("templates", exist_ok=True)

# 1. BASE.HTML - Identidade Visual "A QUEBRADA"
base_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A QUEBRADA — Futebol & Peladas</title>
  <style>
    :root {
      --primary: #15803d;
      --primary-dark: #14532d;
      --accent: #f97316;
      --dark: #0f172a;
      --bg: #f1f5f9;
      --card: #ffffff;
      --text: #1e293b;
      --muted: #64748b;
      --border: #e2e8f0;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    header { background: linear-gradient(135deg, #0f172a 0%, #14532d 100%); color: #fff; padding: 14px 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); position: sticky; top: 0; z-index: 100; }
    .nav-container { max-width: 1080px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
    .brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: #fff; font-weight: 900; font-size: 1.35rem; letter-spacing: 0.5px; }
    .brand span.badge-logo { background: var(--accent); color: #fff; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; }
    nav { display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }
    nav a { color: #e2e8f0; text-decoration: none; font-size: 0.92rem; font-weight: 600; padding: 6px 10px; border-radius: 6px; transition: 0.2s; }
    nav a:hover { background: rgba(255,255,255,0.12); color: #fff; }
    .btn-sair { background: rgba(239,68,68,0.2); color: #fca5a5 !important; border: 1px solid rgba(239,68,68,0.4); }
    .container { max-width: 1040px; margin: 28px auto; padding: 0 18px; }
    .hero-banner { background: linear-gradient(rgba(15,23,42,0.72), rgba(20,83,45,0.82)), url('https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=1200&q=80') center/cover; color: #fff; padding: 32px 28px; border-radius: 14px; margin-bottom: 24px; box-shadow: 0 6px 18px rgba(0,0,0,0.12); }
    .hero-banner h1 { font-size: 1.85rem; margin-bottom: 6px; }
    .hero-banner p { color: #cbd5e1; font-size: 1rem; }
    .card { background: var(--card); border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 2px 8px rgba(15,23,42,0.05); overflow: hidden; margin-bottom: 18px; }
    .card-body { padding: 20px; }
    .grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
    .pelada-img { width: 100%; height: 170px; object-fit: cover; display: block; background: #cbd5e1; }
    .tag { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; }
    .tag-green { background: #dcfce7; color: #166534; }
    .tag-orange { background: #ffedd5; color: #9a3412; }
    .tag-gray { background: #e2e8f0; color: #334155; }
    .tag-red { background: #fee2e2; color: #991b1b; }
    .btn { display: inline-block; padding: 10px 16px; border-radius: 8px; border: none; font-weight: 700; font-size: 0.92rem; cursor: pointer; text-decoration: none; text-align: center; transition: 0.2s; }
    .btn-primary { background: var(--primary); color: #fff; }
    .btn-primary:hover { background: var(--primary-dark); }
    .btn-accent { background: var(--accent); color: #fff; }
    .btn-outline { background: #fff; color: var(--text); border: 1px solid var(--border); }
    .btn-danger { background: #dc2626; color: #fff; }
    .btn-whatsapp { background: #22c55e; color: #fff; }
    .form-group { margin-bottom: 14px; }
    label { display: block; font-weight: 600; margin-bottom: 5px; font-size: 0.9rem; color: #334155; }
    input, select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; background: #fff; }
    input:focus, select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(21,128,61,0.15); }
    .alert { padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-weight: 600; }
    .alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .alert-success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .price { font-size: 1.25rem; font-weight: 800; color: var(--primary); }
    footer { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 28px 16px; }
  </style>
</head>
<body>
  <header>
    <div class="nav-container">
      <a href="/buscar" class="brand">⚽ A QUEBRADA <span class="badge-logo">PELADAS</span></a>
      {% if session.get('usuario_id') %}
      <nav>
        <a href="/buscar">Buscar Peladas</a>
        <a href="/pelada/nova">+ Criar Pelada</a>
        <a href="/minhas-peladas">Minhas Peladas</a>
        <a href="/solicitacoes">Solicitações</a>
        <a href="/meus-pedidos">Meus Pedidos</a>
        <a href="/logout" data-cy="sair" class="btn-sair">Sair</a>
      </nav>
      {% endif %}
    </div>
  </header>
  <div class="container">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, msg in messages %}
          <div class="alert {{ 'alert-error' if category == 'error' else 'alert-success' }}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
  <footer>A QUEBRADA — Plataforma de Organização de Peladas &bull; Projeto A3</footer>
</body>
</html>
"""

# 2. LOGIN.HTML - Tela dividida com foto de futebol
login_html = """{% extends 'base.html' %}
{% block content %}
<div style="max-width: 860px; margin: 20px auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
  <div style="background: linear-gradient(rgba(15,23,42,0.65), rgba(20,83,45,0.85)), url('https://images.unsplash.com/photo-1518605368461-1ee7e53f6664?auto=format&fit=crop&w=800&q=80') center/cover; color: #fff; padding: 36px; display: flex; flex-direction: column; justify-content: space-between;">
    <div>
      <span class="tag tag-orange" style="margin-bottom: 12px;">FUTEBOL AMADOR</span>
      <h1 style="font-size: 2rem; line-height: 1.2; margin-bottom: 12px;">Bem-vindo à A QUEBRADA</h1>
      <p style="color: #e2e8f0;">Encontre peladas perto de você, garanta sua vaga na resenha ou organize seu próprio racha sem dor de cabeça.</p>
    </div>
    <p style="font-size: 0.85rem; color: #cbd5e1; margin-top: 24px;">⚽ Society &bull; Futsal &bull; Campo</p>
  </div>
  <div style="padding: 36px;">
    <h2 style="margin-bottom: 6px;">Entrar na conta</h2>
    <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">Use seu e-mail e senha para entrar em campo.</p>
    {% if erro %}
      <div class="alert alert-error" data-cy="login-erro">{{ erro }}</div>
    {% endif %}
    <form method="POST">
      <div class="form-group">
        <label>E-mail</label>
        <input type="email" name="email" data-cy="login-email" placeholder="seu@email.com">
      </div>
      <div class="form-group">
        <label>Senha</label>
        <input type="password" name="senha" data-cy="login-senha" placeholder="••••••">
      </div>
      <button type="submit" data-cy="login-enviar" class="btn btn-primary" style="width: 100%; margin-top: 6px;">Entrar em Campo</button>
    </form>
    <p style="margin-top: 18px; text-align: center; font-size: 0.92rem;">
      Ainda não joga com a gente? <a href="/cadastro" data-cy="criar-conta" style="color: #15803d; font-weight: 700;">Criar conta</a>
    </p>
  </div>
</div>
{% endblock %}
"""

# 3. CADASTRO.HTML
cadastro_html = """{% extends 'base.html' %}
{% block content %}
<div class="card" style="max-width: 480px; margin: 20px auto;">
  <div class="card-body" style="padding: 30px;">
    <h2 style="margin-bottom: 6px;">Criar conta na A QUEBRADA</h2>
    <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">Cadastre-se para buscar jogos ou criar suas peladas.</p>
    {% if erro %}
      <div class="alert alert-error" data-cy="cadastro-erro">{{ erro }}</div>
    {% endif %}
    <form method="POST">
      <div class="form-group">
        <label>Nome completo *</label>
        <input type="text" name="nome" data-cy="cadastro-nome" placeholder="Ex: Carlos Silva">
      </div>
      <div class="form-group">
        <label>E-mail *</label>
        <input type="email" name="email" data-cy="cadastro-email" placeholder="carlos@peladas.com">
      </div>
      <div class="form-group">
        <label>Senha *</label>
        <input type="password" name="senha" data-cy="cadastro-senha" placeholder="Mínimo 6 caracteres">
      </div>
      <div class="form-group">
        <label>WhatsApp (com DDD)</label>
        <input type="text" name="telefone" data-cy="cadastro-telefone" placeholder="5581999990000">
      </div>
      <div class="form-group">
        <label>Posição preferida</label>
        <select name="posicao">
          <option value="Meia">Meia</option>
          <option value="Atacante">Atacante</option>
          <option value="Zagueiro">Zagueiro</option>
          <option value="Lateral">Lateral</option>
          <option value="Goleiro">Goleiro</option>
        </select>
      </div>
      <button type="submit" data-cy="cadastro-enviar" class="btn btn-primary" style="width: 100%;">Concluir Cadastro</button>
    </form>
  </div>
</div>
{% endblock %}
"""

# 4. BUSCAR.HTML - Cards estilo marketplace com fotos de arenas
buscar_html = """{% extends 'base.html' %}
{% block content %}
<div class="hero-banner">
  <h1>Encontre sua próxima pelada na A QUEBRADA</h1>
  <p>Filtre por bairro, arena ou nível de jogo e garanta sua vaga em poucos cliques.</p>
</div>

<div class="card">
  <div class="card-body">
    <form method="GET" action="/buscar" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; align-items: end;">
      <div>
        <label>Bairro ou Arena</label>
        <input type="text" name="local" data-cy="busca-local" value="{{ request.args.get('local', '') }}" placeholder="Ex: Boa Viagem, Arena...">
      </div>
      <div>
        <label>Data</label>
        <input type="date" name="data" value="{{ request.args.get('data', '') }}">
      </div>
      <div>
        <label>Nível</label>
        <select name="nivel">
          <option value="">Todos os níveis</option>
          <option value="Casual" {{ 'selected' if request.args.get('nivel') == 'Casual' }}>Casual</option>
          <option value="Intermediário" {{ 'selected' if request.args.get('nivel') == 'Intermediário' }}>Intermediário</option>
          <option value="Competitivo" {{ 'selected' if request.args.get('nivel') == 'Competitivo' }}>Competitivo</option>
        </select>
      </div>
      <button type="submit" data-cy="busca-enviar" class="btn btn-primary">Buscar Peladas</button>
    </form>
  </div>
</div>

{% set fotos = [
  'https://images.unsplash.com/photo-1529900748604-07564a03e7a6?auto=format&fit=crop&w=700&q=80',
  'https://images.unsplash.com/photo-1575361204480-aadea25e6e68?auto=format&fit=crop&w=700&q=80',
  'https://images.unsplash.com/photo-1551958219-acbc608c6377?auto=format&fit=crop&w=700&q=80'
] %}

{% if peladas %}
  <div class="grid-cards">
    {% for p in peladas %}
    <div class="card" data-cy="pelada-card">
      <img src="{{ fotos[loop.index0 % 3] }}" alt="Campo de Futebol" class="pelada-img">
      <div class="card-body">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span class="tag tag-green">{{ p['nivel'] }}</span>
          <span class="tag {{ 'tag-red' if p['vagas_livres'] == 0 else 'tag-orange' }}">
            {{ 'Lotada' if p['vagas_livres'] == 0 else p['vagas_livres'] ~ ' vagas livres' }}
          </span>
        </div>
        <h3 style="margin-bottom: 4px;">{{ p['local_nome'] }}</h3>
        <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 10px;">📍 {{ p['bairro'] }} &bull; Org: {{ p['organizador_nome'] }}</p>
        <p style="font-size: 0.9rem; margin-bottom: 14px;">📅 <strong>{{ p['data'] }}</strong> às <strong>{{ p['hora'] }}</strong></p>
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 12px;">
          <span class="price">R$ {{ "%.2f"|format(p['valor']) }}</span>
          <a href="/pelada/{{ p['id'] }}" data-cy="ver-detalhes" class="btn btn-primary">Ver detalhes</a>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
{% else %}
  <div class="card" data-cy="sem-resultados">
    <div class="card-body" style="text-align: center; padding: 40px;">
      <h3>Nenhuma pelada encontrada</h3>
      <p style="color: #64748b;">Tente limpar os filtros ou crie uma nova pelada na sua quebrada!</p>
    </div>
  </div>
{% endif %}
{% endblock %}
"""

# 5. DETALHES.HTML - Foto grande da arena + informações completas
detalhes_html = """{% extends 'base.html' %}
{% block content %}
<div class="card">
  <img src="https://images.unsplash.com/photo-1529900748604-07564a03e7a6?auto=format&fit=crop&w=1100&q=80" alt="Arena" style="width: 100%; height: 240px; object-fit: cover;">
  <div class="card-body" style="padding: 28px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
      <div>
        <span class="tag tag-green" style="margin-bottom: 8px;">{{ pelada['nivel'] }}</span>
        <h1 style="font-size: 1.7rem;">{{ pelada['local_nome'] }}</h1>
        <p style="color: #64748b;">📍 {{ pelada['endereco'] }} — {{ pelada['bairro'] }}</p>
      </div>
      <div style="text-align: right;">
        <span class="price" style="font-size: 1.6rem;">R$ {{ "%.2f"|format(pelada['valor']) }}</span>
        <p style="color: #64748b; font-size: 0.85rem;">por jogador</p>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; background: #f8fafc; padding: 16px; border-radius: 10px; margin-bottom: 20px;">
      <div><strong>📅 Data e Hora:</strong><br>{{ pelada['data'] }} às {{ pelada['hora'] }}</div>
      <div><strong>👥 Vagas:</strong><br>{{ pelada['vagas_livres'] }} livres de {{ pelada['vagas_total'] }}</div>
      <div><strong>🏆 Organizador:</strong><br>{{ pelada['organizador_nome'] }}</div>
      <div><strong>📌 Status:</strong><br>{{ pelada['status'] }}</div>
    </div>

    {% if pelada['organizador_id'] != session.get('usuario_id') %}
      {% if not solicitacao %}
        <form method="POST" action="/pelada/{{ pelada['id'] }}/solicitar">
          <button type="submit" data-cy="solicitar-vaga" class="btn btn-accent">⚽ Solicitar Vaga na Pelada</button>
        </form>
      {% else %}
        <div class="alert alert-success">Status da sua solicitação: <strong>{{ solicitacao['status'] }}</strong></div>
        {% if solicitacao['status'] == 'Aceita' %}
          <a href="https://wa.me/{{ pelada['organizador_telefone'] }}" target="_blank" data-cy="abrir-whatsapp" class="btn btn-whatsapp">💬 Chamar Organizador no WhatsApp</a>
        {% endif %}
      {% endif %}
    {% else %}
      <a href="/pelada/{{ pelada['id'] }}/editar" class="btn btn-outline">✏️ Gerenciar / Editar Minha Pelada</a>
    {% endif %}
  </div>
</div>
{% endblock %}
"""

# 6. MINHAS_PELADAS.HTML
minhas_peladas_html = """{% extends 'base.html' %}
{% block content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
  <h2>Minhas Peladas Organizadas</h2>
  <a href="/pelada/nova" class="btn btn-primary">+ Nova Pelada</a>
</div>

{% if peladas %}
  {% for p in peladas %}
  <div class="card" data-cy="minha-pelada">
    <div class="card-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
      <div style="display: flex; gap: 16px; align-items: center;">
        <img src="https://images.unsplash.com/photo-1575361204480-aadea25e6e68?auto=format&fit=crop&w=200&q=80" alt="Campo" style="width: 84px; height: 84px; border-radius: 10px; object-fit: cover;">
        <div>
          <h3>{{ p['local_nome'] }}</h3>
          <p style="color: #64748b; font-size: 0.9rem;">📅 {{ p['data'] }} às {{ p['hora'] }} &bull; R$ {{ "%.2f"|format(p['valor']) }}</p>
          <span class="tag tag-green" style="margin-top: 6px;">Vagas: {{ p['vagas_livres'] }} de {{ p['vagas_total'] }}</span>
        </div>
      </div>
      <div style="display: flex; gap: 8px; align-items: center;">
        <a href="/pelada/{{ p['id'] }}/editar" data-cy="editar" class="btn btn-outline">Editar</a>
        <button type="button" data-cy="excluir" class="btn btn-danger" onclick="document.getElementById('confirm-{{ p['id'] }}').style.display='inline-flex'">Excluir</button>
        <div id="confirm-{{ p['id'] }}" style="display: none; gap: 6px; align-items: center;">
          <form method="POST" action="/pelada/{{ p['id'] }}/excluir" style="display:inline;">
            <button type="submit" data-cy="confirmar-exclusao" class="btn btn-danger">Confirmar</button>
          </form>
          <button type="button" class="btn btn-outline" onclick="document.getElementById('confirm-{{ p['id'] }}').style.display='none'">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
  {% endfor %}
{% else %}
  <div class="card"><div class="card-body"><p>Você ainda não criou nenhuma pelada.</p></div></div>
{% endif %}
{% endblock %}
"""

arquivos = {
    "templates/base.html": base_html,
    "templates/login.html": login_html,
    "templates/cadastro.html": cadastro_html,
    "templates/buscar.html": buscar_html,
    "templates/detalhes.html": detalhes_html,
    "templates/minhas_peladas.html": minhas_peladas_html,
}

for caminho, conteudo in arquivos.items():
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"Atualizado: {caminho}")

print("\\nVisual de A QUEBRADA atualizado com sucesso!")