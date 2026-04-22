# Development Log

Chronological record of development sessions, decisions, and changes.

---

## 2026-04-19 — Initialize AIoT HW2-1 Environment & Fetch CWA Data

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- 建立以 `uv` 管理的 `.venv` 統一虛擬環境，避免污染全域 Python。
- 安裝 `requests` 套件。
- 建立 HW2-1 資料夾與 `main.py`。
- 撰寫 Python 腳本向中央氣象署的開放資料 API 發送 HTTP GET 請求。
- 使用 `json.loads`（`response.json()`）與 `json.dumps` 確認並格式化解析資料。
- 將抓取到的資料輸出為 `output.json`。

**Files touched:**
- `HW2-1/main.py` — 新增取得開放資料 api 的程式。
- `DEVLOG.md` — 建立與更新開發紀錄。

**Decisions & rationale:**
- 依據指示在根目錄建立 `d:\SchoolProject\AIoTHW2\.venv` 使全專案擁有統一的開發環境。
- 在 `requests.get()` 中加入 `verify=False` 參數，因為該政府網站的憑證在本地有時會引發 SSLError。

**Known issues / tech debt:**
- `verify=False` 關閉了 SSL 檢查，不適合用於正式生產環境中。

**Next steps:**
- 進行作業後續的其他資料處理需求。

---

## 2026-04-19 — Merge HW2-1 and HW2-2 Directories

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** refactor

**Changes:**
- 將 `HW2-1` 與 `HW2-2` 目錄合併，並重新命名為 `HW2-1_2-2`。

**Files touched:**
- `HW2-1/` → `HW2-1_2-2/` (Moved/Renamed)
- `HW2-2/` (Deleted)

**Decisions & rationale:**
- 依據指示合併後續開發，移除原本空的 `HW2-2` 資料夾，並保留 `HW2-1` 中已撰寫的氣象資料抓取程式於 `HW2-1_2-2` 內。

**Known issues / tech debt:**
- None.

**Next steps:**
- 繼續依照 HW2-1_2-2 新需求開發。

---

## 2026-04-19 — Output JSON Structure Analysis

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** docs

**Changes:**
- 檢視並分析 `output.json` 的巢狀結構。
- 確認中央氣象署農業氣象預報資料中最高溫 (`MaxT`) 與最低溫 (`MinT`) 位於 `weatherForecasts.location[i].weatherElements` 節點內。
- 建立 `record.md` 紀錄該 JSON 結構分析結果與數值存放路徑。

**Files touched:**
- `HW2-1_2-2/record.md` — 新增分析文檔。

**Decisions & rationale:**
- 將繁雜的氣象開放資料結構梳理為 Markdown 文件，以便後續撰寫分析或圖表呈現程式時參考對應的資料節點。

**Known issues / tech debt:**
- None.

**Next steps:**
- 根據提取到的溫度路徑，開發能擷取與應用這些資訊的功能程式。

---

## 2026-04-19 — Add Data Categories to Record

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** docs

**Changes:**
- 分析 `output.json` 中宣告的所有氣象指標類別 (`weatherElements`)。
- 在 `record.md` 內補充「資料類別清單」，記錄如 `weather`、`degreeDay`、`accumulatedTemperature`、`cardinalTemperatures` 等類別的意義與對應英文欄位。

**Files touched:**
- `HW2-1_2-2/record.md` — 補充資料類別清單。

**Decisions & rationale:**
- 完整紀錄可用的氣象指標，有助於未來專案擴建時快速查閱所需資料，而不必每次重新梳理 JSON 架構。

**Known issues / tech debt:**
- None.

**Next steps:**
- 依照作業或專案指示持續利用這些已知的指標進行程式開發。

---

## 2026-04-19 — Convert Weather Output JSON to CSV format

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- 撰寫 `to_csv.py` 以讀取並解析 `output.json`，將原始多層巢狀資料扁平化。
- 擷取每日各地的「天氣狀況 (`Wx`)」、「最高溫 (`MaxT`)」及「最低溫 (`MinT`)」。
- 將正規化後的資料運用內建 `csv` 模組導出為 `weather_data.csv`。

**Files touched:**
- `HW2-1_2-2/to_csv.py` — 新增資料轉型腳本。
- `HW2-1_2-2/weather_data.csv` — 新增結果檔案 (執行腳本生成)。

