"""
GUI Application for HTML Search Engine

This module provides the main graphical user interface for the HTML search engine,
featuring a dynamic layout that transitions from centered search to results view.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import zipfile
from typing import Optional, List, Dict, Any
from html_indexer import HtmlIndexer
from gui_styles import (
    COLORS, SIZES, SPACING, ICONS, LAYOUTS, TTK_STYLES,
    get_font, get_spacing, apply_ttk_styles
)
from gui_components import (
    SearchEntry, ResultCard, StatsPanel, LoadingLabel, 
    FileContentDialog, ScrollableFrame
)


class GuiApp:
    """
    Main GUI application class for the HTML Search Engine.
    
    This class manages the dynamic interface that transforms from a centered
    search view to a results display with card-based layout.
    """
    
    def __init__(self, zip_path: str = "Jan.zip"):
        """
        Initialize the GUI application.
        
        Args:
            zip_path: Path to the zip file containing HTML files
        """
        self.zip_path = zip_path
        self.indexer: Optional[HtmlIndexer] = None
        self.is_initialized = False
        self.current_search_term = ""
        self.current_results: List[str] = []
        
        # UI state management
        self.search_mode = "center"  # "center" or "top"
        self.widgets = {}
        
        self._create_main_window()
        self._setup_styles()
        self._create_ui()
        self._start_initialization()
        
    def _create_main_window(self):
        """Create and configure the main application window."""
        self.root = tk.Tk()
        self.root.title("HTML Search Engine")
        self.root.configure(bg=COLORS['background'])
        
        # Set window size and minimum size
        self.root.geometry(f"{SIZES['window_default_width']}x{SIZES['window_default_height']}")
        self.root.minsize(SIZES['window_min_width'], SIZES['window_min_height'])
        
        # Center the window on screen
        self._center_window()
        
        # Configure main grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
    def _center_window(self):
        """Center the main window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def _setup_styles(self):
        """Setup TTK styles for the application."""
        self.style = ttk.Style()
        
        # Apply custom styles
        apply_ttk_styles(self.style)
        
        # Add hover effect for cards
        self.style.configure(
            'CardHover.TFrame',
            background=COLORS['card_hover'],
            bordercolor=COLORS['border_focus'],
            relief='solid',
            borderwidth=1
        )
        
    def _create_ui(self):
        """Create the main user interface."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=get_spacing('lg'), pady=get_spacing('lg'))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create initial centered layout
        self._create_center_layout()
        
    def _create_center_layout(self):
        """Create the initial centered search layout."""
        # Center container
        center_frame = ttk.Frame(self.main_frame)
        center_frame.grid(row=0, column=0, sticky='nsew')
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)
        
        # Content frame (centered)
        content_frame = ttk.Frame(center_frame)
        content_frame.grid(row=0, column=0)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            content_frame,
            text="HTML Search Engine",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, pady=(0, get_spacing('xxl')))
        
        # Search entry
        self.widgets['search_entry'] = SearchEntry(
            content_frame,
            placeholder="Search for terms...",
            on_search=self._on_search
        )
        self.widgets['search_entry'].grid(row=1, column=0, sticky='ew', pady=(0, get_spacing('lg')))
        
        # Loading label
        self.widgets['loading_label'] = LoadingLabel(
            content_frame,
            text="Initializing search engine",
            font=get_font('body'),
            foreground=COLORS['text_secondary']
        )
        self.widgets['loading_label'].grid(row=2, column=0, pady=(0, get_spacing('md')))
        
        # Stats panel
        self.widgets['stats_panel'] = StatsPanel(content_frame)
        self.widgets['stats_panel'].grid(row=3, column=0, pady=get_spacing('lg'))
        
        # Initially disable search
        self.widgets['search_entry'].search_btn.config(state='disabled')
        
        # Store references for layout switching
        self.center_frame = center_frame
        self.content_frame = content_frame
        
    def _create_results_layout(self):
        """Create the results layout with search at top."""
        # Clear center layout
        self.center_frame.destroy()
        
        # Create top layout
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, sticky='nsew')
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)
        
        # Top bar with search and stats
        top_bar = ttk.Frame(top_frame)
        top_bar.grid(row=0, column=0, sticky='ew', pady=(0, get_spacing('lg')))
        top_bar.grid_columnconfigure(0, weight=1)
        
        # Search section
        search_frame = ttk.Frame(top_bar)
        search_frame.grid(row=0, column=0, sticky='w')
        
        # Create new search entry for results view
        self.widgets['results_search_entry'] = SearchEntry(
            search_frame,
            placeholder="Search for terms...",
            on_search=self._on_search
        )
        self.widgets['results_search_entry'].pack(side=tk.LEFT)
        
        # Set current search term
        if self.current_search_term:
            self.widgets['results_search_entry'].set_search_term(self.current_search_term)
            
        # Stats section (top right)
        stats_frame = ttk.Frame(top_bar)
        stats_frame.grid(row=0, column=1, sticky='e')
        
        # Compact stats display
        self._create_compact_stats(stats_frame)
        
        # Results header
        results_header = ttk.Frame(top_frame)
        results_header.grid(row=1, column=0, sticky='ew', pady=(0, get_spacing('md')))
        results_header.grid_columnconfigure(0, weight=1)
        
        # Results title (store reference for real-time updates)
        results_count = len(self.current_results)
        if results_count > 0:
            header_text = f"{ICONS['results']} Found {results_count} matches for \"{self.current_search_term}\""
            header_color = COLORS['success']
        else:
            header_text = f"{ICONS['error']} No matches found for \"{self.current_search_term}\""
            header_color = COLORS['error']
            
        self.widgets['results_title'] = ttk.Label(
            results_header,
            text=header_text,
            font=get_font('heading', 'medium'),
            foreground=header_color
        )
        self.widgets['results_title'].grid(row=0, column=0, sticky='w')
        
        # Clear button
        clear_btn = ttk.Button(
            results_header,
            text="New Search",
            command=self._clear_results
        )
        clear_btn.grid(row=0, column=1, sticky='e')
        
        # Results area
        self.widgets['results_frame'] = ScrollableFrame(top_frame)
        self.widgets['results_frame'].grid(row=2, column=0, sticky='nsew')
        
        # Populate results
        self._populate_results()
        
        # Update search mode
        self.search_mode = "top"
        
    def _create_compact_stats(self, parent):
        """Create compact statistics display for results view."""
        stats_text = f"{ICONS['stats']} {self.indexer.get_file_count()} files | {self.indexer.get_vocabulary_size():,} words"
        
        stats_label = ttk.Label(
            parent,
            text=stats_text,
            font=get_font('caption'),
            foreground=COLORS['text_secondary']
        )
        stats_label.pack()
        
    def _populate_results(self):
        """Populate the results area with result cards."""
        if not self.current_results:
            # Show no results message
            no_results_frame = ttk.Frame(self.widgets['results_frame'].scrollable_frame)
            no_results_frame.grid(row=0, column=0, padx=get_spacing('xl'), pady=get_spacing('xxl'))
            
            no_results_label = ttk.Label(
                no_results_frame,
                text=f"No files contain the term \"{self.current_search_term}\"\n\nTry a different search term or check your spelling.",
                font=get_font('body'),
                foreground=COLORS['text_secondary'],
                justify=tk.CENTER
            )
            no_results_label.pack()
            
            return
            
        # Calculate grid layout
        columns = min(LAYOUTS['results_grid']['columns'], len(self.current_results))
        if len(self.current_results) > 6:
            columns = LAYOUTS['results_grid']['max_columns']
            
        # Create result cards
        for i, filename in enumerate(self.current_results):
            row = i // columns
            col = i % columns
            
            # Get word count for this file
            word_count = len(self.indexer.get_words_in_file(filename) or set())
            
            # Create card
            card = ResultCard(
                self.widgets['results_frame'].scrollable_frame,
                filename=filename,
                word_count=word_count,
                on_view=self._on_view_file
            )
            
            card.grid(
                row=row, 
                column=col, 
                padx=get_spacing('sm'),
                pady=get_spacing('sm'),
                sticky='ew'
            )
            
        # Configure grid weights for equal column widths
        for col in range(columns):
            self.widgets['results_frame'].scrollable_frame.grid_columnconfigure(col, weight=1)
            
    def _start_initialization(self):
        """Start the background initialization process."""
        self.widgets['loading_label'].start_animation()
        
        def initialize_indexer():
            try:
                self.indexer = HtmlIndexer(self.zip_path)
                self.indexer.build_index()
                
                # Update UI on main thread
                self.root.after(0, self._on_initialization_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self._on_initialization_error(str(e)))
                
        # Start initialization in background thread
        init_thread = threading.Thread(target=initialize_indexer, daemon=True)
        init_thread.start()
        
    def _on_initialization_complete(self):
        """Handle successful initialization."""
        self.is_initialized = True
        
        # Stop loading animation
        self.widgets['loading_label'].stop_animation("Ready to search!")
        
        # Enable search
        self.widgets['search_entry'].search_btn.config(state='normal')
        self.widgets['search_entry'].focus()
        
        # Update stats safely
        stats_panel = self.widgets.get('stats_panel')
        if stats_panel and hasattr(stats_panel, 'update_stats'):
            try:
                stats_panel.update_stats(
                    files_count=self.indexer.get_file_count(),
                    vocabulary_size=self.indexer.get_vocabulary_size()
                )
            except tk.TclError:
                # Widget was destroyed, ignore the error
                pass
        
    def _on_initialization_error(self, error_message: str):
        """Handle initialization error."""
        self.widgets['loading_label'].stop_animation("Initialization failed")
        
        messagebox.showerror(
            "Initialization Error",
            f"Failed to initialize search engine:\n\n{error_message}\n\nPlease check that Jan.zip exists."
        )
        
    def _on_search(self, search_term: str):
        """Handle search request."""
        if not self.is_initialized:
            messagebox.showwarning("Not Ready", "Search engine is still initializing. Please wait.")
            return
            
        if not search_term.strip():
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return
            
        # Perform search
        self.current_search_term = search_term
        self.current_results = self.indexer.search_word(search_term) or []
        
        # Switch to results layout if in center mode
        if self.search_mode == "center":
            self._create_results_layout()
        else:
            # Update existing results
            self._update_results_display()
            
        # Update stats after layout is created/updated
        self._update_stats_if_available(search_term)
            
    def _update_results_display(self):
        """Update the results display with new search results."""
        # Clear existing results
        self.widgets['results_frame'].clear_content()
        
        # Update header text and color in real-time
        results_count = len(self.current_results)
        if results_count > 0:
            header_text = f"{ICONS['results']} Found {results_count} matches for \"{self.current_search_term}\""
            header_color = COLORS['success']
        else:
            header_text = f"{ICONS['error']} No matches found for \"{self.current_search_term}\""
            header_color = COLORS['error']
            
        # Update the results title widget in real-time
        if 'results_title' in self.widgets:
            try:
                self.widgets['results_title'].config(text=header_text, foreground=header_color)
            except tk.TclError:
                # Widget was destroyed, ignore error
                pass
        
        # Repopulate results
        self._populate_results()
        
        # Scroll to top
        self.widgets['results_frame'].scroll_to_top()
        
    def _update_stats_if_available(self, search_term: str):
        """Update stats panel if it exists and is valid."""
        stats_panel = self.widgets.get('stats_panel')
        if stats_panel and hasattr(stats_panel, 'update_stats'):
            try:
                stats_panel.update_stats(
                    last_search=search_term,
                    current_results=len(self.current_results)
                )
            except tk.TclError:
                # Widget was destroyed, ignore the error
                pass
        
    def _on_view_file(self, filename: str):
        """Handle file content view request."""
        try:
            # Read file content from zip
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # Remove ./ prefix for zip file access
                zip_filename = filename.replace('./', '')
                with zip_ref.open(zip_filename) as file:
                    content = file.read().decode('utf-8', errors='ignore')
                    
            # Show content dialog
            FileContentDialog(
                self.root,
                filename=filename,
                content=content,
                search_term=self.current_search_term
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not load file content:\n\n{str(e)}"
            )
            
    def _clear_results(self):
        """Clear results and return to center search mode."""
        self.current_search_term = ""
        self.current_results = []
        self.search_mode = "center"
        
        # Recreate center layout
        self.main_frame.destroy()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=get_spacing('lg'), pady=get_spacing('lg'))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self._create_center_layout()
        
        # Update initialization status
        if self.is_initialized:
            self._on_initialization_complete()
            
    def run(self):
        """Run the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()
            
    def quit(self):
        """Quit the application."""
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point for the GUI application."""
    app = GuiApp("Jan.zip")
    app.run()


if __name__ == "__main__":
    main()