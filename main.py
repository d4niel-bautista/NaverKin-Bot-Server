from networking.server import server
from mangum import Mangum

handler = Mangum(server.app)