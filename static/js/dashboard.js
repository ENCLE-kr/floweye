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
});

