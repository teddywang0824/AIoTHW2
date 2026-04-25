# 臺灣農業氣象溫度分布預報 (AIoT 全端氣象儀表板)

## 📖 專案簡介 (Project Summary)
本專案為一個完整的全端 (Full-Stack) 應用程式，專注於提供台灣各區未來一週的農業氣象與溫度趨勢視覺化。專案從最初單純的 API 爬蟲腳本逐步進化，最終整合重構成為一套支援前後端分離、背景自動更新資料，並完美相容於 **Vercel Serverless** 雲端佈署的現代化 Web 儀表板。

### ✨ 核心亮點：
- **智慧延遲更新系統 (Lazy Update)**：徹底廢除死板的定時排程。當使用者開啟網頁時，後端會自動比對氣象署最新發布時間 (18:00)，確保只在資料過期時發起爬蟲請求，達成真正的零浪費與效能最大化。
- **SQLite / PostgreSQL 雙棲資料庫**：將複雜巢狀 JSON 扁平化並轉存至關聯式資料庫中。本地端開發預設採用輕量級 `SQLite`；雲端部署可無縫對接 `Vercel Postgres`，達成真正的 Serverless 雲端原生持久化儲存。
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
│   │   ├── data_updater.py # 核心爬蟲腳本 (負責呼叫 CWA API、直接於記憶體處理寫入 DB)
│   │   ├── data.db         # [自動生成] SQLite 資料庫 (存放氣象預報資料)
│   │   ├── requirements.txt# Python 依賴清單
│   │   └── vercel.json     # 後端專屬 Vercel 設定檔 (供 Microfrontends 識別 Python)
│   ├── frontend/           # 前端 UI 介面區 (React + Vite)
│   │   ├── src/            # 核心元件庫 (App, MapComponent, DailyTable, WeeklyChart)
│   │   ├── index.css       # 全域樣式與 RWD 響應式配置
│   │   ├── package.json    # Node.js 依賴清單
│   │   └── vite.config.js  # Vite 配置 (包含 0.0.0.0 IP 綁定與 /api Proxy 設定)
│   ├── vercel.json         # 雲端佈署設定檔 (處理 /api 路由轉發)
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
> 後端啟動後，不論是本地或雲端，當使用者開啟網頁 (觸發 API) 時，系統會自動比對時間，若資料過期便會自動進行背景爬取與更新。

### 2. 啟動前端 (Vite)
```bash
cd CompleteProject/frontend
npm install
npm run dev
```
> 前端運行後，您不僅能在 `http://localhost:5173` 看到畫面，由於已經配好 Host IP 綁定，您也可以用同個 Wi-Fi 下的手機輸入您的電腦 IP (例如 `http://192.168.x.x:5173`) 來預覽完美支援手機的儀表板。

---

## ☁️ Vercel 佈署指南

此專案已完全相容 Vercel Serverless Functions 與 Vercel Postgres 雲端資料庫。
1. 當您將專案推送到 GitHub 後，請直接在 Vercel 中匯入專案，系統將自動套用 `vercel.json` 裡的轉發與自動更新排程。
2. 進入 Vercel 專案的 **Settings > Environment Variables**，新增一組環境變數：
   - Key: `CWA_API_KEY`
   - Value: `您申請的中央氣象署 API Key`
3. 在專案的 **Storage** 頁籤中點擊 **Create Database** 建立一個 **Postgres** 資料庫並連結。
4. 連結完成後 Vercel 會自動注入 `POSTGRES_URL`，此時只需觸發重新部署 (Redeploy)，您的儀表板就會瞬間進化為使用雲端資料庫的強大生產環境了！
