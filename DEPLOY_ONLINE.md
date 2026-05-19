# Publicacao online do Icaro

## Rotas principais

- `/` ou `/landing`: landing page publica.
- `/login`: entrada com usuario e senha.
- `/app`: area de trabalho protegida.
- `/auth/logout`: encerra a sessao.
- `/health`: verificacao simples do servidor.

## Variaveis de ambiente

Defina estas variaveis no servidor antes de iniciar:

```powershell
$env:ICARO_AUTH_USER="seu_usuario"
$env:ICARO_AUTH_PASSWORD="sua_senha_forte"
$env:ICARO_AUTH_SECRET="um_segredo_longo_aleatorio"
$env:ICARO_COOKIE_SECURE="1"
```

Em ambiente local sem HTTPS, use `ICARO_COOKIE_SECURE=0`.

## Comando de servidor

```powershell
.\venv\Scripts\uvicorn.exe api:app --host 0.0.0.0 --port 8100
```

Em Linux:

```bash
uvicorn api:app --host 0.0.0.0 --port "${PORT:-8100}"
```

## Observacoes para producao

- Use HTTPS no dominio publico.
- Troque sempre `ICARO_AUTH_USER`, `ICARO_AUTH_PASSWORD` e `ICARO_AUTH_SECRET`.
- Faca backup periodico da pasta `data`, pois o banco SQLite fica nela.
- Se usar Render, Railway, Fly.io ou VPS, configure o comando de start acima e persista a pasta de dados quando o provedor permitir.
