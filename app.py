# app.py
import re
import html
from datetime import datetime
from urllib.parse import urlparse
import streamlit as st

# Secure enterprise dynamic core builder
try:
    import requests
    from bs4 import BeautifulSoup
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ModuleNotFoundError:
    import pip
    pip.main(["install", "requests", "beautifulsoup4", "reportlab"])
    import requests
    from bs4 import BeautifulSoup
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def clean_filename(title: str, url: str) -> str:
    parsed = urlparse(url)
    base_name = title if title else parsed.netloc + parsed.path
    clean_name = re.sub(r"[^\w\-]", "_", base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{clean_name.strip('_')[:50]}_{timestamp}"

def extract_enterprise_content(html_content: str):
    """Ultra-Advanced Parsing Matrix: Extracts core articles while omitting structural noise."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract structural header data
    title_tag = soup.find("h1") or soup.find("title")
    page_title = title_tag.get_text().strip() if title_tag else "Enterprise Document Extraction"
    
    # Erase clutter nodes
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "iframe", "ads"]):
        element.decompose()
        
    # Isolate main payload body
    content_div = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"content|article|body|post|main-text", re.I))
    target_node = content_div if content_div else soup
    
    paragraphs = []
    for p in target_node.find_all(['p', 'h1', 'h2', 'h3', 'li']):
        txt = p.get_text().strip()
        # Quality control filter: strips short utility snippets and layout links
        if txt and len(txt) > 20: 
            paragraphs.append(txt)
            
    return page_title, paragraphs

def generate_summary_bullets(paragraphs: list, count: int = 3) -> list:
    """Algorithmic Content Summarizer: extracts core introductory and impact summary items."""
    bullets = []
    candidates = [p for p in paragraphs if len(p) > 60 and not p.startswith("http")]
    
    # Select critical contextual anchors
    if len(candidates) >= 1:
        bullets.append(f"📌 Key Topic: {candidates[0][:120]}...")
    if len(candidates) >= 3:
        bullets.append(f"🔍 Core Context: {candidates[len(candidates)//2][:120]}...")
    if len(candidates) >= 2:
        bullets.append(f"💡 Conclusion / Summary: {candidates[-1][:120]}...")
        
    return bullets[:count]

# --- ENTERPRISE USER DASHBOARD INTERFACE ---
st.set_page_config(page_title="Enterprise Data Engine", page_icon="⚡", layout="wide")

# Advanced Styling Control Center in Sidebar / 左側控制面板
st.sidebar.header("⚙️ Configuration Matrix / 進階設定")
export_format = st.sidebar.selectbox("Output Target / 導出格式:", ["Professional PDF (.pdf)", "Clean Text Log (.txt)"])
font_size = st.sidebar.slider("PDF Text Font Size / 字體大小:", min_value=9, max_value=16, value=11)
enable_summary = st.sidebar.checkbox("Generate AI Executive Summary / 開啟自動核心摘要", value=True)

st.title("⚡ Enterprise Data & Content Conversion Engine")
st.write("Convert intricate web intelligence layouts into clear, structural executive briefs.")

# Main Input Interface
user_url = st.text_input("🔗 Target Intelligence URL / 請輸入採集網址:", placeholder="https://example.com")

if user_url:
    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    # Main action container with locked blue primary styling
    if st.button("🚀 Execute Enterprise Conversion", type="primary"):
        with st.spinner("⚡ Initializing Data Matrix... Running anti-blocking bypass routines..."):
            try:
                # Anti-blocking session encapsulation
                session = requests.Session()
                session.max_redirects = 20
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://bing.com"
                }
                
                response = session.get(user_url, headers=headers, timeout=25, allow_redirects=True)
                response.raise_for_status()
                
                # Run content core parsing
                page_title, raw_paragraphs = extract_enterprise_content(response.text)
                
                if not raw_paragraphs:
                    st.warning("⚠️ Warning: Text payload was sparse. The webpage layout may be locked behind an interactive login wall.")
                    raw_paragraphs = ["No explicit text blocks could be programmatically detected at the root level of this specific target URL layout."]
                
                file_base = clean_filename(page_title, user_url)
                
                # --- FORMAT OUTPUT CONSTRUCTOR ---
                if "PDF" in export_format:
                    filename = f"{file_base}.pdf"
                    pdf_path = f"/tmp/{filename}"
                    
                    # Typography rules and spacing bounds
                    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                    styles = getSampleStyleSheet()
                    
                    # Compute line metrics safely
                    line_leading = font_size + 5
                    
                    title_style = ParagraphStyle('EntTitle', parent=styles['Heading1'], fontSize=18, leading=22, spaceAfter=12, textColor='#1E3A8A')
                    meta_style = ParagraphStyle('EntMeta', parent=styles['Normal'], fontSize=9, leading=13, spaceAfter=12, textColor='#4B5563')
                    body_style = ParagraphStyle('EntBody', parent=styles['Normal'], fontSize=font_size, leading=line_leading, spaceAfter=10, wordWrap='CJK')
                    summary_style = ParagraphStyle('EntSum', parent=styles['Normal'], fontSize=font_size, leading=line_leading, spaceAfter=8, textColor='#047857')
                    
                    # Layout Assembly Line
                    story = [
                        Paragraph(f"<b>{html.escape(page_title)}</b>", title_style),
                        Paragraph(f"<b>DATA LOG:</b> {user_url}<br/><b>TIMESTAMP:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style),
                        HRFlowable(width="100%", thickness=1, color="#D1D5DB", spaceBefore=5, spaceAfter=15)
                    ]
                    
                    # Inject AI Smart Summary Box if requested
                    if enable_summary:
                        story.append(Paragraph("<b>📊 EXECUTIVE SUMMARY MATRIX / 核心摘要簡報:</b>", body_style))
                        bullet_points = generate_summary_bullets(raw_paragraphs, count=3)
                        for bullet in bullet_points:
                            story.append(Paragraph(f"<i>{html.escape(bullet)}</i>", summary_style))
                        story.append(HRFlowable(width="100%", thickness=1, color="#E5E7EB", spaceBefore=10, spaceAfter=15))
                    
                    # Populate document items securely
                    for block in raw_paragraphs[:250]:
                        safe_block = html.escape(block).strip()
                        if safe_block:
                            story.append(Paragraph(safe_block, body_style))
                            
                    doc.build(story)
                    
                    with open(pdf_path, "rb") as f:
                        file_bytes = f.read()
                    mime_type = "application/pdf"
                    
                else:
                    # Comprehensive Plain Text Compilation
                    filename = f"{file_base}.txt"
                    text_blocks = [
                        f"SYSTEM INTELLIGENCE OVERVIEW",
                        f"TITLE: {page_title}",
                        f"SOURCE: {user_url}",
                        f"TIMESTAMP: {datetime.now()}\n",
                        "="*40
                    ]
                    
                    if enable_summary:
                        text_blocks.append("\n[EXECUTIVE SUMMARY MATRIX]")
                        text_blocks.extend(generate_summary_bullets(raw_paragraphs, count=3))
                        text_blocks.append("="*40 + "\n")
                        
                    text_blocks.extend(raw_paragraphs)
                    file_bytes = "\n\n".join(text_blocks).encode('utf-8', errors='ignore')
                    mime_type = "text/plain"

                # Render successful status layout
                st.success("🎉 Enterprise Processing Pipeline Complete! Your dashboard layout is reset and stable.")
                st.download_button(
                    label=f"📥 Download Processed File ({filename.split('.')[-1].upper()})",
                    data=file_bytes,
                    file_name=filename,
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"❌ Core Pipeline Exception: {e}\n\nTroubleshooting: Verify that the website is not behind a security recaptcha system.")
