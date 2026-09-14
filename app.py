# app.py
import re
import html
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import streamlit as st

def url_to_filename(title: str, url: str) -> str:
    parsed = urlparse(url)
    base_name = title if title else parsed.netloc + parsed.path
    clean_name = re.sub(r"[^\w\-]", "_", base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{clean_name.strip('_')[:50]}_{timestamp}"

def clean_html_smart(html_content: str):
    """Native Smart Parser: Extracts title and structured paragraphs while stripping Wikipedia numbers completely."""
    # 1. Extract Title safely
    title_match = re.search(r'<title.*?>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    page_title = title_match.group(1).strip() if title_match else "Web Article Intelligence"
    page_title = html.unescape(page_title)
    
    # Strip "- Wikipedia" suffix from title block / 移除標題結尾的維基百科字樣
    page_title = re.sub(r'\s*-\s*Wikipedia.*', '', page_title, flags=re.IGNORECASE)
    
    # 2. Erase scripts, codes, style formatting, and nav structures
    html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<nav.*?>.*?</nav>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<footer.*?>.*?</footer>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # 🌟 ULTIMATE FIX: Strip reference tags (like <sup id="cite_ref...">[1]</sup>) completely from the core HTML
    # 🌟 終極修復：直接從 HTML 原始碼中將整組參照標籤（連同裡面的括號與數字）完全抹除
    html_content = re.sub(r'<sup\b[^>]*>.*?</sup>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Backup check: Clean up any rogue text-only brackets left over / 備用清理：清除可能殘留的純文字方括號
    html_content = re.sub(r'\[\d+\]', '', html_content)
    
    # 3. Split content into logical clean text blocks
    raw_blocks = re.split(r'</?(?:p|h1|h2|h3|li|div|article|section)>', html_content, flags=re.IGNORECASE)
    
    paragraphs = []
    for block in raw_blocks:
        # Strip all remaining inline sub-tags (like <a>, <span>, <strong>)
        clean_block = re.sub(r'<[^>]+>', ' ', block)
        clean_block = html.unescape(clean_block)
        clean_block = re.sub(r'\s+', ' ', clean_block).strip()
        
        # Filter out layout junk, navigation labels, and noise links
        if len(clean_block) > 25 and not clean_block.startswith(("http", "javascript", "{", "/*", "^")):
            # Extra cleanup for Wikipedia specific edit buttons text / 順手清除維基百科常見的「編輯」按鈕殘留字樣
            clean_block = re.sub(r'\s*\[\s*edit\s*\]', '', clean_block, flags=re.IGNORECASE)
            paragraphs.append(clean_block)
            
    return page_title, paragraphs


def create_native_pdf(title: str, source_url: str, paragraphs: list, font_size: int, show_summary: bool) -> bytes:
    """Ultra-Advanced PDF Matrix built entirely using 100% pure native Python binary wrappers."""
    # Line width logic based on customizable font size
    max_char_width = 90 if font_size < 11 else (75 if font_size < 14 else 60)
    line_spacing = font_size + 4
    
    lines = []
    
    # Optional Executive Brief Summary Box Matrix / 自動摘要矩陣
    if show_summary and len(paragraphs) > 2:
        lines.append("--- EXECUTIVE BRIEF BRIEFING ---")
        lines.append(f" * CORE ANALYSIS: {paragraphs[0][:75]}...")
        if len(paragraphs) > 4:
            lines.append(f" * SYSTEM LOG CONTEXT: {paragraphs[len(paragraphs)//2][:75]}...")
        lines.append("--------------------------------")
        lines.append("")

    # Populate and wrap structural text blocks smoothly
    for p in paragraphs[:150]:
        words = p.split(' ')
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > max_char_width:
                lines.append(' '.join(current_line))
                current_line = []
        if current_line:
            lines.append(' '.join(current_line))
        lines.append("") # Paragraph spacing line

    # Standard Compliant PDF Stream Architecture Tree
    pdf_lines = [
        b"%PDF-1.4",
        b"1 0 obj", b"<< /Type /Catalog /Pages 2 0 R >>", b"endobj",
        b"2 0 obj", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"endobj",
        b"3 0 obj", f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>".encode('latin1'), b"endobj"
    ]
    
    # Generate content stream coordinates
    stream_content = [
        b"BT",
        f"/F1 {font_size} Tf".encode('latin1'),
        f"{line_spacing} TL".encode('latin1'),
        b"45 800 Td",
        f"({title.encode('latin1', 'ignore').decode('latin1')}) Tj T*".encode('latin1'),
        f"(Source: {source_url.encode('latin1', 'ignore').decode('latin1')}) Tj T*".encode('latin1'),
        f"(Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj T*".encode('latin1'),
        b"T*",
    ]
    
    y_position = 730
    for line in lines[:100]: # Safety boundary limits
        if y_position < 50: # Page break safety line override
            break
        clean_line = line.encode('latin1', 'ignore').decode('latin1').replace('(', '\\(').replace(')', '\\)')
        stream_content.append(f"({clean_line}) Tj T*".encode('latin1'))
        y_position -= line_spacing
        
    stream_content.append(b"ET")
    stream_binary = b"\n".join(stream_content)
    
    pdf_lines.extend([
        b"4 0 obj", f"<< /Length {len(stream_binary)} >>".encode('latin1'), b"stream", stream_binary, b"endstream", b"endobj",
        b"5 0 obj", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"endobj",
        b"xref", b"0 6", b"0000000000 65535 f ", b"trailer", b"<< /Size 6 /Root 1 0 R >>", b"%%EOF"
    ])
    
    return b"\n".join(pdf_lines)

# --- ADVANCED DASHBOARD CONTROL ENVIRONMENT ---
st.set_page_config(page_title="Advanced Intelligence Engine", page_icon="⚡", layout="wide")

# Sidebar Parameter Matrix Layout / 側邊設定面板
st.sidebar.header("⚙️ Design Parameters / 進階設定")
export_format = st.sidebar.selectbox("File Export Type / 導出格式:", ["Professional Document (.pdf)", "Raw Text Brief (.txt)"])
ui_font_size = st.sidebar.slider("Text Font Scaling / 字體大小調整:", min_value=10, max_value=15, value=11)
ui_enable_summary = st.sidebar.checkbox("Include Executive Summary / 自動附加摘要", value=True)

st.title("⚡ Enterprise Intelligence & Content Extraction Suite")
st.write("Deconstruct complex web intelligence layouts and convert them into clean formats instantly.")

user_url = st.text_input("🔗 Target Web URL / 請輸入網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    # Action Trigger - Locked Blue Layout Component
    if st.button("🚀 Process & Extract Content", type="primary"):
        with st.spinner("⚡ Processing core pipeline parameters... Resolving source redirections..."):
            try:
                # Built-in robust request core network pipeline
                req = Request(user_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.5'
                })
                
                with urlopen(req, timeout=15) as response:
                    raw_html = response.read().decode('utf-8', errors='ignore')
                
                # Execute native advanced extraction algorithm
                page_title, clean_paragraphs = clean_html_smart(raw_html)
                file_base = url_to_filename(page_title, user_url)
                
                if not clean_paragraphs:
                    clean_paragraphs = ["No explicit text blocks could be extracted from the target layout context."]
                
                # --- PROCESS DOWNLOAD PAYLOAD ---
                if "PDF" in export_format:
                    filename = f"{file_base}.pdf"
                    file_bytes = create_native_pdf(page_title, user_url, clean_paragraphs, ui_font_size, ui_enable_summary)
                    mime_type = "application/pdf"
                else:
                    filename = f"{file_base}.txt"
                    text_lines = [f"TITLE: {page_title}", f"SOURCE: {user_url}", f"TIMESTAMP: {datetime.now()}\n", "="*40, ""]
                    if ui_enable_summary:
                        text_lines.append("[EXECUTIVE BRIEF BRIEFING SUMMARY]")
                        text_lines.append(f"- Core Point: {clean_paragraphs[0][:100]}...\n" if len(clean_paragraphs) > 0 else "")
                    text_lines.extend(clean_paragraphs)
                    file_bytes = "\n".join(text_lines).encode('utf-8', errors='ignore')
                    mime_type = "text/plain"

                st.success("🎉 Processing Matrix Complete! Your conversion was successful.")
                st.download_button(
                    label=f"📥 Download Processed {filename.split('.')[-1].upper()} Brief",
                    data=file_bytes,
                    file_name=filename,
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"❌ Intelligence Extraction Exception: {e}")
