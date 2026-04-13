#!/usr/bin/env bash
set -euo pipefail

install_base_packages() {
  local packages=(git python3 python3-venv python3-pip)
  if [ "$#" -gt 0 ]; then
    packages+=("$@")
  fi
  apt-get install -y "${packages[@]}"
}

merge_dir_into_target() {
  local source_dir="$1"
  local target_dir="$2"
  mkdir -p "$target_dir"
  if [ -d "$source_dir" ]; then
    cp -a "$source_dir"/. "$target_dir"/
    rm -rf "$source_dir"
  fi
}

adopt_runtime_path() {
  local app_dir="$1"
  local runtime_dir="$2"
  local app_rel="$3"
  local runtime_rel="$4"

  local source_path="$app_dir/$app_rel"
  local target_path="$runtime_dir/$runtime_rel"

  if [ -L "$source_path" ]; then
    return
  fi

  if [ ! -e "$source_path" ]; then
    return
  fi

  mkdir -p "$(dirname "$target_path")"

  if [ -d "$source_path" ] && [ ! -f "$source_path" ]; then
    if [ -e "$target_path" ]; then
      merge_dir_into_target "$source_path" "$target_path"
    else
      mv "$source_path" "$target_path"
    fi
    return
  fi

  if [ -e "$target_path" ]; then
    rm -f "$source_path"
  else
    mv "$source_path" "$target_path"
  fi
}

ensure_git_checkout() {
  local app_dir="$1"
  local repo_url="$2"
  local branch="$3"
  local timestamp
  timestamp="$(date +%Y%m%d-%H%M%S)"

  if [ -d "$app_dir/.git" ]; then
    git -C "$app_dir" fetch --prune --depth 1 origin "$branch"
    git -C "$app_dir" checkout "$branch"
    git -C "$app_dir" reset --hard "origin/$branch"
    return
  fi

  local tmp_clone="${app_dir}.clone-${timestamp}"
  rm -rf "$tmp_clone"
  git clone --depth 1 --branch "$branch" "$repo_url" "$tmp_clone"

  if [ -e "$app_dir" ]; then
    mv "$app_dir" "${app_dir}.legacy-${timestamp}"
  fi

  mv "$tmp_clone" "$app_dir"
}

link_runtime_path() {
  local app_dir="$1"
  local runtime_dir="$2"
  local app_rel="$3"
  local runtime_rel="$4"

  local app_path="$app_dir/$app_rel"
  local runtime_path="$runtime_dir/$runtime_rel"

  mkdir -p "$(dirname "$app_path")"
  mkdir -p "$(dirname "$runtime_path")"
  rm -rf "$app_path"
  ln -s "$runtime_path" "$app_path"
}
