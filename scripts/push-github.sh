#!/bin/bash
# 推送代码到 GitHub 脚本

echo "🚀 准备推送到 GitHub..."
echo ""
echo "请执行以下命令手动推送："
echo ""
echo "  cd /root/.openclaw/workspace/ai-tetris"
echo "  git remote -v  # 确认远程仓库"
echo "  git push origin main"
echo ""
echo "或者设置 Git 凭证后再次尝试："
echo "  git config --global credential.helper store"
echo "  git push origin main"
echo ""

# 检查远程仓库
if git remote -v | grep -q "origin"; then
    echo "✅ 远程仓库已配置:"
    git remote -v
    echo ""
    echo "现在可以运行：git push origin main"
else
    echo "⚠️  未找到远程仓库，请先添加："
    echo "  git remote add origin https://github.com/nanfeng2021/ai-tetris.git"
fi
