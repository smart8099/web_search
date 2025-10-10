"""
Reusable GUI Components for HTML Search Engine

This module contains custom Tkinter components and widgets that provide
enhanced functionality and consistent styling throughout the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable, Optional, List, Dict, Any
from gui_styles import COLORS, FONTS, SIZES, SPACING, ICONS, get_font, get_spacing


class SearchEntry(ttk.Frame):
    """
    Custom search entry widget with placeholder text and search button.
    """
    
    def __init__(self, parent, placeholder: str = "Search for terms...", 
                 on_search: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.on_search = on_search
        self.has_focus = False
        
        self._create_widgets()
        self._setup_bindings()
        
    def _create_widgets(self):
        """Create the search entry and button widgets."""
        # Search entry
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(
            self, 
            textvariable=self.entry_var,
            style='SearchEntry.TEntry',
            font=get_font('body'),
            width=50
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, get_spacing('sm')))
        
        # Search button with centered icon - using tk.Button with white background
        self.search_btn = tk.Button(
            self,
            text=f" {ICONS['search']} Search ",
            command=self._on_search_clicked,
            bg='white',
            fg='black',
            font=get_font('button', 'medium'),
            relief='solid',
            bd=1,
            padx=12,
            pady=8,
            cursor='hand2',
            activebackground=COLORS['card_hover'],
            activeforeground='black'
        )
        self.search_btn.pack(side=tk.RIGHT, padx=(get_spacing('sm'), 0))
        
        # Set placeholder initially
        self._show_placeholder()
        
    def _setup_bindings(self):
        """Setup event bindings for the search entry."""
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_enter_pressed)
        self.entry.bind('<KeyPress>', self._on_key_press)
        self.entry.bind('<Button-1>', self._on_click)
        
    def _show_placeholder(self):
        """Show placeholder text in the entry."""
        if not self.has_focus and not self.entry_var.get():
            self.entry.config(foreground=COLORS['text_hint'])
            self.entry_var.set(self.placeholder)
            
    def _hide_placeholder(self):
        """Hide placeholder text when user focuses the entry."""
        if not self.has_focus and self.entry_var.get() == self.placeholder:
            self.entry.config(foreground=COLORS['text_primary'])
            self.entry_var.set('')
            
    def _on_focus_in(self, event):
        """Handle focus in event."""
        self.has_focus = True
        self._hide_placeholder()
        
    def _on_focus_out(self, event):
        """Handle focus out event."""
        self.has_focus = False
        self._show_placeholder()
        
    def _on_enter_pressed(self, event):
        """Handle Enter key press."""
        self._on_search_clicked()
        
    def _on_click(self, event):
        """Handle mouse click on entry."""
        self._clear_placeholder_if_needed()
        
    def _on_key_press(self, event):
        """Handle key press events."""
        # Clear placeholder immediately when user starts typing
        self._clear_placeholder_if_needed()
        
    def _clear_placeholder_if_needed(self):
        """Clear placeholder if it's currently shown."""
        if self.entry_var.get() == self.placeholder:
            self.entry.config(foreground=COLORS['text_primary'], font=get_font('body', 'bold'))
            self.entry_var.set('')
            self.has_focus = True
            
    def _on_search_clicked(self):
        """Handle search button click."""
        search_term = self.get_search_term()
        if search_term and self.on_search:
            self.on_search(search_term)
            
    def get_search_term(self) -> str:
        """Get the current search term, excluding placeholder."""
        current_text = self.entry_var.get().strip()
        if current_text == self.placeholder:
            return ''
        return current_text
        
    def set_search_term(self, term: str):
        """Set the search term programmatically."""
        self.entry.config(foreground=COLORS['text_primary'], font=get_font('body', 'bold'))
        self.entry_var.set(term)
        self.has_focus = True
        
    def clear(self):
        """Clear the search entry."""
        self.entry_var.set('')
        self.has_focus = False
        self._show_placeholder()
        
    def focus(self):
        """Set focus to the search entry."""
        self.entry.focus_set()


