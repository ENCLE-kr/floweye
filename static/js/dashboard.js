// Dashboard 그래프 초기화
document.addEventListener('DOMContentLoaded', function() {
  // 색상 설정
  const primaryColor = '#3498db';
  const backgroundColor = 'rgba(52, 152, 219, 0.1)';
  const borderColor = '#3498db';

  // 공통 차트 옵션
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          label: function(context) {
            return context.parsed.y.toLocaleString();
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          color: '#6c757d',
          font: {
            size: 12
          }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#6c757d',
          font: {
            size: 12
          }
        }
      }
    }
  };

  // 현재 총 체류 인원 추이 그래프
  const occupancyCtx = document.getElementById('occupancyChart');
  if (occupancyCtx) {
    new Chart(occupancyCtx, {
      type: 'line',
      data: {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [{
          label: '체류 인원',
          data: [850, 620, 1200, 1800, 1500, 1100, 1234],
          borderColor: borderColor,
          backgroundColor: backgroundColor,
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#fff',
          pointBorderColor: borderColor,
          pointBorderWidth: 2
        }]
      },
      options: commonOptions
    });
  }

  // 현재 총 밀집도 추이 그래프
  const densityCtx = document.getElementById('densityChart');
  if (densityCtx) {
    new Chart(densityCtx, {
      type: 'line',
      data: {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [{
          label: '밀집도',
          data: [45, 32, 65, 85, 72, 58, 68],
          borderColor: '#e74c3c',
          backgroundColor: 'rgba(231, 76, 60, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#fff',
          pointBorderColor: '#e74c3c',
          pointBorderWidth: 2
        }]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            max: 100,
            ticks: {
              ...commonOptions.scales.y.ticks,
              callback: function(value) {
                return value + '%';
              }
            }
          }
        },
        plugins: {
          ...commonOptions.plugins,
          tooltip: {
            ...commonOptions.plugins.tooltip,
            callbacks: {
              label: function(context) {
                return context.parsed.y + '%';
              }
            }
          }
        }
      }
    });
  }

  // 오늘 누적 방문 인원 추이 그래프
  const visitorsCtx = document.getElementById('visitorsChart');
  if (visitorsCtx) {
    new Chart(visitorsCtx, {
      type: 'bar',
      data: {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
        datasets: [{
          label: '누적 방문 인원',
          data: [1200, 2100, 3200, 4200, 5100, 5600, 5678],
          backgroundColor: '#28a745',
          borderColor: '#28a745',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        ...commonOptions,
        plugins: {
          ...commonOptions.plugins,
          tooltip: {
            ...commonOptions.plugins.tooltip,
            callbacks: {
              label: function(context) {
                return '누적: ' + context.parsed.y.toLocaleString() + '명';
              }
            }
          }
        }
      }
    });
  }

  // 스파크라인 그래프 초기화
  initSparklineCharts();
  
  // 알람 로그 초기화
  initAlarmLog();
  
  // 주기적으로 알람 체크 (30초마다)
  setInterval(checkDensityAlarms, 30000);
});

// 스파크라인 그래프 초기화 함수
function initSparklineCharts() {
  const sparklineCanvases = document.querySelectorAll('.sparkline-chart');
  
  // 각 디바이스별 데이터
  const deviceData = {
    '1': [65, 70, 72, 75, 78, 76, 78], // Device-001: 높은 밀집도
    '2': [40, 42, 44, 45, 43, 45, 45], // Device-002: 보통 밀집도
    '3': [], // Device-003: 오프라인
    '4': [20, 21, 22, 22, 21, 22, 22]  // Device-004: 낮은 밀집도
  };

  sparklineCanvases.forEach(canvas => {
    const deviceId = canvas.getAttribute('data-device-id');
    const data = deviceData[deviceId] || [];

    if (data.length === 0) {
      // 오프라인 디바이스는 그래프를 그리지 않음
      return;
    }

    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: Array(data.length).fill(''),
        datasets: [{
          data: data,
          borderColor: getDensityColor(data[data.length - 1]),
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 0,
          tension: 0.4,
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            enabled: false
          }
        },
        scales: {
          x: {
            display: false
          },
          y: {
            display: false,
            min: 0,
            max: 100
          }
        },
        elements: {
          point: {
            radius: 0
          }
        }
      }
    });
  });
}

