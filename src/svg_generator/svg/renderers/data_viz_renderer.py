# src/svg_generator/svg/renderers/data_viz_renderer.py
"""
Data visualization renderer for SVG generation.
"""
import math
import logging
from typing import List, Dict, Any, Tuple, Optional, Union

from svg_generator.svg.shapes import ShapeFactory
from svg_generator.utils.colors import ColorUtils
from svg_generator.utils.text_utils import TextUtils

logger = logging.getLogger(__name__)

class DataVizRenderer:
    """
    Renders data visualizations as SVG elements.
    """
    
    def __init__(self, width: float = 800, height: float = 600):
        """Initialize data visualization renderer."""
        self.width = width
        self.height = height
        logger.debug(f"DataVizRenderer initialized: {width}x{height}")
    
    def generate_bar_chart(self, data: List[float], 
                          labels: Optional[List[str]] = None,
                          x: float = 50, y: float = 50,
                          width: float = 700, height: float = 400,
                          colors: Optional[List[str]] = None,
                          show_values: bool = True,
                          **attributes) -> List[Dict[str, Any]]:
        """Generate a bar chart visualization."""
        if not data:
            return []
            
        # Calculate dimensions
        bar_count = len(data)
        padding = 0.2  # Space between bars (20% of bar width)
        bar_width = width / (bar_count * (1 + padding))
        max_value = max(data)
        
        # Generate colors if not provided
        if not colors:
            base_color = attributes.get('fill', '#3366cc')
            colors = ColorUtils.generate_palette(base_color, bar_count, 'analogous')
        
        elements = []
        
        # Draw background/frame if specified
        if attributes.get('show_frame', True):
            frame = ShapeFactory.create_rect(
                x, y, width, height,
                fill="none", 
                stroke=attributes.get('frame_stroke', '#cccccc'),
                stroke_width=attributes.get('frame_stroke_width', '1')
            )
            elements.append(frame)
            
        # Draw bars
        for i, value in enumerate(data):
            # Skip zero or negative values
            if value <= 0:
                continue
                
            # Calculate bar height and position
            bar_height = (value / max_value) * height
            bar_x = x + i * bar_width * (1 + padding)
            bar_y = y + height - bar_height
            
            # Create bar element
            bar = ShapeFactory.create_rect(
                bar_x, bar_y, bar_width, bar_height,
                fill=colors[i % len(colors)],
                stroke=attributes.get('stroke', 'none'),
                stroke_width=attributes.get('stroke_width', '0')
            )
            elements.append(bar)
            
            # Add value label if requested
            if show_values:
                # Create text for value
                value_str = str(round(value, 1))
                
                text_element = TextUtils.create_text_element(
                    text=value_str,
                    x=bar_x + bar_width/2,
                    y=bar_y - 5,
                    font_size=attributes.get('font_size', 12),
                    font_family=attributes.get('font_family', 'Arial'),
                    fill=attributes.get('text_fill', '#333333'),
                    text_anchor='middle'
                )
                elements.append(text_element)
            
            # Add label if provided
            if labels and i < len(labels):
                label_text = TextUtils.create_text_element(
                    text=labels[i],
                    x=bar_x + bar_width/2,
                    y=y + height + 15,
                    font_size=attributes.get('font_size', 12),
                    font_family=attributes.get('font_family', 'Arial'),
                    fill=attributes.get('text_fill', '#333333'),
                    text_anchor='middle'
                )
                elements.append(label_text)
                
        return elements
    
    def generate_pie_chart(self, data: List[float], 
                         labels: Optional[List[str]] = None,
                         cx: float = 400, cy: float = 300,
                         radius: float = 150,
                         colors: Optional[List[str]] = None,
                         **attributes) -> List[Dict[str, Any]]:
        """Generate a pie chart visualization."""
        if not data or sum(data) == 0:
            return []
            
        # Generate colors if not provided
        if not colors:
            base_color = attributes.get('fill', '#3366cc')
            colors = ColorUtils.generate_palette(base_color, len(data), 'analogous')
        
        elements = []
        total = sum(data)
        
        # Track starting angle
        start_angle = attributes.get('start_angle', 0)
        
        # Draw pie slices
        for i, value in enumerate(data):
            # Skip zero or negative values
            if value <= 0:
                continue
                
            # Calculate slice angles
            slice_angle = (value / total) * 360
            end_angle = start_angle + slice_angle
            
            # Create slice path
            large_arc = 1 if slice_angle > 180 else 0
            
            # Calculate start and end points
            start_x = cx + radius * math.cos(math.radians(start_angle))
            start_y = cy + radius * math.sin(math.radians(start_angle))
            end_x = cx + radius * math.cos(math.radians(end_angle))
            end_y = cy + radius * math.sin(math.radians(end_angle))
            
            # Create path
            path_data = f"M {cx},{cy} L {start_x},{start_y} "
            path_data += f"A {radius},{radius} 0 {large_arc},1 {end_x},{end_y} Z"
            
            # Create slice element
            slice_color = colors[i % len(colors)]
            slice_element = ShapeFactory.create_path(
                path_data,
                fill=slice_color,
                stroke=attributes.get('stroke', '#ffffff'),
                stroke_width=attributes.get('stroke_width', '1')
            )
            elements.append(slice_element)
            
            # Add label if provided
            if labels and i < len(labels):
                # Position label at the middle of the slice
                label_angle = start_angle + slice_angle / 2
                label_radius = radius * 0.7  # Position inside the slice
                
                label_x = cx + label_radius * math.cos(math.radians(label_angle))
                label_y = cy + label_radius * math.sin(math.radians(label_angle))
                
                # Create text element
                # For competition SVGs, consider skipping text elements
                if not attributes.get('skip_text', False):
                    text_element = TextUtils.create_text_element(
                        text=labels[i],
                        x=label_x,
                        y=label_y,
                        font_size=attributes.get('font_size', 12),
                        font_family=attributes.get('font_family', 'Arial'),
                        fill=ColorUtils.get_contrast_color(slice_color),
                        text_anchor='middle',
                        dominant_baseline='middle'
                    )
                    elements.append(text_element)
            
            # Update start angle for next slice
            start_angle = end_angle
                
        return elements
    
    def generate_line_chart(self, data_series: List[List[float]], 
                          x_labels: Optional[List[str]] = None,
                          x: float = 50, y: float = 50,
                          width: float = 700, height: float = 400,
                          colors: Optional[List[str]] = None,
                          show_points: bool = True,
                          **attributes) -> List[Dict[str, Any]]:
        """Generate a line chart visualization."""
        if not data_series or not data_series[0]:
            return []
            
        elements = []
        
        # Find min and max values across all series
        all_values = [val for series in data_series for val in series]
        min_value = min(all_values) if all_values else 0
        max_value = max(all_values) if all_values else 1
        
        # Adjust min and max for better visualization
        value_range = max_value - min_value
        min_value = min_value - value_range * 0.05
        max_value = max_value + value_range * 0.05
        
        # Generate colors if not provided
        if not colors:
            base_color = attributes.get('fill', '#3366cc')
            colors = ColorUtils.generate_palette(base_color, len(data_series), 'analogous')
        
        # Draw background/frame if specified
        if attributes.get('show_frame', True):
            frame = ShapeFactory.create_rect(
                x, y, width, height,
                fill="none", 
                stroke=attributes.get('frame_stroke', '#cccccc'),
                stroke_width=attributes.get('frame_stroke_width', '1')
            )
            elements.append(frame)
            
        # Draw each data series
        for series_idx, series in enumerate(data_series):
            if not series:
                continue
                
            points = []
            for i, value in enumerate(series):
                # Calculate point position
                point_x = x + (i / (len(series) - 1)) * width if len(series) > 1 else x
                point_y = y + height - ((value - min_value) / (max_value - min_value)) * height
                
                points.append((point_x, point_y))
                
            # Create path for the line
            path_data = f"M {points[0][0]},{points[0][1]}"
            for point in points[1:]:
                path_data += f" L {point[0]},{point[1]}"
                
            # Create line element
            line_color = colors[series_idx % len(colors)]
            line_element = ShapeFactory.create_path(
                path_data,
                fill="none",
                stroke=line_color,
                stroke_width=attributes.get('stroke_width', '2')
            )
            elements.append(line_element)
            
            # Add points if requested
            if show_points:
                for point_x, point_y in points:
                    point_element = ShapeFactory.create_circle(
                        point_x, point_y, 
                        radius=attributes.get('point_radius', 4),
                        fill=attributes.get('point_fill', '#ffffff'),
                        stroke=line_color,
                        stroke_width=attributes.get('point_stroke_width', '2')
                    )
                    elements.append(point_element)
        
        # Add x-axis labels if provided
        if x_labels:
            label_spacing = width / (len(x_labels) - 1) if len(x_labels) > 1 else width
            
            for i, label in enumerate(x_labels):
                label_x = x + i * label_spacing
                label_y = y + height + 15
                
                label_element = TextUtils.create_text_element(
                    text=label,
                    x=label_x,
                    y=label_y,
                    font_size=attributes.get('font_size', 12),
                    font_family=attributes.get('font_family', 'Arial'),
                    fill=attributes.get('text_fill', '#333333'),
                    text_anchor='middle'
                )
                elements.append(label_element)
                
        return elements
    
    def generate_scatter_plot(self, x_values: List[float], y_values: List[float],
                           x: float = 50, y: float = 50,
                           width: float = 700, height: float = 400,
                           color: str = '#3366cc',
                           **attributes) -> List[Dict[str, Any]]:
        """Generate a scatter plot visualization."""
        if not x_values or not y_values or len(x_values) != len(y_values):
            return []
            
        elements = []
        
        # Find min and max values
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        
        # Adjust ranges for better visualization
        x_range = max_x - min_x
        y_range = max_y - min_y
        
        min_x = min_x - x_range * 0.05
        max_x = max_x + x_range * 0.05
        min_y = min_y - y_range * 0.05
        max_y = max_y + y_range * 0.05
        
        # Draw background/frame if specified
        if attributes.get('show_frame', True):
            frame = ShapeFactory.create_rect(
                x, y, width, height,
                fill="none", 
                stroke=attributes.get('frame_stroke', '#cccccc'),
                stroke_width=attributes.get('frame_stroke_width', '1')
            )
            elements.append(frame)
            
        # Draw each data point
        for i in range(len(x_values)):
            # Calculate point position
            point_x = x + ((x_values[i] - min_x) / (max_x - min_x)) * width
            point_y = y + height - ((y_values[i] - min_y) / (max_y - min_y)) * height
            
            # Create point element
            point_element = ShapeFactory.create_circle(
                point_x, point_y, 
                radius=attributes.get('point_radius', 5),
                fill=color,
                stroke=attributes.get('stroke', 'none'),
                stroke_width=attributes.get('stroke_width', '0')
            )
            elements.append(point_element)
                
        return elements