**Decisions & rationale:**
- 使用 Python 內建的 `json` 以及 `csv` 模組而非外部的 `pandas`，藉此維持依賴環境輕量且依然滿足扁平化處理需求。
- 在 `open` csv 檔案時使用了 `encoding="utf-8-sig"`，確保未來使用 Excel 打開 CSV 時中文能被正常解析顯示，不會出現亂碼。

**Known issues / tech debt:**
- 目前提取了基本的溫濕度資訊，隨著未來開發需求擴展，或許會重構此部分讓使用者自定想要的欄位輸出。

**Next steps:**
- 讀取建立好的 CSV 檔案進行資料視覺化 (例如繪製長條圖或折線圖等) 分析。

---

## 2026-04-19 — Rename main.py to get_api.py

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** refactor

**Changes:**
- 將負責呼叫 HTTP GET 請求與解析 JSON 的 `main.py` 更名為 `get_api.py`，使檔案名稱更符合其實際功能。

**Files touched:**
- `HW2-1_2-2/main.py` → `HW2-1_2-2/get_api.py` (Renamed)

**Decisions & rationale:**
- `get_api.py` 在這份專案內能更精確地傳達「此檔案專責取得第三方 API 資訊」的意義。

**Known issues / tech debt:**
- None.

**Next steps:**
- 進行 HW2-3 資料庫操作與應用。

---

## 2026-04-19 — Initiate HW2-3 and Store Data to SQLite

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- 建立 `HW2-3` 目錄，並撰寫 `save_to_db.py` 處理資料庫儲存。
- 使用內建模組 `sqlite3` 自動建立名為 `data.db` 的資料庫檔案。
- 定義並建立 `TemperatureForecasts` 資料表，包含 `id` (主鍵)、`regionName`、`dataDate`、`mint` 及 `maxt` 等欄位。
- 載入並解析 `HW2-1_2-2/output.json`，將各地區每日最低溫與最高溫配對後，批量寫入 `TemperatureForecasts` 資料表內。

**Files touched:**
- `HW2-3/save_to_db.py` — 新增資料庫操作腳本。
- `HW2-3/data.db` — 新增生成的 SQLite 資料庫。

**Decisions & rationale:**
- 採用 SQLite3 作為輕量資料庫解決方案，因為內建於 Python 且無須繁雜的伺服器架設即可滿足作業上 CRUD 或 SQL 查詢練習需求。
- 資料由字串轉換成 `INTEGER` 儲存，確保後續能夠正確利用 SQL 語法進行氣溫大小的查詢過濾。

**Known issues / tech debt:**
- 腳本在寫入前會先清空 Table (`DELETE FROM TemperatureForecasts`) 以避免資料重複寫入，若未來需保留歷史資料需改寫為 `INSERT OR IGNORE` 或 `UPDATE`。

**Next steps:**
- 準備 HW2-3 後續可能的 SQL 查詢、資料撈取比對等實驗開發。

---

## 2026-04-19 — Test and Query SQLite Database

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- 撰寫 `test_db.py` 以驗證資料庫 `data.db` 中資料的正確性。
- 利用 SQLite 查詢指令印出所有不重複的「地區名稱」(`SELECT DISTINCT regionName ...`)。
- 撈出並列印「中部地區」從第一天至最後一天的日期與氣溫變化。

**Files touched:**
- `HW2-3/test_db.py` — 新增資料庫測試腳本。

**Decisions & rationale:**
- 將測試與儲存腳本分離，讓 `test_db.py` 專注於 SELECT 讀取與資料呈現，提升程式碼的可讀性，也方便直接於終端機查閱結果。

**Known issues / tech debt:**
- None.

**Next steps:**
- 進行 HW2-4 的網頁開發作業。

---

## 2026-04-19 — Implement HW2-4 Full Stack Weather App

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- **總體架構**：建立 `HW2-4` 資料夾，分設 `backend` (Flask) 以及 `frontend` (React + Vite) 兩個子專案。
- **後端 (Backend)**：在 `.venv` 中安裝了 `flask` 與 `flask-cors`。撰寫了 `backend/app.py` 建立 API 路由 `/api/options` 與 `/api/forecast` 來對應 SQLite 資料庫 `HW2-3/data.db` 抓取資料。
- **前端 (Frontend)**：初始化最新的 Vite + React 應用，撰寫了包含玻璃擬態（Glassmorphism）與漸層背景（Gradient）的高級質感現代化 UI 版面。
- **打通通訊**：前端 `App.jsx` 利用 `fetch` 從 Flask 端口取得所有可選的「地區」以及「日期」，並透過兩個自定義樣式的 Select 標籤讓用戶任意選擇與切換，即時更新天氣面板的數字變化。

