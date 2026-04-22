import React from 'react';

const DailyTable = ({ allData, selectedDate }) => {
  if (!allData || Object.keys(allData).length === 0) {
    return (
      <div className="temperature-card placeholder" style={{ height: '350px' }}>
        <p style={{ color: 'var(--text-muted)' }}>請選擇欲查詢的日期</p>
      </div>
    );
  }

  // 將 Object 轉為 Array 並可選擇排序 (這裡依據地區預設排序，也可不排)
  const regionsList = Object.entries(allData).map(([region, temps]) => ({
    region,
    ...temps
  }));

  return (
    <div className="temperature-card" style={{ height: '350px', overflowY: 'auto' }}>
      <h3 style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'white', marginBottom: '1rem', textAlign: 'center' }}>
        全台各區氣溫總覽 ({selectedDate})
      </h3>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', color: '#94a3b8' }}>
            <th style={{ padding: '0.75rem' }}>地區</th>
            <th style={{ padding: '0.75rem' }}>最低溫 (˚C)</th>
            <th style={{ padding: '0.75rem' }}>最高溫 (˚C)</th>
          </tr>
        </thead>
        <tbody>
          {regionsList.map((item, idx) => (
            <tr key={idx} style={{ 
                borderBottom: '1px solid rgba(255,255,255,0.05)', 
                color: '#f8fafc',
                transition: 'background 0.2s',
                ...(idx % 2 === 0 ? { background: 'rgba(255,255,255,0.02)' } : {}) 
            }}
            onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            onMouseOut={(e) => e.currentTarget.style.background = idx % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent'}
            >
              <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>{item.region}</td>
              <td style={{ padding: '0.75rem', color: '#93c5fd' }}>{item.mint}</td>
              <td style={{ padding: '0.75rem', color: '#fca5a5' }}>{item.maxt}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DailyTable;
