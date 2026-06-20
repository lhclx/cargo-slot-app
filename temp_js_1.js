
// 使用配置的 API 地址，如果没有配置则使用相对路径（本地开发）
const API = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE_URL) ? CONFIG.API_BASE_URL + '/api' : '/api';
let allData=[]; let editId=null;
let currentUser = null;
console.log('API endpoint:', API);

const ST_MAP={'空闲':0,'已预订':1,'已确认':2,'已放货':3,'已完结':4};
const ST_CLS=['bg-0','bg-1','bg-2','bg-3','bg-4'];
const CHART_COLORS=['#2F5496','#28a745','#ffc107','#17a2b8','#fd7e14','#6f42c1','#e83e8c','#20c997','#fd7e14','#6610f2'];

// ==================== Authentication Functions ====================

async function checkAuth() {
  try {
    const resp = await fetch(API + '/auth/me', { credentials: 'include' });
    if (resp.ok) {
      currentUser = await resp.json();
      document.getElementById('loginView').style.display = 'none';
      document.getElementById('mainContent').style.display = 'block';
      document.getElementById('userNickname').textContent = currentUser.nickname || currentUser.username;
      document.getElementById('userRole').textContent = currentUser.role;
      // Load main data
      refreshData();
    } else {
      // Not authenticated, show login
      document.getElementById('loginView').style.display = 'flex';
      document.getElementById('mainContent').style.display = 'none';
    }
  } catch(e) {
    console.error('Auth check failed:', e);
    document.getElementById('loginView').style.display = 'flex';
    document.getElementById('mainContent').style.display = 'none';
  }
}

async function doLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const msgEl = document.getElementById('loginMsg');
  
  if (!username || !password) {
    msgEl.className = 'login-msg error';
    msgEl.textContent = '请输入用户名和密码';
    return;
  }
  
  try {
    const resp = await fetch(API + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });
    
    const data = await resp.json();
    
    if (resp.ok && data.ok) {
      msgEl.className = 'login-msg success';
      msgEl.textContent = '登录成功！';
      setTimeout(() => checkAuth(), 500);
    } else {
      msgEl.className = 'login-msg error';
      msgEl.textContent = data.error || '登录失败';
    }
  } catch(e) {
    msgEl.className = 'login-msg error';
    msgEl.textContent = '网络错误：' + e.message;
  }
}

async function doLogout() {
  try {
    await fetch(API + '/auth/logout', { 
      method: 'POST',
      credentials: 'include' 
    });
  } catch(e) {
    console.error('Logout error:', e);
  }
  currentUser = null;
  document.getElementById('loginUsername').value = '';
  document.getElementById('loginPassword').value = '';
  document.getElementById('loginView').style.display = 'flex';
  document.getElementById('mainContent').style.display = 'none';
  document.getElementById('userDropdown').classList.remove('on');
}

function toggleUserMenu() {
  const dropdown = document.getElementById('userDropdown');
  dropdown.classList.toggle('on');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const userMenu = document.getElementById('userMenu');
  if (userMenu && !userMenu.contains(e.target)) {
    document.getElementById('userDropdown').classList.remove('on');
  }
});

// Allow Enter key to trigger login
document.getElementById('loginPassword').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') doLogin();
});

// ==================== Change Password ====================

function openChangePasswordModal() {
  document.getElementById('userDropdown').classList.remove('on');
  document.getElementById('changePwdModal').classList.add('on');
  document.getElementById('oldPassword').value = '';
  document.getElementById('newPassword').value = '';
  document.getElementById('confirmPassword').value = '';
  document.getElementById('changePwdMsg').textContent = '';
}

function closeChangePasswordModal() {
  document.getElementById('changePwdModal').classList.remove('on');
}

