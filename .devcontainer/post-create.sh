#!/bin/bash
set -e

# 安装基础工具
uv pip install autopep8 flake8 isort -i https://mirrors.aliyun.com/pypi/simple && \
apt update -y && apt install -y git ssh zsh autojump curl git-flow

# 安装 Oh My Zsh
if [ ! -d ~/.oh-my-zsh ]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# 安装插件
plugins=(
  "zsh-users/zsh-autosuggestions"
  "zsh-users/zsh-syntax-highlighting"
)

for plugin in "${plugins[@]}"; do
  repo_name=$(basename $plugin)
  if [ ! -d ~/.oh-my-zsh/custom/plugins/$repo_name ]; then
    git clone --depth=1 https://github.com/$plugin.git ~/.oh-my-zsh/custom/plugins/$repo_name
  fi
done

# 安装主题
if [ ! -d ~/.oh-my-zsh/custom/themes/powerlevel10k ]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k
fi

# 应用自定义配置
if [ -f /workspace/.devcontainer/zshrc-config ]; then
  cp /workspace/.devcontainer/zshrc-config ~/.zshrc
else
  # 若没有自定义配置，生成基础 .zshrc
  cat << EOF > ~/.zshrc
export ZSH="\$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git zsh-autosuggestions zsh-syntax-highlighting autojump)
source \$ZSH/oh-my-zsh.sh

# 启用 autojump
[[ -s /usr/share/autojump/autojump.sh ]] && source /usr/share/autojump/autojump.sh
EOF
fi

# 确保 autojump 配置生效（即使已有自定义配置）
if ! grep -q "autojump.sh" ~/.zshrc; then
  echo '[[ -s /usr/share/autojump/autojump.sh ]] && source /usr/share/autojump/autojump.sh' >> ~/.zshrc
fi
ln -s /opt/.uv.venv /app/.venv
echo "Post-create setup completed!"