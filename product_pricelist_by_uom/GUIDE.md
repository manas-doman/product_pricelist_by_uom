# คู่มือเบื้องต้น: Product Pricelist By UOM

**โมดูล:** `product_pricelist_by_uom`  
**พัฒนาโดย:** Doman Soft  
**รองรับ Odoo:** 19.0  
**License:** LGPL-3

---

## 1. ปัญหาที่โมดูลนี้แก้ไข

ระบบ Pricelist มาตรฐานของ Odoo กำหนดราคาได้เฉพาะหน่วยฐาน (Base UOM) ของสินค้าเท่านั้น เช่น ถ้าสินค้ามีหน่วยเป็น **ตัว** ก็กำหนดราคาได้แค่ **ราคา/ตัว** เท่านั้น

โมดูลนี้เพิ่มความสามารถให้กำหนดราคาแยกตามหน่วยที่ขายได้ เช่น:

| หน่วย | ราคา |
|---|---|
| ตัว (Unit) | 5 บาท/ตัว |
| โหล (Dozen) | 45 บาท/โหล |

---

## 2. โครงสร้างโมดูล

```
product_pricelist_by_uom/
├── __init__.py                          # Entry point + post_init_hook
├── __manifest__.py                      # ข้อมูลโมดูล
├── models/
│   ├── __init__.py
│   ├── product_pricelist.py             # Override logic การคำนวณราคา
│   ├── product_pricelist_item.py        # เพิ่มฟิลด์ pricelist_uom_id
│   └── sale_order_line.py               # ขยายสำหรับอนาคต
└── views/
    └── product_pricelist_item_views.xml # เพิ่ม field UoM บน form view
```

---

## 3. วิธีการทำงาน (Architecture)

### 3.1 ฟิลด์ใหม่: `pricelist_uom_id`

ไฟล์: `models/product_pricelist_item.py`

```python
pricelist_uom_id = fields.Many2one('uom.uom', string='Pricelist UoM')
```

เพิ่ม field **Many2one** ลิงก์ไปยังตาราง `uom.uom` บน model `product.pricelist.item`  
ทำให้แต่ละ Pricelist Rule สามารถระบุหน่วยได้อย่างอิสระ

### 3.2 Auto-fill เมื่อเลือกสินค้า

```python
@api.onchange('product_tmpl_id')
def _onchange_product_tmpl_id(self):
    super()._onchange_product_tmpl_id()
    if self.product_tmpl_id and not self.pricelist_uom_id:
        self.pricelist_uom_id = self.product_tmpl_id.uom_id  # ดึงหน่วยฐานของสินค้า
    else:
        self.pricelist_uom_id = False
```

เมื่อผู้ใช้เลือกสินค้าบน Pricelist Rule ระบบจะ **ดึงหน่วยฐาน** ของสินค้ามาใส่อัตโนมัติ  
ผู้ใช้สามารถเปลี่ยนเป็นหน่วยอื่นได้ด้วยตนเอง

### 3.3 Logic การคำนวณราคา

ไฟล์: `models/product_pricelist.py`

**ขั้นตอนที่ 1** — ส่ง UOM ปัจจุบันไปพร้อมกับการคำนวณ:

```python
def _compute_price_rule(self, products, quantity, *, uom=None, ...):
    if uom not in [None, '']:
        kwargs['sale_uom'] = uom          # เก็บ UOM ที่ใช้ขายจริงไว้ใน kwargs
    result = super()._compute_price_rule(...)
    return result
```

**ขั้นตอนที่ 2** — กรอง Rule ให้ตรงกับ UOM:

```python
def _get_applicable_rules_domain(self, products, date, **kwargs):
    domain = super()._get_applicable_rules_domain(...)
    if 'sale_uom' in kwargs and len(products) == 1:
        uom = kwargs['sale_uom']
        domain.insert(1, ('pricelist_uom_id', '=', uom.id))  # เพิ่มเงื่อนไข UOM
    return domain
```

ผลลัพธ์: ระบบจะเลือก Pricelist Rule ที่ `pricelist_uom_id` ตรงกับ UOM บนใบสั่งขายเท่านั้น

### 3.4 Post-Init Hook

ไฟล์: `__init__.py`

