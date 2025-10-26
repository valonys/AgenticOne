"""
Markdown to PDF Converter
Multiple methods for converting Markdown documents to professional PDFs
"""

import os
import sys
import markdown
from pathlib import Path
from typing import Optional
import argparse

class MarkdownToPDFConverter:
    """Convert Markdown files to PDF using multiple methods"""
    
    def __init__(self):
        self.methods = {
            "1": self.weasyprint_method,
            "2": self.pandoc_method, 
            "3": self.pdfkit_method,
            "4": self.reportlab_method
        }
    
    def weasyprint_method(self, markdown_file: str, output_file: str) -> bool:
        """Method 1: WeasyPrint (Recommended) - Best for professional styling"""
        try:
            import weasyprint
            
            # Read markdown file
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'toc', 'codehilite']
            )
            
            # Add professional CSS styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @top-center {{
                            content: "AgenticOne Professional Report";
                            font-size: 10px;
                            color: #666;
                        }}
                        @bottom-right {{
                            content: "Page " counter(page);
                            font-size: 10px;
                            color: #666;
                        }}
                    }}
                    
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                    }}
                    
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-top: 30px;
                        page-break-before: always;
                    }}
                    
                    h1:first-child {{
                        page-break-before: avoid;
                    }}
                    
                    h2 {{
                        color: #34495e;
                        border-bottom: 2px solid #ecf0f1;
                        padding-bottom: 5px;
                        margin-top: 25px;
                    }}
                    
                    h3 {{
                        color: #7f8c8d;
                        margin-top: 20px;
                    }}
                    
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    th, td {{
                        border: 1px solid #bdc3c7;
                        padding: 12px;
                        text-align: left;
                    }}
                    
                    th {{
                        background-color: #3498db;
                        color: white;
                        font-weight: 600;
                    }}
                    
                    tr:nth-child(even) {{
                        background-color: #f8f9fa;
                    }}
                    
                    .risk-high {{ color: #e74c3c; font-weight: bold; }}
                    .risk-medium {{ color: #f39c12; font-weight: bold; }}
                    .risk-low {{ color: #27ae60; font-weight: bold; }}
                    
                    .recommendation {{
                        background-color: #ecf0f1;
                        padding: 15px;
                        border-left: 4px solid #3498db;
                        margin: 10px 0;
                    }}
                    
                    .technical-details {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                        font-family: 'Courier New', monospace;
                        font-size: 0.9em;
                    }}
                    
                    ul, ol {{
                        margin: 15px 0;
                        padding-left: 30px;
                    }}
                    
                    li {{
                        margin: 5px 0;
                    }}
                    
                    .footer {{
                        margin-top: 50px;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        text-align: center;
                        font-size: 0.9em;
                        color: #7f8c8d;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Convert to PDF
            weasyprint.HTML(string=styled_html).write_pdf(output_file)
            return True
            
        except ImportError:
            print("❌ WeasyPrint not installed. Install with: pip install weasyprint")
            return False
        except Exception as e:
            print(f"❌ WeasyPrint conversion failed: {e}")
            return False
    
    def pandoc_method(self, markdown_file: str, output_file: str) -> bool:
        """Method 2: Pandoc - Best for academic papers with TOC"""
        try:
            import pypandoc
            
            # Convert markdown to PDF using pandoc
            pypandoc.convert_file(
                markdown_file,
                'pdf',
                outputfile=output_file,
                extra_args=[
                    '--pdf-engine=xelatex',
                    '--toc',
                    '--toc-depth=3',
                    '--highlight-style=tango',
                    '--variable', 'geometry:margin=2cm',
                    '--variable', 'fontsize=11pt',
                    '--variable', 'documentclass=article'
                ]
            )
            return True
            
        except ImportError:
            print("❌ pypandoc not installed. Install with: pip install pypandoc")
            print("   Also install Pandoc from: https://pandoc.org/installing.html")
            return False
        except Exception as e:
            print(f"❌ Pandoc conversion failed: {e}")
            return False
    
    def pdfkit_method(self, markdown_file: str, output_file: str) -> bool:
        """Method 3: PDFKit - Good balance of features"""
        try:
            import pdfkit
            import markdown
            
            # Read and convert markdown
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            html_content = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'toc']
            )
            
            # Add basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1, h2, h3 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Convert to PDF
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            
            pdfkit.from_string(styled_html, output_file, options=options)
            return True
            
        except ImportError:
            print("❌ pdfkit not installed. Install with: pip install pdfkit")
            print("   Also install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
            return False
        except Exception as e:
            print(f"❌ PDFKit conversion failed: {e}")
            return False
    
    def reportlab_method(self, markdown_file: str, output_file: str) -> bool:
        """Method 4: ReportLab - Pure Python solution"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            import markdown
            
            # Read markdown file
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert to HTML first, then extract text
            html_content = markdown.markdown(markdown_content)
            
            # Create PDF
            doc = SimpleDocTemplate(output_file, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            story.append(Paragraph("AgenticOne Professional Report", title_style))
            story.append(Spacer(1, 20))
            
            # Add content (simplified - in practice you'd parse HTML properly)
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=12
            )
            
            # Split content into paragraphs
            paragraphs = html_content.split('\n')
            for para in paragraphs:
                if para.strip():
                    # Remove HTML tags (basic cleanup)
                    clean_text = para.replace('<p>', '').replace('</p>', '').replace('<br>', '')
                    if clean_text.strip():
                        story.append(Paragraph(clean_text, content_style))
                        story.append(Spacer(1, 6))
            
            doc.build(story)
            return True
            
        except ImportError:
            print("❌ reportlab not installed. Install with: pip install reportlab")
            return False
        except Exception as e:
            print(f"❌ ReportLab conversion failed: {e}")
            return False
    
    def convert(self, markdown_file: str, output_file: str = None, method: str = None) -> bool:
        """Convert markdown file to PDF using specified method"""
        
        if not os.path.exists(markdown_file):
            print(f"❌ Markdown file not found: {markdown_file}")
            return False
        
        if not output_file:
            output_file = markdown_file.replace('.md', '.pdf')
        
        if method and method in self.methods:
            print(f"🔄 Converting using {method} method...")
            return self.methods[method](markdown_file, output_file)
        
        # Try all methods until one works
        for method_name, method_func in self.methods.items():
            print(f"🔄 Trying method {method_name}...")
            if method_func(markdown_file, output_file):
                print(f"✅ Successfully converted using method {method_name}")
                return True
        
        print("❌ All conversion methods failed")
        return False
    
    def interactive_convert(self):
        """Interactive conversion with method selection"""
        print("📄 Markdown to PDF Converter")
        print("=" * 40)
        
        # Get input file
        markdown_file = input("Enter markdown file path: ").strip()
        if not markdown_file:
            markdown_file = "corrosion_report.md"  # Default
        
        if not os.path.exists(markdown_file):
            print(f"❌ File not found: {markdown_file}")
            return False
        
        # Get output file
        output_file = input("Enter output PDF path (or press Enter for auto): ").strip()
        if not output_file:
            output_file = markdown_file.replace('.md', '.pdf')
        
        # Select method
        print("\nAvailable conversion methods:")
        print("1. WeasyPrint (Recommended) - Professional styling, CSS control")
        print("2. Pandoc - Academic papers, automatic TOC")
        print("3. PDFKit - Good balance of features")
        print("4. ReportLab - Pure Python solution")
        print("5. Try all methods until one works")
        
        choice = input("\nSelect method (1-5): ").strip()
        
        if choice == "5":
            return self.convert(markdown_file, output_file)
        elif choice in self.methods:
            return self.methods[choice](markdown_file, output_file)
        else:
            print("❌ Invalid choice")
            return False


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF")
    parser.add_argument("input_file", help="Input markdown file")
    parser.add_argument("-o", "--output", help="Output PDF file")
    parser.add_argument("-m", "--method", choices=["1", "2", "3", "4"], 
                       help="Conversion method (1=WeasyPrint, 2=Pandoc, 3=PDFKit, 4=ReportLab)")
    parser.add_argument("-i", "--interactive", action="store_true", 
                       help="Interactive mode")
    
    args = parser.parse_args()
    
    converter = MarkdownToPDFConverter()
    
    if args.interactive:
        converter.interactive_convert()
    else:
        success = converter.convert(args.input_file, args.output, args.method)
        if success:
            print(f"✅ PDF created successfully: {args.output or args.input_file.replace('.md', '.pdf')}")
        else:
            print("❌ Conversion failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
