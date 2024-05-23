@echo off
chcp 65001 >nul
title ddns-py-huawei
python ddns.py
echo >nul
echo ==============================================
echo 程序已退出，按任意键关闭...
pause >nul
