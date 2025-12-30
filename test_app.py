import pytest
from app import app, get_db_connection

#setting up a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True       #only testing not running the server for real
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

#cleaning the database before each test
@pytest.fixture
def setup_database():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM urls")
    connection.commit()
    cursor.close()
    connection.close()
    yield

#testing url with no expiry
def test_no_expiry(client):
    response = client.post('/shorten', data = {'url' : 'https://google.com'})             #sending POST request
    assert response.status_code == 200             #to check if we get a response
    json_data = response.get_json()
    assert 'short_code' in json_data        #to check if we get a short code
    assert json_data['original_url'] == 'https://google.com'        #to check if the url is correct or not 

    response01 = client.post('/shorten', data = {'url' : 'https://wikipedia.com'})
    assert response01.status_code == 200
    json_data01 = response01.get_json()
    assert 'short_code' in json_data01
    assert json_data01['original_url'] == 'https://wikipedia.com'


#testing url with expiry
def test_expiry(client):
    response1 = client.post('/shorten', data = {'url' : 'https://youtube.com', 'expires_in_days' : '2'})
    assert response1.status_code == 200
    json_data1 = response1.get_json()
    assert json_data1 is not None
    assert 'short_code' in json_data1


#testing if redirect works
def test_redirect(client):
    response2 = client.post('/shorten', data = {'url' : 'https://muscleblaze.com', 'expires_in_days' : '3'})
    json_data2 = response2.get_json()
    assert json_data2 is not None
    short_code1  = json_data2['short_code']            #receiving the short code 

    response3 = client.post('/shorten', data = {'url' : 'https://amazon.com', 'expires_in_days' : '5'})
    json_data3 = response3.get_json()
    assert json_data3 is not None
    short_code2 = json_data3['short_code']

    response4 = client.post('/shorten', data = {'url' : 'https://instagram.com', 'expires_in_days' : '5'})
    json_data4 = response4.get_json()
    assert json_data4 is not None
    short_code3 = json_data4['short_code']

    redirect2 = client.get(f'/{short_code1}', follow_redirects = False)
    assert redirect2.status_code == 302           #302 is redirect status
    assert 'muscleblaze.com' in redirect2.location

    redirect3 = client.get(f'/{short_code2}', follow_redirects = False)
    assert redirect3.status_code == 302
    assert 'amazon.com' in redirect3.location

    redirect4 = client.get(f'/{short_code3}', follow_redirects = False)
    assert redirect4.status_code == 302
    assert 'instagram.com' in redirect4.location






