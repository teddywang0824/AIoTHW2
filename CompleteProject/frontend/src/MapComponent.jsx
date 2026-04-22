import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// 近似中心點對應 (這些座標供示意位置用，表示台灣各地區)
const REGION_COORDS = {
  "北部地區": [24.9, 121.3],
  "中部地區": [23.9, 120.8],
  "南部地區": [22.8, 120.4],
  "東北部地區": [24.6, 121.7],
  "東部地區": [23.5, 121.4],
  "東南部地區": [22.6, 120.9],
  "澎湖縣": [23.57, 119.58],
  "金門縣": [24.45, 118.32],
  "連江縣": [26.15, 119.95]
};

// 溫度對應顏色的輔助函數 (越高溫越偏紅/橘，越涼爽越綠/藍)
const getColor = (temp) => {
  if (!temp) return '#ffffff';
  if (temp >= 32) return '#ef4444'; // Red
  if (temp >= 28) return '#f97316'; // Orange
  if (temp >= 24) return '#eab308'; // Yellow
  if (temp >= 20) return '#22c55e'; // Green
  return '#3b82f6'; // Blue
};

const MapComponent = ({ allData, selectedRegion, onRegionChange }) => {
  return (
    <div style={{ height: '400px', width: '100%', borderRadius: '20px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)', animation: 'fadeIn 0.5s ease-out' }}>
      <MapContainer 
        center={[23.7, 120.9]} 
        zoom={7} 
        style={{ height: '100%', width: '100%', background: '#0f172a' }} // 深藍黑底色
        attributionControl={false}
      >
        {/* 切換回 CartoDB Dark Matter 的地圖圖層，讓整體風格跟著儀表板黑底契合 */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {Object.entries(REGION_COORDS).map(([region, coords]) => {
          const data = allData ? allData.find(item => item.region === region) : null;
          const isSelected = region === selectedRegion;
          const mapTempColor = getColor(data?.maxt);
          
          return (
            <CircleMarker
              key={region}
              center={coords}
              radius={isSelected ? 16 : 11}
              pathOptions={{
                color: isSelected ? '#ffffff' : mapTempColor,
                fillColor: mapTempColor,
                fillOpacity: isSelected ? 0.8 : 0.6,
                weight: isSelected ? 3 : 1
              }}
              eventHandlers={{
                click: () => onRegionChange && onRegionChange(region)
              }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                <div style={{ textAlign: 'center', fontWeight: 'bold' }}>
                  {region}
                  {data && (
                    <div style={{ fontSize: '0.85rem', color: '#555', marginTop: '2px' }}>
                      {data.mint}˚C - {data.maxt}˚C
                    </div>
                  )}
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapComponent;