async function doChangePassword() {
  const oldPwd = document.getElementById('oldPassword').value;
  const newPwd = document.getElementById('newPassword').value;
  const confirmPwd = document.getElementById('confirmPassword').value;
  const msgEl = document.getElementById('changePwdMsg');
  
  if (!oldPwd || !newPwd || !confirmPwd) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '请填写所有字段';
    return;
  }
  
  if (newPwd.length < 6) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '新密码至少6位';
    return;
  }
  
  if (newPwd !== confirmPwd) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '两次输入的新密码不一致';
    return;
  }
  
  try {
    const resp = await fetch(API + '/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
    });
    
    const data = await resp.json();
    
    if (resp.ok && data.ok) {
      msgEl.style.color = '#28a745';
      msgEl.textContent = '密码修改成功！';
      setTimeout(closeChangePasswordModal, 1500);
    } else {
      msgEl.style.color = '#dc3545';
      msgEl.textContent = data.error || '修改失败';
    }
  } catch(e) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '网络错误：' + e.message;
  }
}

// ==================== User Management ====================

async function openUserMgmtModal() {
  document.getElementById('userDropdown').classList.remove('on');
  document.getElementById('userMgmtModal').classList.add('on');
  await loadUsers();
}

function closeUserMgmtModal() {
  document.getElementById('userMgmtModal').classList.remove('on');
}

function openAddUserForm() {
  document.getElementById('addUserForm').style.display = 'block';
  document.getElementById('newUserUsername').value = '';
  document.getElementById('newUserPassword').value = '';
  document.getElementById('newUserNickname').value = '';
  document.getElementById('newUserRole').value = 'operator';
  document.getElementById('newUserPermissions').value = '';
  document.getElementById('addUserMsg').textContent = '';
}

function cancelAddUser() {
  document.getElementById('addUserForm').style.display = 'none';
}

async function loadUsers() {
  try {
    const resp = await fetch(API + '/users', { credentials: 'include' });
    const data = await resp.json();
    
    if (!resp.ok) {
      document.getElementById('userTableContainer').innerHTML = '<p style="color:red;">加载失败：' + (data.error || '未知错误') + '</p>';
      return;
    }
    
    let html = '<table class="user-table"><thead><tr><th>ID</th><th>用户名</th><th>昵称</th><th>角色</th><th>权限</th><th>创建时间</th><th>操作</th></tr></thead><tbody>';
    
    data.forEach(user => {
      html += `<tr>
        <td>${user.id}</td>
        <td>${esc(user.username)}</td>
        <td>${esc(user.nickname || '')}</td>
        <td><span class="bg ${user.role === 'admin' ? 'bg-0' : user.role === 'operator' ? 'bg-1' : 'bg-4'}">${user.role}</span></td>
        <td>${esc(user.permissions || '-')}</td>
        <td>${user.created_at ? fmtDate(user.created_at) : '-'}</td>
        <td class="act">
          <button class="btn btn-s btn-p" onclick="openEditUser(${user.id})">编辑</button>
          ${user.id !== currentUser.id ? `<button class="btn btn-s btn-r" onclick="deleteUser(${user.id}, '${esc(user.username)}')">删除</button>` : ''}
        </td>
      </tr>`;
    });
    
    html += '</tbody></table>';
    document.getElementById('userTableContainer').innerHTML = html;
  } catch(e) {
    document.getElementById('userTableContainer').innerHTML = '<p style="color:red;">加载失败：' + e.message + '</p>';
  }
}

async function doAddUser() {
  const username = document.getElementById('newUserUsername').value.trim();
  const password = document.getElementById('newUserPassword').value;
  const nickname = document.getElementById('newUserNickname').value.trim();
  const role = document.getElementById('newUserRole').value;
  const permissions = document.getElementById('newUserPermissions').value.trim();
  const msgEl = document.getElementById('addUserMsg');
  
  if (!username || !password) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '用户名和密码为必填项';
    return;
  }
  
  try {
    const resp = await fetch(API + '/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password, nickname, role, permissions })
    });
    
    const data = await resp.json();
    
    if (resp.ok && data.ok) {
      msgEl.style.color = '#28a745';
      msgEl.textContent = '添加成功！';
      document.getElementById('addUserForm').style.display = 'none';
      await loadUsers();
    } else {
      msgEl.style.color = '#dc3545';
      msgEl.textContent = data.error || '添加失败';
    }
  } catch(e) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '网络错误：' + e.message;
  }
}

