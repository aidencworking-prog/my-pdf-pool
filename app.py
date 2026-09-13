# app.py
import re
import html
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import streamlit as st

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    name = re.sub(r"[^\w\-]", "_", parsed.netloc + parsed.path)
    name = name.strip("_")[:80] or "page"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}.pdf"

def clean_html_to_text(html_content: str) -> str:
    # 移除網頁中的腳本與樣式內容（防止亂碼）
    html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
    # 移除所有 HTML 標籤，只保留純文字
    text = re.sub(r'<[^>]+>', ' ', html_content)
    # 解碼網頁特殊符號（例如將 &amp; 還原成 &）
    text = html.unescape(text)
    # 整理多餘的空白字元
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_pure_pdf(source_url: str, content_text: str) -> bytes:
    """利用 Python 完全內建的二進位排版技術，直接生成標準的 PDF 檔案"""
    words = content_text[:30000].split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 85:  # 每行約 85 個字元時自動折行
            lines.append(' '.join(current_line))
            current_line = []
    if current_line:
        lines.append(' '.join(current_line))

    # 建立符合國際標準格式的純文字 PDF 結構
    pdf_lines = [
        b"%PDF-1.4",
        b"1 0 obj",
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"endobj",
        b"2 0 obj",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"endobj",
        b"3 0 obj",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"endobj"
    ]
    
    # 繪製文字與內容流
    stream_content = [
        b"BT",
        b"/F1 10 Tf",
        b"14 TL",
        b"50 800 Td",
        f"({source_url.encode('latin1', 'ignore').decode('latin1')}) Tj T*".encode('latin1'),
        b"T*",
    ]
    
    for line in lines[:50]:  # 安全限制在前 50 行以內（約一頁 A4 滿版）
        clean_line = line.encode('latin1', 'ignore').decode('latin1').replace('(', '\\(').replace(')', '\\)')
        stream_content.append(f"({clean_line}) Tj T*".encode('latin1'))
        
    stream_content.append(b"ET")
    stream_binary = b"\n".join(stream_content)
    
    pdf_lines.extend([
        b"4 0 obj",
        f"<< /Length {len(stream_binary)} >>".encode('latin1'),
        b"stream",
        stream_binary,
        b"endstream",
        b"endobj",
        b"5 0 obj",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"endobj",
        b"xref",
        b"0 6",
        b"0000000000 65535 f ",
        b"trailer",
        b"<< /Size 6 /Root 1 0 R >>",
        b"%%EOF"
    ])
    
    return b"\n".join(pdf_lines)

# 前端網頁介面
st.set_page_config(page_title="Web to PDF", page_icon="🌐")
st.title("🌐 Web to PDF Light / 網頁轉 PDF 輕量版")
st.write("Convert any article into a standard text PDF instantly. / 將網頁文章立即轉為純文字 PDF 檔案。")

user_url = st.text_input("Enter URL / 輸入網頁網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    if st.button("Convert to PDF / 開始轉換", type="primary"):
        with st.spinner("Extracting text data... / 正在擷取資料中..."):
            try:
                # 採用純 Python 原生網路請求，絕不觸發任何系統權限阻擋
                req = Request(user_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=10) as response:
                    raw_html = response.read().decode('utf-8', errors='ignore')
                
                plain_text = clean_html_to_text(raw_html)
                filename = url_to_filename(user_url)
                
                # 呼叫純內建二進位 PDF 產生器
                pdf_data = create_pure_pdf(user_url, plain_text)

                st.success("🎉 Conversion Successful! / 轉換成功！")
                st.download_button(
                    label="📥 Download PDF / 下載 PDF 檔案",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error / 發生錯誤: {e}")
