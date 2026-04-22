# 臺灣農業氣象溫度分布預報 (AIoT 全端氣象儀表板)

## 📖 專案簡介 (Project Summary)
本專案為一個完整的全端 (Full-Stack) 應用程式，專注於提供台灣各區未來一週的農業氣象與溫度趨勢視覺化。專案從最初單純的 API 爬蟲腳本逐步進化，最終整合重構成為一套支援前後端分離、背景自動更新資料，並完美相容於 **Vercel Serverless** 雲端佈署的現代化 Web 儀表板。

### ✨ 核心亮點：
- **自動化資料爬取**：內建智慧雙軌排程系統。本地端透過 Background Thread 執行，Vercel 雲端則透過 Cron Jobs 觸發，每 4 小時自動向「中央氣象署 (CWA)」撈取最新一週氣象資料。
- **SQLite 資料庫整合**：將複雜巢狀 JSON 扁平化並轉存至 SQLite，提升 API 查詢效率，並特製冷啟動 (Cold Start) 偵測機制以完美適應 Serverless 唯讀檔案系統。
- **現代化互動前端**：前端採用 React + Vite 構建，介面採用深色玻璃擬態 (Glassmorphism) 風格。
  - **Leaflet 互動地圖**：結合 CartoDB Dark Matter 深色底圖，並依據最高溫自動在地圖上打上熱力色彩標記。
  - **Recharts 趨勢圖**：具備一週高低溫雙折線圖，並提供一鍵切換為「數據清單表格」的彈性功能。
  - **響應式設計 (RWD)**：佈局可根據行動裝置完美彈性縮放，確保手機瀏覽體驗。

---

## 📂 檔案結構 (Directory Structure)

專案內保留了完整的演進歷史，並將最終可直接上線的版本統一收納於 `CompleteProject/` 目錄下：

```text
AIoTHW2/
├── CompleteProject/        # 🚀 [最終交付版本] 完美整合且支援 Vercel 佈署的專案核心
│   ├── backend/            # 後端 API 與資料處理區
│   │   ├── app.py          # Flask 伺服器主程式 (負責 API 路由定義)
│   │   ├── data_updater.py # 核心爬蟲腳本 (負責呼叫 CWA API、寫入暫存區並更新 SQLite)
│   │   ├── data.db         # [自動生成] SQLite 資料庫 (存放氣象預報資料)
│   │   └── requirements.txt# Python 依賴清單
│   ├── frontend/           # 前端 UI 介面區 (React + Vite)
│   │   ├── src/            # 核心元件庫 (App, MapComponent, DailyTable, WeeklyChart)
│   │   ├── index.css       # 全域樣式與 RWD 響應式配置
│   │   ├── package.json    # Node.js 依賴清單
│   │   └── vite.config.js  # Vite 配置 (包含 0.0.0.0 IP 綁定與 /api Proxy 設定)
│   ├── vercel.json         # 雲端佈署設定檔 (處理 /api 路由轉發與排程 Cron Jobs)
│   └── .gitignore          
│
├── HW2-1_2-2/              # [歷史階段 1] 氣象資料抓取與 JSON 解析腳本
├── HW2-3/                  # [歷史階段 2] SQLite 資料庫連線與寫入測試
├── HW2-4/                  # [歷史階段 3] Flask API 與 React 前端開發雛形
└── DEVLOG.md               # 完整專案開發歷程與 Debug 日誌
```

---

## 🚀 快速啟動 (Quick Start - 本地開發)

若要在您的本機電腦上完整運行 `CompleteProject`，請開啟兩個終端機並分別執行以下指令：

### 1. 啟動後端 (Flask)
```bash
cd CompleteProject/backend
# 確保您已經安裝好 requirements.txt 內的依賴
python app.py
```
> 後端啟動時，若偵測到本地無資料庫，會自動執行第一次爬取。後續每隔 4 小時會自動在背景更新資料。

### 2. 啟動前端 (Vite)
```bash
cd CompleteProject/frontend
npm install
npm run dev
```
> 前端運行後，您不僅能在 `http://localhost:5173` 看到畫面，由於已經配好 Host IP 綁定，您也可以用同個 Wi-Fi 下的手機輸入您的電腦 IP (例如 `http://192.168.x.x:5173`) 來預覽完美支援手機的儀表板。

---

## ☁️ Vercel 佈署指南

此專案已完全相容 Vercel Serverless Functions。當您將專案推送到 GitHub 後，請直接在 Vercel 中匯入 `CompleteProject` 根目錄，不須手動進行複雜配置，系統將自動套用 `vercel.json` 裡的轉發與自動更新排程。