async function openEditUser(userId) {
  try {
    const resp = await fetch(API + '/users', { credentials: 'include' });
    const data = await resp.json();
    const user = data.find(u => u.id === userId);
    
    if (!user) {
      alert('用户不存在');
      return;
    }
    
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUserUsername').value = user.username;
    document.getElementById('editUserNickname').value = user.nickname || '';
    document.getElementById('editUserRole').value = user.role;
    document.getElementById('editUserPermissions').value = user.permissions || '';
    document.getElementById('editUserMsg').textContent = '';
    document.getElementById('editUserModal').classList.add('on');
  } catch(e) {
    alert('加载用户失败：' + e.message);
  }
}

function closeEditUserModal() {
  document.getElementById('editUserModal').classList.remove('on');
}

async function doEditUser() {
  const userId = document.getElementById('editUserId').value;
  const nickname = document.getElementById('editUserNickname').value.trim();
  const role = document.getElementById('editUserRole').value;
  const permissions = document.getElementById('editUserPermissions').value.trim();
  const msgEl = document.getElementById('editUserMsg');
  
  try {
    const resp = await fetch(API + '/users/' + userId, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ nickname, role, permissions })
    });
    
    const data = await resp.json();
    
    if (resp.ok && data.ok) {
      msgEl.style.color = '#28a745';
      msgEl.textContent = '保存成功！';
      setTimeout(async () => {
        closeEditUserModal();
        await loadUsers();
      }, 1000);
    } else {
      msgEl.style.color = '#dc3545';
      msgEl.textContent = data.error || '保存失败';
    }
  } catch(e) {
    msgEl.style.color = '#dc3545';
    msgEl.textContent = '网络错误：' + e.message;
  }
}

async function deleteUser(userId, username) {
  if (!confirm(`确定要删除用户 "${username}" 吗？此操作不可恢复！`)) return;
  
  try {
    const resp = await fetch(API + '/users/' + userId, {
      method: 'DELETE',
      credentials: 'include'
    });
    
    const data = await resp.json();
    
    if (resp.ok && data.ok) {
      alert('删除成功！');
      await loadUsers();
    } else {
      alert('删除失败：' + (data.error || '未知错误'));
    }
  } catch(e) {
    alert('删除失败：' + e.message);
  }
}

// ==================== Main App Functions ====================

async function loadStats(){
  const r=await fetch(API+'/stats', { credentials: 'include' }); const d=await r.json();
  const c={total:'#2F5496','空闲':'#28a745','已预订':'#ffc107','已确认':'#17a2b8','已放货':'#fd7e14','已完结':'#6c757d'};
  let h=`<div class="sc"><div class="sn">${d.total}</div><div class="sl">总舱位</div></div>`;
  for(const s of['空闲','已预订','已确认','已放货','已完结']) h+=`<div class="sc"><div class="sn" style="color:${c[s]}">${d.by_status[s]||0}</div><div class="sl">${s}</div></div>`;
  document.getElementById('statsRow').innerHTML=h;
  await loadWeekOptions();
  await loadTeuStats();

  // charts
  renderChart('cs',d.by_status);
  renderChart('cc',d.by_carrier);
  renderChart('cp',d.by_destination);
  renderChart('co',d.by_operator);

  // populate filter dropdowns
  const carriers=new Set(); const ops=new Set();
  const slotsResp = await fetch(API+'/slots', { credentials: 'include' });
  const arr = await slotsResp.json();
  arr.forEach(s=>{carriers.add(s.carrier);ops.add(s.operator||'');});
  const fc=document.getElementById('fc'); Array.from(fc.options).forEach(o=>{if(o.value&&o.value!=='全部船公司') o.remove()});
  carriers.forEach(v=>{if(v) fc.appendChild(new Option(v,v))});
  const fo=document.getElementById('fo'); Array.from(fo.options).forEach(o=>{if(o.value&&o.value!=='全部操作') o.remove()});
  ops.forEach(v=>{if(v) fo.appendChild(new Option(v,v))});
}

