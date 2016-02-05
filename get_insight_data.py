import facebook
from pprintpp import pprint as pp

def get_insight_data(post_id="124616330906800_938376599530765", edge=""):
  # Fill in the values noted in previous steps here
  cfg = {
    "page_id"      : "124616330906800",  # Step 1
    "access_token" : "CAAW9dhL0jPQBAFQ9SLBLmhNxx5wrMqmfAZA1eiMtPzrZAzZA6IAxOooCxDwBgAo5SnXkzSm4wmU6ZAhdZC2JXzYYYVYdu8p0e8G45XjvxLVOjiygA4croj2ZCD7TNQZBdemxZB4x8rMamEvXi9IZC0RE2fUvvP7CcaHEzDQNB4SUkKawUuz6yQYNPCEdIXS4wyfwZD"   # Step 3
    }

  api = get_api(cfg)
  status = api.get_connections(post_id, "insights/")
  #pp(status)
  return status

def get_insight(graph):
   insight = graph.get(insights)
   pp(insight)


def get_api(cfg):
  graph = facebook.GraphAPI(cfg['access_token'])
  # Get page token to post as the page. You can skip
  # the following if you want to post as yourself.
  resp = graph.get_object('me/accounts')
  page_access_token = None
  for page in resp['data']:
    if page['id'] == cfg['page_id']:
      page_access_token = page['access_token']
  graph = facebook.GraphAPI(page_access_token)
  return graph
  # You can also skip the above if you get a page token:
  # http://stackoverflow.com/questions/8231877/facebook-access-token-for-pages
  # and make that long-lived token as in Step 3

def main():
  get_insight_data()
if __name__ == "__main__":
  main()
