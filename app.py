# app.py
import asyncio
import re
import sys
import importlib
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st

# Secure internal loop installation / 確保 Playwright 在雲端被正確載入
try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError:
    import pip
    pip.main(["install", "playwright"])
    importlib.invalidate_caches()
    from playwright.async_api import async_playwright

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    name = re.sub(r"[^\w\-]", "_", parsed.netloc + parsed.path)
    name = name.strip("_")[:80] or "page"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}.pdf"

st.set_page_config(page_title="Web to PDF", page_icon="🌐")
st.title("🌐 Web to PDF Converter / 網頁轉 PDF 工具")
st.write("Convert any complex webpage into a clean A4 PDF file. / 將任何複雜網頁轉換為 A4 PDF 檔案。")

user_url = st.text_input("Enter URL / 輸入網頁網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    if st.button("Convert to PDF / 開始轉換", type="primary"):
        with st.spinner("Launching cloud browser engine... Please wait / 正在啟動雲端瀏覽器核心，請稍候..."):
            
            async def capture_pdf(target_url):
                async with async_playwright() as p:
                    # Launch a real virtual browser / 啟動真實虛擬瀏覽器防止被網站封鎖
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    # Mimic a real human browser agent / 模擬真人瀏覽器標頭
                    await page.set_extra_http_headers({
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    
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
                pdf_bytes = asyncio.run(capture_pdf(user_url))
                filename = url_to_filename(user_url)
                
                st.success("🎉 Conversion Successful! / 轉換成功！")
                st.download_button(
                    label="📥 Download PDF / 下載 PDF 檔案",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
            except Exception as e:
                # Automate browser download if the operating system lacks the chromium binary
                # 如果 Linux 系統缺少瀏覽器本體，會自動執行背景補包下載，並提示使用者再點一次
                if "executable doesn't exist" in str(e).lower() or "playwright install" in str(e).lower():
                    st.info("🔧 Initializing browser environment... Please wait 10 seconds and click 'Convert' again! / 正在初始化雲端瀏覽器環境，請稍候 10 秒並重新點擊轉換！")
                    try:
                        import subprocess
                        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
                    except:
                        pass
                else:
                    st.error(f"❌ Error / 發生錯誤: {e}")

