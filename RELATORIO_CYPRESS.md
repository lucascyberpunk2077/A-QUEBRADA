# 🌐 Relatório de Testes End-to-End (E2E) — Cypress

Este documento registra a validação automatizada de interface e fluxos completos de usuário (E2E) da plataforma **A QUEBRADA**, executada diretamente no navegador via **Cypress**.

---

## ⚙️ Ambiente e Execução

- **Aplicação:** Flask + SQLite + Jinja2 (`http://127.0.0.1:5001`)
- **Framework E2E:** Cypress (`peladas_e2e.cy.js`)
- **Comando de Execução:**
  ```bash
  npx cypress run

  ✅ Fluxos End-to-End Validados no NavegadorMódulo / SuiteCasos de Teste E2EComportamento Validado na InterfaceStatusAutenticação & SessãoCT 09-01 a CT 09-09Login válido, erro de credenciais, logout, bloqueio de histórico após sair e proteção de rotas privadas.✅ PASSBusca & FiltrosCT 09-21 a CT 09-23Filtragem por localidade (data-cy="busca-local"), exibição de cards de arenas e acesso aos detalhes (/pelada/<id>).✅ PASSCRUD de PeladasCT 09-10 a CT 09-20Criação, edição, validação de campos obrigatórios/datas/vagas/valores e exclusão confirmada em Minhas Peladas.✅ PASSSolicitações & WhatsAppCT 01-01, CT 01-03, CT 01-04, CT 01-12Envio de solicitação de vaga, bloqueio de duplicidade, aceite pelo organizador, atualização de vagas e liberação do link wa.me/.✅ PASSAvaliaçõesCT 06-01, CT 06-02Avaliação pós-jogo (nota 1 a 5 e comentário) entre participantes confirmados e bloqueio de autoavaliação.✅ PASS

  ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Tests:        32                                                                               │
  │ Passing:      32                                                                               │
  │ Failing:      0                                                                                │
  │ Pending:      0                                                                                │
  │ Skipped:      0                                                                                │
  │ Screenshots:  0                                                                                │
  │ Video:        false                                                                            │
  │ Duration:     57 seconds                                                                       │
  │ Spec Ran:     peladas_e2e.cy.js                                                                │
  └────────────────────────────────────────────────────────────────────────────────────────────────┘

  ✔  peladas_e2e.cy.js                        00:57       32       32        -        -        - │
  └────────────────────────────────────────────────────────────────────────────────────────────────┘
    ✔  All specs passed!                        00:57       32       32        -        -        -