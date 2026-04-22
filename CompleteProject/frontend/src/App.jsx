import React, { useState, useEffect } from 'react';
import MapComponent from './MapComponent';
import WeeklyChart from './WeeklyChart';
import DailyTable from './DailyTable';
import './index.css';

function App() {
  const [options, setOptions] = useState({ regions: [], dates: [] });
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  
  const [forecast, setForecast] = useState(null);
  const [allForecasts, setAllForecasts] = useState(null); // 地圖用的全區資料
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 1. 取得下拉選單選項
  useEffect(() => {
    fetch('/api/options')
      .then((res) => res.json())
      .then((data) => {
        setOptions(data);
        if (data.regions.length > 0) setSelectedRegion(data.regions[0]);
        if (data.dates.length > 0) setSelectedDate(data.dates[0]);
      })
      .catch((err) => {
        console.error(err);
        setError('無法連接後端伺服器 (請確認 Flask 是否啟動運行於 5000 port)');
      });
  }, []);

  // 2. 當日期變更時，抓取全區域的該日數值(餵給地圖與表格)
  useEffect(() => {
    if (!selectedDate) return;
    fetch(`/api/forecast_all?date=${encodeURIComponent(selectedDate)}`)
        .then(res => res.json())
        .then(data => setAllForecasts(data))
        .catch(console.error);
  }, [selectedDate]);

  // 3. 當地區與日期更動時，請求具體卡片天氣資訊
  useEffect(() => {
    if (!selectedRegion || !selectedDate) return;
    
    setLoading(true);
    setError('');
    
    fetch(`/api/forecast?region=${encodeURIComponent(selectedRegion)}&date=${encodeURIComponent(selectedDate)}`)
      .then(res => {
        if (!res.ok) throw new Error('找不到該日期/地區的資料');
        return res.json();
      })
      .then(data => {
        setForecast(data);
      })
      .catch(err => {
        setError(err.message);
        setForecast(null);
      })
      .finally(() => {
        setLoading(false);
      });
      
  }, [selectedRegion, selectedDate]);

  return (
    <div className="dashboard-container" style={{maxWidth: '1200px', margin: '0 auto'}}>
      <header className="dashboard-header">
        <h1>臺灣農業氣象溫度分布預報</h1>
        <p>資料來源：中央氣象署 (CWA API)</p>
      </header>

      {error && <div style={{color: '#fca5a5', textAlign: 'center', marginBottom: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.2)', borderRadius: '8px'}}>{error}</div>}

      <div className="controls-section">
        <div className="control-group">
          <label htmlFor="date-select">觀測日期預報 (地圖與表格連動)</label>
          <select 
            id="date-select"
            className="glass-select"
            value={selectedDate} 
            onChange={(e) => setSelectedDate(e.target.value)}
          >
            {options.dates.map(date => (
              <option key={date} value={date}>{date}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="region-select">觀測地區 (亦可點擊地圖)</label>
          <select 
            id="region-select"
            className="glass-select"
            value={selectedRegion} 
            onChange={(e) => setSelectedRegion(e.target.value)}
          >
            {options.regions.map(region => (
               <option key={region} value={region}>{region}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 上半部：地圖與當日單區卡片 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', gap: '2rem', marginBottom: '2rem' }}>
        <div style={{ minWidth: 0 }}>
            {allForecasts && (
                <MapComponent 
                    allData={allForecasts} 
                    selectedRegion={selectedRegion} 
                    onRegionChange={setSelectedRegion} 
                />
            )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', minWidth: 0 }}>
            {loading ? (
                <div className="temperature-card placeholder" style={{ height: '400px' }}>
                    <div className="loader"></div>
                </div>
            ) : forecast ? (
                <div className="temperature-card" style={{ height: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '2.5rem' }}>
                    <h2 className="responsive-title">{selectedRegion} - {selectedDate}</h2>
                    <div className="responsive-temps-display">
                        <div className="temp-pill low" style={{ flex: 1, textAlign: 'center', padding: '1.5rem' }}>
                            <div className="temp-label">最低溫 (MinT)</div>
                            <div className="temp-value">
                                {forecast.mint}
                                <span className="temp-unit">˚C</span>
                            </div>
                        </div>
                        <div className="temp-pill high" style={{ flex: 1, textAlign: 'center', padding: '1.5rem' }}>
                            <div className="temp-label">最高溫 (MaxT)</div>
                            <div className="temp-value">
                                {forecast.maxt}
                                <span className="temp-unit">˚C</span>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="temperature-card placeholder" style={{ height: '400px' }}>
                    <p style={{color: 'var(--text-muted)'}}>請選擇欲查詢的日期與區域</p>
                </div>
            )}
        </div>
      </div>
      
      {/* 下半部：當日全台表格與單區一週折線圖 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 320px), 1fr))', gap: '2rem' }}>
        <div style={{ minWidth: 0 }}>
            <DailyTable allData={allForecasts} selectedDate={selectedDate} />
        </div>
        <div style={{ minWidth: 0 }}>
            <WeeklyChart region={selectedRegion} />
        </div>
      </div>
    </div>
  );
}

export default App;
