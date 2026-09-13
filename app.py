# app.py
import asyncio
import re
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st
from playwright.async_api import async_playwright

# Keep your original filename logic / 保留你原本的檔名邏輯
def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    name = re.sub(r"[^\w\-]", "_", parsed.netloc + parsed.path)
    name = name.strip("_")[:80] or "page"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}.pdf"

# Web Interface Title / 網頁介面標題
st.set_page_config(page_title="Web to PDF", page_icon="🌐")
st.title("🌐 Web to PDF Converter / 網頁轉 PDF 工具")
st.write("Convert any webpage into a clean A4 PDF file. / 將任何網頁轉換為 A4 PDF 檔案。")

# Input field / 輸入框
user_url = st.text_input("Enter URL / 輸入網頁網址:", placeholder="https://example.com")

if user_url:
    # Auto-fix missing protocol / 自動修正缺少的協定
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    # Convert button / 轉換按鈕
    if st.button("Convert to PDF / 開始轉換", type="primary"):
        with st.spinner("Processing... Please wait / 正在處理中，請稍候..."):
            
            # Asynchronous PDF generation / 非同步 PDF 生成
            async def capture_pdf(target_url):
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(target_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(1000)
                    pdf_data = await page.pdf(
                        format="A4",
                        print_background=True,
                        margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
                    )
                    await browser.close()
                    return pdf_data

            try:
                # Run the async core / 執行非同步核心
                pdf_bytes = asyncio.run(capture_pdf(user_url))
                filename = url_to_filename(user_url)
                
                # Success message and download button / 成功提示與下載按鈕
                st.success("🎉 Conversion Successful! / 轉換成功！")
                st.download_button(
                    label="📥 Download PDF / 下載 PDF 檔案",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error / 發生錯誤: {e}")
