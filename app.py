import streamlit as st
import json
from generate import get_cover_previews, get_outline_previews, hydrate_content_section
import time
from fpdf import FPDF
from io import BytesIO
import base64
import copy 
import hmac

class CustomPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_from_json(json_input):
    try:
        data = json.loads(json_input)
    except json.JSONDecodeError:
        st.error("Invalid JSON input")
        return None

    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for page in data['pages']:
        page_type = page.get('type', 'content_page')
        
        pdf.add_page()
        if page_type == 'cover_page':
            pdf.set_font('Arial', 'B', 18)
            title_width = pdf.get_string_width(page.get('title', 'No Title')) + 6
            document_width = pdf.w - 2*pdf.l_margin
            title_x = (document_width - title_width) / 2
            pdf.set_xy(title_x, pdf.h / 2 - 10)  # Adjusted for vertical centering
            pdf.cell(title_width, 10, page.get('title', 'No Title'), 0, 1, 'C')
            if 'subtext' in page:
                pdf.set_font('Arial', 'I', 14)
                pdf.cell(0, 10, page['subtext'], 0, 1, 'C')
            if 'author' in page:
                pdf.set_font('Arial', 'I', 12)
                pdf.cell(0, 10, f"Author: {page['author']}", 0, 1, 'C')

        elif page_type == 'introduction':
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, page.get('title', 'Introduction'), 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, page.get('text', ''))

        elif page_type == 'overview':
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Overview', 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, page.get('text', ''))
        
        elif page_type == 'table_of_contents':
            print('table of contents')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Table of Contents', 0, 1)
            for section in page.get('sections', []):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, section.get('title', 'Item'), 0, 1)
                for point in section.get('points', []):
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 10, point.get('text', ''))

        elif page_type == 'section':
            section = page.get('section')
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, section.get('title'), 0, 1)
            for point in section.get('points', []):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, point.get('text', 'placeholder'), 0, 1)
                for paragraph in point.get('paragraphs', []):
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 10, paragraph.get('content', ''))

    pdf_content = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_content)
    return pdf_buffer

def displayPDF(pdf_buffer):
    base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    if not check_password():
        st.stop()

    st.set_page_config(layout="wide")
    st.title("PDF Generator :sparkles:")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.header("1: Inputs", divider="rainbow")

        if 'selected_cover_preview' not in st.session_state:
            st.session_state.selected_cover_preview = None

        if 'outline_preview' not in st.session_state:
            st.session_state.outline_preview = None

        if 'output_json' not in st.session_state:
            st.session_state.output_json = None
        
        if 'pdf_bytes' not in st.session_state:
            st.session_state.pdf_bytes = None
        
        author_name = st.text_input("Author Name","John Doe")
        doc_type = st.selectbox("Type", ["Comprehensive Guide", "How-to"], index=0)
        topic = st.text_input("Topic", "Personal Branding")

        if st.button("Generate Teasers"):
            cover_results = json.loads(get_cover_previews(content_type=doc_type, topic=topic))
            cover_previews = cover_results.get('covers', [])
            for cover in cover_previews:
                cover['author'] = author_name
            st.session_state.cover_previews = cover_previews  # Store in session state
            st.session_state.selected_cover_preview = None  # Reset selected cover_preview

        # user has generated previews
        st.header("2: Teasers", divider="rainbow")
        if 'cover_previews' in st.session_state and isinstance(st.session_state.cover_previews, list):
            cover_previews = st.session_state.cover_previews
            options = [f"{cover_preview['title']} - {cover_preview['subtext']}" for cover_preview in cover_previews]
            option = st.selectbox("Teasers:", options, key="cover_preview_select")
            
            if st.button("Select Teaser"):
                selected_index = options.index(option)
                st.session_state.selected_cover_preview = cover_previews[selected_index]

        # user has selected 
        if st.session_state.selected_cover_preview:
            st.text("Selected Teaser:")
            st.code(json.dumps(st.session_state.selected_cover_preview, indent=2), language='json')

            if st.button("Generate Outline"):
                outline_results = json.loads(get_outline_previews(title=st.session_state.selected_cover_preview['title'], subtext=st.session_state.selected_cover_preview['subtext']))
                outline_preview = outline_results.get('outline')
                outline_preview['title'] = st.session_state.selected_cover_preview.get('title', '')
                outline_preview['subtext'] = st.session_state.selected_cover_preview.get('subtext', '')
                st.session_state.outline_preview = outline_preview  # Store in session state
        with col2:
            st.header("3: Outline", divider="rainbow") 
            if st.session_state.outline_preview:
                with st.container(height=700):
                    st.code(json.dumps(st.session_state.outline_preview, indent=2), language='json')
                pages = []

                pages.append({"type": "cover_page", "title": st.session_state.selected_cover_preview.get('title', ""), "author": author_name, "subtext": st.session_state.selected_cover_preview.get('subtext', "")})
                pages.append({"type": "overview", "text": st.session_state.outline_preview.get('overview','')})
                pages.append({"type": "table_of_contents", "sections": st.session_state.outline_preview.get('tableOfContents','')})
                
                if st.button("Generate content"):
                    table_of_contents = list(st.session_state.outline_preview.get('tableOfContents'))
                    content_progress = st.progress(0, text="Generating content")
                    percent_complete = 0
                    total = len(table_of_contents)
                    i = 0
                    for section in table_of_contents:
                        i=i+1
                        percent_complete = round((i / total) * 100)
                        section_title = section.get('title')
                        content_progress.progress(percent_complete, text=f"{i}/{total}-{section_title}")
                        points = copy.deepcopy(section.get('points'))
                        section = {
                            "title": section.get('title'),
                            "points": []
                        }

                        for point in points:
                            hydration_results = json.loads(hydrate_content_section(tableOfContents=json.dumps(table_of_contents), overview=st.session_state.outline_preview.get('overview'), title=section.get('title'), point=point.get('text')))
                            paragraphs = hydration_results.get('paragraphs',[])
                            point['paragraphs'] = paragraphs
                            section['points'].append(point)

                        #st.code(json.dumps(section, indent=4), language='json')
                        # build sections from paragraphs and append to new page in json output

                        pages.append({"type": "section", "section": section})
                        
                    content_progress.empty()
                
                    output_json = {
                        "created_at": int(time.time()),
                        "pages": pages
                    }

                    #st.write(output_json)
                    st.session_state.output_json = output_json
        with col3:
            st.header("4: Content", divider="rainbow") 
            if st.session_state.output_json:
                with st.container(height=700):
                    st.code(json.dumps(st.session_state.output_json, indent=2), language='json')
                if st.button("Create PDF"):
                    st.session_state.pdf_bytes = create_pdf_from_json(json.dumps(st.session_state.output_json))

        with col4:
            st.header("5: Download", divider="rainbow") 
            if st.session_state.pdf_bytes:
                st.success("PDF generated successfully!")
                displayPDF(st.session_state.pdf_bytes)
                st.download_button(label="Download PDF",
                                data=st.session_state.pdf_bytes.getvalue(),
                                file_name="generated_pdf.pdf",
                                mime="application/pdf")
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if __name__ == "__main__":
    main()