"""
Unit tests for GUI components and application

Tests the GUI functionality including components, layout transitions,
and user interactions using mocked backends.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui_components import SearchEntry, ResultCard, StatsPanel, LoadingLabel, ScrollableFrame
from gui_styles import COLORS, FONTS, SIZES
from html_indexer import HtmlIndexer


class TestSearchEntry(unittest.TestCase):
    """Test cases for SearchEntry component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    def test_search_entry_initialization(self):
        """Test SearchEntry initialization."""
        search_entry = SearchEntry(self.root, placeholder="Test placeholder")
        
        self.assertIsInstance(search_entry, ttk.Frame)
        self.assertEqual(search_entry.placeholder, "Test placeholder")
        self.assertFalse(search_entry.has_focus)
        
    def test_placeholder_functionality(self):
        """Test placeholder text behavior."""
        search_entry = SearchEntry(self.root, placeholder="Search here...")
        
        # Initially should show placeholder
        self.assertEqual(search_entry.entry_var.get(), "Search here...")
        
        # Simulate focus in
        search_entry._on_focus_in(None)
        self.assertTrue(search_entry.has_focus)
        self.assertEqual(search_entry.entry_var.get(), "")
        
        # Add some text
        search_entry.entry_var.set("test search")
        
        # Simulate focus out
        search_entry._on_focus_out(None)
        self.assertFalse(search_entry.has_focus)
        self.assertEqual(search_entry.entry_var.get(), "test search")  # Should keep user text
        
    def test_search_callback(self):
        """Test search callback functionality."""
        callback_mock = Mock()
        search_entry = SearchEntry(self.root, on_search=callback_mock)
        
        # Set search term and trigger search
        search_entry.set_search_term("test query")
        search_entry._on_search_clicked()
        
        callback_mock.assert_called_once_with("test query")
        
    def test_get_search_term(self):
        """Test getting search term excluding placeholder."""
        search_entry = SearchEntry(self.root, placeholder="Enter search...")
        
        # Should return empty string when showing placeholder
        self.assertEqual(search_entry.get_search_term(), "")
        
        # Should return actual search term
        search_entry.set_search_term("actual search")
        self.assertEqual(search_entry.get_search_term(), "actual search")
        
    def test_clear_functionality(self):
        """Test clearing the search entry."""
        search_entry = SearchEntry(self.root, placeholder="Search...")
        
        search_entry.set_search_term("some text")
        search_entry.clear()
        
        self.assertEqual(search_entry.entry_var.get(), "Search...")
        self.assertFalse(search_entry.has_focus)


class TestResultCard(unittest.TestCase):
    """Test cases for ResultCard component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    def test_result_card_initialization(self):
        """Test ResultCard initialization."""
        callback_mock = Mock()
        card = ResultCard(
            self.root,
            filename="./Jan/test.html",
            word_count=150,
            on_view=callback_mock
        )
        
        self.assertIsInstance(card, ttk.Frame)
        self.assertEqual(card.filename, "./Jan/test.html")
        self.assertEqual(card.word_count, 150)
        self.assertEqual(card.on_view, callback_mock)
        
    def test_filename_formatting(self):
        """Test filename display formatting."""
        card = ResultCard(self.root, filename="./Jan/very_long_filename_that_should_be_truncated.html", word_count=100)
        
        # Test that long filenames are truncated
        formatted = card._format_filename("./Jan/very_long_filename_that_should_be_truncated.html")
        self.assertTrue(len(formatted) <= 28)  # Max length + ellipsis
        self.assertTrue("..." in formatted or len(formatted) <= 25)
        
    def test_view_callback(self):
        """Test view button callback."""
        callback_mock = Mock()
        card = ResultCard(self.root, filename="./Jan/test.html", word_count=100, on_view=callback_mock)
        
        # Simulate button click
        card._on_view_clicked()
        
        callback_mock.assert_called_once_with("./Jan/test.html")


class TestStatsPanel(unittest.TestCase):
    """Test cases for StatsPanel component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    def test_stats_panel_initialization(self):
        """Test StatsPanel initialization."""
        panel = StatsPanel(self.root)
        
        self.assertIsInstance(panel, ttk.Frame)
        self.assertEqual(panel.stats['files_count'], 0)
        self.assertEqual(panel.stats['vocabulary_size'], 0)
        
    def test_stats_update(self):
        """Test updating statistics."""
        panel = StatsPanel(self.root)
        
        panel.update_stats(
            files_count=31,
            vocabulary_size=1855,
            current_results=3,
            last_search="music"
        )
        
        self.assertEqual(panel.stats['files_count'], 31)
        self.assertEqual(panel.stats['vocabulary_size'], 1855)
        self.assertEqual(panel.stats['current_results'], 3)
        self.assertEqual(panel.stats['last_search'], "music")


