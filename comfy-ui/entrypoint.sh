#!/usr/bin/env bash

# ComfyUI Docker Startup File v1.0.2 by John Aldred
# http://www.johnaldred.com
# http://github.com/kaouthia

set -e

# --- Force ComfyUI-Manager config (uv off, no file logging, safe DB) ---
# Make sure user dirs exist and are writable (handles Windows bind mounts)
mkdir -p /app/ComfyUI/user /app/ComfyUI/user/default
chown -R "$(id -u)":"$(id -g)" /app/ComfyUI/user || true
chmod -R u+rwX /app/ComfyUI/user || true

CFG_DIR="/app/ComfyUI/user/default/ComfyUI-Manager"
CFG_FILE="$CFG_DIR/config.ini"
DB_DIR="$CFG_DIR"
DB_PATH="${DB_DIR}/manager.db"
SQLITE_URL="sqlite:////${DB_PATH}"

mkdir -p "$CFG_DIR"

if [ ! -f "$CFG_FILE" ]; then
  echo "↳ Creating ComfyUI-Manager config.ini (uv OFF, no file logging, DB cache)"
  cat > "$CFG_FILE" <<EOF
[default]
use_uv = False
file_logging = False
db_mode = cache
database_url = ${SQLITE_URL}
EOF
else
  echo "↳ Updating ComfyUI-Manager config.ini (uv OFF, no file logging, DB cache)"
  # use_uv = False
  grep -q '^use_uv' "$CFG_FILE" \
    && sed -i 's/^use_uv.*/use_uv = False/' "$CFG_FILE" \
    || printf '\nuse_uv = False\n' >> "$CFG_FILE"

  # file_logging = False (and drop any existing log_path line)
  grep -q '^file_logging' "$CFG_FILE" \
    && sed -i 's/^file_logging.*/file_logging = False/' "$CFG_FILE" \
    || printf '\nfile_logging = False\n' >> "$CFG_FILE"
  sed -i '/^log_path[[:space:]=]/d' "$CFG_FILE" || true

  # db_mode = cache (prevents file DB usage)
  grep -q '^db_mode' "$CFG_FILE" \
    && sed -i 's/^db_mode.*/db_mode = cache/' "$CFG_FILE" \
    || printf '\ndb_mode = cache\n' >> "$CFG_FILE"

  # Provide a safe DB URL anyway (future-proof if Manager flips off cache)
  grep -q '^database_url' "$CFG_FILE" \
    && sed -i "s|^database_url.*|database_url = ${SQLITE_URL}|" "$CFG_FILE" \
    || printf "database_url = ${SQLITE_URL}\n" >> "$CFG_FILE"
fi


# --- Prepare custom nodes ---
CN_DIR=/app/ComfyUI/custom_nodes
INIT_MARKER="$CN_DIR/.custom_nodes_initialized"

declare -A REPOS=(
  ["ComfyUI-Manager"]="https://github.com/ltdrdata/ComfyUI-Manager.git"
  ["ComfyUI_essentials"]="https://github.com/cubiq/ComfyUI_essentials.git"
  ["ComfyUI-Crystools"]="https://github.com/crystian/ComfyUI-Crystools.git"
  ["rgthree-comfy"]="https://github.com/rgthree/rgthree-comfy.git"
  ["ComfyUI-KJNodes"]="https://github.com/kijai/ComfyUI-KJNodes.git"
  ["ComfyUI_UltimateSDUpscale"]="https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git"
  ["ComfyUI_IPAdapter_plus"]="https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"
  ["A8R8_ComfyUI_nodes"]="https://github.com/ramyma/A8R8_ComfyUI_nodes.git"
)

if [ ! -f "$INIT_MARKER" ]; then
  echo "↳ First run: initializing custom_nodes…"
  mkdir -p "$CN_DIR"
  for name in "${!REPOS[@]}"; do
    url="${REPOS[$name]}"
    target="$CN_DIR/$name"
    if [ -d "$target" ]; then
      echo "  ↳ $name already exists, skipping clone"
    else
      echo "  ↳ Cloning $name"
      git clone --depth 1 "$url" "$target"
    fi
  done

  echo "↳ Installing/upgrading dependencies…"
  for dir in "$CN_DIR"/*/; do
    req="$dir/requirements.txt"
    if [ -f "$req" ]; then
      echo "  ↳ pip install --upgrade -r $req"
      python -m pip install --no-cache-dir --upgrade -r "$req"
    fi
  done

  # Create marker file
  touch "$INIT_MARKER"
else
  echo "↳ Custom nodes already initialized, skipping clone and dependency installation."
fi

# --- Download checkpoints and LoRAs ---
MODEL_DIR="/app/ComfyUI/models/checkpoints"
LORA_DIR="/app/ComfyUI/models/loras"

mkdir -p "$MODEL_DIR" "$LORA_DIR"

# Пример списка файлов для загрузки
declare -A CHECKPOINTS=(
  ["juggernautXL_ragnarokBy.safetensors"]="https://civitai.com/api/download/models/1759168?type=Model&format=SafeTensor&size=full&fp=fp16&token=${CIVITAI_TOKEN}"
)

declare -A LORAS=(
  ["Cartoon_Saloon_Style_XL_kk-000009.safetensors"]="https://civitai.com/api/download/models/204327?type=Model&format=SafeTensor&token=${CIVITAI_TOKEN}"
)

echo "↳ Checking for missing checkpoints and LoRAs..."

for name in "${!CHECKPOINTS[@]}"; do
  path="$MODEL_DIR/$name"
  if [ ! -f "$path" ]; then
    echo "  ↳ Downloading checkpoint: $name"
    wget -q --show-progress -O "$path" "${CHECKPOINTS[$name]}"
  else
    echo "  ↳ $name already present"
  fi
done

for name in "${!LORAS[@]}"; do
  path="$LORA_DIR/$name"
  if [ ! -f "$path" ]; then
    echo "  ↳ Downloading LoRA: $name"
    wget -q --show-progress -O "$path" "${LORAS[$name]}"
  else
    echo "  ↳ $name already present"
  fi
done

# --- Download IPAdapter and CLIP models ---
echo "↳ Checking for IPAdapter and CLIP models..."

CLIP_DIR="/app/ComfyUI/models/clip_vision"
IPADAPTER_DIR="/app/ComfyUI/models/ipadapter"
mkdir -p "$CLIP_DIR" "$IPADAPTER_DIR"

declare -A CLIP_MODELS=(
  ["CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"]="https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
  ["CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors"]="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors"
)

declare -A IP_MODELS=(
  ["ip-adapter-plus_sdxl_vit-h.safetensors"]="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"
)

for name in "${!CLIP_MODELS[@]}"; do
  path="$CLIP_DIR/$name"
  if [ ! -f "$path" ]; then
    echo "  ↳ Downloading CLIP model: $name"
    wget -q --show-progress -O "$path" "${CLIP_MODELS[$name]}"
  else
    echo "  ↳ CLIP model $name already present"
  fi
done

for name in "${!IP_MODELS[@]}"; do
  path="$IPADAPTER_DIR/$name"
  if [ ! -f "$path" ]; then
    echo "  ↳ Downloading IPAdapter model: $name"
    wget -q --show-progress -O "$path" "${IP_MODELS[$name]}"
  else
    echo "  ↳ IPAdapter model $name already present"
  fi
done

echo "↳ Launching ComfyUI"
exec "$@"