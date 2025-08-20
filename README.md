# hictonZeroday1（SJU `data.php?tpl=...` 同款結構）

這個專案重現https://zeroday.hitcon.org/vulnerability/ZD-2025-00613：
`data.php` 以 `tpl` 參數反射，
包含：
- `data.php`：未修復（汙染版）
- `data_safe.php`：已修復（乾淨版，含 CSP）
- `payloads.txt`：幾個常見測試 payload
- `make_dataset.py`：自動抓取兩版本頁面，輸出到 `datasets/` 生成乾淨/汙染樣本與 `labels.csv`

> 僅供**本機/可控環境**安全測試使用，請勿用於第三方站點。

docker run --rm -it -p 8000:8000 -v "${PWD}:/srv" -w /srv php:8.2-cli php -S 0.0.0.0:8000
docker run --rm -it -p 8000:8000 -v "%cd%:/srv" -w /srv php:8.2-cli php -S 0.0.0.0:8000(上面失敗的話)
## 1) 啟動內建 PHP 伺服器

```bash
php -S 127.0.0.1:8000
```

## 2) 手動測試

- 汙染版：<http://127.0.0.1:8000/data.php?tpl=%3Csvg%20onload%3Dalert(1)%3E>
- 乾淨版：<http://127.0.0.1:8000/data_safe.php?tpl=%3Csvg%20onload%3Dalert(1)%3E>

預期：汙染版會彈窗；乾淨版只顯示文字。

## 3) 批次產生資料集

另開一個終端機：

```bash
pip install requests
python make_dataset.py
```

會在 `datasets/` 產生：
```
datasets/
  clean/*.html
  polluted/*.html
  labels.csv
```

## 4) 注意事項
- 真正修補線上站點時，請確保所有動態輸出都做**情境對應的輸出編碼**（例如 PHP `htmlspecialchars`）。
- CSP 可以作為第二道防線，但不能取代輸出編碼。
