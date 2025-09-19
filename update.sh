#!/bin/bash
# update.sh - 自动提交并推送到 GitHub

# 提示用户输入本次提交说明
read -p "Enter commit message: " msg

# 检查是否输入为空
if [ -z "$msg" ]; then
    echo "Commit message cannot be empty."
    exit 1
fi

# 添加所有修改
git add .

# 提交
git commit -m "$msg"

# 推送到当前分支（假设已绑定远程）
git push

echo "✅ Code pushed to GitHub successfully!"
