import config
from crawler import MultiThreadedCrawler

def main():
    multi = MultiThreadedCrawler(config.SUBREDDITS)
    multi.start()

if __name__ == '__main__':
    main()