**Files touched:**
- `HW2-4/backend/app.py` — Flask API 進入點。
- `HW2-4/frontend/package.json` — Vite 依賴設定（為配合目前的 Node 版號，使用了較早的 Vite 5 版本）。
- `HW2-4/frontend/src/App.jsx` — React 主程式面版。
- `HW2-4/frontend/src/index.css` — 現代化 UI 設計的核心 CSS 變數與樣式表。

**Decisions & rationale:**
- 選用前後端分離（SPA）架構而非使用 Flask 內建 Jinja 推動網頁，是因為這樣能在使用者切換時間時帶來不需刷新整個網頁的優異體驗。
- 前端樣式大量運用高對比毛玻璃技術，讓中央氣象局原本傳統的預報畫面躍升為具有「現代科技儀表板」質感的系統，符合前端工程 UI/UX 最佳實踐。

**Known issues / tech debt:**
- None.

**Next steps:**
- 無。

---

## 2026-04-19 — Add Dynamic Leaflet Map Component

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- **資源安裝**：於前端利用 npm 安裝 `leaflet` 與 `react-leaflet` 二維地圖套件。
- **後端新增路由**：於 Flask 開發了 `/api/forecast_all`，接受指定日期並一次搜刮出資料庫中該日期下所有區域的氣溫供前端地圖打點使用。
- **地圖渲染**：建立 `<MapComponent />` 將氣象資料結合經緯度呈現在深色模式的 CartoDB Map。
- **地標熱度與資料聯動**：根據最高溫 (MaxT) 為各個點位的 Marker 上色（譬如低溫為藍色，超過32度為紅色）。並綁定 `onClick` 事件通知父元件 (`App.jsx`) 切換使用者選取的區域以更新右側面板。

**Files touched:**
- `HW2-4/backend/app.py` — 新增全區氣溫 API Endpoint。
- `HW2-4/frontend/package.json` — 增加 Leaflet 模組。
- `HW2-4/frontend/src/MapComponent.jsx` — 全新地圖元件與動態著色邏輯。
- `HW2-4/frontend/src/App.jsx` — 整合地圖元件與原有 UI，執行多路 Async Fetch 串起所有資料流。

**Decisions & rationale:**
- 使用 react-leaflet 因其體積輕巧且可客製化高質量 Marker。比起自行準備巨大的 GeoJSON 台灣縣市邊界，直接取各區中心點放置「發光的熱度圓點」不僅效能好，也更符合本作業科技儀表板的美術定調。

**Known issues / tech debt:**
- 經緯度採用粗略的中間點區分各大區，若日後氣象局提供更詳細測站或縣市邊界向量，可替換升級為細膩的多邊形熱力圖。

**Update (Later):**
- 將地圖由深色 (Dark Matter) 調整為亮色 (Light All)，並取消了地圖氣溫標籤的常駐顯示，改為純粹滑鼠懸停 (Hover) 顯示，以提升畫面整潔度。

---

## 2026-04-19 — Add Data Table and Weekly Line Chart

**Conversation ID:**
- 927ab4e6-2969-4512-9a8a-ed1bd20a4230

**Scope:** feature

**Changes:**
- **折線圖安裝**：前端透過 npm 安裝 `recharts`。
- **後端新增路由**：擴建 API `/api/forecast_week`，輸入地區名稱後直接吐出針對時間遞增排序的多天天氣趨勢。
- **建立 Recharts 元件**：創建 `WeeklyChart.jsx` 接收 API 資料並呈現動態折線圖，擁有獨立的 Loading 提示。
- **建立 Table 元件**：創建 `DailyTable.jsx` 將整理過的 JS 物件映射為原生 HTML `<Table>`。
- **版面整合**：於 `App.jsx` 採用 CSS Grid 佈局，將四個核心組建分配為上下兩區對齊展示，所有互動狀態能維持同步。

**Files touched:**
- `HW2-4/backend/app.py` — 新增一週資料 API Endpoint。
- `HW2-4/frontend/src/WeeklyChart.jsx`
- `HW2-4/frontend/src/DailyTable.jsx` 
- `HW2-4/frontend/src/App.jsx`

**Decisions & rationale:**
- 使用 `recharts` 因為它在 React 生態系中能完美與其他組件協同，且可以任意客製化顏色以配合本身的 Glassmorphism 漸層主題。

**Known issues / tech debt:**
- 目前 Table 的排序尚未加入遞增/遞減按鈕，未來可再升級。

