"""
GUI Application for HTML Search Engine - Google Style

This module provides a Google-style search interface with blue titles, green URLs,
and gray description snippets in a clean vertical layout.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import zipfile
from typing import Optional, List, Dict, Any
from html_indexer import HtmlIndexer
from query_processor import QueryProcessor, QueryResult


class GoogleResultCard(tk.Frame):
    """Google-style search result card."""

    def __init__(self, parent, filename, word_count, relevance_score=0.0, on_view=None, **kwargs):
        super().__init__(parent, bg='white', relief='flat', **kwargs)

        self.filename = filename
        self.word_count = word_count
        self.relevance_score = relevance_score
        self.on_view = on_view

        self._create_google_layout()

    def _create_google_layout(self):
        """Create Google-style layout."""
        self.grid_columnconfigure(0, weight=1)

        # Main content frame
        content_frame = tk.Frame(self, bg='white')
        content_frame.grid(row=0, column=0, sticky='nsew', padx=24, pady=12)
        content_frame.grid_columnconfigure(0, weight=1)

        # Title (Blue, clickable) - GOOGLE STYLE
        title_label = tk.Label(
            content_frame,
            text=self.filename,
            font=('Arial', 18, 'normal'),
            fg='#1a0dab',  # Google result blue
            bg='white',
            cursor='hand2',
            anchor='w'
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(0, 2))

        # Hover effects
        def title_enter(e):
            title_label.config(font=('Arial', 18, 'underline'))
        def title_leave(e):
            title_label.config(font=('Arial', 18, 'normal'))
        def title_click(e):
            if self.on_view:
                self.on_view(self.filename)

        title_label.bind('<Enter>', title_enter)
        title_label.bind('<Leave>', title_leave)
        title_label.bind('<Button-1>', title_click)

        # URL line (Green) - GOOGLE STYLE
        url_label = tk.Label(
            content_frame,
            text=f"📄 Document ID: {self.filename}",
            font=('Arial', 12, 'normal'),
            fg='#006621',  # Google URL green
            bg='white',
            anchor='w'
        )
        url_label.grid(row=1, column=0, sticky='ew', pady=(0, 4))

        # Description (Gray) - GOOGLE STYLE
        snippet_parts = [f"Document contains {self.word_count} words"]
        if self.relevance_score > 0:
            snippet_parts.append(f"Relevance score: {self.relevance_score:.3f}")
        snippet_text = " • ".join(snippet_parts)

        snippet_label = tk.Label(
            content_frame,
            text=snippet_text,
            font=('Arial', 13, 'normal'),
            fg='#545454',  # Google description gray
            bg='white',
            anchor='w',
            wraplength=600
        )
        snippet_label.grid(row=2, column=0, sticky='ew', pady=(0, 8))

        # Action buttons
        actions_frame = tk.Frame(content_frame, bg='white')
        actions_frame.grid(row=3, column=0, sticky='w')

        view_btn = tk.Button(
            actions_frame,
            text='📖 View Content',
            font=('Arial', 11, 'normal'),
            bg='#f8f9fa',
            fg='#3c4043',
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=lambda: self.on_view(self.filename) if self.on_view else None
        )
        view_btn.pack(side=tk.LEFT)

        # Star badge for high scores
        if self.relevance_score > 0.5:
            score_badge = tk.Label(
                actions_frame,
                text=f'⭐ {self.relevance_score:.2f}',
                font=('Arial', 11, 'normal'),
                fg='#ea4335',  # Google red
                bg='white'
            )
            score_badge.pack(side=tk.LEFT, padx=(10, 0))


class GuiApp:
    """Google-style search engine GUI."""

    def __init__(self, zip_path: str = "Jan.zip"):
        self.zip_path = zip_path
        self.indexer: Optional[HtmlIndexer] = None
        self.query_processor: Optional[QueryProcessor] = None
        self.is_initialized = False
        self.current_results: List[QueryResult] = []

        self._create_main_window()
        self._create_ui()
        self._start_initialization()
        
    def _create_main_window(self):
        """Create and configure the main application window."""
        self.root = tk.Tk()
        self.root.title("HTML Search Engine - Google Style")
        self.root.geometry("1000x700")
        self.root.configure(bg='white')

        # Configure main grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
    def _create_ui(self):
        """Create the Google-style UI."""
        # Header
        header_frame = tk.Frame(self.root, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=(20, 10))

        title_label = tk.Label(
            header_frame,
            text="🔍 HTML Search Engine",
            font=('Arial', 24, 'bold'),
            fg='#202124',
            bg='white'
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Google-Style Search Results",
            font=('Arial', 14, 'normal'),
            fg='#5f6368',
            bg='white'
        )
        subtitle_label.pack()

        # Search section
        search_frame = tk.Frame(self.root, bg='white')
        search_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 20))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = tk.Entry(
            search_frame,
            font=('Arial', 14),
            width=50,
            relief='solid',
            bd=1
        )
        self.search_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        self.search_entry.bind('<Return>', self._on_search)

        search_btn = tk.Button(
            search_frame,
            text='🔍 Search',
            font=('Arial', 12, 'bold'),
            bg='#4285f4',  # Google blue color
            fg='white',
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._on_search
        )
        search_btn.grid(row=0, column=1)

        # Results area with scrolling
        self.results_canvas = tk.Canvas(self.root, bg='white')
        scrollbar = tk.Scrollbar(self.root, orient='vertical', command=self.results_canvas.yview)
        self.results_frame = tk.Frame(self.results_canvas, bg='white')

        self.results_frame.bind(
            '<Configure>',
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox('all'))
        )

        self.results_canvas.create_window((0, 0), window=self.results_frame, anchor='nw')
        self.results_canvas.configure(yscrollcommand=scrollbar.set)

        self.results_canvas.grid(row=2, column=0, sticky='nsew', padx=(20, 0))
        scrollbar.grid(row=2, column=1, sticky='ns', padx=(0, 20))

        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)

        # Initial message
        self.status_label = tk.Label(
            self.results_frame,
            text="Initializing search engine...",
            font=('Arial', 12),
            fg='#666666',
            bg='white'
        )
        self.status_label.pack(pady=50)

    def _start_initialization(self):
        """Initialize search engine in background."""
        def init_worker():
            try:
                print("🔄 Initializing search engine...")
                self.indexer = HtmlIndexer(self.zip_path)
                self.indexer.build_index()
                self.query_processor = QueryProcessor(self.indexer)
                self.is_initialized = True

                # Update UI
                self.root.after(0, self._on_init_complete)
            except Exception as e:
                self.root.after(0, lambda: self._on_init_error(str(e)))

        thread = threading.Thread(target=init_worker, daemon=True)
        thread.start()

    def _on_init_complete(self):
        """Called when initialization completes."""
        self.status_label.config(
            text='✅ Ready! Try searching for:\n• "web page"\n• "rhf joke"\n• "legal advice"',
            justify=tk.CENTER
        )
        print("✅ Search engine ready!")

    def _on_init_error(self, error):
        """Called when initialization fails."""
        self.status_label.config(
            text=f"❌ Error: {error}",
            fg='red'
        )

    def _on_search(self, event=None):
        """Handle search requests."""
        if not self.is_initialized:
            return

        query = self.search_entry.get().strip()
        if not query:
            return

        print(f"🔍 Searching for: {query}")

        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Perform search
        try:
            self.current_results = self.query_processor.process_query(query)

            # Results header
            header = tk.Label(
                self.results_frame,
                text=f'Found {len(self.current_results)} matches for "{query}"',
                font=('Arial', 16, 'normal'),
                fg='#202124',
                bg='white'
            )
            header.pack(anchor='w', padx=20, pady=(20, 15))

            # Create Google-style cards
            for i, result in enumerate(self.current_results):
                filename = result.doc_id
                score = result.score
                word_count = len(self.indexer.get_words_in_file(filename) or set())

                card = GoogleResultCard(
                    self.results_frame,
                    filename=filename,
                    word_count=word_count,
                    relevance_score=score,
                    on_view=self._view_file
                )

                # Stack vertically - GOOGLE STYLE
                card.pack(fill=tk.X, pady=(0, 8))

            print(f"✅ Displayed {len(self.current_results)} Google-style cards")

            # Update scroll region
            self.results_frame.update_idletasks()
            self.results_canvas.configure(scrollregion=self.results_canvas.bbox('all'))

        except Exception as e:
            error_label = tk.Label(
                self.results_frame,
                text=f"Search error: {e}",
                font=('Arial', 12),
                fg='red',
                bg='white'
            )
            error_label.pack(pady=50)

    def _view_file(self, filename):
        """Handle file view requests."""
        try:
            # Read file content from zip
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                original_path = self.indexer.get_original_path(filename)
                if original_path:
                    zip_filename = original_path.replace('./', '')
                else:
                    zip_filename = filename.replace('./', '')

                with zip_ref.open(zip_filename) as file:
                    content = file.read().decode('utf-8', errors='ignore')

            # Simple content dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Content: {filename}")
            dialog.geometry("800x600")
            dialog.configure(bg='white')

            # Header
            header_frame = tk.Frame(dialog, bg='white')
            header_frame.pack(fill=tk.X, padx=20, pady=20)

            title_label = tk.Label(
                header_frame,
                text=f"📄 {filename}",
                font=('Arial', 16, 'bold'),
                bg='white',
                fg='#202124'
            )
            title_label.pack(side=tk.LEFT)

            close_btn = tk.Button(
                header_frame,
                text="❌ Close",
                command=dialog.destroy,
                font=('Arial', 12),
                bg='#f8f9fa',
                relief='flat',
                padx=15,
                pady=5
            )
            close_btn.pack(side=tk.RIGHT)

            # Content
            text_widget = scrolledtext.ScrolledText(
                dialog,
                wrap=tk.WORD,
                font=('Arial', 11),
                bg='#f8f9fa',
                fg='#202124'
            )
            text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

            # Insert content and highlight search terms
            text_widget.insert(tk.END, content)

            # Configure highlighting tag
            text_widget.tag_configure(
                'highlight',
                background='#ffeb3b',  # Yellow highlight
                foreground='#000000'
            )

            # Highlight search terms
            if hasattr(self, 'search_entry') and self.search_entry.get().strip():
                original_query = self.search_entry.get().strip()
                content_lower = content.lower()

                # Extract terms to highlight based on query type
                terms_to_highlight = []

                # Handle quoted phrases like "web page"
                if original_query.startswith('"') and original_query.endswith('"'):
                    # For quoted phrases, ONLY highlight the exact phrase
                    phrase = original_query.strip('"').lower()
                    terms_to_highlight = [phrase]  # Only the full phrase, not individual words
                else:
                    # For regular searches, split on spaces
                    terms_to_highlight = [term.lower() for term in original_query.split() if term.strip()]

                # Highlight each term
                for search_term in terms_to_highlight:
                    if not search_term:
                        continue

                    start_pos = 0
                    while True:
                        pos = content_lower.find(search_term, start_pos)
                        if pos == -1:
                            break

                        # Convert position to line.char format for tkinter
                        lines_before = content[:pos].count('\n')
                        char_in_line = pos - content[:pos].rfind('\n') - 1
                        if char_in_line < 0:  # First line
                            char_in_line = pos

                        start_index = f"{lines_before + 1}.{char_in_line}"
                        end_index = f"{lines_before + 1}.{char_in_line + len(search_term)}"

                        text_widget.tag_add('highlight', start_index, end_index)
                        start_pos = pos + 1

            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load file content:\n\n{str(e)}")

    def run(self):
        """Run the GUI application."""
        print("🚀 GOOGLE-STYLE GUI STARTING")
        print("=" * 50)
        print("✅ Clean implementation with Google-style cards")
        print("✅ Blue clickable titles")
        print("✅ Green document URLs")
        print("✅ Gray description text")
        print("✅ Vertical stacking layout")
        print("✅ Star badges for high scores")
        print()
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    app = GuiApp("Jan.zip")
    app.run()


if __name__ == "__main__":
    main()