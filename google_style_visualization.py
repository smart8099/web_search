#!/usr/bin/env python3
"""
Google-Style Search Engine Architecture Visualization

This script generates comprehensive visualizations of the Google-style search engine's
architecture with emphasis on UI components and data flow.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np

def create_google_style_architecture():
    """Create Google-style architecture diagram."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Google-Style HTML Search Engine - Complete Architecture',
                 fontsize=20, fontweight='bold', y=0.98)

    # Google colors
    colors = {
        'google_blue': '#4285f4',
        'google_red': '#ea4335',
        'google_yellow': '#fbbc05',
        'google_green': '#34a853',
        'result_blue': '#1a0dab',
        'url_green': '#006621',
        'snippet_gray': '#545454',
        'background': '#ffffff'
    }

    # 1. Google-Style UI Components (Top Left)
    ax1.set_title('Google-Style UI Components', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)

    # Search interface
    search_box = FancyBboxPatch((1, 8), 8, 1.5,
                               boxstyle="round,pad=0.1",
                               facecolor='white',
                               edgecolor=colors['google_blue'], linewidth=3)
    ax1.add_patch(search_box)
    ax1.text(5, 8.75, '🔍 Google-Style Search Interface', ha='center', va='center',
             fontsize=14, fontweight='bold', color=colors['google_blue'])

    # Result cards
    card_colors = [colors['result_blue'], colors['url_green'], colors['snippet_gray']]
    card_labels = ['Blue Clickable Titles', 'Green Document URLs', 'Gray Description Text']

    for i, (color, label) in enumerate(zip(card_colors, card_labels)):
        card = FancyBboxPatch((0.5, 6-i*1.5), 9, 1,
                             boxstyle="round,pad=0.1",
                             facecolor='white',
                             edgecolor=color, linewidth=2)
        ax1.add_patch(card)
        ax1.text(5, 6.5-i*1.5, label, ha='center', va='center',
                 fontsize=12, fontweight='bold', color=color)

    # Google features
    features_box = FancyBboxPatch((2, 1), 6, 1.5,
                                 boxstyle="round,pad=0.1",
                                 facecolor=colors['google_yellow'],
                                 edgecolor='orange', linewidth=2)
    ax1.add_patch(features_box)
    ax1.text(5, 1.75, '⭐ Star Badges • 📖 View Content\n🔤 Search Highlighting',
             ha='center', va='center', fontsize=10, fontweight='bold')

    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.axis('off')

    # 2. GoogleResultCard Architecture (Top Right)
    ax2.set_title('GoogleResultCard Component', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)

    # Card structure
    card_frame = FancyBboxPatch((1, 2), 8, 7,
                               boxstyle="round,pad=0.1",
                               facecolor='white',
                               edgecolor='black', linewidth=2)
    ax2.add_patch(card_frame)

    # Title section
    title_section = FancyBboxPatch((1.5, 7.5), 7, 1,
                                  boxstyle="round,pad=0.05",
                                  facecolor=colors['result_blue'],
                                  alpha=0.3, edgecolor=colors['result_blue'])
    ax2.add_patch(title_section)
    ax2.text(5, 8, 'Document Title (#1a0dab)', ha='center', va='center',
             fontsize=12, fontweight='bold', color=colors['result_blue'])

    # URL section
    url_section = FancyBboxPatch((1.5, 6), 7, 0.8,
                                boxstyle="round,pad=0.05",
                                facecolor=colors['url_green'],
                                alpha=0.3, edgecolor=colors['url_green'])
    ax2.add_patch(url_section)
    ax2.text(5, 6.4, '📄 Document ID (#006621)', ha='center', va='center',
             fontsize=11, fontweight='bold', color=colors['url_green'])

    # Snippet section
    snippet_section = FancyBboxPatch((1.5, 4.5), 7, 1,
                                    boxstyle="round,pad=0.05",
                                    facecolor=colors['snippet_gray'],
                                    alpha=0.3, edgecolor=colors['snippet_gray'])
    ax2.add_patch(snippet_section)
    ax2.text(5, 5, 'Word count • Relevance score (#545454)', ha='center', va='center',
             fontsize=11, fontweight='bold', color=colors['snippet_gray'])

    # Action buttons
    action_section = FancyBboxPatch((1.5, 3), 7, 1,
                                   boxstyle="round,pad=0.05",
                                   facecolor='#f8f9fa',
                                   edgecolor='gray')
    ax2.add_patch(action_section)
    ax2.text(5, 3.5, '📖 View Content Button + ⭐ Star Badge', ha='center', va='center',
             fontsize=11, fontweight='bold')

    # Hover effects annotation
    ax2.text(5, 1, 'Hover Effects:\n• Title underline\n• Cursor pointer',
             ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow'))

    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.axis('off')

    # 3. Search Flow with Google Features (Bottom Left)
    ax3.set_title('Google-Style Search Flow', fontsize=16, fontweight='bold', pad=20)
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 10)

    # Search steps with Google styling
    google_steps = [
        ('User Query', 8.5, colors['google_blue'], '"web page"'),
        ('Query Processing', 7, colors['google_green'], 'Parse quotes, extract terms'),
        ('Hash Lookup', 5.5, colors['google_red'], 'O(1) search operation'),
        ('Google Cards', 4, colors['google_yellow'], 'Vertical stacking layout'),
        ('File Preview', 2.5, colors['result_blue'], 'Yellow highlighting')
    ]

    for i, (label, y, color, detail) in enumerate(google_steps):
        # Main step
        box = FancyBboxPatch((1, y-0.5), 4, 1,
                            boxstyle="round,pad=0.1",
                            facecolor=color,
                            alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.add_patch(box)
        ax3.text(3, y, f'{i+1}. {label}', ha='center', va='center',
                 fontsize=11, fontweight='bold', color='white')

        # Detail
        detail_box = FancyBboxPatch((5.5, y-0.3), 3.5, 0.6,
                                   boxstyle="round,pad=0.05",
                                   facecolor='white',
                                   edgecolor=color, linewidth=1)
        ax3.add_patch(detail_box)
        ax3.text(7.25, y, detail, ha='center', va='center',
                 fontsize=9, style='italic')

        # Arrows
        if i < len(google_steps) - 1:
            ax3.arrow(3, y-0.5, 0, -1, head_width=0.15, head_length=0.15,
                     fc=color, ec=color, linewidth=2)

    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.axis('off')

    # 4. Performance & Features (Bottom Right)
    ax4.set_title('Google-Style Features & Performance', fontsize=16, fontweight='bold', pad=20)
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)

    # Google-style features
    features = [
        ('🔵 Blue Titles (#1a0dab)', 9, colors['result_blue']),
        ('🟢 Green URLs (#006621)', 8.2, colors['url_green']),
        ('⚪ Gray Snippets (#545454)', 7.4, colors['snippet_gray']),
        ('📱 Vertical Stacking', 6.6, colors['google_blue']),
        ('🔍 Search Highlighting', 5.8, colors['google_yellow']),
        ('⭐ Star Badges (>0.5)', 5, colors['google_red']),
        ('📖 Content Preview', 4.2, colors['google_green']),
        ('🖱️ Hover Effects', 3.4, 'purple')
    ]

    for feature, y, color in features:
        box = FancyBboxPatch((0.5, y-0.3), 9, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor=color,
                            alpha=0.2, edgecolor=color, linewidth=1.5)
        ax4.add_patch(box)
        ax4.text(5, y, feature, ha='center', va='center',
                 fontsize=11, fontweight='bold', color=color)

    # Performance metrics
    ax4.text(5, 2.2, 'Performance Metrics:', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax4.text(5, 1.5, '• Search: O(1) hash lookup\n• UI: Instant card rendering\n• Memory: Efficient data structures',
             ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))

    ax4.set_xticks([])
    ax4.set_yticks([])
    ax4.axis('off')

    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    return fig

