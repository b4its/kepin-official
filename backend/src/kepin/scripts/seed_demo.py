from __future__ import annotations

import asyncio
import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from kepin.core.config import get_settings
from kepin.db.base import Base
from kepin.db.models import (
    Account,
    Branch,
    Customer,
    CustomerPayment,
    CustomerPaymentAllocation,
    GoodsReceipt,
    GoodsReceiptLine,
    Incident,
    InventoryLocation,
    Invoice,
    InvoiceLine,
    JournalEntry,
    JournalLine,
    Membership,
    Notification,
    OrganizationSetting,
    OutboxEvent,
    Plan,
    PlatformAuditEvent,
    Product,
    PurchaseOrder,
    PurchaseOrderLine,
    StockBalance,
    StockMovement,
    Subscription,
    SubscriptionEvent,
    Supplier,
    Tenant,
    TenantAuditEvent,
    Transaction,
    User,
)

IDR = "IDR"
WIB = "Asia/Jakarta"
TODAY = date.today()
NOW = datetime.now(timezone.utc)

UID_ADMIN = str(uuid4())
UID_BUDI = str(uuid4())
UID_ANI = str(uuid4())
UID_SITI = str(uuid4())


TENANTS_DATA = [
    {
        "slug": "toko-maju",
        "name": "Toko Maju Jaya",
        "legal_name": "CV Toko Maju Jaya",
        "sector": "retail",
        "plan_code": "platinum",
        "status": "active",
        "members": [
            {"user_id": UID_BUDI, "role": "owner"},
            {"user_id": UID_ANI, "role": "manager"},
        ],
    },
    {
        "slug": "bengkel-maju",
        "name": "Bengkel Maju Motor",
        "legal_name": "Bengkel Maju Motor",
        "sector": "automotive",
        "plan_code": "basic",
        "status": "active",
        "members": [],
    },
    {
        "slug": "warung-segar",
        "name": "Warung Segar",
        "legal_name": "Warung Segar",
        "sector": "food",
        "plan_code": "premium",
        "status": "active",
        "members": [
            {"user_id": UID_SITI, "role": "accountant"},
        ],
    },
    {
        "slug": "fashion-baru",
        "name": "Fashion Baru",
        "legal_name": "Fashion Baru",
        "sector": "fashion",
        "plan_code": "free",
        "status": "suspended",
        "members": [],
    },
]

PRODUCT_CATEGORIES = {
    "retail": [
        "Elektronik", "Makanan & Minuman", "Rumah Tangga",
        "ATK & Kantor", "Kosmetik & Perawatan", "Mainan & Hobi",
        "Olahraga & Outdoor", "Perlengkapan Bayi", "Otomotif",
        "Buku & Media", "Fashion", "Peralatan Dapur",
        "Alat Kesehatan", "Pertukangan", "Aksesoris HP",
        "Tanaman & Kebun",
    ],
    "automotive": [
        "Sparepart Mesin", "Ban & Velg", "Oli & Pelumas",
        "Aksesoris Interior", "Body Part", "Sistem Kelistrikan",
        "Tools & Workshop", "Filter & Busi", "Rem & Kopling",
        "Suspensi", "Knalpot", "Lampu & LED",
        "Audio Mobil", "Perawatan Body", "Aki & Baterai",
        "Transmisi",
    ],
    "food": [
        "Bahan Baku", "Bumbu & Rempah", "Minuman Kemasan",
        "Snack & Cemilan", "Kemasan & Packaging", "Peralatan Masak",
        "Kebersihan Dapur", "Kue & Roti", "Produk Beku",
        "Saus & Sambal", "Beras & Sembako", "Susu & Olahan",
        "Mie & Pasta", "Makanan Kaleng", "Gula & Pemanis",
        "Bahan Kue",
    ],
    "fashion": [
        "Atasan Pria", "Bawahan Pria", "Atasan Wanita",
        "Bawahan Wanita", "Aksesoris", "Sepatu Pria",
        "Sepatu Wanita", "Tas & Dompet", "Jam Tangan",
        "Pakaian Muslim Pria", "Pakaian Muslim Wanita",
        "Pakaian Anak", "Perhiasan", "Kacamata",
        "Ikat Pinggang", "Topi & Syal",
    ],
}

SECTOR_COMPANIES = {
    "retail": ["Toko Maju Jaya", "Retail Makmur", "Sentra Belanja"],
    "automotive": ["Bengkel Maju Motor", "Auto Sparepart", "Garasi Kita"],
    "food": ["Warung Segar", "Dapur Lezat", "Pasar Rasa"],
    "fashion": ["Fashion Baru", "Mode Trendi", "Busana Kita"],
}

ACCOUNT_GROUPS: list[dict] = [
    {"prefix": "1-1", "name": "Kas & Bank", "type": "asset", "normal_balance": "debit", "count": 15},
    {"prefix": "1-2", "name": "Piutang Usaha", "type": "asset", "normal_balance": "debit", "count": 10},
    {"prefix": "1-3", "name": "Persediaan", "type": "asset", "normal_balance": "debit", "count": 20},
    {"prefix": "1-4", "name": "Aset Lancar Lainnya", "type": "asset", "normal_balance": "debit", "count": 10},
    {"prefix": "1-5", "name": "Aset Tetap", "type": "asset", "normal_balance": "debit", "count": 15},
    {"prefix": "2-1", "name": "Hutang Usaha", "type": "liability", "normal_balance": "credit", "count": 15},
    {"prefix": "2-2", "name": "Hutang Pajak", "type": "liability", "normal_balance": "credit", "count": 10},
    {"prefix": "2-3", "name": "Hutang Lainnya", "type": "liability", "normal_balance": "credit", "count": 10},
    {"prefix": "2-4", "name": "Hutang Jangka Panjang", "type": "liability", "normal_balance": "credit", "count": 5},
    {"prefix": "3-1", "name": "Modal", "type": "equity", "normal_balance": "credit", "count": 10},
    {"prefix": "3-2", "name": "Laba Ditahan", "type": "equity", "normal_balance": "credit", "count": 5},
    {"prefix": "3-3", "name": "Prive & Dividen", "type": "equity", "normal_balance": "debit", "count": 5},
    {"prefix": "3-4", "name": "Selisih Persediaan", "type": "equity", "normal_balance": "credit", "count": 5},
    {"prefix": "4-1", "name": "Pendapatan Penjualan", "type": "income", "normal_balance": "credit", "count": 20},
    {"prefix": "4-2", "name": "Pendapatan Lainnya", "type": "income", "normal_balance": "credit", "count": 10},
    {"prefix": "4-3", "name": "Diskon & Retur", "type": "income", "normal_balance": "debit", "count": 5},
    {"prefix": "5-1", "name": "Beban Operasional", "type": "expense", "normal_balance": "debit", "count": 20},
    {"prefix": "5-2", "name": "Beban Gaji", "type": "expense", "normal_balance": "debit", "count": 5},
    {"prefix": "5-3", "name": "Beban Pemasaran", "type": "expense", "normal_balance": "debit", "count": 5},
    {"prefix": "5-4", "name": "Beban Administrasi", "type": "expense", "normal_balance": "debit", "count": 10},
    {"prefix": "5-5", "name": "Penyusutan & Amortisasi", "type": "expense", "normal_balance": "debit", "count": 5},
    {"prefix": "6-1", "name": "Harga Pokok Penjualan", "type": "expense", "normal_balance": "debit", "count": 5},
]

