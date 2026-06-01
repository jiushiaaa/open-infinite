#!/usr/bin/env bash
set -euo pipefail

BACKEND_PORT=8765
FRONTEND_PORT=5173
SKIP_INSTALL=0
NO_BROWSER=0
CHECK_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend-port)
      BACKEND_PORT="$2"
      shift 2
      ;;
    --frontend-port)
      FRONTEND_PORT="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
      ;;
    --no-browser)
      NO_BROWSER=1
      shift
      ;;
    --check-only)
      CHECK_ONLY=1
      shift
      ;;
    *)
      echo "未知参数：$1" >&2
      exit 2
      ;;
  esac
done

log() {
  printf '[LNE] %s\n' "$1"
}

require_command() {
  local name="$1"
  local hint="$2"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "$name 未找到。$hint" >&2
    exit 1
  fi
}

wait_http() {
  local url="$1"
  local seconds="${2:-45}"
  local start
  start="$(date +%s)"
  while true; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    if (( "$(date +%s)" - start >= seconds )); then
      echo "等待本地服务超时：$url" >&2
      exit 1
    fi
    sleep 1
  done
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENGINE_DIR="$ROOT_DIR/engine"
UI_DIR="$ENGINE_DIR/ui"
VENV_DIR="$ENGINE_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
LOG_DIR="$ROOT_DIR/.local-run"

log "项目目录：$ROOT_DIR"

require_command python3 "请先安装 Python 3.10+。"
require_command node "请先安装 Node.js 18+。"

if ! command -v pnpm >/dev/null 2>&1; then
  if command -v corepack >/dev/null 2>&1; then
    log "未找到 pnpm，尝试通过 corepack 启用。"
    corepack enable
  fi
fi
require_command pnpm "请安装 pnpm，或运行 corepack enable 后重试。"

log "Python：$(command -v python3)"
log "Node：$(command -v node)"
log "pnpm：$(command -v pnpm)"

if [[ "$CHECK_ONLY" == "1" ]]; then
  log "检查完成；未安装依赖，也未启动服务。"
  exit 0
fi

if [[ "$SKIP_INSTALL" == "0" ]]; then
  if [[ ! -x "$PYTHON_BIN" ]]; then
    log "创建 Python 虚拟环境。"
    python3 -m venv "$VENV_DIR"
  fi
  log "安装后端依赖。"
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -e "$ENGINE_DIR"

  log "安装前端依赖。"
  (cd "$UI_DIR" && pnpm install)
else
  log "已跳过依赖安装。"
fi

mkdir -p "$LOG_DIR"

BACKEND_URL="http://127.0.0.1:$BACKEND_PORT/api/settings/model-configuration"
FRONTEND_URL="http://127.0.0.1:$FRONTEND_PORT/"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  log "本地服务已停止。"
}
trap cleanup EXIT INT TERM

log "启动后端：http://127.0.0.1:$BACKEND_PORT/"
(cd "$ENGINE_DIR" && "$PYTHON_BIN" -m living_novel_engine.cli browse --host 127.0.0.1 --port "$BACKEND_PORT" --no-open) >"$LOG_DIR/backend.log" 2>"$LOG_DIR/backend.err.log" &
BACKEND_PID="$!"

log "启动前端：$FRONTEND_URL"
(cd "$UI_DIR" && pnpm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT") >"$LOG_DIR/frontend.log" 2>"$LOG_DIR/frontend.err.log" &
FRONTEND_PID="$!"

wait_http "$BACKEND_URL"
wait_http "$FRONTEND_URL"

log "本地服务已启动。"
printf '前端入口：%s\n' "$FRONTEND_URL"
printf '后端入口：http://127.0.0.1:%s/\n' "$BACKEND_PORT"
printf '日志目录：%s\n' "$LOG_DIR"

if [[ "$NO_BROWSER" == "0" ]]; then
  if command -v open >/dev/null 2>&1; then
    open "$FRONTEND_URL"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$FRONTEND_URL" >/dev/null 2>&1 || true
  fi
fi

read -r -p "按回车停止本地服务"
