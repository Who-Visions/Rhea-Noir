"""
Gemini Document Processing Skill for Rhea-Noir
PDF analysis, extraction, and Q&A
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import io


class DocumentsSkill:
    """Skill for Gemini document processing."""

    name = "documents"
    version = "1.0.0"
    description = "Gemini Documents - PDF analysis and extraction"

    MODEL = "gemini-3-flash-preview"

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client()
        return self._client

    def _success(self, data: Any) -> Dict:
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        return {"success": False, "error": message}

    def _load_pdf(self, file_path: str, use_files_api: bool = False):
        """Load PDF from file path or URL."""
        from google.genai import types
        client = self._get_client()

        path = Path(file_path)

        if file_path.startswith("http"):
            # URL - fetch and upload
            import httpx
            pdf_data = io.BytesIO(httpx.get(file_path).content)
            if use_files_api:
                return client.files.upload(
                    file=pdf_data,
                    config=dict(mime_type='application/pdf')
                )
            else:
                return types.Part.from_bytes(
                    data=pdf_data.read(),
                    mime_type='application/pdf'
                )
        elif path.exists():
            # Local file
            if use_files_api or path.stat().st_size > 10 * 1024 * 1024:  # >10MB
                return client.files.upload(file=file_path)
            else:
                return types.Part.from_bytes(
                    data=path.read_bytes(),
                    mime_type='application/pdf'
                )
        else:
            raise FileNotFoundError(f"PDF not found: {file_path}")

    def summarize(
        self,
        file_path: str,
        model: str = None
    ) -> Dict:
        """
        Summarize a PDF document.

        Args:
            file_path: Path to PDF or URL
            model: Gemini model to use

        Returns:
            Dict with summary
        """
        try:
            client = self._get_client()
            pdf = self._load_pdf(file_path)

            response = client.models.generate_content(
                model=model or self.MODEL,
                contents=[pdf, "Summarize this document"]
            )

            return self._success({
                "summary": response.text,
                "file": file_path
            })
        except Exception as e:
            return self._error(str(e))

    def ask(
        self,
        file_path: str,
        question: str,
        model: str = None
    ) -> Dict:
        """
        Ask a question about a PDF.

        Args:
            file_path: Path to PDF or URL
            question: Question to ask
            model: Gemini model to use

        Returns:
            Dict with answer
        """
        try:
            client = self._get_client()
            pdf = self._load_pdf(file_path)

            response = client.models.generate_content(
                model=model or self.MODEL,
                contents=[pdf, question]
            )

            return self._success({
                "answer": response.text,
                "question": question,
                "file": file_path
            })
        except Exception as e:
            return self._error(str(e))

    def extract(
        self,
        file_path: str,
        fields: List[str],
        model: str = None
    ) -> Dict:
        """
        Extract structured data from a PDF.

        Args:
            file_path: Path to PDF or URL
            fields: Fields to extract
            model: Gemini model to use

        Returns:
            Dict with extracted data as JSON
        """
        try:
            client = self._get_client()
            pdf = self._load_pdf(file_path)

            fields_str = ", ".join(fields)
            prompt = f"Extract the following fields from this document: {fields_str}. Return as JSON."

            response = client.models.generate_content(
                model=model or self.MODEL,
                contents=[pdf, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            return self._success({
                "extracted": response.text,
                "fields": fields,
                "file": file_path
            })
        except Exception as e:
            return self._error(str(e))

    def compare(
        self,
        file_paths: List[str],
        question: str,
        model: str = None
    ) -> Dict:
        """
        Compare multiple PDF documents.

        Args:
            file_paths: List of PDF paths or URLs
            question: Comparison question
            model: Gemini model to use

        Returns:
            Dict with comparison
        """
        try:
            client = self._get_client()

            # Load all PDFs (use Files API for multiple)
            pdfs = [self._load_pdf(fp, use_files_api=True) for fp in file_paths]

            response = client.models.generate_content(
                model=model or self.MODEL,
                contents=[*pdfs, question]
            )

            return self._success({
                "comparison": response.text,
                "question": question,
                "files": file_paths
            })
        except Exception as e:
            return self._error(str(e))

    def transcribe(
        self,
        file_path: str,
        output_format: str = "markdown",
        model: str = None
    ) -> Dict:
        """
        Transcribe PDF content preserving layout.

        Args:
            file_path: Path to PDF or URL
            output_format: "markdown", "html", or "text"
            model: Gemini model to use

        Returns:
            Dict with transcribed content
        """
        try:
            client = self._get_client()
            pdf = self._load_pdf(file_path)

            format_instructions = {
                "markdown": "Transcribe this document to Markdown, preserving structure and formatting.",
                "html": "Transcribe this document to HTML, preserving layout and formatting.",
                "text": "Transcribe the text content of this document."
            }

            prompt = format_instructions.get(output_format, format_instructions["text"])

            response = client.models.generate_content(
                model=model or self.MODEL,
                contents=[pdf, prompt]
            )

            return self._success({
                "content": response.text,
                "format": output_format,
                "file": file_path
            })
        except Exception as e:
            return self._error(str(e))


skill = DocumentsSkill()
