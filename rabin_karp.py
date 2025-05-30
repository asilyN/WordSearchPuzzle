"""
Rabin-Karp algorithm implementation for efficient string matching
"""

class RabinKarp:
    def __init__(self, base=256, prime=101):
        """
        Initialize Rabin-Karp algorithm with base and prime number
        
        Args:
            base: Base for hash calculation (number of characters in alphabet)
            prime: Prime number for modular arithmetic
        """
        self.base = base
        self.prime = prime
    
    def _hash(self, text, length):
        """Calculate hash value for a string of given length"""
        hash_value = 0
        for i in range(length):
            hash_value = (hash_value * self.base + ord(text[i])) % self.prime
        return hash_value
    
    def _rolling_hash(self, old_hash, old_char, new_char, length):
        """Calculate rolling hash by removing old character and adding new one"""
        # Calculate base^(length-1) % prime
        h = pow(self.base, length - 1, self.prime)
        
        # Remove old character and add new character
        new_hash = (old_hash - ord(old_char) * h) % self.prime
        new_hash = (new_hash * self.base + ord(new_char)) % self.prime
        
        # Handle negative hash values
        new_hash = (new_hash + self.prime) % self.prime
        
        return new_hash
    
    def search(self, pattern, text):
        """
        Search for pattern in text using Rabin-Karp algorithm
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            
        Returns:
            List of starting indices where pattern is found
        """
        if not pattern or not text or len(pattern) > len(text):
            return []
        
        pattern_len = len(pattern)
        text_len = len(text)
        pattern_hash = self._hash(pattern, pattern_len)
        text_hash = self._hash(text, pattern_len)
        
        matches = []
        
        # Check first window
        if pattern_hash == text_hash and text[:pattern_len] == pattern:
            matches.append(0)
        
        # Rolling hash for remaining windows
        for i in range(1, text_len - pattern_len + 1):
            # Calculate hash for current window
            text_hash = self._rolling_hash(
                text_hash, 
                text[i - 1], 
                text[i + pattern_len - 1], 
                pattern_len
            )
            
            # If hash matches, verify with string comparison
            if pattern_hash == text_hash:
                if text[i:i + pattern_len] == pattern:
                    matches.append(i)
        
        return matches
    
    def search_multiple(self, patterns, text):
        """
        Search for multiple patterns in text
        
        Args:
            patterns: List of patterns to search for
            text: Text to search in
            
        Returns:
            Dictionary mapping pattern to list of indices
        """
        results = {}
        for pattern in patterns:
            results[pattern] = self.search(pattern, text)
        return results
    
    def contains_pattern(self, pattern, text):
        """
        Check if pattern exists in text
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            
        Returns:
            Boolean indicating if pattern is found
        """
        return len(self.search(pattern, text)) > 0
    
    def contains_unwanted_pattern(self, text):
        """
        Check if text contains any unwanted patterns (simple implementation)
        This can be extended with a list of unwanted words
        
        Args:
            text: Text to check
            
        Returns:
            Boolean indicating if unwanted patterns are found
        """
        # Simple check for common unwanted short words
        unwanted_patterns = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL']
        
        for pattern in unwanted_patterns:
            if self.contains_pattern(pattern, text.upper()):
                return True
        
        return False
    
    def find_all_substrings(self, text, min_length=3):
        """
        Find all substrings of minimum length in text
        
        Args:
            text: Text to analyze
            min_length: Minimum length of substrings to find
            
        Returns:
            Set of all substrings found
        """
        substrings = set()
        
        for length in range(min_length, len(text) + 1):
            for i in range(len(text) - length + 1):
                substrings.add(text[i:i + length])
        
        return substrings
    
    def verify_grid_integrity(self, grid, placed_words):
        """
        Verify that a grid only contains intended words using Rabin-Karp
        
        Args:
            grid: 2D grid of characters
            placed_words: List of words that should be in the grid
            
        Returns:
            Boolean indicating if grid integrity is maintained
        """
        # Extract all possible strings from the grid
        all_strings = self._extract_all_strings(grid)
        
        # Check each string for unwanted patterns
        for string in all_strings:
            if len(string) >= 3:  # Only check strings of length 3 or more
                # Skip if this is one of our intended words
                if string in placed_words or string[::-1] in placed_words:
                    continue
                
                # Check if this forms unwanted words
                if self.contains_unwanted_pattern(string):
                    return False
        
        return True
    
    def _extract_all_strings(self, grid):
        """Extract all possible strings from a grid in all directions"""
        strings = []
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        # Horizontal strings
        for row in range(rows):
            current_string = ""
            for col in range(cols):
                if grid[row][col] != ' ':
                    current_string += grid[row][col]
                else:
                    if len(current_string) >= 3:
                        strings.append(current_string)
                    current_string = ""
            if len(current_string) >= 3:
                strings.append(current_string)
        
        # Vertical strings
        for col in range(cols):
            current_string = ""
            for row in range(rows):
                if grid[row][col] != ' ':
                    current_string += grid[row][col]
                else:
                    if len(current_string) >= 3:
                        strings.append(current_string)
                    current_string = ""
            if len(current_string) >= 3:
                strings.append(current_string)
        
        # Diagonal strings (both directions)
        # Main diagonals (top-left to bottom-right)
        for start_row in range(rows):
            for start_col in range(cols):
                # Down-right diagonal
                current_string = ""
                row, col = start_row, start_col
                while row < rows and col < cols:
                    if grid[row][col] != ' ':
                        current_string += grid[row][col]
                    else:
                        if len(current_string) >= 3:
                            strings.append(current_string)
                        current_string = ""
                    row += 1
                    col += 1
                if len(current_string) >= 3:
                    strings.append(current_string)
                
                # Down-left diagonal
                current_string = ""
                row, col = start_row, start_col
                while row < rows and col >= 0:
                    if grid[row][col] != ' ':
                        current_string += grid[row][col]
                    else:
                        if len(current_string) >= 3:
                            strings.append(current_string)
                        current_string = ""
                    row += 1
                    col -= 1
                if len(current_string) >= 3:
                    strings.append(current_string)
        
        return strings
