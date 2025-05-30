"""
Leaderboard management with persistent file storage
"""

import json
import os
from datetime import datetime

class Leaderboard:
    def __init__(self, filename="scores.txt"):
        """Initialize leaderboard with file storage"""
        self.filename = filename
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        """Load scores from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as file:
                    self.scores = json.load(file)
            else:
                self.scores = []
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, start with empty scores
            self.scores = []
            self.save_scores()
    
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.scores, file, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, name, score, rank):
        """Add a new score to the leaderboard"""
        score_entry = {
            'name': name.strip(),
            'score': score,
            'rank': rank,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.scores.append(score_entry)
        
        # Sort scores by score (descending) and then by rank
        self.scores.sort(key=lambda x: (-x['score'], self._rank_to_number(x['rank'])))
        
        # Keep only top 100 scores to prevent file from growing too large
        self.scores = self.scores[:100]
        
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        """Get top scores from leaderboard"""
        return self.scores[:limit]
    
    def get_player_scores(self, player_name):
        """Get all scores for a specific player"""
        player_scores = [score for score in self.scores if score['name'].lower() == player_name.lower()]
        return sorted(player_scores, key=lambda x: -x['score'])
    
    def get_player_best_score(self, player_name):
        """Get the best score for a specific player"""
        player_scores = self.get_player_scores(player_name)
        return player_scores[0] if player_scores else None
    
    def get_rank_statistics(self):
        """Get statistics about rank distribution"""
        rank_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for score in self.scores:
            rank = score.get('rank', 'D')
            if rank in rank_counts:
                rank_counts[rank] += 1
        
        return rank_counts
    
    def get_average_score(self):
        """Get the average score across all entries"""
        if not self.scores:
            return 0
        
        total_score = sum(score['score'] for score in self.scores)
        return total_score / len(self.scores)
    
    def get_score_percentile(self, score):
        """Get the percentile ranking for a given score"""
        if not self.scores:
            return 100
        
        better_scores = sum(1 for s in self.scores if s['score'] > score)
        percentile = (1 - better_scores / len(self.scores)) * 100
        return round(percentile, 1)
    
    def is_high_score(self, score, top_n=10):
        """Check if a score qualifies as a high score (top N)"""
        if len(self.scores) < top_n:
            return True
        
        nth_best_score = sorted([s['score'] for s in self.scores], reverse=True)[top_n - 1]
        return score >= nth_best_score
    
    def clear_scores(self):
        """Clear all scores (admin function)"""
        self.scores = []
        self.save_scores()
    
    def export_scores(self, export_filename):
        """Export scores to a different file"""
        try:
            with open(export_filename, 'w') as file:
                json.dump(self.scores, file, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting scores: {e}")
            return False
    
    def import_scores(self, import_filename):
        """Import scores from a different file"""
        try:
            with open(import_filename, 'r') as file:
                imported_scores = json.load(file)
            
            # Validate imported data
            for score in imported_scores:
                if self._validate_score_entry(score):
                    self.scores.append(score)
            
            # Re-sort and save
            self.scores.sort(key=lambda x: (-x['score'], self._rank_to_number(x['rank'])))
            self.scores = self.scores[:100]  # Keep top 100
            self.save_scores()
            return True
        
        except Exception as e:
            print(f"Error importing scores: {e}")
            return False
    
    def _validate_score_entry(self, entry):
        """Validate a score entry has required fields"""
        required_fields = ['name', 'score', 'rank']
        return all(field in entry for field in required_fields)
    
    def _rank_to_number(self, rank):
        """Convert rank letter to number for sorting"""
        rank_values = {'S': 1, 'A': 2, 'B': 3, 'C': 4, 'D': 5}
        return rank_values.get(rank, 6)
    
    def get_leaderboard_summary(self):
        """Get a summary of leaderboard statistics"""
        if not self.scores:
            return {
                'total_players': 0,
                'total_games': 0,
                'average_score': 0,
                'best_score': 0,
                'rank_distribution': {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
            }
        
        unique_players = len(set(score['name'] for score in self.scores))
        total_games = len(self.scores)
        average_score = self.get_average_score()
        best_score = max(score['score'] for score in self.scores)
        rank_distribution = self.get_rank_statistics()
        
        return {
            'total_players': unique_players,
            'total_games': total_games,
            'average_score': round(average_score, 1),
            'best_score': best_score,
            'rank_distribution': rank_distribution
        }
