# app.py
import asyncio
import re
import sys
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st

# Force Streamlit to install playwright inside the Python loop dynamically if missing
# 用最安全、不觸發權限阻擋的方式在執行期動態補裝套件
try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError:
    import pip
    pip.main(["install", "playwright"])
    from playwright.async_api import async_playwright

def url_to_filename(url: str) -> str:
    parsed = urlparse(url)
    name = re.sub(r"[^\w\-]", "_", parsed.netloc + parsed.path)
    name = name.strip("_")[:80] or "page"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}.pdf"

st.set_page_config(page_title="Web to PDF", page_icon="🌐")
st.title("🌐 Web to PDF Converter / 網頁轉 PDF 工具")
st.write("Convert any webpage into a clean A4 PDF file. / 將任何網頁轉換為 A4 PDF 檔案。")

user_url = st.text_input("Enter URL / 輸入網頁網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    if st.button("Convert to PDF / 開始轉換", type="primary"):
        with st.spinner("Processing... Please wait / 正在處理中，請稍候..."):
            
            async def capture_pdf(target_url):
                async with async_playwright() as p:
                    # Headless launch / 以無頭瀏覽器模式啟動
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
                # Automate the system core binary if the browser framework is empty
                # 如果是缺少瀏覽器本體，則在畫面上提示並自動幫忙修復核心
                if "Executable doesn't exist" in str(e) or "playwright install" in str(e).lower():
                    st.info("🔧 Setting up browser engine for the first time... Re-clicking in 10s! / 正在初始化雲端瀏覽器核心，請在十秒後重新點擊轉換！")
                    try:
                        import subprocess
                        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
                    except:
                        pass
                else:
                    st.error(f"❌ Error / 發生錯誤: {e}")