ACCOUNT_NAMES: dict[str, list[str]] = {
    "1-1": [
        "Kas Kecil", "Kas Besar", "Bank BCA", "Bank Mandiri", "Bank BNI",
        "Bank BRI", "Bank Syariah", "Giro BCA", "Giro Mandiri", "Deposito",
        "Tabungan BCA", "Tabungan Mandiri", "Kas Harian", "Kas Toko", "Kas Cabang",
    ],
    "1-2": [
        "Piutang Usaha", "Piutang Karyawan", "Piutang Direksi", "Piutang Afiliasi",
        "Piutang Lainnya", "Piutang Konsinyasi", "DP Pembelian", "Tagihan Tertunda",
        "Piutang Tak Tertagih", "Cadangan Piutang",
    ],
    "1-3": [
        "Persediaan Barang Jadi", "Persediaan Bahan Baku", "Persediaan WIP",
        "Persediaan Packaging", "Barang Konsinyasi Masuk", "Barang Dalam Perjalanan",
        "Persediaan ATK", "Persediaan Sparepart", "Persediaan Makanan",
        "Persediaan Minuman", "Persediaan Fashion", "Persediaan Elektronik",
        "Persediaan Kosmetik", "Persediaan Obat", "Persediaan Alat Tulis",
        "Persediaan Buku", "Persediaan Mainan", "Persediaan Aksesoris",
        "Persediaan Pakaian", "Persediaan Sepatu",
    ],
    "1-4": [
        "Biaya Dibayar Dimuka Sewa", "Biaya Dibayar Dimuka Asuransi",
        "Biaya Dibayar Dimuka Lainnya", "Uang Muka Pembelian", "Uang Muka Karyawan",
        "PPN Masukan", "Pajak Dibayar Dimuka", "Setoran Jaminan",
        "Pendapatan Masih Akan Diterima", "Aset Lancar Lainnya",
    ],
    "1-5": [
        "Tanah", "Gedung", "Renovasi Gedung", "Kendaraan", "Mobil Operasional",
        "Motor Operasional", "Peralatan Kantor", "Komputer & Laptop",
        "Mesin Produksi", "Perlengkapan Toko", "Furniture Kantor",
        "Instalasi Listrik", "Mesin Kasir", "Rak Display", "AC & Elektronik",
    ],
    "2-1": [
        "Hutang Usaha Supplier A", "Hutang Usaha Supplier B", "Hutang Usaha Supplier C",
        "Hutang Usaha Lainnya", "Hutang Konsinyasi", "Hutang Komisi",
        "Hutang Pembelian Aset", "Hutang Freight", "Hutang Listrik & Air",
        "Hutang Telepon & Internet", "Hutang Sewa", "Hutang Langganan",
        "Hutang Jasa Profesional", "Hutang Bonus Karyawan", "Hutang THR",
    ],
    "2-2": [
        "Hutang PPh 21", "Hutang PPh 23", "Hutang PPh 25", "Hutang PPh 29",
        "Hutang PPN Keluaran", "Hutang PPN JLN", "Hutang Pajak Daerah",
        "Hutang Pajak Lainnya", "Hutang Bea Masuk", "Hutang Pajak Final",
    ],
    "2-3": [
        "Hutang Gaji", "Hutang BPJS", "Hutang Jamsostek", "Hutang THR Karyawan",
        "Hutang Bonus Akhir Tahun", "Hutang Lembur", "Hutang Pinjaman Karyawan",
        "Hutang Lainnya", "Titipan Pelanggan", "Setoran Jaminan Pelanggan",
    ],
    "2-4": [
        "Hutang Bank", "Hutang Leasing", "Obligasi", "Pinjaman Pemegang Saham",
        "Pinjaman Lainnya",
    ],
    "3-1": [
        "Modal Disetor", "Modal Pemilik 1", "Modal Pemilik 2",
        "Agio Saham", "Tambahan Modal Disetor", "Modal Donasi",
        "Modal Hibah", "Modal Ventura", "Setoran Modal Lainnya",
        "Cadangan Modal",
    ],
    "3-2": [
        "Laba Ditahan Tahun Lalu", "Laba Ditahan Periode Berjalan",
        "Cadangan Laba", "Saldo Laba", "Akumulasi Laba",
    ],
    "3-3": [
        "Prive Pemilik 1", "Prive Pemilik 2", "Dividen", "Prive Lainnya",
        "Penarikan Modal",
    ],
    "4-1": [
        "Penjualan Barang", "Penjualan Jasa", "Penjualan Eceran", "Penjualan Grosir",
        "Penjualan Online", "Penjualan Offline", "Penjualan Konsinyasi",
        "Penjualan Packaging", "Penjualan Sparepart", "Penjualan Makanan",
        "Penjualan Minuman", "Penjualan Fashion", "Penjualan Elektronik",
        "Pendapatan Langganan", "Pendapatan Keanggotaan", "Pendapatan Komisi",
        "Pendapatan Ongkir", "Pendapatan Instalasi", "Pendapatan Servis",
        "Penjualan Lainnya",
    ],
    "4-2": [
        "Pendapatan Bunga Bank", "Pendapatan Sewa", "Pendapatan Royalti",
        "Pendapatan Dividen", "Pendapatan Denda", "Pendapatan Administrasi",
        "Pendapatan Kurs", "Pendapatan Lelang", "Pendapatan Kupon",
        "Pendapatan Lainnya",
    ],
    "4-3": [
        "Diskon Penjualan", "Retur Penjualan", "Potongan Penjualan",
        "Penyesuaian Penjualan", "Diskon Akhir Bulan",
    ],
    "5-1": [
        "Beban Sewa Toko", "Beban Sewa Gudang", "Beban Air", "Beban Listrik",
        "Beban Telepon", "Beban Internet", "Beban Kebersihan", "Beban Keamanan",
        "Beban ATK", "Beban Cetak & Fotokopi", "Beban Perlengkapan Toko",
        "Beban Pengiriman", "Beban Bahan Bakar", "Beban Perjalanan Dinas",
        "Beban Konsumsi", "Beban Entertainment", "Beban Pemeliharaan Gedung",
        "Beban Pemeliharaan Kendaraan", "Beban Asuransi", "Beban Lainnya",
    ],
    "5-2": [
        "Beban Gaji Pokok", "Beban Tunjangan", "Beban BPJS Kesehatan",
        "Beban BPJS Ketenagakerjaan", "Beban THR",
    ],
    "5-3": [
        "Beban Iklan Online", "Beban Iklan Offline", "Beban Promosi",
        "Beban Sosial Media", "Beban Event & Sponsorship",
    ],
    "5-4": [
        "Beban Legal & Notaris", "Beban Perizinan", "Beban Pajak & Retribusi",
        "Beban Pelatihan", "Beban Langganan Software", "Beban Konsultan",
        "Beban Audit", "Beban Bank", "Beban Administrasi Bank",
        "Beban Materai & Perangko",
    ],
    "5-5": [
        "Penyusutan Gedung", "Penyusutan Kendaraan", "Penyusutan Peralatan",
        "Penyusutan Komputer", "Amortisasi Goodwill",
    ],
    "6-1": [
        "Harga Pokok Penjualan", "HPP Barang Dagangan", "HPP Jasa",
        "HPP Produksi", "HPP Lainnya",
    ],
    "3-4": [
        "Selisih Persediaan", "Selisih Stock Opname", "Koreksi Persediaan",
        "Selisih Harga", "Penyesuaian Persediaan",
    ],
}

