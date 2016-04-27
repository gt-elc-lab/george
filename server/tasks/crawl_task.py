import task
from collection import crawler
from collection import config

class CrawlTask(task.Task):
    """ Task for scraping reddit """
    @staticmethod
    def execute():
        crawler.MultiThreadedCrawler([{'name': 'Georgia Tech', 'subreddit': 'gatech'}]).start()
        return

if __name__ == '__main__':
    CrawlTask.execute()