// 밀집도에 따른 색상 반환
function getDensityColor(density) {
  if (density >= 70) return '#dc3545'; // 높음 - 빨간색
  if (density >= 40) return '#f39c12'; // 보통 - 주황색
  return '#28a745'; // 낮음 - 초록색
}

// 알람 로그 기능
let alarmLog = [];
const MAX_ALARMS = 50;

function initAlarmLog() {
  checkDensityAlarms();
}

function checkDensityAlarms() {
  const rows = document.querySelectorAll('.device-table tbody tr');
  const currentTime = new Date();
  
  rows.forEach(row => {
    const deviceId = row.getAttribute('data-device-id');
    const densityLevelBadge = row.querySelector('.density-level-badge');
    const deviceName = row.querySelector('.device-name-text').textContent;
    const deviceLocation = row.querySelector('.device-location-text').textContent;
    const statusBadge = row.querySelector('.device-status-badge');
    
    // 오프라인이거나 점검 중인 디바이스는 제외
    if (statusBadge && (statusBadge.classList.contains('offline') || statusBadge.classList.contains('maintenance'))) {
      return;
    }
    
    if (densityLevelBadge) {
      const level = densityLevelBadge.textContent.trim();
      const levelClass = densityLevelBadge.classList.contains('medium') ? 'medium' : 
                        densityLevelBadge.classList.contains('high') ? 'high' : null;
      
      // 보통 이상인 경우 알람 추가
      if (levelClass === 'medium' || levelClass === 'high') {
        const existingAlarm = alarmLog.find(alarm => 
          alarm.deviceId === deviceId && 
          alarm.level === levelClass &&
          (currentTime - alarm.timestamp) < 60000 // 1분 이내의 동일 알람은 제외
        );
        
        if (!existingAlarm) {
          addAlarm({
            deviceId: deviceId,
            deviceName: deviceName,
            location: deviceLocation,
            level: levelClass,
            levelText: level,
            timestamp: currentTime
          });
        }
      }
    }
  });
}

function addAlarm(alarmData) {
  // 최대 알람 수 제한
  if (alarmLog.length >= MAX_ALARMS) {
    alarmLog.shift(); // 가장 오래된 알람 제거
  }
  
  alarmLog.push(alarmData);
  renderAlarmLog();
}

function renderAlarmLog() {
  const alarmLogContainer = document.getElementById('alarmLog');
  if (!alarmLogContainer) return;
  
  // 최신 알람이 위에 오도록 정렬
  const sortedAlarms = [...alarmLog].sort((a, b) => b.timestamp - a.timestamp);
  
  alarmLogContainer.innerHTML = sortedAlarms.map(alarm => {
    const timeStr = formatTime(alarm.timestamp);
    const levelClass = alarm.level;
    const levelText = alarm.level === 'high' ? '높음' : '보통';
    
    return `
      <div class="alarm-item ${levelClass}">
        <div class="alarm-time">${timeStr}</div>
        <div class="alarm-content">
          <span class="alarm-device">${alarm.deviceName}</span>
          <span class="alarm-location">(${alarm.location})</span>
          <span class="alarm-level ${levelClass}">밀집레벨: ${levelText}</span>
        </div>
      </div>
    `;
  }).join('');
  
  // 스크롤을 맨 위로
  alarmLogContainer.scrollTop = 0;
}

function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

window.clearAlarms = function() {
  if (confirm('모든 알람을 지우시겠습니까?')) {
    alarmLog = [];
    renderAlarmLog();
  }
};