function renderChart(id,data){
  const el=document.getElementById(id); if(!el) return;
  const entries=Object.entries(data).sort((a,b)=>b[1]-a[1]).slice(0,10);
  if(!entries.length){el.innerHTML='<p style="color:var(--lt);text-align:center;width:100%">暂无数据</p>';return;}
  const max=Math.max(...entries.map(e=>e[1]),1);
  el.innerHTML=entries.map(([k,v],i)=>`<div class="cbw"><div class="cb" style="height:${v/max*140}px;background:${CHART_COLORS[i%CHART_COLORS.length]}"></div><div class="cbv">${v}</div><div class="cbl" title="${k}">${k}</div></div>`).join('');
}

async function loadWeekOptions(){
  try{
    const r=await fetch(API+'/stats/weeks', { credentials: 'include' });
    const weeks=await r.json();
    const sel=document.getElementById('fWeek');
    const cur=sel.value;
    sel.innerHTML='<option value="">全部周</option>';
    weeks.forEach(w=>{const o=document.createElement('option');o.value=w;o.textContent=w;sel.appendChild(o);});
    if(cur && weeks.includes(cur)) sel.value=cur;
  }catch(e){console.warn('加载周选项失败',e);}
}

async function loadTeuStats(){
  const week=document.getElementById('fWeek').value;
  try{
    const r=await fetch(API+'/stats/teu'+(week?'?week='+encodeURIComponent(week):''), { credentials: 'include' });
    const d=await r.json();
    const bsa=d.stats['BSA']||{};
    const ltr=d.stats['LTR']||{};
    const nor=d.stats['NOR']||{};
    document.getElementById('teuBsa').textContent=bsa.teu||0;
    document.getElementById('teuLtr').textContent=ltr.teu||0;
    document.getElementById('teuNor').textContent=nor.teu||0;
    document.getElementById('teuTotal').textContent=d.total_teu||0;
  }catch(e){console.warn('加载TEU统计失败',e);}
}

async function loadSlots(){
  const p=new URLSearchParams();
  const fw=document.getElementById('fWeek').value; if(fw) p.append('week',fw);
  const fs=document.getElementById('fs').value; if(fs) p.append('status',fs);
  const fc=document.getElementById('fc').value; if(fc) p.append('carrier',fc);
  const fo=document.getElementById('fo').value; if(fo) p.append('operator',fo);
  const fq=document.getElementById('fq').value; if(fq) p.append('q',fq);
  const etdStart=document.getElementById('fEtdStart').value; if(etdStart) p.append('etd_start',etdStart);
  const etdEnd=document.getElementById('fEtdEnd').value; if(etdEnd) p.append('etd_end',etdEnd);
  const r=await fetch(API+'/slots?'+p.toString(), { credentials: 'include' }); allData=await r.json();
  // 按ETD升序排序，相同ETD按约号归类
  allData.sort((a,b)=>{if(!a.etd)return 1;if(!b.etd)return -1;const c=a.etd.localeCompare(b.etd);if(c!==0)return c;return (a.booking_ref||'').localeCompare(b.booking_ref||'');});
  renderTable();
  loadTeuStats();  // 周筛选变化时同步更新 TEU 统计
}

