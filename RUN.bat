@echo off

rem このバッチファイルにJsonファイルをドラッグ＆ドロップすると、そのJsonファイルとサーバーから取得した情報を比較します
rem このバッチファイルを直接実行すると、Jsonフォルダ内の最新のJsonファイルとサーバーから取得した情報を比較します

cd %~dp0
python BpBugList.py %1
pause