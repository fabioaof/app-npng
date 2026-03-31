#!/usr/bin/env bash
# Deploy NP-NG (frontend Quasar + backend FastAPI em Docker) para o servidor via SSH/rsync.
#
# Variáveis (opcional):
#   DEPLOY_USER=root
#   DEPLOY_HOST=209.38.203.28
#   DEPLOY_PATH_FRONTEND=/var/www/nopain-nogain
#   DEPLOY_PATH_API=/var/www/nopain-nogain-api
#
# Uso: a partir da raiz do projeto:
#   chmod +x scripts/deploy.sh
#   ./scripts/deploy.sh
#
# No servidor: Docker + Docker Compose, Nginx, e ficheiro .env em DEPLOY_PATH_API
# (ver deploy/env.docker.example e deploy/nginx-*.example).

set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-root}"
DEPLOY_HOST="${DEPLOY_HOST:-209.38.203.28}"
DEPLOY_PATH_FRONTEND="${DEPLOY_PATH_FRONTEND:-/var/www/nopain-nogain}"
DEPLOY_PATH_API="${DEPLOY_PATH_API:-/var/www/nopain-nogain-api}"

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

echo "==> rsync backend + compose"
rsync -avz --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${BACKEND_DIR}/" "${SSH_TARGET}:${DEPLOY_PATH_API}/backend/"

rsync -avz "${ROOT_DIR}/docker-compose.yml" "${SSH_TARGET}:${DEPLOY_PATH_API}/"

echo "==> rsync frontend estático (Quasar PWA: dist/pwa -> servidor dist/)"
rsync -avz --delete \
  "${FRONTEND_DIR}/dist/pwa/" "${SSH_TARGET}:${DEPLOY_PATH_FRONTEND}/dist/"

echo "==> Remoto: Docker Compose (build + up)"
ssh "${SSH_TARGET}" bash -s -- "${DEPLOY_PATH_API}" <<'REMOTE'
set -euo pipefail
DEPLOY_PATH_API="$1"
cd "${DEPLOY_PATH_API}"
if [[ ! -f .env ]]; then
  echo "Erro: falta ${DEPLOY_PATH_API}/.env"
  echo "Copia deploy/env.docker.example para o servidor como .env e define segredos."
  exit 1
fi
docker compose build api
docker compose up -d
if command -v nginx >/dev/null 2>&1; then
  sudo nginx -t && sudo systemctl reload nginx
fi
echo "API atualizada em ${DEPLOY_PATH_API}"
REMOTE

echo ""
echo "Deploy concluído."
