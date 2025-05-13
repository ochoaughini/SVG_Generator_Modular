# src/svg_generator/utils/math_utils.py
"""
Mathematical utilities for SVG generation.
"""
import math
import random
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union, Callable
import logging

logger = logging.getLogger(__name__)

class MathUtils:
    """
    Provides mathematical functions and utilities for SVG generation.
    
    This class contains methods for various mathematical operations,
    interpolations, and transformations used in SVG generation.
    """
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """
        Linear interpolation between two values.
        
        Args:
            a: Start value
            b: End value
            t: Interpolation factor (0-1)
            
        Returns:
            Interpolated value
        """
        return a + (b - a) * t
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp a value between a minimum and maximum.
        
        Args:
            value: Value to clamp
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Clamped value
        """
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def map_range(value: float, from_min: float, from_max: float, 
                 to_min: float, to_max: float) -> float:
        """
        Map a value from one range to another.
        
        Args:
            value: Value to map
            from_min: Original range minimum
            from_max: Original range maximum
            to_min: Target range minimum
            to_max: Target range maximum
            
        Returns:
            Mapped value
        """
        # Avoid division by zero
        if from_max == from_min:
            return to_min
            
        # Calculate normalized position in original range
        normalized = (value - from_min) / (from_max - from_min)
        
        # Map to new range
        return to_min + normalized * (to_max - to_min)
    
    @staticmethod
    def ease_in_out(t: float, power: float = 2.0) -> float:
        """
        Smooth ease-in-out interpolation.
        
        Args:
            t: Input value (0-1)
            power: Power factor (higher = more pronounced easing)
            
        Returns:
            Eased value (0-1)
        """
        if t < 0.5:
            return 0.5 * math.pow(2 * t, power)
        else:
            return 1 - 0.5 * math.pow(2 * (1 - t), power)
    
    @staticmethod
    def ease_in(t: float, power: float = 2.0) -> float:
        """
        Ease-in interpolation.
        
        Args:
            t: Input value (0-1)
            power: Power factor (higher = more pronounced easing)
            
        Returns:
            Eased value (0-1)
        """
        return math.pow(t, power)
    
    @staticmethod
    def ease_out(t: float, power: float = 2.0) -> float:
        """
        Ease-out interpolation.
        
        Args:
            t: Input value (0-1)
            power: Power factor (higher = more pronounced easing)
            
        Returns:
            Eased value (0-1)
        """
        return 1 - math.pow(1 - t, power)
    
    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Calculate the Euclidean distance between two points.
        
        Args:
            p1: First point (x, y)
            p2: Second point (x, y)
            
        Returns:
            Distance between the points
        """
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def angle_between(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Calculate the angle between two points, in degrees.
        
        Args:
            p1: First point (x, y)
            p2: Second point (x, y)
            
        Returns:
            Angle in degrees (0-360)
        """
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Convert to 0-360 range
        if angle_deg < 0:
            angle_deg += 360
            
        return angle_deg
    
    @staticmethod
    def point_on_circle(center: Tuple[float, float], radius: float, 
                       angle_deg: float) -> Tuple[float, float]:
        """
        Calculate a point on a circle given center, radius, and angle.
        
        Args:
            center: Circle center (x, y)
            radius: Circle radius
            angle_deg: Angle in degrees
            
        Returns:
            Point coordinates (x, y)
        """
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        
        return (x, y)
    
    @staticmethod
    def distribute_values(start: float, end: float, count: int, 
                         distribution: str = 'linear') -> List[float]:
        """
        Distribute values between start and end according to a distribution.
        
        Args:
            start: Start value
            end: End value
            count: Number of values to generate
            distribution: Distribution type ('linear', 'exponential', 'logarithmic')
            
        Returns:
            List of distributed values
        """
        values = []
        
        if count <= 0:
            return values
            
        if count == 1:
            return [start]
            
        if distribution == 'linear':
            # Linear distribution
            for i in range(count):
                t = i / (count - 1)
                values.append(start + t * (end - start))
                
        elif distribution == 'exponential':
            # Exponential distribution (power = 2)
            for i in range(count):
                t = i / (count - 1)
                # Apply quadratic easing
                t_eased = t * t
                values.append(start + t_eased * (end - start))
                
        elif distribution == 'logarithmic':
            # Logarithmic distribution (inverse of exponential)
            for i in range(count):
                t = i / (count - 1)
                # Apply square root easing
                t_eased = math.sqrt(t)
                values.append(start + t_eased * (end - start))
                
        else:
            # Default to linear if distribution not recognized
            logger.warning(f"Unknown distribution '{distribution}', using linear.")
            for i in range(count):
                t = i / (count - 1)
                values.append(start + t * (end - start))
        
        return values
    
    @staticmethod
    def generate_perlin_noise(width: int, height: int, scale: float = 0.1, 
                            octaves: int = 1, persistence: float = 0.5, 
                            lacunarity: float = 2.0, seed: Optional[int] = None) -> List[List[float]]:
        """
        Generate 2D Perlin noise.
        
        This method requires the numpy package.
        
        Args:
            width: Width of the noise grid
            height: Height of the noise grid
            scale: Scale of the noise (smaller = more zoomed out)
            octaves: Number of octaves (detail layers)
            persistence: How much each octave contributes
            lacunarity: How frequency increases with each octave
            seed: Random seed
            
        Returns:
            2D list of noise values (0-1)
        """
        try:
            # Set random seed if provided
            if seed is not None:
                np.random.seed(seed)
                
            # Initialize the noise grid
            noise = [[0 for _ in range(width)] for _ in range(height)]
            
            # Generate noise for each point
            for y in range(height):
                for x in range(width):
                    # Initialize amplitude, frequency, and noise value
                    amplitude = 1.0
                    frequency = 1.0
                    noise_value = 0.0
                    
                    # Generate noise with multiple octaves
                    for i in range(octaves):
                        # Calculate sample points based on frequency and scale
                        sample_x = x * scale * frequency
                        sample_y = y * scale * frequency
                        
                        # Use numpy's implementation or a simple alternative
                        # (simplified approximation - real perlin noise is more complex)
                        perlin_value = np.random.uniform(0, 1) - 0.5
                        
                        # Add weighted noise to the total
                        noise_value += perlin_value * amplitude
                        
                        # Update amplitude and frequency for next octave
                        amplitude *= persistence
                        frequency *= lacunarity
                        
                    # Store noise value in the grid
                    noise[y][x] = noise_value
                    
            # Normalize to 0-1 range
            min_val = min(min(row) for row in noise)
            max_val = max(max(row) for row in noise)
            
            for y in range(height):
                for x in range(width):
                    noise[y][x] = (noise[y][x] - min_val) / (max_val - min_val)
                    
            return noise
            
        except Exception as e:
            logger.error(f"Error generating Perlin noise: {e}")
            # Fallback to random noise
            return [[random.random() for _ in range(width)] for _ in range(height)]
    
    @staticmethod
    def generate_wave(length: int, amplitude: float = 1.0, frequency: float = 1.0,
                     wave_type: str = 'sine', phase: float = 0.0) -> List[float]:
        """
        Generate wave values.
        
        Args:
            length: Number of points to generate
            amplitude: Wave amplitude
            frequency: Wave frequency
            wave_type: Type of wave ('sine', 'square', 'triangle', 'sawtooth')
            phase: Phase offset in radians
            
        Returns:
            List of wave values
        """
        values = []
        
        for i in range(length):
            t = i / (length - 1) if length > 1 else 0
            angle = 2 * math.pi * frequency * t + phase
            
            if wave_type == 'sine':
                # Sine wave
                value = amplitude * math.sin(angle)
                
            elif wave_type == 'square':
                # Square wave
                value = amplitude if math.sin(angle) >= 0 else -amplitude
                
            elif wave_type == 'triangle':
                # Triangle wave
                value = amplitude * (1 - 2 * abs((angle / (2 * math.pi)) % 1 - 0.5))
                
            elif wave_type == 'sawtooth':
                # Sawtooth wave
                value = amplitude * (2 * ((angle / (2 * math.pi)) % 1) - 1)
                
            else:
                # Default to sine if type not recognized
                logger.warning(f"Unknown wave type '{wave_type}', using sine.")
                value = amplitude * math.sin(angle)
                
            values.append(value)
            
        return values
    
    @staticmethod
    def smooth_values(values: List[float], window_size: int = 3) -> List[float]:
        """
        Apply a moving average smoothing to a list of values.
        
        Args:
            values: List of values to smooth
            window_size: Size of the moving average window
            
        Returns:
            Smoothed values
        """
        if window_size <= 1 or len(values) <= window_size:
            return values[:]
            
        # Ensure window size is odd for centered window
        if window_size % 2 == 0:
            window_size += 1
            
        half_window = window_size // 2
        smoothed = []
        
        for i in range(len(values)):
            # Calculate window boundaries
            start = max(0, i - half_window)
            end = min(len(values), i + half_window + 1)
            
            # Calculate average within window
            window_values = values[start:end]
            smoothed.append(sum(window_values) / len(window_values))
            
        return smoothed
    
    @staticmethod
    def rotate_matrix(matrix: List[List[float]], angle_deg: float) -> List[List[float]]:
        """
        Rotate a 2D matrix around its center.
        
        This method requires numpy.
        
        Args:
            matrix: 2D list representing the matrix
            angle_deg: Rotation angle in degrees
            
        Returns:
            Rotated matrix
        """
        try:
            # Convert to numpy array for easier rotation
            arr = np.array(matrix)
            
            # Get dimensions
            rows, cols = arr.shape
            
            # Calculate center
            center_x = cols / 2
            center_y = rows / 2
            
            # Convert angle to radians
            angle_rad = math.radians(angle_deg)
            
            # Create rotation matrix
            cos_theta = math.cos(angle_rad)
            sin_theta = math.sin(angle_rad)
            
            # Create output array
            rotated = np.zeros_like(arr)
            
            # Apply rotation to each point
            for y in range(rows):
                for x in range(cols):
                    # Translate to origin
                    x_centered = x - center_x
                    y_centered = y - center_y
                    
                    # Rotate
                    x_rot = x_centered * cos_theta - y_centered * sin_theta
                    y_rot = x_centered * sin_theta + y_centered * cos_theta
                    
                    # Translate back and round to get source pixel
                    src_x = int(round(x_rot + center_x))
                    src_y = int(round(y_rot + center_y))
                    
                    # Check if source point is within bounds
                    if 0 <= src_x < cols and 0 <= src_y < rows:
                        rotated[y, x] = arr[src_y, src_x]
            
            # Convert back to list
            return rotated.tolist()
            
        except Exception as e:
            logger.error(f"Error rotating matrix: {e}")
            return matrix  # Return original if rotation fails
    
    @staticmethod
    def apply_function_map(width: int, height: int, 
                         func: Callable[[float, float], float]) -> List[List[float]]:
        """
        Apply a 2D function to create a map of values.
        
        Args:
            width: Width of the output map
            height: Height of the output map
            func: Function that takes normalized (x, y) coordinates and returns a value
            
        Returns:
            2D list of function values
        """
        result = []
        
        for y in range(height):
            row = []
            
            for x in range(width):
                # Normalize coordinates to 0-1 range
                norm_x = x / (width - 1) if width > 1 else 0
                norm_y = y / (height - 1) if height > 1 else 0
                
                # Apply function
                value = func(norm_x, norm_y)
                row.append(value)
                
            result.append(row)
            
        return result
    
    @staticmethod
    def matrix_to_contours(matrix: List[List[float]], 
                         levels: List[float], 
                         smooth: bool = True) -> List[List[Tuple[float, float]]]:
        """
        Extract contour lines from a 2D value matrix.
        
        Args:
            matrix: 2D list of values
            levels: List of contour levels to extract
            smooth: Whether to smooth the contours
            
        Returns:
            List of contours, each contour is a list of (x, y) points
        """
        # This is a simplified contour extraction algorithm
        # Real implementations would use marching squares or similar methods
        
        # Placeholder implementation - would need a proper algorithm for real use
        # This just returns some sample contours for illustration
        contours = []
        
        # Mock contour data (circles of different radii)
        height = len(matrix)
        width = len(matrix[0]) if height > 0 else 0
        
        center_x = width / 2
        center_y = height / 2
        
        for i, level in enumerate(levels):
            # Create a circular contour
            radius = min(width, height) * (0.2 + 0.1 * i)
            
            contour = []
            points = 50  # Number of points on the contour
            
            for j in range(points):
                angle = 2 * math.pi * j / points
                
                # Basic circle with some noise
                r = radius * (1 + 0.1 * math.sin(5 * angle) * level)
                
                x = center_x + r * math.cos(angle)
                y = center_y + r * math.sin(angle)
                
                contour.append((x, y))
                
            contours.append(contour)
            
        # Note: In a real implementation, this would analyze the matrix and
        # extract actual contours using proper algorithms
        
        return contours
