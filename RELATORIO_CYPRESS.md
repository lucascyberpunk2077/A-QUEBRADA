# 🌐 Relatório de Testes End-to-End (E2E) — Cypress

Este documento registra a validação automatizada de interface e fluxos completos de usuário (E2E) da plataforma **A QUEBRADA**, executada diretamente no navegador via **Cypress**[cite: 1].

---

## ⚙️ Ambiente e Execução

- **Aplicação:** Flask + SQLite + Jinja2 (`http://127.0.0.1:5001`)
- **Framework E2E:** Cypress
- **Comando de Execução:**
  ```bash
  npx cypress run