import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

const WeeklyChart = ({ region }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('chart'); // 'chart' or 'table'

  useEffect(() => {
    if (!region) return;

    setLoading(true);
    setError('');

    // 呼叫新寫的 /api/forecast_week 來取得一週趨勢
    fetch(`/api/forecast_week?region=${encodeURIComponent(region)}`)
      .then(res => {
        if (!res.ok) throw new Error('無法取得一週數據');
        return res.json();
      })
      .then(result => {
        // 為了讓 X 軸不要太長，只取 MM-DD
        const formattedData = result.map(item => ({
          ...item,
          shortDate: item.date.split('-').slice(1).join('-') // "2026-04-19" -> "04-19"
        }));
        setData(formattedData);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [region]);

  if (loading) {
    return (
      <div className="temperature-card placeholder" style={{ height: '350px' }}>
        <div className="loader"></div>
      </div>
    );
  }

  if (error || data.length === 0) {
    return (
      <div className="temperature-card placeholder" style={{ height: '350px' }}>
        <p style={{ color: 'var(--text-muted)' }}>{error || '目前無資料'}</p>
      </div>
    );
  }

  return (
    <div className="temperature-card" style={{ height: '350px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'white', margin: 0 }}>
          {region} - 近一週溫度趨勢
        </h3>
        <button 
          onClick={() => setViewMode(viewMode === 'chart' ? 'table' : 'chart')}
          style={{ 
            background: 'rgba(255,255,255,0.1)', 
            border: '1px solid rgba(255,255,255,0.2)', 
            color: 'white', 
            padding: '4px 12px', 
            borderRadius: '20px', 
            cursor: 'pointer',
            fontSize: '0.85rem',
            transition: 'background 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
          onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
        >
          切換為{viewMode === 'chart' ? '表格' : '圖表'}
        </button>
      </div>
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto' }}>
        {viewMode === 'chart' ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="shortDate" stroke="#cbd5e1" fontSize={12} tickMargin={10} />
              <YAxis stroke="#cbd5e1" fontSize={12} domain={['dataMin - 2', 'dataMax + 2']} tickFormatter={(v) => `${v}˚`} />
              <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Line 
                  type="monotone" 
                  dataKey="maxt" 
                  name="最高溫 (MaxT)" 
                  stroke="#f87171" 
                  strokeWidth={3}
                  activeDot={{ r: 6 }} 
              />
              <Line 
                  type="monotone" 
                  dataKey="mint" 
                  name="最低溫 (MinT)" 
                  stroke="#60a5fa" 
                  strokeWidth={3}
                  activeDot={{ r: 6 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', color: '#94a3b8' }}>
                <th style={{ padding: '0.75rem', position: 'sticky', top: 0, background: 'rgba(30, 41, 59, 0.9)' }}>日期</th>
                <th style={{ padding: '0.75rem', position: 'sticky', top: 0, background: 'rgba(30, 41, 59, 0.9)' }}>最低溫 (˚C)</th>
                <th style={{ padding: '0.75rem', position: 'sticky', top: 0, background: 'rgba(30, 41, 59, 0.9)' }}>最高溫 (˚C)</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, idx) => (
                <tr key={idx} style={{ 
                    borderBottom: '1px solid rgba(255,255,255,0.05)', 
                    color: '#f8fafc',
                    transition: 'background 0.2s',
                    ...(idx % 2 === 0 ? { background: 'rgba(255,255,255,0.02)' } : {}) 
                }}
                onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                onMouseOut={(e) => e.currentTarget.style.background = idx % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent'}
                >
                  <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>{item.shortDate}</td>
                  <td style={{ padding: '0.75rem', color: '#93c5fd' }}>{item.mint}</td>
                  <td style={{ padding: '0.75rem', color: '#fca5a5' }}>{item.maxt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default WeeklyChart;
