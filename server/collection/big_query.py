import bigquery
import config
import pymongo
import datetime
import os

if __name__ == '__main__':
    project_id = os.environ.get('PROJECT_ID')
    service_account = os.environ.get('SERVICE_ACCOUNT')
    key = 'george-key.p12'
    client = bigquery.get_client(project_id, service_account=service_account,
                        private_key_file=key, readonly=True)
    tables = ['2007', '2008', '2009', '2010', '2011', '2012', 
              '2013', '2014', '2015_01', '2015_02', '2015_03', 
              '2015_04', '2015_05', '2015_06', '2015_07', 
              '2015_08', '2015_09']
    subreddits = ['"%s"' % item['subreddit'] 
                    for item in config.SUBREDDITS]
    for table in tables:
        print 'Querying table:', table
        query = 'SELECT * FROM [fh-bigquery:reddit_comments.{}] WHERE subreddit IN ({})'.format(table, ','.join(subreddits))
        job_id, _results = client.query(query)
        complete, row_count = client.check_job(job_id)
        if complete:
            print 'Downloading', table, row_count
            results = client.get_query_rows(job_id)
            records = [r for r in list(results)]
            for record in records:
                record['created_utc'] = datetime.datetime.utcfromtimestamp(record['created_utc'])
            db = pymongo.MongoClient()['reddit']
            if records:
                db.data_dump.insert_many(records)
