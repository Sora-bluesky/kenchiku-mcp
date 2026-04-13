"""
File mixin for AutoCAD adapter.

Handles file operations (save, open, close, new, switch).
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from core import get_config

logger = logging.getLogger(__name__)


class FileMixin:
    """Mixin for file operations."""

    if TYPE_CHECKING:
        document: Any

        def _get_document(self, operation: str = "operation") -> Any: ...
        def _get_application(self, operation: str = "operation") -> Any: ...
        def _validate_document(self) -> bool: ...
        def resolve_export_path(
            self, filename: str, folder_type: str = "drawings"
        ) -> str: ...
        def _sanitize_command_input(self, user_input: str) -> str: ...
        def _wait_for(
            self, condition: Any, timeout: float = 20.0, interval: float = 0.1
        ) -> bool: ...

    def save_drawing(
        self, filepath: str = "", filename: str = "", format: str = "dwg"
    ) -> bool:
        """Save drawing to file.

        Args:
            filepath: Full path to save file (e.g., 'C:/drawings/myfile.dwg').
                     When a directory is included, saves directly to that path.
            filename: Just the filename (e.g., 'myfile.dwg'). If provided without
                     filepath, uses configured output directory.
            format: File format (dwg, dxf, pdf). Default: dwg.
                   For pdf, delegates to export_pdf().

        Returns:
            bool: True if successful, False otherwise

        Note:
            - If both filepath and filename provided, filepath takes precedence
            - If only filename provided, saved to config output directory
            - If neither provided, uses current document name
        """
        try:
            # Delegate PDF to dedicated export method (SaveAs doesn't support PDF)
            if format.lower() == "pdf":
                return self.export_pdf(filepath=filepath, filename=filename)

            document = self._get_document("save_drawing")

            # ========== Determine Save Path ==========
            if filepath:
                filepath_path = Path(filepath)
                if filepath_path.parent != Path("."):
                    # Full path provided — save directly to that path
                    save_filename = filepath_path.name
                    if not save_filename.lower().endswith(f".{format}"):
                        save_filename = f"{save_filename}.{format}"
                    final_path = (filepath_path.parent / save_filename).resolve()
                    final_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Bare filename via filepath param (no directory)
                    save_filename = filepath_path.name
                    if not save_filename.lower().endswith(f".{format}"):
                        save_filename = f"{save_filename}.{format}"
                    final_path = Path(
                        self.resolve_export_path(save_filename, "drawings")
                    )
            elif filename:
                save_filename = filename
                if not save_filename.lower().endswith(f".{format}"):
                    save_filename = f"{save_filename}.{format}"
                final_path = Path(
                    self.resolve_export_path(save_filename, "drawings")
                )
            else:
                # No filepath or filename — use document name or generate one
                if document.Name:
                    save_filename = document.Name
                else:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_filename = f"drawing_{timestamp}.{format}"
                if not save_filename.lower().endswith(f".{format}"):
                    save_filename = f"{save_filename}.{format}"
                final_path = Path(
                    self.resolve_export_path(save_filename, "drawings")
                )

            # Save the drawing (DWG/DXF only)
            document.SaveAs(str(final_path))
            logger.info(f"Saved drawing to {final_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save drawing: {e}")
            return False

    def export_pdf(self, filepath: str = "", filename: str = "") -> bool:
        """Export current drawing to PDF using EXPORTPDF command.

        Uses ZWCAD/AutoCAD's built-in _EXPORTPDF command via SendCommand.
        Falls back to -PLOT command with DWG To PDF.pc3 if EXPORTPDF fails.

        Args:
            filepath: Full path for PDF output (e.g., 'C:/output/drawing.pdf').
            filename: Just the filename (e.g., 'drawing.pdf'). Uses config dir.

        Returns:
            bool: True if successful, False otherwise
        """
        import os
        import time

        try:
            document = self._get_document("export_pdf")

            # ========== Determine output path ==========
            if filepath:
                filepath_path = Path(filepath)
                if filepath_path.parent != Path("."):
                    pdf_filename = filepath_path.name
                    if not pdf_filename.lower().endswith(".pdf"):
                        pdf_filename = f"{filepath_path.stem}.pdf"
                    final_path = str(
                        (filepath_path.parent / pdf_filename).resolve()
                    )
                    Path(final_path).parent.mkdir(parents=True, exist_ok=True)
                else:
                    pdf_filename = filepath_path.stem + ".pdf"
                    final_path = self.resolve_export_path(
                        pdf_filename, "drawings"
                    )
            elif filename:
                pdf_filename = Path(filename).stem + ".pdf"
                final_path = self.resolve_export_path(pdf_filename, "drawings")
            else:
                if document.Name:
                    pdf_filename = Path(document.Name).stem + ".pdf"
                else:
                    from datetime import datetime

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_filename = f"drawing_{timestamp}.pdf"
                final_path = self.resolve_export_path(pdf_filename, "drawings")

            # Ensure backslashes for CAD command on Windows
            filepath_cad = final_path.replace("/", "\\")
            safe_path = self._sanitize_command_input(filepath_cad)

            logger.info(f"Exporting PDF to {safe_path}")

            # Clear any pending commands
            document.SendCommand("\x1b\x1b")
            time.sleep(0.1)

            # Disable file dialog to prevent interactive prompts
            document.SendCommand("FILEDIA 0\n")
            time.sleep(0.1)

            # ========== Attempt 1: EXPORTPDF command ==========
            document.SendCommand(f"_EXPORTPDF\n{safe_path}\n")

            pdf_created = self._wait_for(
                lambda: os.path.exists(final_path)
                and os.path.getsize(final_path) > 0,
                timeout=15.0,
                interval=0.5,
            )

            # Re-enable file dialog
            document.SendCommand("FILEDIA 1\n")

            if pdf_created:
                logger.info(f"PDF exported via EXPORTPDF to {final_path}")
                return True

            # ========== Attempt 2: -PLOT fallback ==========
            logger.warning(
                "EXPORTPDF did not produce file, trying -PLOT fallback..."
            )

            document.SendCommand("\x1b\x1b")
            time.sleep(0.1)
            document.SendCommand("FILEDIA 0\n")
            time.sleep(0.1)

            plot_cmd = (
                "_-PLOT\n"
                "Y\n"
                "\n"
                "DWG To PDF.pc3\n"
                "ISO A3 (420.00 x 297.00 MM)\n"
                "M\n"
                "E\n"
                "N\n"
                "F\n"
                f"{safe_path}\n"
                "Y\n"
                "Y\n"
            )
            document.SendCommand(plot_cmd)

            pdf_created = self._wait_for(
                lambda: os.path.exists(final_path)
                and os.path.getsize(final_path) > 0,
                timeout=30.0,
                interval=1.0,
            )

            document.SendCommand("FILEDIA 1\n")

            if pdf_created:
                logger.info(f"PDF exported via -PLOT to {final_path}")
                return True

            logger.error(
                f"PDF export failed: file not created at {final_path}"
            )
            return False

        except Exception as e:
            # Ensure FILEDIA is restored even on error
            try:
                document.SendCommand("FILEDIA 1\n")
            except Exception:
                pass
            logger.error(f"Failed to export PDF: {e}")
            return False

    def open_drawing(self, filepath: str) -> bool:
        """Open a drawing file in the CAD application via COM.

        Args:
            filepath: Absolute path to the drawing file to open (e.g. ``C:/drawings/plan.dwg``).

        Returns:
            True if the file was opened successfully, False otherwise.
        """
        try:
            application = self._get_application("open_drawing")
            self.document = application.Documents.Open(filepath)
            logger.info(f"Opened drawing from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to open drawing: {e}")
            return False

    def new_drawing(self) -> bool:
        """Create a new blank drawing document in the CAD application via COM.

        Returns:
            True if the document was created successfully, False otherwise.
        """
        try:
            application = self._get_application("new_drawing")
            self.document = application.Documents.Add()
            self._refresh_document_reference()
            logger.info("Created new blank drawing")
            return True
        except Exception as e:
            logger.error(f"Failed to create new drawing: {e}")
            return False

    def _refresh_document_reference(self, auto_create: bool = True) -> bool:
        """Refresh internal document reference to ActiveDocument.

        This ensures self.document always points to the active document
        in the application. Useful after creating or switching documents.

        Args:
            auto_create: If True and no documents open, create a new one (default: True)

        Returns:
            True if successful, False otherwise
        """
        try:
            application = self._get_application("_refresh_document_reference")

            # Case 1: Documents are open, use the active one
            if application.Documents.Count > 0:
                self.document = application.ActiveDocument
                if self.document is not None:
                    logger.debug(f"Document reference refreshed: {self.document.Name}")
                return True

            # Case 2: No documents open
            if auto_create:
                logger.warning("No documents open. Creating a new blank document...")
                self.document = application.Documents.Add()
                if self.document is not None:
                    logger.info(f"Auto-created new document: {self.document.Name}")
                return True
            else:
                logger.warning("No documents open")
                return False

        except Exception as e:
            logger.error(f"Failed to refresh document reference: {e}")
            return False

    def get_open_drawings(self) -> list:
        """Get list of all open drawing filenames.

        Returns:
            List of drawing names (e.g., ["drawing1.dwg", "drawing2.dwg"])
        """
        try:
            application = self._get_application("get_open_drawings")
            drawings = []

            # Use direct iteration instead of Item indexing
            for doc in application.Documents:
                drawings.append(doc.Name)

            logger.info(f"Found {len(drawings)} open drawings: {drawings}")
            return drawings
        except Exception as e:
            logger.error(f"Failed to get open drawings: {e}")
            return []

    def switch_drawing(self, drawing_name: str) -> bool:
        """Switch to a different open drawing.

        Args:
            drawing_name: Name of the drawing to switch to (e.g., "drawing1.dwg")

        Returns:
            True if successful, False otherwise
        """
        try:
            application = self._get_application("switch_drawing")

            # Use direct iteration instead of Item indexing
            for doc in application.Documents:
                if doc.Name == drawing_name:
                    # Intenta activar a través del documento
                    doc.Activate()
                    # Intenta también forzarlo a nivel de aplicación (ZWCAD/AutoCAD)
                    try:
                        application.ActiveDocument = doc
                    except Exception:
                        pass

                    self.document = doc

                    # Pump Windows messages briefly to let CAD process the GUI switch
                    try:
                        import pythoncom

                        for _ in range(5):
                            pythoncom.PumpWaitingMessages()
                    except ImportError:
                        pass

                    logger.info(f"Switched to drawing: {drawing_name}")
                    return True

            logger.warning(f"Drawing not found: '{drawing_name}'")
            return False

        except Exception as e:
            logger.error(f"Failed to switch drawing: {e}")
            return False

    def close_drawing(self, save_changes: bool = False) -> bool:
        """Close the current drawing.

        Args:
            save_changes: Whether to save changes before closing (default: False)
                         True = save changes
                         False = discard changes without prompting

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._validate_document() or self.document is None:
                logger.warning("No document to close")
                return False

            document = self.document
            doc_name = document.Name

            # Close document using COM API
            document.Close(save_changes)

            # Try to update connection to remaining open document
            refresh_success = self._refresh_document_reference(auto_create=False)

            if refresh_success and self.document is not None:
                logger.info(
                    f"Closed drawing: {doc_name} (save_changes={save_changes}). "
                    f"Switched to: {self.document.Name}"
                )
            else:
                # No other documents open - attempt to create one to maintain connection
                logger.warning(
                    f"No other documents open after closing {doc_name}. "
                    "Attempting to create a new blank document..."
                )
                try:
                    application = self._get_application("close_drawing_reconnect")
                    self.document = application.Documents.Add()
                    logger.info(
                        f"Closed drawing: {doc_name} (save_changes={save_changes}). "
                        f"Created new document: {self.document.Name}"
                    )
                except Exception as e:
                    self.document = None
                    logger.info(
                        f"Closed drawing: {doc_name} (save_changes={save_changes}). "
                        "Could not create new document."
                    )
                    logger.debug(f"Auto-create error: {e}")

            return True

        except Exception as e:
            logger.error(f"Failed to close drawing: {e}")
            return False