```python
def _setup_initial_price_uom(env):
    for company in env.companies:
        # หา pricelist item ที่ยังไม่มี uom กำหนด
        items = env['product.pricelist.item'].search([
            ('product_tmpl_id', '!=', False),
            ('pricelist_uom_id', '=', False)
        ])
        for item in items:
            item.pricelist_uom_id = item.product_tmpl_id.uom_id  # set หน่วยฐานให้อัตโนมัติ
```

เมื่อติดตั้งโมดูลครั้งแรก ระบบจะวิ่งอัปเดต Pricelist Rule **ที่มีอยู่เดิม** ทั้งหมดโดยกำหนดหน่วยฐานให้อัตโนมัติ เพื่อไม่ให้ข้อมูลเก่าพัง

### 3.5 View (XML)

ไฟล์: `views/product_pricelist_item_views.xml`

```xml
<xpath expr="//field[@name='product_id']" position="after">
    <field name="pricelist_uom_id" invisible="display_applied_on != '1_product'"/>
</xpath>
```

เพิ่ม field `Pricelist UoM` ต่อจาก field `Product` บน form view  
Field นี้จะ **ซ่อนอัตโนมัติ** ถ้า Rule ไม่ได้ระบุสินค้าเฉพาะเจาะจง

---

## 4. วิธีติดตั้ง

1. คัดลอกโฟลเดอร์ `product_pricelist_by_uom` ไปไว้ใน addons path ของ Odoo
2. รีสตาร์ท Odoo server
3. ไปที่ **Settings → Apps → Update Apps List**
4. ค้นหา `Product Pricelist By UOM` แล้วกด **Install**

> **หมายเหตุ:** โมดูลนี้ต้องการ module `sale` เป็น dependency

---

## 5. วิธีใช้งาน

### ตั้งค่า Pricelist Rule ตามหน่วย

1. ไปที่ **Sales → Configuration → Pricelists**
2. เลือก Pricelist ที่ต้องการแก้ไข
3. ในส่วน **Rules** กด **Add a line**
4. ตั้งค่า:
   - **Apply On:** `1 Product` (ต้องเลือกเป็นสินค้าเฉพาะ)
   - **Product:** เลือกสินค้า
   - **Pricelist UoM:** เลือกหน่วยที่ต้องการกำหนดราคา เช่น `โหล`
   - **Price:** กำหนดราคาสำหรับหน่วยนั้น เช่น `45`
5. กด **Save**

### ตัวอย่างการตั้งค่า

| Product | Pricelist UoM | Price | หมายความว่า |
|---|---|---|---|
| สินค้า A | ตัว (Unit) | 5.00 | 5 บาท/ตัว |
| สินค้า A | โหล (Dozen) | 45.00 | 45 บาท/โหล |

### สร้างใบสั่งขาย

1. สร้าง Sales Order ใหม่
2. เลือก Pricelist ที่ตั้งค่าไว้
3. เพิ่มสินค้า แล้วเลือก **UoM** เป็น `โหล`
4. ระบบจะดึงราคา **45 บาท** มาให้อัตโนมัติ

---

## 6. ข้อควรระวัง

| หัวข้อ | รายละเอียด |
|---|---|
| `display_applied_on` | Field `Pricelist UoM` จะปรากฏก็ต่อเมื่อ Rule ถูกตั้งค่าเป็น **1 Product** เท่านั้น |
| ข้อมูลเดิม | Post-init hook จะตั้งหน่วยให้อัตโนมัติ แต่ควรตรวจสอบว่าหน่วยที่ถูก assign ตรงตามที่ต้องการ |
| Rule ที่ไม่มี UOM | ถ้า Rule ไม่มี `pricelist_uom_id` ระบบจะไม่เลือก Rule นั้นเมื่อมีการส่ง `sale_uom` มา |
| `sale_order_line.py` | ปัจจุบันยังว่างอยู่ เตรียมไว้สำหรับขยาย logic เพิ่มเติมในอนาคต |

---

## 7. Flow สรุป

```
ผู้ใช้เลือก UoM บน Sale Order Line
         │
         ▼
_compute_price_rule() รับ uom parameter
         │
         ▼
เก็บ uom เป็น kwargs['sale_uom']
         │
         ▼
_get_applicable_rules_domain() เพิ่ม filter (pricelist_uom_id = uom.id)
         │
         ▼
ระบบเลือกเฉพาะ Rule ที่ UoM ตรงกัน
         │
         ▼
คืนค่าราคาที่ถูกต้องตามหน่วย
```