class TestLoadingLabel(unittest.TestCase):
    """Test cases for LoadingLabel component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    def test_loading_label_initialization(self):
        """Test LoadingLabel initialization."""
        label = LoadingLabel(self.root, text="Loading data")
        
        self.assertIsInstance(label, ttk.Label)
        self.assertEqual(label.base_text, "Loading data")
        self.assertFalse(label.animation_active)
        
    def test_animation_control(self):
        """Test animation start and stop."""
        label = LoadingLabel(self.root, text="Processing")
        
        # Start animation
        label.start_animation()
        self.assertTrue(label.animation_active)
        
        # Stop animation
        label.stop_animation("Complete!")
        self.assertFalse(label.animation_active)


class TestScrollableFrame(unittest.TestCase):
    """Test cases for ScrollableFrame component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    def test_scrollable_frame_initialization(self):
        """Test ScrollableFrame initialization."""
        frame = ScrollableFrame(self.root)
        
        self.assertIsInstance(frame, ttk.Frame)
        self.assertIsInstance(frame.canvas, tk.Canvas)
        self.assertIsInstance(frame.scrollbar, ttk.Scrollbar)
        self.assertIsInstance(frame.scrollable_frame, ttk.Frame)
        
    def test_content_management(self):
        """Test adding and clearing content."""
        frame = ScrollableFrame(self.root)
        
        # Add a test widget
        test_label = ttk.Label(frame.scrollable_frame, text="Test")
        frame.add_widget(test_label, row=0, column=0)
        
        # Check that widget was added
        children = frame.scrollable_frame.winfo_children()
        self.assertIn(test_label, children)
        
        # Clear content
        frame.clear_content()
        children_after = frame.scrollable_frame.winfo_children()
        self.assertEqual(len(children_after), 0)


class TestGuiIntegration(unittest.TestCase):
    """Integration tests for GUI components with mocked backend."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
        
    @patch('gui_app.HtmlIndexer')
    def test_gui_app_initialization(self, mock_indexer_class):
        """Test GUI app initialization with mocked indexer."""
        # Mock indexer
        mock_indexer = Mock()
        mock_indexer.get_file_count.return_value = 31
        mock_indexer.get_vocabulary_size.return_value = 1855
        mock_indexer.build_index.return_value = None
        mock_indexer_class.return_value = mock_indexer
        
        # Import after patching
        from gui_app import GuiApp
        
        # Create app (but don't run mainloop)
        app = GuiApp("test.zip")
        
        # Verify app was created
        self.assertIsNotNone(app.root)
        self.assertEqual(app.zip_path, "test.zip")
        self.assertFalse(app.is_initialized)
        
        # Clean up
        app.root.destroy()
        
    def test_search_workflow_simulation(self):
        """Test complete search workflow with mocked components."""
        # Create search entry
        callback_mock = Mock()
        search_entry = SearchEntry(self.root, on_search=callback_mock)
        
        # Create stats panel
        stats_panel = StatsPanel(self.root)
        
        # Create scrollable frame for results
        results_frame = ScrollableFrame(self.root)
        
        # Simulate search workflow
        search_entry.set_search_term("music")
        search_entry._on_search_clicked()
        
        # Update stats
        stats_panel.update_stats(
            files_count=31,
            vocabulary_size=1855,
            current_results=2,
            last_search="music"
        )
        
        # Verify callback was triggered
        callback_mock.assert_called_once_with("music")
        
        # Verify stats were updated
        self.assertEqual(stats_panel.stats['last_search'], "music")
        self.assertEqual(stats_panel.stats['current_results'], 2)
        
    def test_result_card_interaction(self):
        """Test result card click interactions."""
        view_callback = Mock()
        
        # Create result cards
        card1 = ResultCard(self.root, "./Jan/test1.html", 150, on_view=view_callback)
        card2 = ResultCard(self.root, "./Jan/test2.html", 200, on_view=view_callback)
        
        # Simulate clicking view buttons
        card1._on_view_clicked()
        card2._on_view_clicked()
        
        # Verify callbacks
        expected_calls = [
            unittest.mock.call("./Jan/test1.html"),
            unittest.mock.call("./Jan/test2.html")
        ]
        view_callback.assert_has_calls(expected_calls)


class TestGuiStyles(unittest.TestCase):
    """Test GUI styling and theming."""
    
    def test_color_constants(self):
        """Test that color constants are properly defined."""
        self.assertIn('primary', COLORS)
        self.assertIn('background', COLORS)
        self.assertIn('text_primary', COLORS)
        self.assertTrue(COLORS['primary'].startswith('#'))
        
    def test_font_constants(self):
        """Test that font constants are properly defined."""
        self.assertIn('default_family', FONTS)
        self.assertIn('body', FONTS)
        self.assertIn('title', FONTS)
        self.assertIsInstance(FONTS['body'], int)
        
    def test_size_constants(self):
        """Test that size constants are properly defined."""
        self.assertIn('window_min_width', SIZES)
        self.assertIn('window_min_height', SIZES)
        self.assertGreater(SIZES['window_min_width'], 0)
        self.assertGreater(SIZES['window_min_height'], 0)


if __name__ == '__main__':
    # Configure test runner to suppress tkinter window flashing
    unittest.main(verbosity=2, buffer=True)