# PyInstaller Troubleshooting

## 問題
打包後執行報錯：
```
ModuleNotFoundError: No module named 'genshin_spire'
```

## 原因
`main.py` 在 `if __name__ == "__main__"` 時才將 `src/` 加入 `sys.path`，但 PyInstaller 的靜態分析器在 **import 階段**找不到 `genshin_spire` 包，因此沒有把它打入執行檔。

## 修復
在 `build.bat` 加入 `--paths "src"`，告訴 PyInstaller 去 `src/` 目錄找 Python 模組：

```batch
py -3 -m PyInstaller --onefile --name "GenshinSpire" --windowed ^
  --paths "src" ^
  --add-data "images;images" --add-data "audio;audio" ^
  main.py
```

## 驗證步驟
1. 刪除舊的 `dist/` 和 `build/` 目錄
2. 執行 `build.bat`
3. 運行 `dist\GenshinSpire.exe`
4. 主選單應能正常出現

## 額外注意事項
- 確保 `images/` 和 `audio/` 目錄與 `main.py` 同級
- 若仍有資源加載問題，檢查 `get_base_path()` 在 PyInstaller 環境下是否回傳正確路徑（應為臨時目錄）
