#!/usr/bin/env bash
# Deploy NP-NG (frontend Quasar + backend FastAPI) para o servidor via SSH/rsync.
#
# Variáveis (opcional):
#   DEPLOY_USER=root
#   DEPLOY_HOST=209.38.203.28
#   DEPLOY_PATH=/opt/npng
#   DOMAIN=app.exemplo.com   # só mostra lembrete certbot ao final
#
# Uso: a partir da raiz do projeto:
#   chmod +x scripts/deploy.sh
#   ./scripts/deploy.sh
#
# Pré-requisitos no servidor: Python 3.10+, PostgreSQL, Nginx, venv, .env, systemd e site Nginx
# (ver ficheiros em deploy/).

set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-root}"
DEPLOY_HOST="${DEPLOY_HOST:-209.38.203.28}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/npng}"
DOMAIN="${DOMAIN:-}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend/app-npng"
BACKEND_DIR="${ROOT_DIR}/backend"
SSH_TARGET="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "==> Build do frontend"
cd "${FRONTEND_DIR}"
if [[ -f "${FRONTEND_DIR}/.env.production" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${FRONTEND_DIR}/.env.production"
  set +a
fi
npm run build

echo "==> rsync backend (sem .venv)"
rsync -avz --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${BACKEND_DIR}/" "${SSH_TARGET}:${DEPLOY_PATH}/backend/"

echo "==> rsync frontend estático (dist/pwa)"
rsync -avz --delete \
  "${FRONTEND_DIR}/dist/pwa/" "${SSH_TARGET}:${DEPLOY_PATH}/frontend/"

echo "==> Remoto: pip, alembic, serviços"
ssh "${SSH_TARGET}" bash -s -- "${DEPLOY_PATH}" <<'REMOTE'
set -euo pipefail
DEPLOY_PATH="$1"
cd "${DEPLOY_PATH}/backend"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
if systemctl is-active --quiet npng-api 2>/dev/null; then
  sudo systemctl restart npng-api
fi
if command -v nginx >/dev/null 2>&1; then
  sudo nginx -t && sudo systemctl reload nginx
fi
echo "Backend atualizado em ${DEPLOY_PATH}"
REMOTE

if [[ -n "${DOMAIN}" ]]; then
  echo ""
  echo "Lembrete HTTPS (no servidor, uma vez por domínio):"
  echo "  sudo certbot --nginx -d ${DOMAIN}"
fi

echo ""
echo "Deploy concluído."
