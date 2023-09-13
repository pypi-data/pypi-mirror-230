from            .server import start_server

if __name__ == '__main__':
  password  = env['MSFRPC_PASSWORD']
  username  = env['MSFRPC_USERNAME']
  upstreamh = env['MSFRPC_HOSTNAME']
  start_server(password, username, upstreamh)


