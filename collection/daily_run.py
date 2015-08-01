from config import CREDENTIALS, SUBREDDITS
from crawler import MultiThreadedCrawler

def main():
	multi = MultiThreadedCrawler(CREDENTIALS, SUBREDDITS)
	multi.start()

if __name__ == '__main__':
	main()