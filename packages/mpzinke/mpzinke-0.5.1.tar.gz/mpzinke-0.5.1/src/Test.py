

from mpzinke import Server
from mpzinke import Generic
from mpzinke import threading


def auth(request):
	"""
	Test for auth
	"""
	if("Authorization" not in request.headers):
		raise Server.EXCEPTIONS[401]()

	return True


@Generic
def test(__args__, a: str, b: int=None):
	return __args__[0]


if(__name__ == "__main__"):
	# thread = threading.DelayThread("Test", action=lambda: print("Test"), time=lambda: 2)
	# thread.start()
	# thread.join()
	# thread2 = threading.LoopingThread("Test", action=lambda: print("Test"), time=lambda: 2)
	# thread2.start()
	# print(test[int].__annotations__)
	# print(test[int](a="", b=0))
	server = Server(template_folder="Hello")
	server.route("/no_auth", lambda: "Hello", authorization=server.no_auth)
	server.route("/auth", lambda: "Hello", authorization=server.bearer_auth("123"))
	print(dict(server))
