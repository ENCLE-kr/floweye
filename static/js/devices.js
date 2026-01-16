document.addEventListener('DOMContentLoaded', () => {
  const deviceGrid = document.getElementById('device-grid');
  const emptyState = document.getElementById('empty-state');
  const totalCount = document.getElementById('total-count');
  const deviceForm = document.getElementById('device-form');
  const modal = document.getElementById('modal');
  const searchInput = document.getElementById('search-input');

  if (!deviceGrid || !deviceForm || !modal || !searchInput) {
    return;
  }

  let devices = JSON.parse(localStorage.getItem('devices_v2')) || [];

  const toggleModal = (show) => {
    if (show) {
      modal.classList.remove('opacity-0', 'pointer-events-none');
      modal.querySelector('div').classList.add('modal-enter');
    } else {
      modal.classList.add('opacity-0', 'pointer-events-none');
      modal.querySelector('div').classList.remove('modal-enter');
      deviceForm.reset();
    }
  };

  const showNotification = (title, message, type = 'success') => {
    const notif = document.getElementById('notification');
    const circle = document.getElementById('notif-circle');
    const icon = document.getElementById('notif-icon');

    document.getElementById('notif-title').innerText = title;
    document.getElementById('notif-message').innerText = message;

    if (type === 'success') {
      circle.className = 'w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center';
      icon.className = 'fas fa-check';
    } else {
      circle.className = 'w-10 h-10 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center';
      icon.className = 'fas fa-exclamation-triangle';
    }

    notif.style.transform = 'translateX(0)';
    setTimeout(() => {
      notif.style.transform = 'translateX(150%)';
    }, 4000);
  };

  const saveToStorage = () => {
    localStorage.setItem('devices_v2', JSON.stringify(devices));
  };

  const renderDevices = () => {
    const searchTerm = searchInput.value.toLowerCase();
    const filtered = devices.filter((device) => {
      return (
        device.device_number.toLowerCase().includes(searchTerm) ||
        device.device_mac.toLowerCase().includes(searchTerm) ||
        device.address.toLowerCase().includes(searchTerm)
      );
    });

    deviceGrid.innerHTML = '';
    totalCount.innerText = devices.length;

    if (filtered.length === 0) {
      emptyState.classList.remove('hidden');
      return;
    }
    emptyState.classList.add('hidden');

    filtered.forEach((device, index) => {
      const card = document.createElement('div');
      card.className = 'glass-panel device-card p-6 rounded-3xl relative overflow-hidden group';

      const status = Math.random() > 0.1 ? 'Online' : 'Warning';
      const statusColor = status === 'Online' ? 'text-emerald-400' : 'text-amber-400';

      card.innerHTML = `
        <div class="flex justify-between items-start mb-6">
          <div class="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-all">
            <i class="fas fa-server text-xl"></i>
          </div>
          <div class="flex gap-2">
            <button data-index="${index}" class="device-delete w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-red-400 hover:bg-red-400/10 transition-all">
              <i class="fas fa-trash-alt text-sm"></i>
            </button>
          </div>
        </div>

        <div class="space-y-1 mb-4">
          <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest">Device Number</h4>
          <p class="text-lg font-bold text-white">${device.device_number}</p>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">MAC Address</p>
            <p class="text-xs font-mono text-slate-300 mt-0.5">${device.device_mac}</p>
          </div>
          <div class="text-right">
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">Status</p>
            <p class="text-xs font-bold ${statusColor} mt-0.5 flex items-center justify-end gap-1">
              <span class="status-dot ${statusColor.replace('text', 'bg')}"></span>
              ${status}
            </p>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 space-y-3">
          <div class="flex items-center gap-3 text-slate-400">
            <i class="fas fa-map-marker-alt text-indigo-400 w-4"></i>
            <span class="text-xs truncate" title="${device.address}">${device.address}</span>
          </div>
          <div class="flex items-center gap-3 text-slate-400">
            <i class="fas fa-globe text-indigo-400 w-4"></i>
            <span class="text-xs font-mono">${device.latitude}, ${device.longitude}</span>
          </div>
        </div>

        <div class="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
      `;
      deviceGrid.appendChild(card);
    });
  };

  deviceForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const newDevice = {
      device_number: document.getElementById('device_number').value,
      device_mac: document.getElementById('device_mac').value.toUpperCase(),
      address: document.getElementById('address').value,
      latitude: document.getElementById('latitude').value,
      longitude: document.getElementById('longitude').value
    };

    const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
    if (!macRegex.test(newDevice.device_mac)) {
      showNotification('Invalid Config', 'MAC 주소 형식이 올바르지 않습니다.', 'error');
      return;
    }

    devices.unshift(newDevice);
    saveToStorage();
    renderDevices();
    toggleModal(false);
    showNotification('Deployment Success', `${newDevice.device_number} 노드가 활성화되었습니다.`);
  });

  deviceGrid.addEventListener('click', (event) => {
    const target = event.target.closest('.device-delete');
    if (!target) {
      return;
    }

    const index = Number(target.dataset.index);
    if (Number.isNaN(index) || !devices[index]) {
      return;
    }

    if (confirm('이 노드를 네트워크에서 제외하시겠습니까?')) {
      const name = devices[index].device_number;
      devices.splice(index, 1);
      saveToStorage();
      renderDevices();
      showNotification('Node Terminated', `${name} 노드가 제거되었습니다.`, 'error');
    }
  });

  searchInput.addEventListener('input', () => {
    renderDevices();
  });

  window.toggleModal = toggleModal;

  if (devices.length === 0) {
    devices = [
      {
        device_number: 'NEXUS-01',
        device_mac: 'A1:B2:C3:D4:E5:F6',
        address: '서울특별시 강남구 테헤란로 123',
        latitude: '37.5002',
        longitude: '127.0365'
      },
      {
        device_number: 'SAT-ALPHA',
        device_mac: 'FF:EE:DD:CC:BB:AA',
        address: '경기도 성남시 분당구 판교역로 231',
        latitude: '37.4012',
        longitude: '127.1086'
      }
    ];
    saveToStorage();
  }

  renderDevices();
});