function renderTable(){
  const tb=document.getElementById('tb'); const es=document.getElementById('es');
  if(!allData.length){tb.innerHTML='';es.style.display='block';return;}
  es.style.display='none';
  tb.innerHTML=allData.map(s=>{
    const si=ST_MAP[s.status]??0;
    return `<tr>
      <td>${s.id}</td><td>${esc(s.carrier)}</td><td style="font-weight:600">${esc(s.so_no)}</td><td>${esc(s.booking_ref)}</td>
      <td>${esc(s.loading_port)}</td><td>${esc(s.destination_port)}</td><td><strong>${esc(s.container_type)}</strong></td>
      <td>${s.quantity}</td><td>${fmtDate(s.etd)}</td><td>${fmtDate(s.eta)}</td>
      <td style="background:#fff3e0;color:#e65100;font-weight:600;text-align:center">${s.week||'-'}</td>
      <td><span class="bg ${ST_CLS[si]||''}">${esc(s.status)}</span></td>
      <td>${esc(s.client)}</td><td>${esc(s.operator)}</td><td style="color:#28a745;font-weight:600">${s.sale_price ? '$'+parseFloat(s.sale_price).toFixed(2) : '-'}</td><td>${esc(s.remark||'')}</td>
      <td class="act"><button class="btn btn-s btn-p" onclick="editSlot(${s.id})">编辑</button><button class="btn btn-s btn-r" onclick="delSlot(${s.id})">删除</button></td>
    </tr>`;
  }).join('');
}

function esc(s){if(!s)return '';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function fmtDate(s){if(!s)return '';const m=String(s).match(/(\d{4}-\d{2}-\d{2})/);return m?m[1]:s;}

function extractDate(s){if(!s)return '';const m=String(s).match(/(\d{4}-\d{2}-\d{2})/);return m?m[1]:'';}

function openModal(){editId=null;document.getElementById('mt').textContent='新增舱位';document.getElementById('fm').reset();document.getElementById('fid').value='';document.getElementById('modal').classList.add('on');}

function closeModal(){document.getElementById('modal').classList.remove('on');}

async function editSlot(id){
  const s=allData.find(x=>x.id===id); if(!s)return;
  editId=id; document.getElementById('mt').textContent='编辑舱位';
  document.getElementById('fid').value=s.id;
  document.getElementById('fcarr').value=s.carrier||'';
  document.getElementById('fso').value=s.so_no||'';
  document.getElementById('fbk').value=s.booking_ref||'';
  document.getElementById('flp').value=s.loading_port||'';
  document.getElementById('fdp').value=s.destination_port||'';
  document.getElementById('fct').value=s.container_type||'';
  document.getElementById('fqy').value=s.quantity||1;
  document.getElementById('fetd').value=extractDate(s.etd);
  document.getElementById('feta').value=extractDate(s.eta);
  document.getElementById('fst').value=s.status||'空闲';
  document.getElementById('fcl').value=s.client||'';
  document.getElementById('fop').value=s.operator||'';
  document.getElementById('fsp').value=s.sale_price||'';
  document.getElementById('frm').value=s.remark||'';
  document.getElementById('modal').classList.add('on');
}

// ==================== SO 识别功能 ====================
async function recognizeSO(file){
  console.log('[SO识别] 开始识别，文件名：', file.name, '，大小：', (file.size/1024).toFixed(1), 'KB');
  if(!file){alert('请选择文件');return;}
  const statusEl=document.getElementById('soRecognizeStatus');
  statusEl.innerHTML='<span style="color:#4a90d9">⏳ 正在识别中，请稍候...</span>';
  
  const fd=new FormData();
  fd.append('file',file);
  
  try{
    console.log('[SO识别] 发送请求到 /api/recognize-so...');
    const resp=await fetch('/api/recognize-so',{method:'POST',body:fd,signal:AbortSignal.timeout(120000), credentials: 'include'});
    console.log('[SO识别] 响应状态：', resp.status, resp.statusText);
    const result=await resp.json();
    console.log('[SO识别] 响应数据：', result);
    
    if(!resp.ok){
      statusEl.innerHTML='<span style="color:red">❌ '+(result.error||'识别失败')+'</span>';
      alert('识别失败: '+(result.error||'未知错误'));
      return;
    }
    
    const d=result.data;
    
    // 填充表单
    if(d.carrier){
      const sel=document.getElementById('fcarr');
      if([...sel.options].some(o=>o.value===d.carrier)){sel.value=d.carrier;}
      else{sel.value='其他';}
    }
    if(d.so_no) document.getElementById('fso').value=d.so_no;
    if(d.booking_ref) document.getElementById('fbk').value=d.booking_ref;
    if(d.loading_port) document.getElementById('flp').value=d.loading_port;
    if(d.destination_port) document.getElementById('fdp').value=d.destination_port;
    if(d.container_type){const s=document.getElementById('fct');if([...s.options].some(o=>o.value===d.container_type))s.value=d.container_type;}
    if(d.quantity) document.getElementById('fqy').value=d.quantity;
    if(d.etd) document.getElementById('fetd').value=extractDate(d.etd);
    if(d.eta) document.getElementById('feta').value=extractDate(d.eta);
    
    statusEl.innerHTML='<span style="color:green">✅ 识别成功！已自动填充，请核对后保存</span>';
    
    // 自动打开新增舱位弹窗（不重置表单，保持已填充数据）
    editId = null;
    document.getElementById('mt').textContent = '新增舱位 (SO识别)';
    document.getElementById('modal').classList.add('on');
    
    // 5秒后清除状态
    setTimeout(()=>{statusEl.innerHTML='';},5000);
    
  }catch(err){
    statusEl.innerHTML='<span style="color:red">❌ 请求失败: '+err.message+'</span>';
  }
}

async function saveSlot(e){
  e.preventDefault();
  const payload={
    carrier:document.getElementById('fcarr').value,
    so_no:document.getElementById('fso').value.trim(),
    booking_ref:document.getElementById('fbk').value.trim(),
    loading_port:document.getElementById('flp').value.trim().toUpperCase(),
    destination_port:document.getElementById('fdp').value.trim().toUpperCase(),
    container_type:document.getElementById('fct').value,
    quantity:parseInt(document.getElementById('fqy').value)||1,
    etd:document.getElementById('fetd').value,
    eta:document.getElementById('feta').value,
    status:document.getElementById('fst').value,
    client:document.getElementById('fcl').value.trim(),
    operator:document.getElementById('fop').value.trim(),
    sale_price:document.getElementById('fsp').value?parseFloat(document.getElementById('fsp').value):'',
    remark:document.getElementById('frm').value.trim()
  };
  if(editId){
    await fetch(API+'/slots/'+editId,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload), credentials: 'include'});
  }else{
    await fetch(API+'/slots',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload), credentials: 'include'});
  }
  closeModal(); refreshData();
}