class ResultCard(tk.Frame):
    """
    Google-style result card for displaying search result information.

    Features:
    - Blue clickable titles like Google search results
    - Green document URLs
    - Gray description snippets
    - Horizontal layout with proper spacing
    - Star badges for high relevance scores
    """

    def __init__(self, parent, filename: str, word_count: int,
                 relevance_score: float = 0.0,
                 on_view: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, bg='white', relief='flat', **kwargs)

        self.filename = filename
        self.word_count = word_count
        self.relevance_score = relevance_score
        self.on_view = on_view

        self._create_google_style_layout()

    def _create_google_style_layout(self):
        """Create Google-style horizontal card layout."""
        self.grid_columnconfigure(0, weight=1)

        # Main content frame with proper Google-style padding
        content_frame = tk.Frame(self, bg='white')
        content_frame.grid(row=0, column=0, sticky='nsew', padx=24, pady=12)
        content_frame.grid_columnconfigure(0, weight=1)

        # Document title - Google-style blue clickable link
        title_text = self._format_filename(self.filename)
        self.title_label = tk.Label(
            content_frame,
            text=title_text,
            font=('Arial', 18, 'normal'),
            fg='#1a0dab',  # Google search result blue
            bg='white',
            cursor='hand2',
            anchor='w'
        )
        self.title_label.grid(row=0, column=0, sticky='ew', pady=(0, 2))
        self.title_label.bind('<Button-1>', lambda e: self._on_view_clicked())

        # Title hover effects - Google style underline
        def title_enter(e):
            self.title_label.config(font=('Arial', 18, 'underline'))
        def title_leave(e):
            self.title_label.config(font=('Arial', 18, 'normal'))

        self.title_label.bind('<Enter>', title_enter)
        self.title_label.bind('<Leave>', title_leave)

        # Document URL line - Google-style green
        url_label = tk.Label(
            content_frame,
            text=f"📄 Document ID: {self.filename}",
            font=('Arial', 12, 'normal'),
            fg='#006621',  # Google URL green
            bg='white',
            anchor='w'
        )
        url_label.grid(row=1, column=0, sticky='ew', pady=(0, 4))

        # Description snippet - Google-style gray
        snippet_parts = [f"Document contains {self.word_count} words"]
        if self.relevance_score > 0:
            score_text = f"Relevance score: {self.relevance_score:.3f}" if self.relevance_score < 1.0 else f"Relevance score: {self.relevance_score:.2f}"
            snippet_parts.append(score_text)
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

        # Action buttons - Google-style inline actions
        actions_frame = tk.Frame(content_frame, bg='white')
        actions_frame.grid(row=3, column=0, sticky='w')

        # View Content button - Google-style subtle design
        self.view_btn = tk.Button(
            actions_frame,
            text="📖 View Content",
            command=self._on_view_clicked,
            bg='#f8f9fa',  # Google button background
            fg='#3c4043',  # Google button text
            font=('Arial', 11, 'normal'),
            relief='flat',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2'
        )
        self.view_btn.pack(side=tk.LEFT)

        # Star badge for high scores - Google-style accent
        if self.relevance_score > 0.5:
            score_badge = tk.Label(
                actions_frame,
                text=f"⭐ {self.relevance_score:.2f}",
                font=('Arial', 11, 'normal'),
                fg='#ea4335',  # Google red accent
                bg='white'
            )
            score_badge.pack(side=tk.LEFT, padx=(10, 0))
        
    def _format_filename(self, filename: str) -> str:
        """Format filename for display, truncating if necessary."""
        # The filename is now in format: filename1234 (already clean)
        display_name = filename

        # Truncate if too long (though random IDs should be short)
        max_length = 25
        if len(display_name) > max_length:
            display_name = display_name[:max_length-3] + '...'

        return display_name
        
    def _setup_hover_effects(self):
        """Hover effects are handled by individual components in the Google-style layout."""
        # Title hover effects are already set up in _create_google_style_layout
        # No additional hover effects needed for the card frame
        pass
            
    def _on_view_clicked(self):
        """Handle view button click."""
        if self.on_view:
            self.on_view(self.filename)


