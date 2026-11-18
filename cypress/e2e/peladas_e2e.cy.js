describe("Suíte E2E - Site de Peladas (CT 09-01 a CT 09-37)", () => {
  beforeEach(() => {
    cy.request("POST", "/reset-db");
  });

  const loginComo = (email) => {
    cy.visit("/login");
    cy.get('[data-cy="login-email"]').type(email);
    cy.get('[data-cy="login-senha"]').type("123456");
    cy.get('[data-cy="login-enviar"]').click();
  };

  // ==========================================
  // 9.1 LOGIN (CT 09-01 a CT 09-06)
  // ==========================================
  it("CT 09-01: Login com credenciais válidas", () => {
    loginComo("u1@peladas.com");
    cy.url().should("include", "/buscar");
    cy.get('[data-cy="sair"]').should("be.visible");
  });

  it("CT 09-02: Login com senha incorreta", () => {
    cy.visit("/login");
    cy.get('[data-cy="login-email"]').type("u1@peladas.com");
    cy.get('[data-cy="login-senha"]').type("senhaerrada");
    cy.get('[data-cy="login-enviar"]').click();
    cy.url().should("include", "/login");
    cy.get('[data-cy="login-erro"]').should("be.visible");
  });

  it("CT 09-03: Login com e-mail inexistente", () => {
    cy.visit("/login");
    cy.get('[data-cy="login-email"]').type("naoexiste@peladas.com");
    cy.get('[data-cy="login-senha"]').type("123456");
    cy.get('[data-cy="login-enviar"]').click();
    cy.url().should("include", "/login");
    cy.get('[data-cy="login-erro"]').should("contain", "E-mail ou senha inválidos");
  });

  it("CT 09-04: Login com campos vazios", () => {
    cy.visit("/login");
    cy.get('[data-cy="login-enviar"]').click();
    cy.url().should("include", "/login");
    cy.get('[data-cy="login-erro"]').should("be.visible");
  });

  it("CT 09-05: Acesso a página protegida sem login", () => {
    cy.visit("/minhas-peladas");
    cy.url().should("include", "/login");
  });

  it("CT 09-06: Logout", () => {
    loginComo("u1@peladas.com");
    cy.get('[data-cy="sair"]').click();
    cy.url().should("include", "/login");
    cy.visit("/minhas-peladas");
    cy.url().should("include", "/login");
  });

  // ==========================================
  // 9.2 CADASTRO DE USUÁRIO (CT 09-07 a CT 09-09)
  // ==========================================
  it("CT 09-07: Cadastro com dados válidos", () => {
    cy.visit("/login");
    cy.get('[data-cy="criar-conta"]').click();
    cy.get('[data-cy="cadastro-nome"]').type("Novo Jogador");
    cy.get('[data-cy="cadastro-email"]').type("novo@peladas.com");
    cy.get('[data-cy="cadastro-senha"]').type("123456");
    cy.get('[data-cy="cadastro-telefone"]').type("5581988887777");
    cy.get('[data-cy="cadastro-enviar"]').click();
    cy.url().should("include", "/login");

    loginComo("novo@peladas.com");
    cy.url().should("include", "/buscar");
  });

  it("CT 09-08: Cadastro com e-mail já existente", () => {
    cy.visit("/cadastro");
    cy.get('[data-cy="cadastro-nome"]').type("Duplicado");
    cy.get('[data-cy="cadastro-email"]').type("u1@peladas.com");
    cy.get('[data-cy="cadastro-senha"]').type("123456");
    cy.get('[data-cy="cadastro-enviar"]').click();
    cy.get('[data-cy="cadastro-erro"]').should("contain", "já está cadastrado");
  });

  it("CT 09-09: Cadastro com campo obrigatório vazio", () => {
    cy.visit("/cadastro");
    cy.get('[data-cy="cadastro-email"]').type("semnome@peladas.com");
    cy.get('[data-cy="cadastro-senha"]').type("123456");
    cy.get('[data-cy="cadastro-enviar"]').click();
    cy.get('[data-cy="cadastro-erro"]').should("be.visible");
  });

  // ==========================================
  // 9.3 CRUD DE PELADA (CT 09-10 a CT 09-20)
  // ==========================================
  it("CT 09-10: Criar pelada válida (Create)", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/nova");
    cy.get('[data-cy="pelada-local"]').select("1");
    cy.get('[data-cy="pelada-data"]').type("2027-05-15");
    cy.get('[data-cy="pelada-hora"]').type("19:30");
    cy.get('[data-cy="pelada-vagas"]').type("10");
    cy.get('[data-cy="pelada-valor"]').type("15");
    cy.get('[data-cy="pelada-nivel"]').select("Casual");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.url().should("include", "/minhas-peladas");
    cy.get('[data-cy="minha-pelada"]').should("have.length", 2);
  });

  it("CT 09-11: Criar pelada sem campo obrigatório", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/nova");
    cy.get('[data-cy="pelada-hora"]').type("19:30");
    cy.get('[data-cy="pelada-vagas"]').type("10");
    cy.get('[data-cy="pelada-valor"]').type("15");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="pelada-erro"]').should("be.visible");
  });

  it("CT 09-12: Criar pelada com vagas zero", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/nova");
    cy.get('[data-cy="pelada-data"]').type("2027-05-15");
    cy.get('[data-cy="pelada-hora"]').type("19:30");
    cy.get('[data-cy="pelada-vagas"]').type("0");
    cy.get('[data-cy="pelada-valor"]').type("15");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="pelada-erro"]').should("contain", "maiores que zero");
  });

  it("CT 09-13: Criar pelada com valor negativo", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/nova");
    cy.get('[data-cy="pelada-data"]').type("2027-05-15");
    cy.get('[data-cy="pelada-hora"]').type("19:30");
    cy.get('[data-cy="pelada-vagas"]').type("10");
    cy.get('[data-cy="pelada-valor"]').type("-10");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="pelada-erro"]').should("contain", "negativo");
  });

  it("CT 09-14: Criar pelada com data no passado", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/nova");
    cy.get('[data-cy="pelada-data"]').type("2020-01-10");
    cy.get('[data-cy="pelada-hora"]').type("19:30");
    cy.get('[data-cy="pelada-vagas"]').type("10");
    cy.get('[data-cy="pelada-valor"]').type("15");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="pelada-erro"]').should("contain", "Data inválida");
  });

  it("CT 09-15: Listar minhas peladas (Read)", () => {
    loginComo("u1@peladas.com");
    cy.visit("/minhas-peladas");
    cy.get('[data-cy="minha-pelada"]').should("have.length", 1);
    cy.get('[data-cy="minha-pelada"]').first().should("contain", "Arena Boa Viagem");
  });

  it("CT 09-16: Editar pelada (Update)", () => {
    loginComo("u1@peladas.com");
    cy.visit("/minhas-peladas");
    cy.get('[data-cy="editar"]').first().click();
    cy.get('[data-cy="pelada-vagas"]').clear().type("8");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="minha-pelada"]').first().should("contain", "8 de 8");
  });

  it("CT 09-17: Editar pelada com dado inválido", () => {
    loginComo("u1@peladas.com");
    cy.visit("/minhas-peladas");
    cy.get('[data-cy="editar"]').first().click();
    cy.get('[data-cy="pelada-vagas"]').clear().type("0");
    cy.get('[data-cy="pelada-salvar"]').click();
    cy.get('[data-cy="pelada-erro"]').should("be.visible");
  });

  it("CT 09-18: Excluir pelada com confirmação (Delete)", () => {
    loginComo("u1@peladas.com");
    cy.visit("/minhas-peladas");
    cy.get('[data-cy="excluir"]').first().click();
    cy.get('[data-cy="confirmar-exclusao"]').first().click();
    cy.get('[data-cy="minha-pelada"]').should("not.exist");
  });

  it("CT 09-19: Cancelar a confirmação de exclusão", () => {
    loginComo("u1@peladas.com");
    cy.visit("/minhas-peladas");
    cy.get('[data-cy="excluir"]').first().click();
    cy.contains("button", "Cancelar").click();
    cy.get('[data-cy="minha-pelada"]').should("have.length", 1);
  });

  it("CT 09-20: Editar pelada de outro organizador", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1/editar");
    cy.url().should("include", "/minhas-peladas");
  });

  // ==========================================
  // 9.4 BUSCA DE PELADAS (CT 09-21 a CT 09-23)
  // ==========================================
  it("CT 09-21: Buscar com filtro", () => {
    loginComo("u2@peladas.com");
    cy.get('[data-cy="busca-local"]').type("Boa Viagem");
    cy.get('[data-cy="busca-enviar"]').click();
    cy.get('[data-cy="pelada-card"]').should("have.length", 1);
  });

  it("CT 09-22: Buscar sem resultados", () => {
    loginComo("u2@peladas.com");
    cy.get('[data-cy="busca-local"]').type("BairroInexistenteXYZ");
    cy.get('[data-cy="busca-enviar"]').click();
    cy.get('[data-cy="pelada-card"]').should("not.exist");
    cy.get('[data-cy="sem-resultados"]').should("be.visible");
  });

  it("CT 09-23: Abrir detalhes da pelada", () => {
    loginComo("u2@peladas.com");
    cy.get('[data-cy="ver-detalhes"]').first().click();
    cy.contains("Arena Boa Viagem").should("be.visible");
    cy.get('[data-cy="abrir-whatsapp"]').should("not.exist");
  });

  // ==========================================
  // 9.5 SOLICITAÇÃO DE VAGA (CT 09-24 a CT 09-28)
  // ==========================================
  it("CT 09-24: Solicitar vaga", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="pedido"]').should("have.length", 1);
    cy.get('[data-cy="pedido-status"]').should("contain", "Pendente");
  });

  it("CT 09-25: Solicitar a mesma vaga duas vezes", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();
    cy.get('[data-cy="solicitar-vaga"]').should("not.exist");
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="pedido"]').should("have.length", 1);
  });

  it("CT 09-26: Organizador solicita a própria pelada", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').should("not.exist");
  });

  it("CT 09-27: Solicitar vaga em pelada lotada", () => {
    loginComo("u1@peladas.com");
    cy.visit("/pelada/1/editar");
    cy.get('[data-cy="pelada-vagas"]').clear().type("1");
    cy.get('[data-cy="pelada-salvar"]').click();

    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();

    loginComo("u1@peladas.com");
    cy.visit("/solicitacoes");
    cy.get('[data-cy="aceitar"]').first().click();

    loginComo("u3@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();
    cy.contains("Pelada lotada").should("be.visible");
  });

  it("CT 09-28: Cancelar solicitação", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="cancelar-solicitacao"]').click();
    cy.get('[data-cy="pedido-status"]').should("contain", "Cancelada");
  });

  // ==========================================
  // 9.6 ACEITE E RECUSA (CT 09-29 a CT 09-31)
  // ==========================================
  it("CT 09-29 e CT 09-30: Aceitar e recusar solicitação", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();

    loginComo("u3@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();

    loginComo("u1@peladas.com");
    cy.visit("/solicitacoes");
    cy.get('[data-cy="aceitar"]').first().click();
    cy.get('[data-cy="vagas-livres"]').should("contain", "1");

    cy.get('[data-cy="recusar"]').first().click();
    cy.get('[data-cy="vagas-livres"]').should("contain", "1");
  });

  it("CT 09-31: Aceitar sem vaga livre", () => {
    cy.visit("/cadastro");
    cy.get('[data-cy="cadastro-nome"]').type("Jogador U4");
    cy.get('[data-cy="cadastro-email"]').type("u4@peladas.com");
    cy.get('[data-cy="cadastro-senha"]').type("123456");
    cy.get('[data-cy="cadastro-enviar"]').click();

    ["u2@peladas.com", "u3@peladas.com", "u4@peladas.com"].forEach((email) => {
      loginComo(email);
      cy.visit("/pelada/1");
      cy.get('[data-cy="solicitar-vaga"]').click();
    });

    loginComo("u1@peladas.com");
    cy.visit("/solicitacoes");
    cy.get('[data-cy="aceitar"]').first().click();
    cy.get('[data-cy="aceitar"]').first().click();
    cy.get('[data-cy="vagas-livres"]').should("contain", "0");
    cy.get('[data-cy="aceitar"]').first().click();
    cy.contains("Sem vagas livres").should("be.visible");
  });

  // ==========================================
  // 9.7 WHATSAPP (CT 09-32 a CT 09-34)
  // ==========================================
  it("CT 09-32, CT 09-33 e CT 09-34: Visibilidade do WhatsApp conforme status", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="abrir-whatsapp"]').should("not.exist");

    loginComo("u3@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();

    loginComo("u1@peladas.com");
    cy.visit("/solicitacoes");
    cy.get('[data-cy="aceitar"]').first().click();
    cy.get('[data-cy="recusar"]').first().click();

    loginComo("u2@peladas.com");
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="abrir-whatsapp"]')
      .should("be.visible")
      .and("have.attr", "href")
      .and("include", "wa.me/5581999990001");

    loginComo("u3@peladas.com");
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="abrir-whatsapp"]').should("not.exist");
  });

  // ==========================================
  // 9.8 AVALIAÇÃO (CT 09-35 a CT 09-37)
  // ==========================================
  it("CT 09-35, CT 09-36 e CT 09-37: Avaliar participante", () => {
    loginComo("u2@peladas.com");
    cy.visit("/pelada/1");
    cy.get('[data-cy="solicitar-vaga"]').click();

    loginComo("u1@peladas.com");
    cy.visit("/solicitacoes");
    cy.get('[data-cy="aceitar"]').first().click();

    loginComo("u2@peladas.com");
    cy.visit("/meus-pedidos");
    cy.get('[data-cy="avaliar"]').click();

    // CT 09-37: Autoavaliação
    cy.get('[data-cy="avaliacao-participante"]').select("2");
    cy.get('[data-cy="avaliacao-nota"]').clear().type("5");
    cy.get('[data-cy="avaliacao-enviar"]').click();
    cy.get('[data-cy="avaliacao-erro"]').should("contain", "a si mesmo");

    // CT 09-36: Nota fora do intervalo
    cy.get('[data-cy="avaliacao-participante"]').select("1");
    cy.get('[data-cy="avaliacao-nota"]').invoke("removeAttr", "max").clear().type("6");
    cy.get('[data-cy="avaliacao-enviar"]').click();
    cy.get('[data-cy="avaliacao-erro"]').should("contain", "entre 1 e 5");

    // CT 09-35: Nota válida
    cy.get('[data-cy="avaliacao-participante"]').select("1");
    cy.get('[data-cy="avaliacao-nota"]').clear().type("5");
    cy.get('[data-cy="avaliacao-enviar"]').click();
    cy.url().should("include", "/meus-pedidos");
    cy.contains("Avaliação registrada com sucesso").should("be.visible");
  });
});