import urllib.request
import json

def test():
    login_data = json.dumps({'email': 'admin@admin', 'senha': 'admin'}).encode('utf-8')
    req1 = urllib.request.Request(
        'http://localhost:8000/auth/login',
        data=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        res1 = urllib.request.urlopen(req1)
        data1 = json.loads(res1.read().decode('utf-8'))
        token = data1['access_token']
        print('Login Success!')
        print('Token:', token)
    except Exception as e:
        print('Login Failed:', e)
        if hasattr(e, 'read'):
            print('Login Error Response:', e.read().decode('utf-8'))
        return

    req2 = urllib.request.Request(
        'http://localhost:8000/contracts/',
        headers={
            'Authorization': f'Bearer {token}',
            'X-API-Token': '123'
        }
    )
    
    try:
        res2 = urllib.request.urlopen(req2)
        print('Contracts success! Response:', res2.read().decode('utf-8'))
    except Exception as e:
        print('Contracts Failed:', e)
        if hasattr(e, 'read'):
            print('Contracts Error Response:', e.read().decode('utf-8'))

if __name__ == '__main__':
    test()