async function delSlot(id){
  if(!confirm('确定删除此条舱位记录？'))return;
  await fetch(API+'/slots/'+id,{method:'DELETE', credentials: 'include'});
  refreshData();
}

function swTab(t){
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  event.target.classList.add('on');
  document.getElementById('listView').style.display=t==='list'?'block':'none';
  document.getElementById('chartView').style.display=t==='chart'?'block':'none';
  document.getElementById('trashView').style.display=t==='trash'?'block':'none';
  if(t==='chart') loadStats();
  if(t==='trash') loadTrash();
}

function exportData(){
  // CSV export
  const headers=['ID','船公司','SO号','约号','起运港','目的港','柜型','数量','ETD','ETA','使用状态','分配客户','操作归属','销售价格(USD)','备注'];
  const rows=[headers.join(',')];
  allData.forEach(s=>{rows.push([s.id,s.carrier,s.so_no,s.booking_ref,s.loading_port,s.destination_port,s.container_type,s.quantity,s.etd,s.eta,s.status,s.client,s.operator,s.sale_price||'',s.remark||''].map(v=>`"${(v||'').replace(/"/g,'""')}"`).join(','));});
  const BOM='\uFEFF'; const blob=new Blob([BOM+rows.join('\n')],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`舱位导出_${new Date().toISOString().slice(0,10)}.csv`; a.click();
}

async function refreshData(){await Promise.all([loadStats(),loadSlots()]);}

// init - check authentication first
checkAuth();

// ========== 回收站功能 ==========
async function loadTrash(){
  try {
    const resp = await fetch(API + '/trash', { credentials: 'include' });
    const result = await resp.json();
    if(!result.ok) return;
    const list = document.getElementById('tbTrash');
    if(!list) return;
    
    if(result.data.length === 0){
      list.innerHTML = '<tr><td colspan="13" style="text-align:center;color:#999;padding:40px;">🗑️ 回收站为空</td></tr>';
      return;
    }
    
    let html = '';
    result.data.forEach(item => {
      html += `<tr>
        <td>${item.id}</td>
        <td>${item.carrier || ''}</td>
        <td>${item.so_no || ''}</td>
        <td>${item.booking_ref || ''}</td>
        <td>${item.loading_port || ''}</td>
        <td>${item.destination_port || ''}</td>
        <td>${item.container_type || ''}</td>
        <td>${item.quantity || ''}</td>
        <td>${item.etd || ''}</td>
        <td>${item.status || ''}</td>
        <td>${item.client || ''}</td>
        <td>${item.deleted_at || ''}</td>
        <td><button class="btn-sm btn-success" onclick="restoreTrash(${item.id})">恢复</button> <button class="btn-sm btn-danger" onclick="permanentDelete(${item.id})">彻底删除</button></td>
      </tr>`;
    });
    list.innerHTML = html;
  } catch(e) {
    console.error('加载回收站失败:', e);
  }
}

async function restoreTrash(id){
  try {
    const resp = await fetch(API + '/trash/' + id + '/restore', { method: 'POST', credentials: 'include' });
    const result = await resp.json();
    if(result.ok){
      alert('✅ 恢复成功');
      loadTrash();
      loadSlots(); // 刷新主列表
    } else {
      alert('❌ 恢复失败：' + (result.error || '未知错误'));
    }
  } catch(e) {
    alert('❌ 恢复失败：' + e.message);
  }
}

async function permanentDelete(id){
  if(!confirm('确定要彻底删除这条舱位吗？删除后无法恢复！')) return;
  try {
    const resp = await fetch(API + '/trash/' + id + '/permanent', { method: 'DELETE', credentials: 'include' });
    const result = await resp.json();
    if(result.ok){
      alert('✅ 彻底删除成功');
      loadTrash();
    } else {
      alert('❌ 删除失败：' + (result.error || '未知错误'));
    }
  } catch(e) {
    alert('❌ 删除失败：' + e.message);
  }
}

async function clearTrash(){
  if(!confirm('确定要清空回收站吗？所有数据将被永久删除！')) return;
  try {
    const resp = await fetch(API + '/trash/clear', { method: 'DELETE', credentials: 'include' });
    const result = await resp.json();
    if(result.ok){
      alert('✅ 回收站已清空');
      loadTrash();
    } else {
      alert('❌ 清空失败：' + (result.error || '未知错误'));
    }
  } catch(e) {
    alert('❌ 清空失败：' + e.message);
  }
}
// ========= SO 识别事件绑定 =========
// 方法 1：DOMContentLoaded 事件（标准方法）
document.addEventListener('DOMContentLoaded', function() {
  bindSOFileInput();
});

// 方法 2：立即执行（备用方案，防止 DOMContentLoaded 已触发）
if (document.readyState !== 'loading') {
  bindSOFileInput();
}

function bindSOFileInput() {
  const soFileInput = document.getElementById('soFileInput');
  if (soFileInput && !soFileInput.dataset.bound) {
    soFileInput.addEventListener('change', function(e) {
      console.log('[SO识别] 文件选择变化：', this.files[0]?.name);
      if (this.files && this.files[0]) {
        recognizeSO(this.files[0]);
      }
    });
    soFileInput.dataset.bound = 'true';
    console.log('[SO识别] 事件绑定成功');
  }
}

// ========== 回收站功能结束 ==========

