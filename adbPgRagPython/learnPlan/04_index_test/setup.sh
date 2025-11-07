#!/bin/bash
# 索引优化学习项目环境设置脚本

echo "============================================================"
echo "索引优化学习项目 - 环境设置"
echo "============================================================"

# 检查 conda 环境
if ! command -v conda &> /dev/null; then
    echo "❌ 未找到 conda 命令，请先安装 conda"
    exit 1
fi

# 激活环境
echo ""
echo "1. 激活 conda 环境 py_311_rag..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate py_311_rag

if [ $? -ne 0 ]; then
    echo "❌ 无法激活环境 py_311_rag"
    echo "   请先创建环境: conda create -n py_311_rag python=3.11"
    exit 1
fi

echo "✅ 环境已激活: $(which python)"

# 安装依赖
echo ""
echo "2. 安装 Python 依赖包..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖包安装成功"
else
    echo "❌ 依赖包安装失败"
    exit 1
fi

# 测试导入
echo ""
echo "3. 测试模块导入..."
python test_imports.py

echo ""
echo "============================================================"
echo "环境设置完成！"
echo "============================================================"
echo ""
echo "💡 下一步："
echo "   1. 生成测试数据:"
echo "      python data_generation/generate_test_data.py --count 5000"
echo ""
echo "   2. 运行性能测试:"
echo "      python performance_testing/benchmark_indexes.py"
echo ""

