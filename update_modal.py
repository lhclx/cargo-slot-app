#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新 index.html 中的 orderModal 表单内容"""

import sys

# 读取文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 旧的表单内容（需要替换）
old_form = '''  <h2 id="omt">新建订单</h2>
  <input type="hidden" id="oId">
  <div class="fg">
    <div class="fg"><label>订单号 *</label><input type="text" id="oJobNo" required placeholder="如 JOB-2026-001"></div>
    <div class="fg"><label>类型</label><select id="oDocType"><option>出口</option><option>进口</option></select></div>
    <div class="fg fl"><label>收货人</label><input type="text" id="oConsignee" placeholder="Consignee name"></div>
    <div class="fg fl"><label>发货人</label><input type="text" id="oShipper" placeholder="Shipper name"></div>
    <div class="fg"><label>起运港</label><input type="text" id="oPol" placeholder="NINGBO"></div>
    <div class="fg"><label>目的港</label><input type="text" id="oPod" placeholder="NZAKL"></div>
    <div class="fg"><label>船公司</label><input type="text" id="oCarrier" placeholder="CMA CGM"></div>
    <div class="fg"><label>船名/航次</label><input type="text" id="oVoyage" placeholder="ANL GUAYAQUIL/624S"></div>
    <div class="fg"><label>ETD</label><input type="date" id="oEtd"></div>
    <div class="fg"><label>ETA</label><input type="date" id="oEta"></div>
    <div class="fg"><label>柜型</label><input type="text" id="oCntr" placeholder="40HQ x 1"></div>
    <div class="fg"><label>操作归属</label><input type="text" id="oOperator" placeholder="跟单操作员"></div>
    <div class="fg"><label>状态</label><select id="oStatus"><option>空闲</option><option>已预订</option><option>已确认</option><option>已放货</option><option>已完结</option></select></div>
    <div class="fg"><label>件数</label><input type="number" id="oPieces" placeholder="0"></div>
    <div class="fg"><label>毛重(KG)</label><input type="number" id="oWeight" placeholder="0"></div>
    <div class="fg"><label>体积(CBM)</label><input type="number" step="0.1" id="oVolume" placeholder="0"></div>
    <div class="fg"><label>销售价格(USD)</label><input type="number" step="0.01" id="oPrice" placeholder="0"></div>
    <div class="fg fl"><label>货物(英文)</label><input type="text" id="oGoodsEn" placeholder="Goods description"></div>
    <div class="fg fl"><label>货物(中文)</label><input type="text" id="oGoodsCn" placeholder="中文描述"></div>
    <div class="fg fl"><label>备注</label><textarea id="oRemark" rows="2" placeholder="备注信息"></textarea></div>
  </div>
  <div class="mft">
    <button type="button" class="btn btn-s" style="background:var(--bdr)" onclick="closeOrderModal()">取消</button>
    <button type="button" class="btn btn-s btn-g" onclick="saveOrderItem()">💾 保存</button>
  </div>
</div>
</div>'''

# 新的表单内容
new_form = '''  <h2 id="omt">新建订单</h2>
  <input type="hidden" id="oId">
  <div class="fg">
    <div class="fg"><label>船司 *</label><input type="text" id="oCarrier" required placeholder="如 MSC"></div>
    <div class="fg"><label>SO号 *</label><input type="text" id="oSoNo" required placeholder="如 MSU2894710"></div>
    <div class="fg"><label>约号</label><input type="text" id="oBookingNo" placeholder="Booking Reference"></div>
    <div class="fg"><label>起运港</label><input type="text" id="oPortLoading" placeholder="NINGBO"></div>
    <div class="fg"><label>目的港</label><input type="text" id="oPortDischarge" placeholder="SYDNEY"></div>
    <div class="fg"><label>柜型</label><input type="text" id="oContainerType" placeholder="40HQ"></div>
    <div class="fg"><label>箱号封号</label><input type="text" id="oContainerSeal" placeholder="箱号/封号"></div>
    <div class="fg"><label>分配客户</label><input type="text" id="oClient" placeholder="客户名称"></div>
    <div class="fg"><label>销售价格</label><input type="number" step="0.01" id="oSalePrice" placeholder="0.00"></div>
    <div class="fg fl"><label>备注</label><textarea id="oRemark" rows="2" placeholder="备注信息"></textarea></div>
    <div class="fg"><label>截VGM时间</label><input type="date" id="oCutVgm"></div>
    <div class="fg"><label>截SI时间</label><input type="date" id="oCutSi"></div>
    <div class="fg fl"><label>拖车</label><input type="text" id="oTruck" placeholder="拖车信息"></div>
    <div class="fg fl"><label>报关</label><input type="text" id="oCustoms" placeholder="报关信息"></div>
    <div class="fg"><label>应付</label><input type="number" step="0.01" id="oPayable" placeholder="0.00"></div>
    <div class="fg"><label>应收</label><input type="number" step="0.01" id="oReceivable" placeholder="0.00"></div>
    <div class="fg"><label>放单</label><select id="oLeased"><option value="否">否</option><option value="是">是</option></select></div>
  </div>
  <div class="mft">
    <button type="button" class="btn btn-s" style="background:var(--bdr)" onclick="closeOrderModal()">取消</button>
    <button type="button" class="btn btn-s btn-g" onclick="saveOrderItem()">💾 保存</button>
  </div>
</div>
</div>'''

# 替换
if old_form in content:
    content = content.replace(old_form, new_form)
    # 保存文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 成功更新 orderModal 表单")
    sys.exit(0)
else:
    print("❌ 未找到旧的表单内容，请手动检查")
    sys.exit(1)
