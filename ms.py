import requests
import json
import time
import statistics
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExchangeLatencyTester:
    def __init__(self):
        self.results = {}
        
        # Updated exchange API endpoints
        self.endpoints = {
            'binance': 'https://api.binance.com/api/v3/time',
            'bybit': 'https://api.bybit.com/v5/market/time',
            'gateio': 'https://api.gateio.ws/api/v4/spot/time'
        }
        
        # Headers for REST API calls
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

    def test_rest_latency(self, exchange: str) -> Dict:
        """Test REST API latency for a specific exchange with one request"""
        endpoint = self.endpoints[exchange]
        
        logger.info(f"Testing REST latency for {exchange.upper()}")
        
        try:
            start_time = time.perf_counter()
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                logger.info(f"Request: {latency:.2f} ms (Status: {response.status_code})")
                return {
                    'exchange': exchange,
                    'test_type': 'rest',
                    'latency': latency,
                    'status_code': response.status_code,
                    'success': True
                }
            else:
                logger.warning(f"Request failed with status code {response.status_code}")
                return {
                    'exchange': exchange,
                    'test_type': 'rest',
                    'latency': float('inf'),
                    'status_code': response.status_code,
                    'success': False
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'exchange': exchange,
                'test_type': 'rest',
                'latency': float('inf'),
                'status_code': None,
                'success': False,
                'error': str(e)
            }

    def run_tests(self):
        """Run latency tests for all exchanges"""
        logger.info("Starting latency tests...")
        
        results = {}
        
        for exchange in ['binance', 'bybit', 'gateio']:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing {exchange.upper()}")
            logger.info(f"{'='*50}")
            
            # Test REST API
            result = self.test_rest_latency(exchange)
            results[exchange] = result
            
            time.sleep(1)  # Brief pause between exchanges
        
        self.results = results
        return results

    def print_results(self):
        """Print formatted test results"""
        if not self.results:
            logger.warning("No results to display. Run tests first.")
            return
        
        print("\n" + "="*80)
        print("LATENCY TEST RESULTS SUMMARY")
        print("="*80)
        
        for exchange, result in self.results.items():
            print(f"\n{exchange.upper()} Results:")
            
            if result['success']:
                print(f"  Latency: {result['latency']:.2f} ms")
                print(f"  Status Code: {result['status_code']}")
            else:
                print(f"  Request failed")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
                print(f"  Status Code: {result.get('status_code', 'N/A')}")

    def save_results_to_file(self, filename: Optional[str] = None):
        """Save results to a JSON file"""
        if not self.results:
            logger.warning("No results to save.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"latency_test_results_{timestamp}.json"
        
        try:
            # Convert inf values to strings for JSON serialization
            serializable_results = {}
            for key, result in self.results.items():
                serializable_result = result.copy()
                if 'latency' in serializable_result and serializable_result['latency'] == float('inf'):
                    serializable_result['latency'] = 'inf'
                serializable_results[key] = serializable_result
            
            with open(filename, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': serializable_results
                }, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main function to run the latency tests"""
    tester = ExchangeLatencyTester()
    
    try:
        # Run tests
        results = tester.run_tests()
        
        # Print results
        tester.print_results()
        
        # Save results to file
        tester.save_results_to_file()
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()