class StatsPanel(ttk.Frame):
    """
    Statistics display panel showing indexing and search information.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.stats = {
            'files_count': 0,
            'vocabulary_size': 0,
            'current_results': 0,
            'last_search': ''
        }
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the statistics display widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            self,
            text=f"{ICONS['stats']} Statistics",
            font=get_font('subheading', 'medium'),
            style='Heading.TLabel'
        )
        title_label.grid(row=0, column=0, sticky='w', pady=(0, get_spacing('md')))
        
        # Statistics labels
        self.files_label = ttk.Label(
            self,
            text="Files: Loading...",
            font=get_font('body'),
            style='Stats.TLabel'
        )
        self.files_label.grid(row=1, column=0, sticky='w', pady=get_spacing('xs'))
        
        self.vocab_label = ttk.Label(
            self,
            text="Vocabulary: Loading...",
            font=get_font('body'),
            style='Stats.TLabel'
        )
        self.vocab_label.grid(row=2, column=0, sticky='w', pady=get_spacing('xs'))
        
        self.results_label = ttk.Label(
            self,
            text="Last search: None",
            font=get_font('body'),
            style='Stats.TLabel'
        )
        self.results_label.grid(row=3, column=0, sticky='w', pady=get_spacing('xs'))
        
    def update_stats(self, **kwargs):
        """Update statistics with new values."""
        self.stats.update(kwargs)
        
        # Update labels
        self.files_label.config(text=f"Files: {self.stats['files_count']}")
        self.vocab_label.config(text=f"Vocabulary: {self.stats['vocabulary_size']:,}")
        
        if self.stats['last_search']:
            results_text = f"'{self.stats['last_search']}': {self.stats['current_results']} matches"
        else:
            results_text = "Last search: None"
            
        self.results_label.config(text=results_text)


class LoadingLabel(ttk.Label):
    """
    Animated loading label with rotating indicator.
    """
    
    def __init__(self, parent, text: str = "Loading", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.base_text = text
        self.animation_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.animation_index = 0
        self.animation_active = False
        self.animation_job = None
        
    def start_animation(self):
        """Start the loading animation."""
        self.animation_active = True
        self._animate()
        
    def stop_animation(self, final_text: str = None):
        """Stop the loading animation."""
        self.animation_active = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            
        if final_text:
            self.config(text=final_text)
        else:
            self.config(text=self.base_text)
            
    def _animate(self):
        """Animate the loading indicator."""
        if not self.animation_active:
            return
            
        char = self.animation_chars[self.animation_index]
        self.config(text=f"{char} {self.base_text}...")
        
        self.animation_index = (self.animation_index + 1) % len(self.animation_chars)
        self.animation_job = self.after(100, self._animate)


class FileContentDialog:
    """
    Dialog for displaying HTML file content with search term highlighting.
    """

    def __init__(self, parent, filename: str, content: str, search_term: str = '', highlight_terms: List[str] = None):
        self.parent = parent
        self.filename = filename
        self.content = content
        self.search_term = search_term.lower()
        self.highlight_terms = highlight_terms or [search_term.lower()] if search_term else []

        self._create_dialog()

    def _create_dialog(self):
        """Create the content dialog window."""
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Content: {self.filename}")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='white')

        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)

        # Header frame
        header_frame = tk.Frame(self.dialog, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f"📄 {self.filename}",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#202124'
        )
        title_label.grid(row=0, column=0, sticky='w')

        # Close button
        close_btn = tk.Button(
            header_frame,
            text="❌ Close",
            command=self.dialog.destroy,
            font=('Arial', 12),
            bg='#f8f9fa',
            relief='flat',
            padx=15,
            pady=5
        )
        close_btn.grid(row=0, column=1, sticky='e')

        # Content area
        content_frame = tk.Frame(self.dialog, bg='white')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Text widget with scrollbar
        self.text_widget = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#f8f9fa',
            fg='#202124',
            selectbackground='#4285f4',
            selectforeground='white',
            relief='solid',
            bd=1
        )
        self.text_widget.grid(row=0, column=0, sticky='nsew')

        # Insert content
        self._insert_content()

        # Center the dialog
        self.dialog.update_idletasks()
        self._center_dialog()
        
    def _insert_content(self):
        """Insert and highlight content in the text widget."""
        self.text_widget.insert(tk.END, self.content)

        # Configure highlighting tag
        self.text_widget.tag_configure(
            'highlight',
            background='#ffeb3b',
            foreground='#000000'
        )
        
        # Highlight search terms if provided
        if self.highlight_terms:
            self._highlight_search_terms()
            
        # Make text widget read-only
        self.text_widget.config(state=tk.DISABLED)
        
    def _highlight_search_terms(self):
        """Highlight all instances of the search terms."""
        import re

        content_lower = self.content.lower()

        # Clean and prepare highlight terms
        terms_to_highlight = []
        for term in self.highlight_terms:
            if term and term.strip():
                clean_term = term.strip().lower()
                # Remove quotes and special characters from phrase searches
                clean_term = clean_term.strip('"\'')
                if clean_term:
                    terms_to_highlight.append(clean_term)

        if not terms_to_highlight:
            return

        # Create regex pattern for word boundaries to avoid partial matches
        # Escape special regex characters in search terms
        escaped_terms = [re.escape(term) for term in terms_to_highlight]
        pattern = r'\b(?:' + '|'.join(escaped_terms) + r')\b'

        try:
            # Find all matches
            for match in re.finditer(pattern, content_lower, re.IGNORECASE):
                start_pos = match.start()
                end_pos = match.end()

                # Convert to Tkinter text indices
                line_start = self.content.count('\n', 0, start_pos) + 1
                col_start = start_pos - self.content.rfind('\n', 0, start_pos) - 1
                col_end = col_start + (end_pos - start_pos)

                start_index = f"{line_start}.{col_start}"
                end_index = f"{line_start}.{col_end}"

                self.text_widget.tag_add('highlight', start_index, end_index)

        except re.error:
            # Fallback to simple string search if regex fails
            for term in terms_to_highlight:
                self._highlight_single_term(term)

    def _highlight_single_term(self, term: str):
        """Fallback method to highlight a single term using simple string search."""
        content_lower = self.content.lower()
        start_pos = 0

        while True:
            pos = content_lower.find(term.lower(), start_pos)
            if pos == -1:
                break

            # Convert to Tkinter text indices
            line_start = self.content.count('\n', 0, pos) + 1
            col_start = pos - self.content.rfind('\n', 0, pos) - 1
            col_end = col_start + len(term)

            start_index = f"{line_start}.{col_start}"
            end_index = f"{line_start}.{col_end}"

            self.text_widget.tag_add('highlight', start_index, end_index)
            start_pos = pos + 1
            
    def _center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


class ScrollableFrame(ttk.Frame):
    """
    Scrollable frame for containing result cards and other content.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=COLORS['background'],
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Bind mousewheel scrolling
        self._bind_mousewheel()
        
    def _bind_mousewheel(self):
        """Bind mousewheel scrolling to the canvas."""
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            
        def bind_to_mousewheel(event):
            self.canvas.bind_all('<MouseWheel>', on_mousewheel)
            
        def unbind_from_mousewheel(event):
            self.canvas.unbind_all('<MouseWheel>')
            
        self.canvas.bind('<Enter>', bind_to_mousewheel)
        self.canvas.bind('<Leave>', unbind_from_mousewheel)
        
    def clear_content(self):
        """Clear all content from the scrollable frame."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
    def add_widget(self, widget, **grid_kwargs):
        """Add a widget to the scrollable frame."""
        widget.grid(in_=self.scrollable_frame, **grid_kwargs)
        
    def scroll_to_top(self):
        """Scroll to the top of the frame."""
        self.canvas.yview_moveto(0)