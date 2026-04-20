# 氣象開放資料 JSON 結構分析與溫度萃取紀錄

## 1. 資料整體結構分析

爬取下來的 `output.json` 包含了來自中央氣象署的一週農業氣象預報資料，整體結構以巢狀（Nested）的 Dictionary 及 List 呈現。

主節點為 `cwaopendata`，其內部主要區分為 `identifier` 等詮釋資料，以及核心內容所在的 `resources`。

最核心的預報資料路徑為：
```json
cwaopendata.resources.resource.data.agrWeatherForecasts
```

在這個節點下有三個主要區塊：
- `weatherProfile`: 天氣概況文字敘述
- `weatherForecasts`: 分區的一週氣象預測數值（包含多個地區的陣列）
- `agrAdvices`: 各區農事建議與積溫累積等資料

## 2. 最高溫與最低溫的資料位置

各地區的最高與最低溫度預測存放於 `weatherForecasts` 節點中，具體位置如下：

### 最高溫 (MaxT)
- **JSON 路徑**:
  `cwaopendata["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"][地區索引]["weatherElements"]["MaxT"]["daily"]`
- **結構範例**:
  陣列中包含每日的資料物件：
  ```json
  {
      "dataDate": "2026-04-19",
      "temperature": "27"
  }
  ```

### 最低溫 (MinT)
- **JSON 路徑**:
  `cwaopendata["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"][地區索引]["weatherElements"]["MinT"]["daily"]`
- **結構範例**:
  與最高溫相似，陣列中包含每日的數值：
  ```json
  {
      "dataDate": "2026-04-19",
      "temperature": "20"
  }
  ```

## 3. 分析結論
- 由於資料依據「地區（如北部地區、中部地區）」存放於 `location` 陣列內，因此要取得全台某天的最高溫或最低溫，需遍歷 `location` 陣列中的各個地區，並進入 `weatherElements` 取出 `MaxT` 與 `MinT` 的 `daily` 陣列。
- `temperature` 屬性中的值為字串型態（如 `"27"`），在後續撰寫程式進行數值計算或大小比較時，需將其強制轉型為 `int` 型別。

## 4. 資料類別清單 (Data Categories)

根據 JSON 檔首的 `metadata.weatherElements` 宣告，除了最高溫和最低溫之外，此開放資料還提供了以下各項農業天氣相關的氣象指標類別：

1. **weather (天氣描述)** / `Wx`：每日天氣陰晴雨狀況（如：晴時多雲）。
2. **temperature (氣溫)** / `MaxT`, `MinT`：當地的最高與最低氣溫 (˚C)。
3. **agrWeatherForecasts (一週農業天氣預報)**：總體農業天氣預報。
4. **weatherProfile (天氣概況)**：未來一週總體天氣現象的文字彙整概述。
5. **weatherForecasts (天氣預報)**：各地區按日切分的氣象資料。
6. **agrAdvices (農事建議)**：針對各區農作物生長的具體農事文字建議與積溫累積日誌。
7. **degreeDay (度日)**：植物發育時所需之有效溫度單位 (GDD)。
8. **accumulatedTemperature (積溫)**：植物發育過程中到達一定發育階段所累積的特定溫度值。
9. **cardinalTemperatures (作物生長溫度區間)**：包含生長最低溫 (`minimum`)、最高溫 (`maximum`) 及最適溫 (`optimum`) 區間設定。
10. **growingDays (生育日數)**：特定農作物的生育歷程天數。
11. **cropStatistics (農業積溫統計)**：針對不同農作物的長期積溫與統計預測。
