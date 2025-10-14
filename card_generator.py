#!/usr/bin/env python3
"""
Card Template PDF Generator

This script generates a PDF file with multiple cards based on a JSON input file.
Each card has a similar design but with different content.
"""

import json
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
import os
from image_search import ImageSearcher
from PIL import Image, ImageDraw, ImageFilter
import io


class CardGenerator:
    """Generate PDF cards from JSON data."""
    
    def __init__(self, page_size=letter, auto_search_images=False, gradient_enabled=True):
        """
        Initialize the card generator.
        
        Args:
            page_size: The page size for the PDF (default: letter)
            auto_search_images: Whether to automatically search for images (default: False)
            gradient_enabled: Whether to apply gradient effects to images (default: True)
        """
        self.page_size = page_size
        self.page_width, self.page_height = page_size
        self.auto_search_images = auto_search_images
        self.gradient_enabled = gradient_enabled
        
        # Initialize image searcher if auto search is enabled
        if self.auto_search_images:
            self.image_searcher = ImageSearcher()
            print("Auto image search enabled")
        else:
            self.image_searcher = None
        
        if self.gradient_enabled:
            print("Gradient effects enabled")
        
        # Card dimensions (120mm x 65mm)
        self.card_width = 65 * 0.0393701 * inch  # 65mm to inches
        self.card_height = 120 * 0.0393701 * inch  # 120mm to inches
        self.card_margin = 0  # No margins between cards
        
        # Calculate optimal layout
        self._calculate_optimal_layout()
        
        # Colors
        self.bg_color = HexColor('#f0f0f0')
        self.border_color = HexColor('#333333')
        self.title_color = HexColor('#2c3e50')
        self.subtitle_color = HexColor('#7f8c8d')
        self.text_color = HexColor('#34495e')
        
        # Mana colors
        self.mana_colors = {
            'red': HexColor('#d32f2f'),
            'blue': HexColor('#1976d2'),
            'green': HexColor('#388e3c'),
            'white': HexColor('#fafafa'),
            'black': HexColor('#424242'),
            'colorless': HexColor('#9e9e9e')
        }
    
    def _calculate_optimal_layout(self):
        """Calculate optimal card layout with rotation if beneficial."""
        # Normal orientation
        normal_per_row = int(self.page_width / self.card_width)
        normal_per_col = int(self.page_height / self.card_height)
        normal_total = normal_per_row * normal_per_col
        
        # Rotated orientation (90 degrees)
        rotated_per_row = int(self.page_width / self.card_height)
        rotated_per_col = int(self.page_height / self.card_width)
        rotated_total = rotated_per_row * rotated_per_col
        
        # Mixed layout (some normal, some rotated)
        # Try fitting normal cards first, then rotated in remaining space
        remaining_width = self.page_width - (normal_per_row * self.card_width)
        remaining_height = self.page_height - (normal_per_col * self.card_height)
        
        extra_rotated_in_width = int(remaining_width / self.card_height) * normal_per_col
        extra_rotated_in_height = int(remaining_height / self.card_width) * normal_per_row
        mixed_total = normal_total + max(extra_rotated_in_width, extra_rotated_in_height)
        
        # Choose best layout
        if mixed_total >= max(normal_total, rotated_total):
            self.layout_type = 'mixed'
            self.cards_per_row = normal_per_row
            self.cards_per_col = normal_per_col
            self.cards_per_page = mixed_total
            self.extra_rotated = max(extra_rotated_in_width, extra_rotated_in_height)
        elif rotated_total > normal_total:
            self.layout_type = 'rotated'
            self.cards_per_row = rotated_per_row
            self.cards_per_col = rotated_per_col
            self.cards_per_page = rotated_total
        else:
            self.layout_type = 'normal'
            self.cards_per_row = normal_per_row
            self.cards_per_col = normal_per_col
            self.cards_per_page = normal_total
        
    def load_cards_data(self, json_file):
        """
        Load card data from JSON file.
        
        Args:
            json_file: Path to the JSON file
            
        Returns:
            List of card dictionaries
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('cards', [])
    
    def draw_card(self, c, x, y, card_data, rotated=False):
        """
        Draw a single card on the canvas.
        
        Args:
            c: Canvas object
            x: X position for the card
            y: Y position for the card
            card_data: Dictionary containing card content
            rotated: Whether to draw the card rotated 90 degrees
        """
        if rotated:
            # Save current state and rotate
            c.saveState()
            c.translate(x + self.card_height, y)
            c.rotate(90)
            # Use swapped dimensions for rotated card
            card_w, card_h = self.card_height, self.card_width
            x, y = 0, 0
        else:
            card_w, card_h = self.card_width, self.card_height
        
        # Get card color
        card_color = card_data.get('color', '#2c3e50')  # Default to title_color if no color specified
        # Draw card background (light gray for better contrast)
        c.setFillColor(HexColor('#f5f5f5'))  # Light gray background
        c.setStrokeColor(self.border_color)
        c.setLineWidth(2)
        c.rect(x, y, card_w, card_h, stroke=1, fill=1)
        
        # Draw header bar with individual card color
        card_color = card_data.get('color', '#2c3e50')  # Default to title_color if no color specified
        c.setFillColor(HexColor(card_color))
        c.rect(x, y + card_h - 0.5 * inch, card_w, 0.5 * inch, stroke=0, fill=1)
        
        # Draw title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        title = card_data.get('title', 'Card Title')
        c.drawCentredString(x + card_w / 2, y + card_h - 0.3 * inch, title)
        
        # Draw card body
        body = card_data.get('body', {})
        if body:
            text_y = y + card_h - 0.7 * inch
            c.setFillColor(self.text_color)
            
            # Calculate space usage
            used_lines, total_lines = self._calculate_body_space_usage(body)
            space_usage_percent = (used_lines / total_lines) * 100 if total_lines > 0 else 100
            
            # Check if we should add an image (less than 50% space used)
            should_add_image = space_usage_percent < 50
            image_path = card_data.get('image')
            image_added = False
            
            if should_add_image and image_path:
                # Calculate available space for image
                used_height = used_lines * 0.15 * inch
                available_height = 2.3 * inch - used_height
                
                # Try to draw image
                if available_height > 0.5 * inch:  # Minimum height for image
                    image_added = self._draw_card_image(c, x, text_y - 2.0 * inch, 
                                                      card_w, card_h, image_path, available_height)
            
            # If no manual image specified but auto search is enabled and space is available
            elif should_add_image and self.auto_search_images and not image_path:
                print(f"Auto-searching image for card: {card_data.get('title', 'Unknown')}")
                auto_image_path = self.image_searcher.get_image_for_card(card_data)
                if auto_image_path:
                    # Calculate available space for image
                    used_height = used_lines * 0.15 * inch
                    available_height = 2.3 * inch - used_height
                    
                    # Try to draw auto-found image
                    if available_height > 0.5 * inch:  # Minimum height for image
                        image_added = self._draw_card_image(c, x, text_y - 2.0 * inch, 
                                                          card_w, card_h, auto_image_path, available_height)
            
            # When
            when = body.get('when', '')
            if when:
                # Draw "When: " in color, then text in normal color on same line
                when_text = f"When: {when}"
                when_lines = self._wrap_text(when_text, 22)  # Reduced from 30
                for i, line in enumerate(when_lines[:3]):  # Max 3 lines
                    if i == 0:
                        # First line: draw "When:" in color
                        c.setFont("Helvetica-Bold", 12)
                        c.setFillColor(HexColor(card_color))
                        c.drawString(x + 0.1 * inch, text_y, "When:")
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        remaining_text = line[5:]  # Remove "When:"
                        c.drawString(x + 0.55 * inch, text_y, remaining_text)
                    else:
                        # Continuation lines: normal text only
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        c.drawString(x + 0.1 * inch, text_y, line)
                    text_y -= 0.18 * inch
                text_y -= 0.05 * inch
            
            # Target
            target = body.get('target', '')
            if target:
                target_text = f"Target: {target}"
                target_lines = self._wrap_text(target_text, 22)  # Reduced from 30
                for i, line in enumerate(target_lines[:3]):  # Max 3 lines
                    if i == 0:
                        c.setFont("Helvetica-Bold", 12)
                        c.setFillColor(HexColor(card_color))
                        c.drawString(x + 0.1 * inch, text_y, "Target:")
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        remaining_text = line[7:]  # Remove "Target:"
                        c.drawString(x + 0.65 * inch, text_y, remaining_text)
                    else:
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        c.drawString(x + 0.1 * inch, text_y, line)
                    text_y -= 0.18 * inch
                text_y -= 0.05 * inch
            
            # Effect
            effect = body.get('effect', '')
            if effect:
                effect_text = f"Effect: {effect}"
                effect_lines = self._wrap_text(effect_text, 22)  # Reduced from 30
                for i, line in enumerate(effect_lines[:4]):  # Max 4 lines
                    if i == 0:
                        c.setFont("Helvetica-Bold", 12)
                        c.setFillColor(HexColor(card_color))
                        c.drawString(x + 0.1 * inch, text_y, "Effect:")
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        remaining_text = line[7:]  # Remove "Effect:"
                        c.drawString(x + 0.65 * inch, text_y, remaining_text)
                    else:
                        c.setFont("Helvetica", 12)
                        c.setFillColor(self.text_color)
                        c.drawString(x + 0.1 * inch, text_y, line)
                    text_y -= 0.18 * inch
                text_y -= 0.05 * inch
            
            # Restriction
            restriction = body.get('restriction', '')
            if restriction and restriction.lower() != 'none':
                restriction_text = f"Restriction: {restriction}"
                restriction_lines = self._wrap_text(restriction_text, 20)  # Reduced
                for i, line in enumerate(restriction_lines[:3]):  # Max 3 lines
                    if i == 0:
                        c.setFont("Helvetica-Bold", 12)
                        c.setFillColor(HexColor(card_color))
                        c.drawString(x + 0.1 * inch, text_y, "Restriction:")
                        c.setFont("Helvetica-Oblique", 12)
                        c.setFillColor(self.subtitle_color)
                        remaining_text = line[12:]  # Remove "Restriction:"
                        c.drawString(x + 0.95 * inch, text_y, remaining_text)
                    else:
                        c.setFont("Helvetica-Oblique", 12)
                        c.setFillColor(self.subtitle_color)
                        c.drawString(x + 0.1 * inch, text_y, line)
                    text_y -= 0.18 * inch
        
        # Draw CP cost in bottom right corner
        cost_data = card_data.get('cost', {})
        if cost_data:
            cost_x = x + card_w - 0.25 * inch
            cost_y = y + 0.25 * inch
            # Get CP cost (handle both old and new format)
            if 'cp' in cost_data:
                total_cost = cost_data.get('cp', 0)
            else:
                # Old format - sum numeric values only
                total_cost = sum(v for v in cost_data.values() 
                               if isinstance(v, (int, float)))
            
            # Draw total cost circle with card color (bigger size)
            c.setFillColor(HexColor(card_color))
            c.setStrokeColor(HexColor(card_color))
            c.circle(cost_x, cost_y, 0.18 * inch, stroke=1, fill=1)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(cost_x, cost_y - 0.04 * inch, str(total_cost))
        
        if rotated:
            c.restoreState()
    
    def _wrap_text(self, text, max_chars):
        """Wrap text to fit within specified character limit."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_gradient_mask(self, width, height, gradient_size=40):
        """Create a gradient mask for blending image with background."""
        mask = Image.new('L', (width, height), 255)  # Start with white (fully opaque)
        draw = ImageDraw.Draw(mask)
        
        # Create gradients on all edges with smoother transition
        for i in range(gradient_size):
            # Use quadratic easing for smoother gradient
            progress = i / gradient_size
            opacity = int(255 * (progress * progress))
            
            # Top gradient
            draw.rectangle([i, i, width-1-i, i], fill=opacity)
            # Bottom gradient  
            draw.rectangle([i, height-1-i, width-1-i, height-1-i], fill=opacity)
            # Left gradient
            draw.rectangle([i, i, i, height-1-i], fill=opacity)
            # Right gradient
            draw.rectangle([width-1-i, i, width-1-i, height-1-i], fill=opacity)
        
        # Apply blur for even smoother transition
        mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
        return mask
    
    def _process_image_with_gradient(self, image_path, target_width, target_height):
        """Process image to add gradient blending with card background color (gray)."""
        try:
            # Open and resize the image
            with Image.open(image_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Calculate size maintaining aspect ratio
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    # Image is wider, fit to width
                    new_width = int(target_width)
                    new_height = int(target_width / img_ratio)
                else:
                    # Image is taller, fit to height
                    new_height = int(target_height)
                    new_width = int(target_height * img_ratio)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create background with gray card color (#f5f5f5)
                bg_color = (245, 245, 245)  # Gray background of the card
                background = Image.new('RGBA', (int(target_width), int(target_height)), bg_color + (255,))
                
                # Center the image on background
                x_offset = (int(target_width) - new_width) // 2
                y_offset = (int(target_height) - new_height) // 2
                
                # Create gradient mask
                gradient_size = min(50, new_width // 6, new_height // 6)  # Larger gradient for better effect
                mask = self._create_gradient_mask(new_width, new_height, gradient_size)
                
                # Create a more pronounced edge blend
                # First, darken the edges slightly to create depth
                edge_overlay = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
                edge_draw = ImageDraw.Draw(edge_overlay)
                edge_thickness = gradient_size // 2
                for i in range(edge_thickness):
                    alpha = int(30 * (1 - i / edge_thickness))  # Subtle darkening
                    edge_draw.rectangle([i, i, new_width-1-i, new_height-1-i], 
                                      outline=(*bg_color, alpha), width=1)
                
                # Composite edge overlay onto image
                img = Image.alpha_composite(img, edge_overlay)
                
                # Apply main gradient mask
                img.putalpha(mask)
                
                # Paste image onto background
                background.paste(img, (x_offset, y_offset), img)
                
                # Convert back to RGB for PDF
                final_image = background.convert('RGB')
                
                # Save to memory buffer
                buffer = io.BytesIO()
                final_image.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                
                return ImageReader(buffer)
                
        except Exception as e:
            print(f"Error processing image with gradient: {e}")
            return None
    
    def _calculate_body_space_usage(self, body_data):
        """Calculate how much space is used by body text."""
        if not body_data:
            return 0, 0  # used_lines, total_available_lines
        
        # Available space for body content (from header to cost section)
        body_height = 2.3 * inch  # Approximate available height for body
        line_height = 0.15 * inch  # Height per line of text
        total_available_lines = int(body_height / line_height)
        
        used_lines = 0
        
        # Count lines for each body section
        sections = ['when', 'target', 'effect', 'restriction']
        for section in sections:
            content = body_data.get(section, '')
            if content and (section != 'restriction' or content.lower() != 'none'):
                used_lines += 1  # For the label
                if section == 'effect':
                    # Effect can span multiple lines
                    effect_lines = self._wrap_text(content, 32)
                    used_lines += min(len(effect_lines), 2)  # Max 2 lines for effect
                elif section == 'restriction':
                    # Restriction can span multiple lines
                    restriction_lines = self._wrap_text(content, 35)
                    used_lines += min(len(restriction_lines), 2)  # Max 2 lines for restriction
        
        return used_lines, total_available_lines
    
    def _draw_card_image(self, c, x, y, card_w, card_h, image_path, available_height):
        """Draw card image with gradient blending if file exists and there's enough space."""
        if not image_path or not os.path.exists(image_path):
            return False
        
        try:
            # Calculate image dimensions (maintain aspect ratio)
            max_width = card_w * 0.8  # 80% of card width
            max_height = available_height * 0.8  # 80% of available height
            
            # Process image with gradient effect if enabled
            if self.gradient_enabled:
                processed_image = self._process_image_with_gradient(
                    image_path, max_width, max_height
                )
            else:
                processed_image = None
            
            if processed_image:
                # Position image in the center of available space
                img_x = x + (card_w - max_width) / 2
                img_y = y + 0.3 * inch  # Some margin from bottom
                
                # Draw the processed image
                c.drawImage(processed_image, img_x, img_y, width=max_width, height=max_height,
                           preserveAspectRatio=True, mask='auto')
                return True
            else:
                # Use original method if gradient processing is disabled or fails
                img_x = x + (card_w - max_width) / 2
                img_y = y + 0.3 * inch
                c.drawImage(image_path, img_x, img_y, width=max_width, height=max_height,
                           preserveAspectRatio=True, mask='auto')
                return True
                
        except Exception as e:
            # If image loading fails, silently continue without image
            print(f"Warning: Could not load image {image_path}: {e}")
            return False
    
    def generate_pdf(self, json_file, output_file):
        """
        Generate PDF with cards from JSON data.
        
        Args:
            json_file: Path to input JSON file
            output_file: Path to output PDF file
        """
        # Load card data
        cards = self.load_cards_data(json_file)
        
        if not cards:
            raise ValueError("No cards found in JSON file")
        
        # Create PDF
        c = canvas.Canvas(output_file, pagesize=self.page_size)
        
        # Draw cards
        for idx, card_data in enumerate(cards):
            # Calculate position based on layout type
            page_idx = idx % self.cards_per_page
            
            if self.layout_type == 'normal':
                row = page_idx // self.cards_per_row
                col = page_idx % self.cards_per_row
                x = col * self.card_width
                y = self.page_height - (row + 1) * self.card_height
                self.draw_card(c, x, y, card_data, rotated=False)
                
            elif self.layout_type == 'rotated':
                row = page_idx // self.cards_per_row
                col = page_idx % self.cards_per_row
                x = col * self.card_height
                y = self.page_height - (row + 1) * self.card_width
                self.draw_card(c, x, y, card_data, rotated=True)
                
            else:  # mixed layout
                normal_cards = self.cards_per_row * self.cards_per_col
                if page_idx < normal_cards:
                    # Normal orientation
                    row = page_idx // self.cards_per_row
                    col = page_idx % self.cards_per_row
                    x = col * self.card_width
                    y = self.page_height - (row + 1) * self.card_height
                    self.draw_card(c, x, y, card_data, rotated=False)
                else:
                    # Rotated orientation in remaining space
                    extra_idx = page_idx - normal_cards
                    # Place rotated cards in remaining width space
                    remaining_width = self.page_width - (self.cards_per_row * self.card_width)
                    if remaining_width >= self.card_height:
                        rotated_col = int(remaining_width / self.card_height)
                        row = extra_idx // rotated_col
                        col = extra_idx % rotated_col
                        x = self.cards_per_row * self.card_width + col * self.card_height
                        y = self.page_height - (row + 1) * self.card_width
                        self.draw_card(c, x, y, card_data, rotated=True)
            
            # Create new page if needed
            if (idx + 1) % self.cards_per_page == 0 and idx < len(cards) - 1:
                c.showPage()
        
        # Save PDF
        c.save()
        print(f"PDF generated successfully: {output_file}")
        print(f"Total cards: {len(cards)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate PDF cards from JSON data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python card_generator.py cards_data.json -o output.pdf
  python card_generator.py my_cards.json --page-size A4
        """
    )
    
    parser.add_argument(
        'input',
        help='Input JSON file containing card data'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='cards_output.pdf',
        help='Output PDF file (default: cards_output.pdf)'
    )
    
    parser.add_argument(
        '--page-size',
        choices=['letter', 'A4'],
        default='letter',
        help='Page size for the PDF (default: letter)'
    )
    
    parser.add_argument(
        '--auto-search',
        action='store_true',
        help='Automatically search and download images for cards based on their content'
    )
    
    parser.add_argument(
        '--no-gradients',
        action='store_true',
        help='Disable gradient effects on images (use original images as-is)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    # Set page size
    page_size = letter if args.page_size == 'letter' else A4
    
    # Generate PDF
    try:
        generator = CardGenerator(
            page_size=page_size, 
            auto_search_images=args.auto_search,
            gradient_enabled=not args.no_gradients
        )
        generator.generate_pdf(args.input, args.output)
        return 0
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
