from typing import List
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("rag-mcp")


# Pydantic models for type safety
class Chapter(BaseModel):
    chapter: str
    pageStart: int
    pageEnd: int
    summary: str


class BookChapters(BaseModel):
    chapters: List[Chapter]


# MinIO client configuration
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


# Add an addition tool
@mcp.tool()
def get_books() -> List[str]:
    """Get list of documents from MinIO storage under /files prefix in documents bucket. Names are base64 encoded."""
    try:
        # List all objects in the documents bucket under /files prefix
        objects = minio_client.list_objects("documents", prefix="files/", recursive=True)
        
        # Extract object names (remove the 'files/' prefix for cleaner output)
        document_names = []
        for obj in objects:
            # Remove 'files/' prefix from the object name
            clean_name = obj.object_name.replace("files/", "", 1)
            document_names.append(clean_name)
        
        return document_names
    except S3Error as e:
        # Handle MinIO errors
        return [f"Error accessing MinIO: {str(e)}"]
    except Exception as e:
        # Handle other errors
        return [f"Unexpected error: {str(e)}"]


@mcp.tool()
def get_chapters_and_summary_of_book(book_title: str) -> BookChapters:
    """Get chapters and summaries of a book from MinIO storage under /chapters prefix in documents bucket.

    Args:
        book_title: Title of the book base64 encoded (with or without .pdf extension)

    Returns a BookChapters object containing a list of Chapter objects with:
    - chapter: Chapter title
    - pageStart: Starting page number
    - pageEnd: Ending page number
    - summary: Chapter summary text
    """
    import json
    
    try:
        if book_title.endswith(".pdf"):
            book_title = book_title[:-4]
        # Construct the JSON file path with chapters prefix
        json_file_path = f"chapters/{book_title}.json"
        
        # Get the object from MinIO
        response = minio_client.get_object("documents", json_file_path)
        
        # Read and decode the content
        content = response.read().decode('utf-8')
        response.close()
        response.release_conn()
        
        # Parse JSON content
        chapters_data = json.loads(content)
        
        # Create and return Pydantic model
        return BookChapters(chapters=chapters_data)
        
    except S3Error as e:
        raise ValueError(f"Error accessing MinIO: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")


@mcp.tool()
def get_content_of_chapter(book_title: str, page_start: int, page_end: int) -> str:
    """Get text content from specific pages of a book PDF stored in MinIO.
    
    Args:
        book_title: Title of the book base64 encoded (with or without .pdf extension)
        page_start: Starting page number (1-indexed)
        page_end: Ending page number (inclusive)
    
    Returns:
        Text content extracted from the specified pages
    """
    import pymupdf

    try:
        # Ensure book_title has .pdf extension
        if not book_title.endswith(".pdf"):
            book_title = f"{book_title}.pdf"
        
        # Construct the file path with files prefix
        pdf_file_path = f"files/{book_title}"
        
        # Get the PDF object from MinIO
        response = minio_client.get_object("documents", pdf_file_path)
        
        # Read PDF content into memory
        pdf_data = response.read()
        response.close()
        response.release_conn()
        
        # Open PDF with PyMuPDF from bytes
        pdf_document = pymupdf.open(stream=pdf_data, filetype="pdf")
        
        # Extract text from specified pages
        text_content = []
        
        # PyMuPDF uses 0-based indexing, so adjust page numbers
        for page_num in range(page_start - 1, min(page_end, len(pdf_document))):
            page = pdf_document[page_num]
            text = page.get_text()
            text_content.append(f"--- Page {page_num + 1} ---\n{text}")
        
        # Close the PDF document
        pdf_document.close()
        
        # Join all page texts
        return "\n\n".join(text_content)
        
    except S3Error as e:
        return f"Error accessing MinIO: {str(e)}"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


# if __name__ == '__main__':
#     print(get_chapters_and_summary_of_book("QnJhbmRzdMOkdGVyMjAxM19Cb29rX0FnaWxlSVQtUHJvamVrdGVFcmZvbGdyZWljaEdlcw==.pdf"))
    # "Brandstäter2013_Book_AgileIT-ProjekteErfolgreichGes.json"