**Update (Later):**
- 將氣溫詳細卡片中的「最低溫」與「最高溫」方塊改為左右並列 (Row) 顯示以善用寬度。並修正外圍包裹器的 Flex 排版，使「地區標題」固定維持在上層而非因為繼承而與方塊左右排列。
- 順帶調整了這張卡片內層的距離，透過 `justifyContent` 與 `alignItems` 置中對齊內容，並將 `gap` 放大拉開元素間距，增添方塊內 padding 以提升呼吸感，視覺上能更聚焦於溫度大寫數字。
- 為了讓 UI 整體美感更高，重新設定回 **Dark Matter 深色質感地圖**，確保跟整體太空/夜間毛玻璃的 Dashboard 風格相互輝映。
- 移除了總覽表格 `DailyTable` 標題的 `position: sticky` 屬性，讓標題能夠自然滑動，符合使用者的瀏覽習慣期望。
- 新增 `WeeklyChart` 的「圖表/表格」切換鈕，使用者點擊即可將折線圖轉為具備黏性標題 (Sticky Header) 的滾動數據清單，呈現每日的「最低溫」與「最高溫」。
- **網路佈署優化**：將 Flask 綁定於 `0.0.0.0` 允許全網域訪問；同時在 `vite.config.js` 設定 `host: '0.0.0.0'` 並配置 `proxy`，讓前端請求統一走相對路徑 `/api`，徹底解決區域網路（LAN）下外部裝置連線時遭遇的連線異常與 CORS 問題。
- **響應式設計 (RWD) 修正**：全面優化行動裝置（如手機）的瀏覽體驗：
  1. 將 CSS Grid 的欄寬從硬編碼的 `400px` 修正為 `minmax(min(100%, 320px), 1fr)`，避免小螢幕破版與橫向捲軸。
  2. 加入 `@media (max-width: 640px)` 斷點，讓外層邊距縮小、標題字體按比例縮小。
  3. 新增 `.responsive-temps-display` 樣式，當在手機上瀏覽時，最高/最低溫的小卡片會自動從「左右並列」切換為「上下堆疊」，確保數字不會擠壓變形。

---

## Session: 2026-04-22 專案整合與 Vercel 佈署架構重構

**Objective:**
將 HW2 所有的零散作業 (HW2-1_2-2, HW2-3, HW2-4) 整合為單一且支援雲端佈署的 `CompleteProject` 完整專案，並實現「自動爬取最新資料更新資料庫」的核心需求。

**Action:**
- 建立了全新的 `CompleteProject` 目錄，內含 `backend` 與 `frontend` 實現乾淨的前後端分離標準專案結構。
- **後端架構大重構 (Vercel Ready)**：
  - 將原先抓取資料的 `get_api.py` 與存入資料庫的 `save_to_db.py` 整合為單一核心模組 `data_updater.py`。
  - 在本地端實作了背景自動排程器 (Background Thread)，於 `app.py` 啟動時自動在背景運作，**每 4 小時自動抓取一次最新天氣資料**。
  - 考量到 Vercel Serverless 平台的特殊限制（無法常駐背景執行緒且檔案系統唯讀），加入了環境變數檢查 (`IS_VERCEL`)，在雲端環境下自動將資料庫與中繼檔案寫入允許寫入的 `/tmp` 暫存區。
  - 新增了 **冷啟動 (Cold Start) 偵測**：若發現 `/tmp` 中的資料庫消失，程式會立刻在發出 API 回應前重新爬取資料，確保網頁永遠有最新資料不會因伺服器重啟而崩潰。
  - 新增了一支專門供定時任務使用的 API 路由 `/api/cron_update`。
- 複製並銜接了前一階段優化好的 Vite + React 前端介面進入 `CompleteProject/frontend`。
- 新增 `vercel.json` 設定檔，定義了路由轉發規則 (將 `/api` 流量導向 Python Flask，其餘全數交給 React)，並且配置了 **Vercel Cron Jobs** 定時器，調整為台灣時間每天晚上 8 點 (12:00 UTC) 觸發資料更新。
- 加入了 `.gitignore` 避免把本地快取、Node Modules 或是本地建立的 SQLite 資料庫檔推送到 GitHub 造成版本髒亂。
- **Bug Fix**: 修正 `CompleteProject/frontend` 中 `MapComponent.jsx` 因為不小心將 Array 誤當 Object 讀取而導致地圖圓點溫度顏色消失的問題，恢復原本的熱力色彩標記。

**Next steps:**
- 使用者將此專案推送到 GitHub 並進行 Vercel 正式上線佈署。