TRANSACTION_DESCRIPTIONS = [
    "Penjualan tunai", "Penjualan kredit", "Pembelian barang dagang",
    "Pembayaran gaji karyawan", "Pembayaran listrik", "Pembayaran telepon & internet",
    "Pembayaran sewa tempat", "Pembelian ATK kantor", "Pendapatan jasa servis",
    "Pembelian perlengkapan toko", "Pembayaran BPJS", "Pembayaran pajak",
    "Pendapatan komisi penjualan", "Pembelian sparepart", "Biaya transportasi",
    "Pendapatan bunga bank", "Pembayaran iklan online", "Biaya perawatan AC",
    "Pembelian kemasan produk", "Pendapatan ongkos kirim",
    "Pembayaran konsultan", "Pembelian bahan baku", "Retur penjualan",
    "Diskon penjualan", "Pembelian furniture kantor",
]

INVOICE_NOTES = [
    "Pembayaran dalam 30 hari", "Termin net 30",
    "Pembayaran tunai sebelum pengiriman", "Termin 14 hari",
    "Pembayaran saat diterima", "Include PPN 11%",
]

PO_NOTES = [
    "Barang harus dikirim sesuai PO", "Termasuk biaya pengiriman",
    "Kualitas barang harus sesuai standar", "Pengiriman bertahap diperbolehkan",
]

NOTIFICATION_TEMPLATES = [
    ("info", "Selamat Datang", "Akun tenant berhasil dibuat dan siap digunakan"),
    ("info", "Invoice Baru", "Invoice baru telah diterbitkan untuk pelanggan"),
    ("warning", "Pembayaran Jatuh Tempo", "Ada invoice yang akan jatuh tempo dalam 3 hari"),
    ("success", "Pembayaran Diterima", "Pembayaran dari pelanggan telah dikonfirmasi"),
    ("info", "Laporan Bulanan", "Laporan keuangan bulan ini siap diunduh"),
    ("warning", "Stok Menipis", "Beberapa produk hampir mencapai batas minimum stok"),
    ("success", "Langganan Diperbarui", "Langganan paket Pro telah diperpanjang"),
    ("info", "Sistem Upgrade", "Pemeliharaan sistem dijadwalkan malam ini pukul 02:00"),
    ("error", "Gagal Sinkronisasi", "Sinkronisasi bank gagal, periksa koneksi"),
    ("success", "Data Dicadangkan", "Backup data harian berhasil dibuat"),
    ("warning", "Batas Penyimpanan", "Penyimpanan mencapai 85%, sebaiknya hapus data lama"),
    ("info", "Pembaruan Aplikasi", "Versi baru aplikasi tersedia, lakukan update"),
    ("success", "Laporan Pajak", "Laporan PPN Masa siap untuk dilaporkan"),
    ("warning", "Masa Trial Berakhir", "Masa percobaan akan berakhir dalam 7 hari"),
    ("info", "Anggaran Baru", "Anggaran bulan depan telah dibuat"),
]

TENANT_AUDIT_ACTIONS = [
    ("user.login", "system", "user"),
    ("user.logout", "system", "user"),
    ("invoice.created", "sales", "invoice"),
    ("invoice.updated", "sales", "invoice"),
    ("invoice.paid", "sales", "invoice"),
    ("invoice.sent", "sales", "invoice"),
    ("payment.received", "sales", "payment"),
    ("purchase_order.created", "purchasing", "purchase_order"),
    ("purchase_order.received", "purchasing", "purchase_order"),
    ("product.created", "inventory", "product"),
    ("product.updated", "inventory", "product"),
    ("stock.adjustment", "inventory", "stock"),
    ("journal.posted", "accounting", "journal"),
    ("journal.reversed", "accounting", "journal"),
    ("settings.updated", "system", "settings"),
    ("membership.added", "system", "membership"),
    ("report.generated", "reporting", "report"),
    ("integration.synced", "integration", "integration"),
    ("backup.completed", "system", "backup"),
    ("tax.filed", "accounting", "tax"),
]

PLATFORM_AUDIT_ACTIONS = [
    ("tenant.created", "System", "tenant", {"slug": "toko-maju"}),
    ("tenant.created", "System", "tenant", {"slug": "bengkel-maju"}),
    ("tenant.created", "System", "tenant", {"slug": "warung-segar"}),
    ("tenant.created", "System", "tenant", {"slug": "fashion-baru"}),
    ("user.registered", "System", "user", {"email": "admin@kepin.io"}),
    ("system.deploy", "DevOps", "deployment", {"version": "1.2.0"}),
    ("system.deploy", "DevOps", "deployment", {"version": "1.2.1"}),
    ("backup.completed", "System", "backup", {"size": "512MB"}),
    ("backup.completed", "System", "backup", {"size": "486MB"}),
    ("plan.upgraded", "System", "subscription", {"from": "trial", "to": "pro"}),
    ("incident.created", "System", "incident", {"severity": "warning"}),
    ("incident.resolved", "System", "incident", {"severity": "warning"}),
    ("user.role_changed", "Admin", "user", {"role": "owner"}),
    ("maintenance.scheduled", "DevOps", "maintenance", {}),
    ("security.audit", "System", "security", {"status": "passed"}),
]


