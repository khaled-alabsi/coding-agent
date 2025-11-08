"""Context and token analyzer for LLM interactions."""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ContextAnalyzer:
    """Analyze context and response lengths for LLM interactions."""

    def __init__(self, avg_chars_per_token: int = 4):
        """
        Initialize the analyzer.

        Args:
            avg_chars_per_token: Average characters per token (default: 4 for English)
        """
        self.avg_chars_per_token = avg_chars_per_token

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text (rough approximation).

        Args:
            text: Text to analyze

        Returns:
            Estimated token count
        """
        return len(text) // self.avg_chars_per_token

    def analyze_log_file(self, log_file_path: str) -> Dict:
        """
        Analyze an agent log file for context and response statistics.

        Args:
            log_file_path: Path to the agent_log_*.json file

        Returns:
            Dictionary with analysis results
        """
        log_path = Path(log_file_path)
        if not log_path.exists():
            return {"error": f"Log file not found: {log_file_path}"}

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except Exception as e:
            return {"error": f"Failed to read log file: {e}"}

        entries = log_data.get('entries', [])

        # Initialize statistics
        stats = {
            'total_requests': 0,
            'by_agent': {},
            'truncated_responses': [],
            'large_contexts': [],
            'max_context_tokens': 0,
            'max_response_tokens': 0,
            'avg_context_tokens': 0,
            'avg_response_tokens': 0
        }

        context_tokens = []
        response_tokens = []

        # Process each entry
        for entry in entries:
            if entry.get('type') != 'llm_request':
                continue

            stats['total_requests'] += 1
            agent = entry.get('agent_name', 'unknown')

            # Initialize agent stats
            if agent not in stats['by_agent']:
                stats['by_agent'][agent] = {
                    'requests': 0,
                    'total_context_chars': 0,
                    'total_response_chars': 0,
                    'avg_context_tokens': 0,
                    'avg_response_tokens': 0
                }

            stats['by_agent'][agent]['requests'] += 1

            # Calculate context size
            context_text = self._extract_context(entry)
            context_chars = len(context_text)
            context_toks = self.estimate_tokens(context_text)
            context_tokens.append(context_toks)

            stats['by_agent'][agent]['total_context_chars'] += context_chars

            # Check for large contexts
            if context_toks > 6000:
                stats['large_contexts'].append({
                    'agent': agent,
                    'request_id': entry.get('request_id'),
                    'estimated_tokens': context_toks,
                    'chars': context_chars
                })

            if context_toks > stats['max_context_tokens']:
                stats['max_context_tokens'] = context_toks

            # Analyze response
            self._analyze_response(entry, entries, agent, stats, response_tokens)

        # Calculate averages
        if context_tokens:
            stats['avg_context_tokens'] = sum(context_tokens) // len(context_tokens)
        if response_tokens:
            stats['avg_response_tokens'] = sum(response_tokens) // len(response_tokens)

        # Calculate per-agent averages
        for agent, agent_stats in stats['by_agent'].items():
            if agent_stats['requests'] > 0:
                agent_stats['avg_context_tokens'] = (
                    self.estimate_tokens(' ' * agent_stats['total_context_chars'])
                    // agent_stats['requests']
                )
                agent_stats['avg_response_tokens'] = (
                    self.estimate_tokens(' ' * agent_stats['total_response_chars'])
                    // agent_stats['requests']
                )

        return stats

    def _extract_context(self, entry: Dict) -> str:
        """Extract full context text from an LLM request entry."""
        messages = entry.get('messages', [])
        system_message = entry.get('system_message', '')

        context_text = system_message
        for msg in messages:
            context_text += msg.get('content', '')

        return context_text

    def _analyze_response(
        self,
        entry: Dict,
        entries: List[Dict],
        agent: str,
        stats: Dict,
        response_tokens: List[int]
    ):
        """Analyze response for a given request."""
        request_id = entry.get('request_id')
        response_entry = next(
            (e for e in entries
             if e.get('type') == 'llm_response'
             and e.get('request_id') == request_id),
            None
        )

        if not response_entry:
            return

        response_text = response_entry.get('response', '')
        response_chars = len(response_text)
        response_toks = self.estimate_tokens(response_text)
        response_tokens.append(response_toks)

        stats['by_agent'][agent]['total_response_chars'] += response_chars

        if response_toks > stats['max_response_tokens']:
            stats['max_response_tokens'] = response_toks

        # Check for potential truncation
        max_tokens = entry.get('max_tokens', 2000)
        if response_toks >= max_tokens * 0.95:
            stats['truncated_responses'].append({
                'agent': agent,
                'request_id': request_id,
                'response_tokens': response_toks,
                'max_tokens': max_tokens,
                'last_100_chars': response_text[-100:]
            })

    def print_analysis(self, stats: Dict):
        """
        Print formatted analysis results.

        Args:
            stats: Statistics dictionary from analyze_log_file()
        """
        print("=" * 80)
        print("CONTEXT & RESPONSE LENGTH ANALYSIS")
        print("=" * 80)

        if 'error' in stats:
            print(f"❌ {stats['error']}")
            return

        self._print_overall_stats(stats)
        self._print_agent_stats(stats)
        self._print_truncation_warnings(stats)
        self._print_large_context_warnings(stats)
        self._print_recommendations(stats)

        print("=" * 80)

    def _print_overall_stats(self, stats: Dict):
        """Print overall statistics."""
        print(f"\n📊 Overall Statistics:")
        print(f"   Total LLM Requests: {stats['total_requests']}")
        print(f"   Max Context Size: {stats['max_context_tokens']:,} tokens "
              f"(~{stats['max_context_tokens']*4:,} chars)")
        print(f"   Max Response Size: {stats['max_response_tokens']:,} tokens "
              f"(~{stats['max_response_tokens']*4:,} chars)")
        print(f"   Avg Context Size: {stats['avg_context_tokens']:,} tokens")
        print(f"   Avg Response Size: {stats['avg_response_tokens']:,} tokens")

    def _print_agent_stats(self, stats: Dict):
        """Print per-agent statistics."""
        print(f"\n🤖 Per-Agent Statistics:")
        for agent, agent_stats in stats['by_agent'].items():
            print(f"\n   {agent}:")
            print(f"      Requests: {agent_stats['requests']}")
            print(f"      Avg Context: {agent_stats['avg_context_tokens']:,} tokens")
            print(f"      Avg Response: {agent_stats['avg_response_tokens']:,} tokens")

    def _print_truncation_warnings(self, stats: Dict):
        """Print truncation warnings."""
        if not stats['truncated_responses']:
            return

        print(f"\n⚠️  Potentially Truncated Responses ({len(stats['truncated_responses'])}):")
        for tr in stats['truncated_responses'][:5]:
            print(f"\n   Agent: {tr['agent']}")
            print(f"   Request ID: {tr['request_id']}")
            print(f"   Response Tokens: {tr['response_tokens']:,} / {tr['max_tokens']:,}")
            print(f"   Last 100 chars: ...{tr['last_100_chars']}")

    def _print_large_context_warnings(self, stats: Dict):
        """Print large context warnings."""
        if not stats['large_contexts']:
            return

        print(f"\n📏 Large Context Warnings ({len(stats['large_contexts'])}):")
        for lc in stats['large_contexts'][:5]:
            print(f"   Agent: {lc['agent']} - {lc['estimated_tokens']:,} tokens")

    def _print_recommendations(self, stats: Dict):
        """Print recommendations based on analysis."""
        print(f"\n💡 Recommendations:")

        if stats['max_context_tokens'] > 6000:
            print(f"   ⚠️  Max context ({stats['max_context_tokens']:,} tokens) is high!")
            print(f"      Consider increasing context_window setting")
            recommended = max(8000, stats['max_context_tokens'] + 2000)
            print(f"      Recommended: context_window={recommended}")

        if stats['truncated_responses']:
            print(f"   ⚠️  Found {len(stats['truncated_responses'])} potentially truncated responses")
            print(f"      Consider increasing max_tokens setting")
            print(f"      Current max_tokens: {stats['truncated_responses'][0]['max_tokens']}")
            recommended_max = stats['max_response_tokens'] + 1000
            print(f"      Recommended: max_tokens={recommended_max}")

        if stats['max_context_tokens'] < 4000 and stats['max_response_tokens'] < 1500:
            print(f"   ✅ Context and response sizes look healthy!")
            print(f"      Current settings appear to be working well")

    def get_optimal_settings(self, log_file_path: str) -> Dict:
        """
        Analyze log and suggest optimal context_window and max_tokens.

        Args:
            log_file_path: Path to agent log file

        Returns:
            Dictionary with recommended settings
        """
        stats = self.analyze_log_file(log_file_path)

        if 'error' in stats:
            return stats

        # Calculate recommended settings with buffer
        recommended_context = max(8000, stats['max_context_tokens'] + 2000)
        recommended_max_tokens = max(2000, stats['max_response_tokens'] + 1000)

        return {
            'current_max_context': stats['max_context_tokens'],
            'current_max_response': stats['max_response_tokens'],
            'recommended_context_window': recommended_context,
            'recommended_max_tokens': recommended_max_tokens,
            'has_truncation_issues': len(stats['truncated_responses']) > 0,
            'has_large_contexts': len(stats['large_contexts']) > 0,
            'truncated_count': len(stats['truncated_responses']),
            'large_context_count': len(stats['large_contexts'])
        }

    def list_log_files(self, log_dir: str = "azure_agent") -> List[Dict]:
        """
        List all available log files with quick stats.

        Args:
            log_dir: Directory containing log files

        Returns:
            List of dictionaries with log file information
        """
        import glob

        log_pattern = f"{log_dir}/agent_log_*.json"
        log_files = sorted(glob.glob(log_pattern), reverse=True)

        results = []
        for log_path in log_files:
            log_name = Path(log_path).name
            timestamp_str = log_name.replace('agent_log_', '').replace('.json', '')

            # Parse timestamp
            try:
                dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = timestamp_str

            # Quick stats
            quick_stats = self.get_optimal_settings(log_path)

            if 'error' in quick_stats:
                status = "error"
            elif quick_stats['has_truncation_issues']:
                status = "truncation"
            else:
                status = "ok"

            results.append({
                'path': log_path,
                'name': log_name,
                'timestamp': formatted_time,
                'status': status,
                'max_context': quick_stats.get('current_max_context', 0),
                'max_response': quick_stats.get('current_max_response', 0)
            })

        return results