def create_search_highlighting_diagram():
    """Create search term highlighting flow diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.suptitle('Search Term Highlighting - Quote Handling & Text Processing',
                 fontsize=18, fontweight='bold')

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 16)

    # Colors
    colors = {
        'input': '#e3f2fd',
        'process': '#e8f5e8',
        'output': '#fff3e0',
        'highlight': '#ffeb3b'
    }

    # Input examples
    examples = [
        ('Regular Search', 2, 14, 'web page', 'Splits into: ["web", "page"]'),
        ('Quoted Search', 8, 14, '"web page"', 'Extracts: ["web page"]'),
        ('Complex Query', 12, 14, 'cat AND dog', 'Boolean: ["cat", "dog"]')
    ]

    for title, x, y, query, result in examples:
        # Query box
        query_box = FancyBboxPatch((x-1.5, y-0.5), 3, 1,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['input'],
                                  edgecolor='blue', linewidth=2)
        ax.add_patch(query_box)
        ax.text(x, y+0.3, title, ha='center', va='center',
                fontsize=11, fontweight='bold')
        ax.text(x, y-0.2, f'"{query}"', ha='center', va='center',
                fontsize=10, fontfamily='monospace')

        # Result box
        result_box = FancyBboxPatch((x-1.5, y-2), 3, 1,
                                   boxstyle="round,pad=0.1",
                                   facecolor=colors['output'],
                                   edgecolor='orange', linewidth=1)
        ax.add_patch(result_box)
        ax.text(x, y-1.5, result, ha='center', va='center',
                fontsize=9, style='italic')

        # Arrow
        ax.arrow(x, y-0.5, 0, -1, head_width=0.2, head_length=0.2,
                fc='purple', ec='purple')

    # Processing flow
    ax.text(7, 11, 'Term Extraction & Highlighting Process', ha='center', va='center',
            fontsize=16, fontweight='bold')

    # Processing steps
    steps = [
        ('1. Query Analysis', 7, 9.5, colors['process'], 'Detect quotes, operators'),
        ('2. Term Extraction', 7, 8.5, colors['process'], 'Split or preserve phrases'),
        ('3. Content Search', 7, 7.5, colors['process'], 'Case-insensitive matching'),
        ('4. Position Calculation', 7, 6.5, colors['process'], 'Line.char indexing'),
        ('5. Highlight Application', 7, 5.5, colors['highlight'], 'Yellow background')
    ]

    for step, x, y, color, detail in steps:
        # Step box
        step_box = FancyBboxPatch((x-2, y-0.3), 4, 0.6,
                                 boxstyle="round,pad=0.1",
                                 facecolor=color,
                                 edgecolor='black', linewidth=1.5)
        ax.add_patch(step_box)
        ax.text(x, y, step, ha='center', va='center',
                fontsize=11, fontweight='bold')

        # Detail
        ax.text(x+3.5, y, detail, ha='left', va='center',
                fontsize=10, style='italic')

        # Arrow to next step
        if 'Highlight' not in step:
            ax.arrow(x, y-0.3, 0, -0.4, head_width=0.15, head_length=0.1,
                    fc='darkgreen', ec='darkgreen')

    # Highlighting examples
    ax.text(7, 4, 'Highlighting Examples in Document View', ha='center', va='center',
            fontsize=14, fontweight='bold')

    highlight_examples = [
        ('Regular: "web"', 3, 2.5, 'Highlights: web, WEB, Web'),
        ('Quoted: "web page"', 7, 2.5, 'Highlights: web page (together)'),
        ('Multiple: "cat dog"', 11, 2.5, 'Highlights: cat, dog separately')
    ]

    for example, x, y, description in highlight_examples:
        example_box = FancyBboxPatch((x-1.5, y-0.5), 3, 1,
                                    boxstyle="round,pad=0.1",
                                    facecolor=colors['highlight'],
                                    edgecolor='orange', linewidth=2)
        ax.add_patch(example_box)
        ax.text(x, y+0.2, example, ha='center', va='center',
                fontsize=10, fontweight='bold')
        ax.text(x, y-0.8, description, ha='center', va='center',
                fontsize=9, style='italic')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

    plt.tight_layout()
    return fig

def save_google_style_diagrams():
    """Generate and save Google-style architecture diagrams."""
    print("📊 Generating Google-style architecture diagrams...")

    # Create diagrams
    google_arch = create_google_style_architecture()
    highlight_flow = create_search_highlighting_diagram()

    # Save diagrams
    google_arch.savefig('google_style_architecture.png', dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
    highlight_flow.savefig('search_highlighting_flow.png', dpi=300, bbox_inches='tight',
                          facecolor='white', edgecolor='none')

    print("✅ Google-style architecture diagrams saved:")
    print("   • google_style_architecture.png")
    print("   • search_highlighting_flow.png")

    print("\n🎨 Features Documented:")
    print("   • Google-style UI components (blue/green/gray)")
    print("   • Search term highlighting with quote handling")
    print("   • GoogleResultCard architecture")
    print("   • Performance metrics and data flow")

    plt.show()

if __name__ == "__main__":
    save_google_style_diagrams()