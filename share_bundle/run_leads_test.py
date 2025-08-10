# run_leads_test.py
import sys

sys.path.insert(0, "src")

from modules.leads_logger import log_lead

log_lead(
    email="client@abc.com",
    package="企業",
    pdf_path="data/archive/quotes/20250713/quote_企業_client@abc_com.pdf",
    company="永信資訊",
)
