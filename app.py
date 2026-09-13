# app.py
import re
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st

# Secure internal fallback for standard light libraries
# 內部安全自動補裝標準輕量級套件
try:
    import requests
    from reportlab.lib.pagesizes import letter
except ModuleNotFoundError:
    import pip
    pip.main(["install", "requests", "reportlab"])
    import requests
    from reportlab.lib.pagesizes import letter

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    name = re.sub(r"[^\w\-]", "_", parsed.netloc + parsed.path)
    name = name.strip("_")[:80] or "page"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}.pdf"

def clean_html(html_text: str) -> str:
    # Remove javascript and styling tags / 移除腳本與樣式內容
    clean = re.sub(r'<script.*?>.*?</script>', '', html_text, flags=re.DOTALL)
    clean = re.sub(r'<style.*?>.*?</style>', '', clean, flags=re.DOTALL)
    # Strip basic HTML tags / 移除所有標籤
    clean = re.sub(r'<[^>]+>', ' ', clean)
    # Standardize whitespace / 整理空白字元
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

# Web UI Layout / 網頁介面佈局
st.set_page_config(page_title="Web to PDF", page_icon="🌐")
st.title("🌐 Web to PDF Text Converter / 網頁轉 PDF 文字工具")
st.write("Convert any webpage article into a clean PDF text file. / 將任何網頁文章轉換為乾淨的 PDF 文字檔。")

user_url = st.text_input("Enter URL / 輸入網頁網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    if st.button("Convert to PDF / 開始轉換", type="primary"):
        with st.spinner("Extracting text... Please wait / 正在擷取文字中，請稍候..."):
            try:
                # Fetch target web text / 抓取網頁內容
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(user_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Extract and clean plain text / 提取並清理文字
                plain_text = clean_html(response.text)
                filename = url_to_filename(user_url)
                
                # Generate standard PDF / 使用 ReportLab 建立標準 PDF
                pdf_path = f"/tmp/{filename}"
                doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
                
                styles = getSampleStyleSheet()
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    wordWrap='CJK'
                )
                
                # Safeguard text length / 限制長度防止記憶體過載
                story = [
                    Paragraph(f"<b>Source URL:</b> {user_url}", normal_style),
                    Spacer(1, 12),
                    Paragraph(plain_text[:40000], normal_style) 
                ]
                
                doc.build(story)
                
                # Output file / 輸出二進位檔案
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.success("🎉 Conversion Successful! / 轉換成功！")
                st.download_button(
                    label="📥 Download PDF / 下載 PDF 檔案",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error / 發生錯誤: {e}")