def rand_decimal(min_val: int, max_val: int) -> Decimal:
    return Decimal(str(random.randint(min_val, max_val)))


def rand_choice[T](items: list[T]) -> T:
    return random.choice(items)


def pick_n[T](items: list[T], n: int) -> list[T]:
    return random.sample(items, min(n, len(items)))


def generate_accounts(tenant_id: str) -> list[Account]:
    accounts = []
    for group in ACCOUNT_GROUPS:
        prefix = group["prefix"]
        names = ACCOUNT_NAMES[prefix]
        for i in range(group["count"]):
            code = f"{prefix}{i + 1:03d}"
            name = names[i] if i < len(names) else f"{group['name']} #{i + 1}"
            accounts.append(Account(
                id=str(uuid4()), tenant_id=tenant_id,
                code=code, name=name,
                type=group["type"],
                normal_balance=group["normal_balance"],
                is_system=False, allow_posting=True,
                status="active", created_at=NOW, updated_at=NOW,
            ))
    return accounts


def generate_customers(tenant_id: str, sector: str, count: int = 200) -> list[Customer]:
    first_names = [
        "Budi", "Ani", "Siti", "Agus", "Dewi", "Rudi", "Mega", "Dwi",
        "Eko", "Tina", "Hendra", "Rina", "Adi", "Nina", "Bayu", "Lina",
        "Cahyo", "Vita", "Doni", "Nia", "Fajar", "Desi", "Gunawan", "Tari",
        "Hadi", "Rani", "Irwan", "Yuli", "Joko", "Sari", "Krisna", "Mira",
    ]
    last_names = [
        "Santoso", "Wijaya", "Kusuma", "Pratama", "Utama", "Setiawan",
        "Saputra", "Purnama", "Permana", "Hidayat", "Susilo", "Nugroho",
        "Hartono", "Gunawan", "Wibowo", "Siregar", "Nasution", "Harahap",
        "Lestari", "Anggraini", "Handayani", "Fitriani", "Rahmawati",
        "Pertiwi", "Kurniawan", "Suherman",
    ]
    customers = []
    used_codes = set()
    for i in range(count):
        code = f"C-{i + 1:04d}"
        used_codes.add(code)
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        phone = f"08{random.randint(100000000, 999999999)}"
        status = "active" if i < 190 else "inactive"
        customers.append(Customer(
            id=str(uuid4()), tenant_id=tenant_id,
            code=code, name=name,
            email=f"{code.lower()}@email.com",
            phone=phone,
            address=f"Jl. Contoh No. {i + 1}, Jakarta",
            credit_limit=Decimal(f"{random.randint(5, 50)}00000"),
            status=status, created_at=NOW, updated_at=NOW,
        ))
    return customers


def generate_suppliers(tenant_id: str, sector: str, count: int = 200) -> list[Supplier]:
    supplier_prefixes = {
        "retail": ["PT", "CV", "UD"],
        "automotive": ["PT", "CV", "Bengkel"],
        "food": ["PT", "CV", "Pabrik"],
        "fashion": ["PT", "CV", "Konveksi"],
    }
    prefixes = supplier_prefixes.get(sector, ["PT", "CV"])
    companies = SECTOR_COMPANIES.get(sector, ["Perusahaan"])
    suppliers = []
    for i in range(count):
        code = f"S-{i + 1:04d}"
        prefix = random.choice(prefixes)
        company = random.choice(companies)
        name = f"{prefix} {company} {i + 1}"
        phone = f"021{random.randint(1000000, 9999999)}"
        status = "active" if i < 190 else "inactive"
        suppliers.append(Supplier(
            id=str(uuid4()), tenant_id=tenant_id,
            code=code, name=name,
            email=f"supplier{i + 1}@example.com",
            phone=phone,
            address=f"Jl. Supplier No. {i + 1}, Jakarta",
            tax_id=f"{random.randint(100000000000000, 999999999999999)}",
            status=status, created_at=NOW, updated_at=NOW,
        ))
    return suppliers


def generate_products(tenant_id: str, sector: str, count: int = 200) -> list[Product]:
    products = []
    categories = PRODUCT_CATEGORIES.get(sector, ["Umum"])
    product_names = {
        "retail": ["Smart TV", "Kulkas", "AC", "Laptop", "HP", "Tablet", "Printer", "Blender", "Rice Cooker", "Dispenser",
                    "Mie Instan", "Kopi", "Teh", "Gula", "Minyak Goreng", "Beras", "Sabun", "Shampoo", "Pasta Gigi", "Detergen",
                    "Buku Tulis", "Pulpen", "Pensil", "Spidol", "Kertas HVS", "Map", "Lem", "Gunting", "Cutter", "Stapler",
                    "Lipstik", "Bedak", "Parfum", "Handbody", "Sunscreen", "Masker", "Toner", "Serum", "Moisturizer", "Conditioner",
                    "Mainan Mobil", "Boneka", "Puzzle", "Lego", "Remote Control", "Robot", "Bola", "Game", "Buku Cerita", "Alat Lukis"],
        "automotive": ["Oli Mesin 5W-30", "Oli Mesin 10W-40", "Oli Gardan", "Oli Transmisi", "Filter Oli", "Filter Udara",
                        "Filter AC", "Busi Iridium", "Busi Standar", "Kampas Rem Depan", "Kampas Rem Belakang", "Cakram Rem",
                        "Aki Basah", "Aki Kering", "Aki Hybrid", "Ban 195/65R15", "Ban 205/55R16", "Ban 215/45R17", "Ban 225/40R18",
                        "Knalpot Racing", "Knalpot Standar", "Lampu LED", "Lampu HID", "Lampu Depan", "Lampu Belakang",
                        "Spion", "Wiper", "Kunci Roda", "Dongkrak", "Toolkit"],
        "food": ["Tepung Terigu", "Tepung Beras", "Gula Pasir", "Gula Halus", "Garam", "Minyak Goreng", "Mentega", "Margarin",
                 "Kecap Manis", "Kecap Asin", "Saus Tomat", "Saus Sambal", "Mayonaise", "Cuka", "MSG",
                 "Kopinya Bubuk", "Teh Celup", "Coklat Bubuk", "Susu Kental Manis", "Susu UHT",
                 "Kemasan Box", "Kemasan Plastik", "Label Stiker", "Kardus", "Tape Sealer",
                 "Snack Coklat", "Keripik", "Kacang", "Biskuit", "Wafer"],
        "fashion": ["Kemeja Pria", "Kaos Pria", "Jaket Pria", "Celana Jeans", "Celana Chino", "Celana Pendek",
                     "Blouse Wanita", "Dress", "Rok", "Cardigan", "Sweater", "Hoodie",
                     "Sepatu Formal", "Sepatu Sneakers", "Sepatu Boots", "Sandal", "Heels", "Flat Shoes",
                     "Tas Selempang", "Tas Ransel", "Tas Tote", "Dompet", "Jam Tangan",
                     "Jilbab Segiempat", "Jilbab Pashmina", "Baju Muslim", "Gamis", "Koko Pria"],
    }
    names = product_names.get(sector, ["Produk Umum"])

    for i in range(count):
        name = names[i % len(names)]
        if i >= len(names):
            name = f"{name} V{1 + i // len(names)}"
        base_price = random.randint(20, 500) * 1000
        cost_price = int(base_price * random.uniform(0.5, 0.75))
        unit = rand_choice(["pcs", "kg", "liter", "box", "pack", "lusin"])
        cat = categories[i % len(categories)]
        min_stock = random.choice([5, 10, 25, 50])
        products.append(Product(
            id=str(uuid4()), tenant_id=tenant_id,
            sku=f"{sector[:3].upper()}-{i + 1:04d}",
            name=name, category=cat,
            unit=unit,
            sale_price=Decimal(str(base_price)),
            cost_price=Decimal(str(cost_price)),
            minimum_stock=Decimal(str(min_stock)),
            status="active" if i < 190 else "inactive",
            created_at=NOW, updated_at=NOW,
        ))
    return products


