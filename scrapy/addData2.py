import os
import sys
import django
from django.db import connection
import pandas as pd

# 讓腳本找到你的 Django 專案
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from myapp.models import Keyword, KeywordGroup

# ---- 1) 先刪光 Keyword（保留 Group） ----
Keyword.objects.all().delete()

# ---- 2) 依資料庫種類重置自動遞增序號 ----
engine = connection.settings_dict.get("ENGINE", "")
table_name = Keyword._meta.db_table  # 'myapp_keyword'

with connection.cursor() as cursor:
    if "sqlite" in engine:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s", [table_name])
    elif "postgresql" in engine:
        seq_name = f"{table_name}_id_seq"
        cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1;")
    elif "mysql" in engine:
        cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
    else:
        print(f"Unknown DB engine: {engine}. Please handle sequence reset manually.")

print(f"✅ Cleared table '{table_name}' and reset its auto-increment (engine={engine}).")

# ---- 3) 從 Excel 匯入關鍵字 ----
keyword_path = r"C:\Users\user\Downloads\keyword.xlsx"
df = pd.read_excel(keyword_path)

keywords = df["關鍵字"].dropna().astype(str).tolist()
keywords = list(set(keywords))  # 去掉重複


# ---- 4) 四大群組的分類規則 ----
group_mapping = {
    "基本概念": ["區塊鏈","區塊","鏈","帳本","共識","共識機制","節點","交易","世界狀態","結構","樹結構","貨幣","證書","根證書","成員"],
    "技術原理": ["拜占庭錯誤","Fabric","Hyperledger Fabric","Gossip","LDAP","MVCC","P2P",
              "SWIFT","圖靈","ASN.1","CA","CRL","CSR","DERIES","Nonce","OCSP","PKCS",
              "PEM","PKI","SM","SM2","PoA","PoS","DPoS","Raft","PBFT","PoW","Rollup",
              "女巫攻擊","錨定","審計性","鏈碼","通道","提交節點","提交","保密","背書節點","背書過程",
              "調用","MSP","排序節點","系統鏈","函數","初始化","密碼學","加密","密鑰","解密",
              "Merkle","雙花攻擊","漏洞","哈希函數","ZKP","超級帳本","分片","跨鏈"],
    "日常應用": ["Fintech","DTCC","智能合約","加密貨幣","以太坊","以太幣","比特幣",
              "DAO","閃電網路","挖礦","礦工","礦機","礦池","BaaS","CBDC","DeFi",
              "Ripple","Corda","Polkadot","Cosmos"],
    "潛力與挑戰": ["隱私保護","擴展性","性能","成本","監管","挑戰","潛在風險"]
}

# ---- 5) 把關鍵字依群組存入 DB ----
for kw in keywords:
    target_group = None
    for group_name, kw_list in group_mapping.items():
        if kw in kw_list:
            target_group, _ = KeywordGroup.objects.get_or_create(name=group_name)
            break

    if not target_group:
        # 如果沒分類到，就放到「基本概念」
        target_group, _ = KeywordGroup.objects.get_or_create(name="基本概念")

    Keyword.objects.create(group=target_group, keyword=kw)
    print(f"已新增：{kw} → {target_group.name}")

print(f"✅ 匯入完成，共 {len(keywords)} 筆關鍵字。")
