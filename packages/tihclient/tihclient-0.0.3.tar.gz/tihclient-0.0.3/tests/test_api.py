from tihclient import TIHClient

def test_api():
    client = TIHClient()
    response = client.get_accommodation(keyword='hotel')
    print(response)

if __name__ == '__main__':
    test_api()