def pick_account(accounts: list[Account], atype: str) -> Account:
    return rand_choice([a for a in accounts if a.type == atype])


async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession)
    async with factory() as session:
        result = await session.execute(select(Tenant).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded, skipping...")
            await engine.dispose()
            return

        rng = random.Random()

        plans = [
            Plan(code="free",     name="Free",     billing_period="monthly", price=Decimal("0"),      active=True),
            Plan(code="basic",    name="Basic",    billing_period="monthly", price=Decimal("99000"),  active=True),
            Plan(code="premium",  name="Premium",  billing_period="monthly", price=Decimal("299000"), active=True),
            Plan(code="platinum", name="Platinum", billing_period="monthly", price=Decimal("799000"), active=True),
        ]
        session.add_all(plans)
        await session.flush()

        from kepin.core.auth import hash_password
        users = [
            User(id=UID_ADMIN, name="Admin KePin", email="admin@kepin.io",
                 password_hash=hash_password("admin123"),
                 status="active", email_verified_at=NOW, created_at=NOW, updated_at=NOW),
            User(id=UID_BUDI, name="Budi Santoso", email="budi@tokomaju.com",
                 password_hash=hash_password("budi123"),
                 status="active", email_verified_at=NOW, created_at=NOW, updated_at=NOW),
            User(id=UID_ANI, name="Ani Lestari", email="ani@tokomaju.com",
                 password_hash=hash_password("ani123"),
                 status="active", email_verified_at=NOW, created_at=NOW, updated_at=NOW),
            User(id=UID_SITI, name="Siti Nurhaliza", email="siti@warungsegar.com",
                 password_hash=hash_password("siti123"),
                 status="active", email_verified_at=NOW, created_at=NOW, updated_at=NOW),
        ]
        session.add_all(users)
        await session.flush()

        all_tenants = []

        for td in TENANTS_DATA:
            tid = str(uuid4())
            td["id"] = tid
            all_tenants.append(td)

            import secrets
            join_code = secrets.token_hex(8)
            tenant = Tenant(
                id=tid,
                owner_id=td["members"][0]["user_id"] if td["members"] else UID_ADMIN,
                slug=td["slug"], join_code=join_code,
                name=td["name"], legal_name=td["legal_name"],
                sector=td["sector"], timezone=WIB, currency=IDR,
                plan_code=td["plan_code"],
                status=td["status"], created_at=NOW, updated_at=NOW,
            )
            td["join_code"] = join_code
            session.add(tenant)
            await session.flush()

            org = OrganizationSetting(
                tenant_id=tid, legal_name=td["legal_name"],
                tax_id=f"{random.randint(100000000000000, 999999999999999)}",
                address=f"Jl. {td['name']} No. 1, Jakarta",
                timezone=WIB, currency=IDR,
                fiscal_year_start_month=1,
                invoice_prefix="INV", po_prefix="PO",
                created_at=NOW, updated_at=NOW,
            )
            session.add(org)

            branch = Branch(
                id=str(uuid4()), tenant_id=tid, code="main", name="Utama",
                is_main=True, status="active", created_at=NOW, updated_at=NOW,
            )
            session.add(branch)

            _plan_prices = {"free": Decimal("0"), "basic": Decimal("99000"), "premium": Decimal("299000"), "platinum": Decimal("799000")}
            plan_price = _plan_prices.get(td["plan_code"], Decimal("0"))
            sub = Subscription(
                id=str(uuid4()), tenant_id=tid, plan_code=td["plan_code"],
                status="active" if td["status"] == "active" else "suspended",
                started_at=NOW - timedelta(days=30),
                current_period_start=NOW - timedelta(days=30),
                current_period_end=NOW + timedelta(days=335),
                amount=plan_price, currency=IDR,
                created_at=NOW, updated_at=NOW,
            )
            session.add(sub)

            sub_event = SubscriptionEvent(
                id=str(uuid4()), tenant_id=tid, subscription_id=sub.id,
                event_type="subscription.started",
                buyer_name_snapshot=td["name"],
                buyer_email_snapshot=f"admin@{td['slug']}.com",
                plan_code=td["plan_code"],
                amount=plan_price,
                occurred_at=NOW - timedelta(days=30),
                period_end=NOW + timedelta(days=335),
                created_at=NOW,
            )
            session.add(sub_event)

            more_events = []
            if td["plan_code"] == "pro":
                for ev_type, ev_meta in [
                    ("subscription.renewed", {"note": "Perpanjangan otomatis"}),
                    ("payment.received", {"method": "transfer_bank"}),
                ]:
                    more_events.append(SubscriptionEvent(
                        id=str(uuid4()), tenant_id=tid, subscription_id=sub.id,
                        event_type=ev_type,
                        buyer_name_snapshot=td["name"],
                        buyer_email_snapshot=f"admin@{td['slug']}.com",
                        plan_code=td["plan_code"],
                        amount=plan_price,
                        occurred_at=NOW - timedelta(days=random.randint(1, 15)),
                        event_meta=ev_meta,
                        created_at=NOW,
                    ))
            session.add_all(more_events)

            for m in td["members"]:
                role = "tenant_owner" if m["role"] == "owner" else "employee"
                membership = Membership(
                    id=str(uuid4()), tenant_id=tid, user_id=m["user_id"],
                    role_name=role, status="active",
                    joined_at=NOW - timedelta(days=30),
                    created_at=NOW, updated_at=NOW,
                )
                session.add(membership)

            accounts = generate_accounts(tid)
            session.add_all(accounts)

            customers = generate_customers(tid, td["sector"], 200)
            session.add_all(customers)

            suppliers = generate_suppliers(tid, td["sector"], 200)
            session.add_all(suppliers)

            products = generate_products(tid, td["sector"], 200)
            session.add_all(products)

            location = InventoryLocation(
                id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                code="WH", name="Gudang Utama", status="active",
                created_at=NOW, updated_at=NOW,
            )
            session.add(location)

            stock_balances = []
            stock_movements = []
            for p in products:
                qty = Decimal(str(random.randint(20, 500)))
                avg_cost = p.cost_price
                sb = StockBalance(
                    tenant_id=tid, product_id=p.id, location_id=location.id,
                    quantity=qty, average_cost=avg_cost, version=1,
                )
                stock_balances.append(sb)
                sm = StockMovement(
                    id=str(uuid4()), tenant_id=tid, product_id=p.id,
                    location_id=location.id,
                    movement_number=f"SM-{p.sku}",
                    movement_date=TODAY - timedelta(days=30),
                    type="in", quantity=qty, before_stock=Decimal("0"),
                    after_stock=qty, unit_cost=avg_cost,
                    reason="Initial stock", reference_type="manual",
                    created_by=UID_ADMIN, created_at=NOW,
                )
                stock_movements.append(sm)
            session.add_all(stock_balances)
            session.add_all(stock_movements)

            extra_stock_movements = []
            for i in range(200 - len(stock_movements)):
                product = random.choice(products)
                sm_type = random.choice(["in", "out", "adjustment"])
                before = Decimal(str(random.randint(20, 200)))
                qty = Decimal(str(random.randint(1, 50)))
                if sm_type == "out":
                    qty = -qty if qty > 0 else qty
                    after = before + qty
                elif sm_type == "adjustment":
                    after = Decimal(str(random.randint(10, 300)))
                else:
                    after = before + qty
                movement_date = TODAY - timedelta(days=random.randint(0, 29))
                reasons = {
                    "in": ["Pembelian barang", "Retur pelanggan", "Transfer masuk", "Produksi selesai"],
                    "out": ["Penjualan", "Retur supplier", "Transfer keluar", "Rusak/hilang"],
                    "adjustment": ["Stok opname", "Koreksi sistem", "Selisih fisik"],
                }
                extra_stock_movements.append(StockMovement(
                    id=str(uuid4()), tenant_id=tid, product_id=product.id,
                    location_id=location.id,
                    movement_number=f"SM-{product.sku}-E{i + 1:03d}",
                    movement_date=movement_date,
                    type=sm_type, quantity=qty,
                    before_stock=before, after_stock=after,
                    unit_cost=product.cost_price,
                    reason=random.choice(reasons[sm_type]),
                    reference_type="manual",
                    created_by=random.choice([UID_ADMIN, UID_BUDI, UID_ANI]),
                    created_at=datetime.combine(movement_date, NOW.time(), tzinfo=timezone.utc),
                ))
            session.add_all(extra_stock_movements)

            income_accts = [a for a in accounts if a.type == "income"]
            expense_accts = [a for a in accounts if a.type == "expense"]
            cash_accts = [a for a in accounts if a.code.startswith("1-1")]
            receivables_accts = [a for a in accounts if a.code.startswith("1-2")]
            payables_accts = [a for a in accounts if a.code.startswith("2-1")]

            transactions = []
            journal_entries = []
            journal_lines = []

            for i in range(200):
                days_ago = random.randint(0, 31)
                txn_date = TODAY - timedelta(days=days_ago)
                txn_type = random.choices(
                    ["income", "expense", "transfer"],
                    weights=[50, 35, 15],
                )[0]
                txn_status = random.choices(
                    ["posted", "draft", "voided"],
                    weights=[70, 20, 10],
                )[0]
                desc = random.choice(TRANSACTION_DESCRIPTIONS)
                amount = Decimal(str(random.randint(50, 2000) * 1000))

                if txn_type == "income":
                    account = random.choice(income_accts)
                    counter_account = random.choice(cash_accts)
                elif txn_type == "expense":
                    account = random.choice(expense_accts)
                    counter_account = random.choice(cash_accts)
                else:
                    account = random.choice(cash_accts)
                    counter_account = random.choice(cash_accts)
                    while counter_account.id == account.id:
                        counter_account = random.choice(cash_accts)

                txn = Transaction(
                    id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                    transaction_number=f"TRX-{i + 1:04d}",
                    transaction_date=txn_date,
                    type=txn_type,
                    description=desc,
                    amount=amount,
                    account_id=account.id,
                    counter_account_id=counter_account.id,
                    status=txn_status,
                    created_at=datetime.combine(txn_date, NOW.time(), tzinfo=timezone.utc),
                    updated_at=NOW,
                )
                transactions.append(txn)

                if txn_status == "posted":
                    je_status = "posted"
                    je = JournalEntry(
                        id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                        journal_number=f"JR-{i + 1:04d}",
                        journal_date=txn_date,
                        reference=txn.transaction_number,
                        description=f"Jurnal: {desc}",
                        status=je_status,
                        posted_at=datetime.combine(txn_date, NOW.time(), tzinfo=timezone.utc),
                        posted_by=random.choice([UID_ADMIN, UID_BUDI, UID_ANI, UID_SITI]),
                        created_at=datetime.combine(txn_date, NOW.time(), tzinfo=timezone.utc),
                        updated_at=NOW,
                    )
                    journal_entries.append(je)
                    txn.journal_entry_id = je.id

                    if txn_type in ("income", "transfer"):
                        journal_lines.extend([
                            JournalLine(
                                id=str(uuid4()), tenant_id=tid, journal_entry_id=je.id,
                                account_id=account.id, line_number=1,
                                description=desc,
                                debit=Decimal("0"), credit=amount,
                            ),
                            JournalLine(
                                id=str(uuid4()), tenant_id=tid, journal_entry_id=je.id,
                                account_id=counter_account.id, line_number=2,
                                description=f"Kontra: {desc}",
                                debit=amount, credit=Decimal("0"),
                            ),
                        ])
                    else:
                        journal_lines.extend([
                            JournalLine(
                                id=str(uuid4()), tenant_id=tid, journal_entry_id=je.id,
                                account_id=account.id, line_number=1,
                                description=desc,
                                debit=amount, credit=Decimal("0"),
                            ),
                            JournalLine(
                                id=str(uuid4()), tenant_id=tid, journal_entry_id=je.id,
                                account_id=counter_account.id, line_number=2,
                                description=f"Kontra: {desc}",
                                debit=Decimal("0"), credit=amount,
                            ),
                        ])
            session.add_all(transactions)
            session.add_all(journal_entries)
            await session.flush()
            session.add_all(journal_lines)

            invoices = []
            invoice_lines = []
            invoice_statuses = ["draft", "sent", "partial", "paid", "overdue"]
            for i in range(200):
                inv_date = TODAY - timedelta(days=random.randint(0, 35))
                due_date = inv_date + timedelta(days=random.randint(14, 45))
                customer = random.choice(customers)
                product = random.choice(products)
                qty = Decimal(str(random.randint(1, 50)))
                unit_price = product.sale_price
                line_total = qty * unit_price
                tax = line_total * Decimal("0.11")
                subtotal = line_total
                total = subtotal + tax
                status = random.choices(
                    invoice_statuses,
                    weights=[10, 15, 20, 35, 20],
                )[0]
                paid_amount = Decimal("0")
                balance_due = total
                if status == "paid":
                    paid_amount = total
                    balance_due = Decimal("0")
                elif status == "partial":
                    paid_amount = total * Decimal(str(random.randint(10, 90))) / Decimal("100")
                    paid_amount = Decimal(str(int(paid_amount / 1000) * 1000))
                    balance_due = total - paid_amount
                elif status == "overdue":
                    balance_due = total

                inv = Invoice(
                    id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                    invoice_number=f"INV-{i + 1:04d}",
                    customer_id=customer.id,
                    invoice_date=inv_date, due_date=due_date,
                    status=status,
                    subtotal=subtotal, tax_total=tax,
                    discount_total=Decimal("0"),
                    total=total,
                    paid_amount=paid_amount, balance_due=balance_due,
                    notes=random.choice(INVOICE_NOTES),
                    created_at=datetime.combine(inv_date, NOW.time(), tzinfo=timezone.utc),
                    updated_at=NOW,
                )
                invoices.append(inv)

                invoice_lines.append(InvoiceLine(
                    id=str(uuid4()), tenant_id=tid, invoice_id=inv.id,
                    line_number=1, product_id=product.id,
                    item_name=product.name,
                    quantity=qty, unit=product.unit,
                    unit_price=unit_price,
                    tax_rate=Decimal("11"), discount_amount=Decimal("0"),
                    line_total=line_total,
                ))
            session.add_all(invoices)
            session.add_all(invoice_lines)
            await session.flush()

            payments = []
            allocations = []
            for inv in invoices:
                if inv.status in ("paid", "partial") and inv.paid_amount > 0:
                    pmt = CustomerPayment(
                        id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                        payment_number=f"PYT-{inv.invoice_number[4:]}",
                        customer_id=inv.customer_id,
                        payment_date=inv.due_date - timedelta(days=random.randint(0, 5)),
                        amount=inv.paid_amount,
                        method=random.choice(["transfer", "cash", "giro", "kartu_kredit"]),
                        status="posted",
                        created_at=datetime.combine(inv.due_date, NOW.time(), tzinfo=timezone.utc),
                        updated_at=NOW,
                    )
                    payments.append(pmt)
                    allocations.append(CustomerPaymentAllocation(
                        id=str(uuid4()), tenant_id=tid,
                        payment_id=pmt.id, invoice_id=inv.id,
                        amount=inv.paid_amount,
                    ))
            session.add_all(payments)
            await session.flush()
            session.add_all(allocations)

            purchase_orders = []
            po_lines = []
            goods_receipts = []
            goods_receipt_lines = []
            po_statuses = ["draft", "sent", "partial", "received", "cancelled"]
            for i in range(200):
                supplier = random.choice(suppliers)
                product = random.choice(products)
                po_date = TODAY - timedelta(days=random.randint(0, 35))
                expected_date = po_date + timedelta(days=random.randint(7, 30))
                qty = Decimal(str(random.randint(5, 200)))
                unit_price = product.cost_price
                line_total = qty * unit_price
                tax = line_total * Decimal("0.11")
                total = line_total + tax
                status = random.choices(
                    po_statuses,
                    weights=[10, 20, 15, 40, 5],
                )[0]
                received_qty = qty if status == "received" else (
                    qty * Decimal(str(random.randint(10, 90))) / Decimal("100") if status == "partial" else Decimal("0")
                )

                po = PurchaseOrder(
                    id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                    po_number=f"PO-{i + 1:04d}",
                    supplier_id=supplier.id,
                    order_date=po_date, expected_date=expected_date,
                    status=status,
                    subtotal=line_total, tax_total=tax,
                    total=total,
                    notes=random.choice(PO_NOTES),
                    created_at=datetime.combine(po_date, NOW.time(), tzinfo=timezone.utc),
                    updated_at=NOW,
                )
                purchase_orders.append(po)

                pol = PurchaseOrderLine(
                    id=str(uuid4()), tenant_id=tid, purchase_order_id=po.id,
                    product_id=product.id, line_number=1,
                    item_name=product.name,
                    quantity=qty, received_quantity=received_qty,
                    unit_price=unit_price, line_total=line_total,
                )
                po_lines.append(pol)

                if received_qty > 0:
                    gr = GoodsReceipt(
                        id=str(uuid4()), tenant_id=tid, branch_id=branch.id,
                        purchase_order_id=po.id,
                        receipt_number=f"GR-{i + 1:04d}",
                        received_at=datetime.combine(po_date + timedelta(days=random.randint(1, 5)), NOW.time(), tzinfo=timezone.utc),
                        status="completed",
                        created_at=NOW, updated_at=NOW,
                    )
                    goods_receipts.append(gr)
                    goods_receipt_lines.append(GoodsReceiptLine(
                        id=str(uuid4()), tenant_id=tid,
                        goods_receipt_id=gr.id,
                        purchase_order_line_id=pol.id,
                        product_id=product.id,
                        quantity=received_qty,
                        unit_cost=unit_price,
                    ))
            session.add_all(purchase_orders)
            await session.flush()
            session.add_all(po_lines)
            session.add_all(goods_receipts)
            await session.flush()
            session.add_all(goods_receipt_lines)

            notifications = []
            base_templates = NOTIFICATION_TEMPLATES
            for i in range(200):
                template = base_templates[i % len(base_templates)]
                ntype, ntitle, nmsg = template
                created = NOW - timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
                read_at = created + timedelta(hours=random.randint(1, 48)) if random.random() < 0.6 else None
                notifications.append(Notification(
                    id=str(uuid4()), tenant_id=tid,
                    user_id=random.choice([None, UID_BUDI, UID_ANI]),
                    type=ntype, title=ntitle, message=nmsg,
                    link="" if random.random() < 0.7 else f"/dashboard/{random.choice(['invoices', 'reports', 'products'])}",
                    read_at=read_at,
                    created_at=created,
                ))
            session.add_all(notifications)

            audit_events = []
            for i in range(200):
                action, module, object_type = random.choice(TENANT_AUDIT_ACTIONS)
                timestamp = NOW - timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
                audit_events.append(TenantAuditEvent(
                    id=str(uuid4()), tenant_id=tid,
                    timestamp=timestamp,
                    actor_id=random.choice([UID_BUDI, UID_ANI, UID_SITI, None]),
                    actor_name=random.choice(["Budi Santoso", "Ani Lestari", "Siti Nurhaliza", "System"]),
                    action=action,
                    module=module,
                    object_type=object_type,
                    object_id=str(random.randint(1, 9999)),
                ))
            session.add_all(audit_events)

        incidents = [
            Incident(
                id=str(uuid4()), severity="warning", title="Gangguan Database",
                description="Latensi database meningkat 3x lipat selama 10 menit pada pukul 14:30 WIB",
                status="resolved",
                started_at=NOW - timedelta(days=7, hours=2),
                resolved_at=NOW - timedelta(days=6, hours=14),
                owner="DevOps Team",
                timeline=[
                    {"time": (NOW - timedelta(days=7, hours=2)).isoformat(), "action": "Incident detected"},
                    {"time": (NOW - timedelta(days=7, hours=1, minutes=45)).isoformat(), "action": "Root cause identified"},
                    {"time": (NOW - timedelta(days=6, hours=14)).isoformat(), "action": "Resolved"},
                ],
                created_at=NOW - timedelta(days=7), updated_at=NOW - timedelta(days=6, hours=14),
            ),
            Incident(
                id=str(uuid4()), severity="critical", title="Downtime API",
                description="API utama tidak dapat diakses selama 5 menit, mempengaruhi seluruh tenant",
                status="resolved",
                started_at=NOW - timedelta(days=3, hours=6),
                resolved_at=NOW - timedelta(days=3, hours=5, minutes=55),
                owner="Platform Team",
                timeline=[
                    {"time": (NOW - timedelta(days=3, hours=6)).isoformat(), "action": "Alert triggered"},
                    {"time": (NOW - timedelta(days=3, hours=5, minutes=55)).isoformat(), "action": "Service restored"},
                ],
                created_at=NOW - timedelta(days=3), updated_at=NOW - timedelta(days=3, hours=5, minutes=55),
            ),
            Incident(
                id=str(uuid4()), severity="info", title="Pemeliharaan Terjadwal",
                description="Upgrade server database pada pukul 02:00-04:00 WIB, estimasi downtime 30 menit",
                status="scheduled",
                started_at=NOW + timedelta(days=2),
                owner="DevOps Team",
                created_at=NOW, updated_at=NOW,
            ),
            Incident(
                id=str(uuid4()), severity="warning", title="SSL Certificate Expiring",
                description="SSL certificate untuk domain app.kepin.io akan kadaluarsa dalam 7 hari",
                status="open",
                started_at=NOW - timedelta(days=1),
                owner="Platform Team",
                created_at=NOW - timedelta(days=1), updated_at=NOW,
            ),
        ]
        session.add_all(incidents)

        platform_audits = []
        for i, (action, actor, obj_type, detail) in enumerate(PLATFORM_AUDIT_ACTIONS):
            timestamp = NOW - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            platform_audits.append(PlatformAuditEvent(
                id=str(uuid4()),
                timestamp=timestamp,
                actor_id=UID_ADMIN if actor == "Admin" else None,
                actor_name=actor,
                action=action,
                object_type=obj_type,
                object_id=detail.get("slug") or detail.get("email") or str(random.randint(1, 100)),
                before=None,
                after=detail,
            ))
        session.add_all(platform_audits)

        outbox_events = [
            OutboxEvent(
                id=str(uuid4()), tenant_id=None,
                event_type="platform.tenant.created",
                aggregate_type="tenant",
                aggregate_id=td["id"],
                payload={"slug": td["slug"], "name": td["name"]},
                occurred_at=NOW,
                processed_at=None,
            )
            for td in all_tenants
        ]
        session.add_all(outbox_events)

        await session.commit()

        print("Seeding complete!")
        print("=" * 50)
        print("AKUN YANG TERSEDIA:")
        print("-" * 50)
        print()
        print("Admin Platform:")
        print("  Email: admin@kepin.io")
        print("  Password: admin123")
        print("  Name: Admin KePin")
        print("  Role: Super Admin")
        print()
        print("Owner Toko Maju:")
        print("  Email: budi@tokomaju.com")
        print("  Password: budi123")
        print("  Name: Budi Santoso")
        print("  Role: Owner")
        print()
        print("Manager Toko Maju:")
        print("  Email: ani@tokomaju.com")
        print("  Password: ani123")
        print("  Name: Ani Lestari")
        print("  Role: Manager")
        print()
        print("Akuntan Warung Segar:")
        print("  Email: siti@warungsegar.com")
        print("  Password: siti123")
        print("  Name: Siti Nurhaliza")
        print("  Role: Akuntan")
        print()
        print()
        print("KODE BERGABUNG ORGANISASI:")
        for td in TENANTS_DATA:
            print(f"  {td['name']}: ID={td.get('id', '?')[:8]}..., Kode={td.get('join_code', '?')}")
        print()
        print("-" * 50)
        total = sum(
            1 for td in TENANTS_DATA
            for table_name in ["accounts", "customers", "suppliers", "products",
                               "transactions", "journal_entries", "invoices",
                               "purchase_orders", "stock_movements", "notifications",
                               "audit_events"]
        )
        print(f"Total tenant records generated: ~{len(TENANTS_DATA) * 11 * 200}")
        print("Platform records: incidents, platform audit events, outbox events")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
