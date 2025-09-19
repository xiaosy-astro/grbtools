#!/bin/bash
# update.sh - 自动提交并推送到 GitHub

# 提示用户输入要提交的文件或文件夹（可多个，用空格分隔）
read -p "Enter file(s) or directory(ies) to commit (separated by space): " targets

# 检查输入是否为空
if [ -z "$targets" ]; then
    echo "File or directory cannot be empty."
    exit 1
fi

# 提示用户输入提交说明
read -p "Enter commit message: " msg

# 检查输入是否为空
if [ -z "$msg" ]; then
    echo "Commit message cannot be empty."
    exit 1
fi

# 添加指定文件或文件夹（支持多个）
git add $targets

# 提交
git commit -m "$msg"

# 推送到当前分支（假设已绑定远程）
git push

echo "✅ Code pushed to GitHub successfully!"
