"""
GUI Styles and Theme Constants for HTML Search Engine

This module defines the visual styling, colors, fonts, and layout constants
used throughout the GUI application for consistent theming.
"""

from typing import Dict, Any

# Color palette - Material Design inspired
COLORS = {
    # Primary colors
    'primary': '#1976D2',           # Deep Blue
    'primary_dark': '#1565C0',      # Darker Blue
    'primary_light': '#BBDEFB',     # Light Blue
    
    # Secondary colors
    'secondary': '#FF5722',         # Deep Orange
    'secondary_light': '#FFCCBC',   # Light Orange
    
    # Background colors
    'background': '#FAFAFA',        # Light Grey
    'surface': '#FFFFFF',           # White
    'card_background': '#FFFFFF',   # White
    'card_hover': '#F5F5F5',        # Very Light Grey
    
    # Text colors
    'text_primary': '#212121',      # Dark Grey
    'text_secondary': '#757575',    # Medium Grey
    'text_hint': '#BDBDBD',         # Light Grey
    'text_disabled': '#E0E0E0',     # Very Light Grey
    
    # Status colors
    'success': '#4CAF50',           # Green
    'warning': '#FF9800',           # Orange
    'error': '#F44336',             # Red
    'info': '#2196F3',              # Blue
    
    # Border colors
    'border': '#E0E0E0',            # Light Grey
    'border_focus': '#1976D2',      # Primary Blue
}

# Font configuration
FONTS = {
    'default_family': 'Segoe UI',
    'fallback_families': ['Helvetica', 'Arial', 'sans-serif'],
    
    # Font sizes
    'title': 24,
    'heading': 18,
    'subheading': 16,
    'body': 12,
    'caption': 10,
    'button': 11,
    
    # Font weights
    'light': 'normal',
    'regular': 'normal',
    'medium': 'bold',
    'bold': 'bold',
}

# Spacing and sizing constants
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
    'xxl': 48,
}

SIZES = {
    # Window dimensions
    'window_min_width': 900,
    'window_min_height': 700,
    'window_default_width': 1100,
    'window_default_height': 800,
    
    # Search components
    'search_box_width': 500,
    'search_box_height': 40,
    'search_button_width': 100,
    'search_button_height': 40,
    
    # Result cards
    'card_width': 280,
    'card_height': 120,
    'card_padding': 12,
    'card_margin': 8,
    
    # Statistics panel
    'stats_panel_width': 200,
    'stats_panel_height': 150,
    
    # Border radius for modern look
    'border_radius': 8,
    'button_radius': 6,
    'card_radius': 8,
}

# Icons and symbols (using Unicode)
ICONS = {
    'search': '🔍',
    'file': '📄',
    'stats': '📊',
    'results': '🎯',  # Better icon for search results
    'matches': '✨',  # Alternative results icon  
    'found': '🔍',    # Search results found
    'check': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'folder': '📁',
    'document': '📋',
    'copy': '📋',
    'close': '✕',
    'minimize': '─',
    'maximize': '☐',
}

# Animation and transition settings
ANIMATIONS = {
    'transition_duration': 300,  # milliseconds
    'fade_steps': 10,
    'slide_steps': 15,
    'hover_delay': 100,
}

# Layout configurations
LAYOUTS = {
    'center_search': {
        'search_y_offset': -50,  # Pixels above center
        'title_spacing': 60,
        'stats_spacing': 40,
    },
    'top_search': {
        'search_y_position': 20,  # Pixels from top
        'results_y_position': 80,
        'stats_x_position': -20,  # Pixels from right
    },
    'results_grid': {
        'columns': 3,
        'max_columns': 4,
        'row_height': 140,
        'scroll_speed': 3,
    }
}

# Tkinter ttk style configurations
TTK_STYLES = {
    'SearchEntry.TEntry': {
        'configure': {
            'fieldbackground': COLORS['surface'],
            'borderwidth': 2,
            'relief': 'solid',
            'bordercolor': COLORS['border'],
            'focuscolor': COLORS['border_focus'],
            'insertcolor': COLORS['text_primary'],
            'font': (FONTS['default_family'], FONTS['body'], FONTS['medium']),
            'foreground': COLORS['text_primary'],
        },
        'map': {
            'bordercolor': [
                ('focus', COLORS['border_focus']),
                ('!focus', COLORS['border']),
            ],
            'foreground': [
                ('focus', COLORS['text_primary']),
                ('!focus', COLORS['text_primary']),
            ]
        }
    },
    'SearchButton.TButton': {
        'configure': {
            'background': COLORS['primary'],
            'foreground': 'white',
            'borderwidth': 0,
            'focuscolor': 'none',
            'font': (FONTS['default_family'], FONTS['button'], FONTS['medium']),
            'padding': (12, 8),  # Horizontal, vertical padding
            'relief': 'flat',
            'anchor': 'center',
        },
        'map': {
            'background': [
                ('active', COLORS['primary_dark']),
                ('pressed', COLORS['primary_dark']),
            ],
            'relief': [
                ('pressed', 'sunken'),
                ('!pressed', 'flat'),
            ]
        }
    },
    'Card.TFrame': {
        'configure': {
            'background': COLORS['card_background'],
            'borderwidth': 1,
            'relief': 'solid',
            'bordercolor': COLORS['border'],
        }
    },
    'Stats.TLabel': {
        'configure': {
            'background': COLORS['background'],
            'foreground': COLORS['text_secondary'],
            'font': (FONTS['default_family'], FONTS['caption'], FONTS['regular']),
        }
    },
    'Title.TLabel': {
        'configure': {
            'background': COLORS['background'],
            'foreground': COLORS['text_primary'],
            'font': (FONTS['default_family'], FONTS['title'], FONTS['bold']),
        }
    },
    'Heading.TLabel': {
        'configure': {
            'background': COLORS['background'],
            'foreground': COLORS['text_primary'],
            'font': (FONTS['default_family'], FONTS['heading'], FONTS['medium']),
        }
    },
    'Body.TLabel': {
        'configure': {
            'background': COLORS['surface'],
            'foreground': COLORS['text_primary'],
            'font': (FONTS['default_family'], FONTS['body'], FONTS['regular']),
        }
    }
}

# Helper functions for style application
def get_font(size: str, weight: str = 'regular') -> tuple:
    """Get a font tuple for Tkinter widgets."""
    return (
        FONTS['default_family'],
        FONTS.get(size, FONTS['body']),
        FONTS.get(weight, FONTS['regular'])
    )

def get_color_scheme() -> Dict[str, str]:
    """Get the complete color scheme for the application."""
    return COLORS.copy()

def get_spacing(size: str) -> int:
    """Get spacing value by size name."""
    return SPACING.get(size, SPACING['md'])

def get_size(component: str) -> int:
    """Get size value for a specific component."""
    return SIZES.get(component, 0)

def apply_ttk_styles(style_obj) -> None:
    """Apply all TTK styles to the given ttk.Style object."""
    for style_name, style_config in TTK_STYLES.items():
        if 'configure' in style_config:
            style_obj.configure(style_name, **style_config['configure'])
        if 'map' in style_config:
            style_obj.map(style_name, **style_config['map'])

# CSS-like helper for padding/margin
def padding(top: int = 0, right: int = None, bottom: int = None, left: int = None) -> Dict[str, int]:
    """Create padding dictionary similar to CSS."""
    if right is None:
        right = top
    if bottom is None:
        bottom = top
    if left is None:
        left = right
    
    return {
        'padx': (left, right),
        'pady': (top, bottom)
    }