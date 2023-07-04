
def status_200(response):
    assert response.status_code == 200, response.text
