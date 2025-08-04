#!/usr/bin/env python3
"""
Test Suite for WebDAV Uploader
==============================

Kompletní testovací sada pro WebDAV uploader API.
Testuje všechny endpointy, autentifikaci, upload funkcionalitu.

Autor: Claude AI Assistant
Datum: 2025-07-05
"""

import unittest
import tempfile
import os
import json
import base64
from unittest.mock import patch, MagicMock
import sys

# Přidání cesty k hlavnímu modulu
sys.path.insert(0, '/root')

# Import hlavního modulu
import webdav_uploader
from webdav_uploader import app, authenticate_user, allowed_file, create_webdav_client


class TestWebDAVUploader(unittest.TestCase):
    """Hlavní testovací třída"""
    
    def setUp(self):
        """Nastavení před každým testem"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Test credentials
        self.valid_auth = ('perplexity', 'secure-password-123')
        self.invalid_auth = ('invalid', 'wrong-password')
        
    def tearDown(self):
        """Úklid po každém testu"""
        pass

    def test_health_endpoint(self):
        """Test health check endpointu"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'OK')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)

    def test_authentication_valid(self):
        """Test platného přihlášení"""
        self.assertTrue(authenticate_user('perplexity', 'secure-password-123'))
        self.assertTrue(authenticate_user('admin', 'admin-password-456'))

    def test_authentication_invalid(self):
        """Test neplatného přihlášení"""
        self.assertFalse(authenticate_user('invalid', 'wrong'))
        self.assertFalse(authenticate_user('perplexity', 'wrong-password'))
        self.assertFalse(authenticate_user('', ''))

    def test_allowed_file_valid(self):
        """Test povolených typů souborů"""
        valid_files = [
            'document.pdf', 'image.jpg', 'text.txt', 'data.json',
            'sheet.xlsx', 'presentation.pptx', 'readme.md'
        ]
        for filename in valid_files:
            self.assertTrue(allowed_file(filename), f"File {filename} should be allowed")

    def test_allowed_file_invalid(self):
        """Test nepovolených typů souborů"""
        invalid_files = [
            'script.exe', 'virus.bat', 'malware.sh', 'dangerous.php',
            'noextension', '.hidden', ''
        ]
        for filename in invalid_files:
            self.assertFalse(allowed_file(filename), f"File {filename} should NOT be allowed")

    def test_config_endpoint_unauthorized(self):
        """Test config endpointu bez autentifikace"""
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 401)

    def test_config_endpoint_authorized(self):
        """Test config endpointu s autentifikací"""
        response = self.app.get('/config', 
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('webdav_config', data)
        self.assertIn('allowed_extensions', data)
        self.assertEqual(data['webdav_config']['webdav_password'], '***')  # Heslo skryté

    def test_list_endpoint_unauthorized(self):
        """Test list endpointu bez autentifikace"""
        response = self.app.get('/list')
        self.assertEqual(response.status_code, 401)

    @patch('webdav_uploader.create_webdav_client')
    def test_list_endpoint_authorized(self, mock_webdav):
        """Test list endpointu s autentifikací"""
        # Mock WebDAV client
        mock_client = MagicMock()
        mock_client.list.return_value = ['file1.txt', 'file2.pdf']
        mock_webdav.return_value = mock_client
        
        response = self.app.get('/list',
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('files', data)
        self.assertIn('path', data)

    @patch('webdav_uploader.create_webdav_client')
    def test_upload_multipart_unauthorized(self, mock_webdav):
        """Test upload endpointu bez autentifikace"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test content')
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.app.post('/upload', 
                    data={'file': (f, 'test.txt')})
            self.assertEqual(response.status_code, 401)
        finally:
            os.unlink(temp_path)

    @patch('webdav_uploader.create_webdav_client')
    def test_upload_multipart_success(self, mock_webdav):
        """Test úspěšného upload přes multipart"""
        # Mock WebDAV client
        mock_client = MagicMock()
        mock_client.upload_sync.return_value = True
        mock_webdav.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test content')
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.app.post('/upload',
                    data={'file': (f, 'test.txt')},
                    headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('message', data)
            self.assertIn('filename', data)
            self.assertEqual(data['filename'], 'test.txt')
        finally:
            os.unlink(temp_path)

    @patch('webdav_uploader.create_webdav_client')
    def test_upload_json_success(self, mock_webdav):
        """Test úspěšného upload přes JSON"""
        # Mock WebDAV client
        mock_client = MagicMock()
        mock_client.upload_sync.return_value = True
        mock_webdav.return_value = mock_client
        
        test_data = {
            'filename': 'test.txt',
            'data': base64.b64encode(b'Test content').decode(),
            'path': '/test'
        }
        
        response = self.app.post('/upload',
            json=test_data,
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['filename'], 'test.txt')

    def test_upload_invalid_file_type(self):
        """Test upload nepovolených typů souborů"""
        test_data = {
            'filename': 'malware.exe',
            'data': base64.b64encode(b'Malicious content').decode()
        }
        
        response = self.app.post('/upload',
            json=test_data,
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_no_file(self):
        """Test upload bez souboru"""
        response = self.app.post('/upload',
            data={},
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        self.assertEqual(response.status_code, 400)

    def test_upload_missing_data(self):
        """Test upload s chybějícími daty"""
        test_data = {
            'filename': 'test.txt'
            # Chybí 'data'
        }
        
        response = self.app.post('/upload',
            json=test_data,
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        self.assertEqual(response.status_code, 400)

    @patch('webdav_uploader.create_webdav_client')
    def test_webdav_connection_failure(self, mock_webdav):
        """Test selhání připojení k WebDAV"""
        mock_webdav.return_value = None  # Simulace chyby připojení
        
        test_data = {
            'filename': 'test.txt',
            'data': base64.b64encode(b'Test content').decode()
        }
        
        response = self.app.post('/upload',
            json=test_data,
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_large_file_rejection(self):
        """Test odmítnutí příliš velkého souboru"""
        # Test přes JSON s velkými daty (lépe kontrolovatelné)
        large_data = 'x' * (60 * 1024 * 1024)  # 60MB string
        
        test_data = {
            'filename': 'large.txt',
            'data': large_data  # Bez base64 enkódování pro rychlost
        }
        
        response = self.app.post('/upload',
            json=test_data,
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        
        # Mělo by vrátit 413 nebo 500 (oba jsou akceptovatelné pro velké soubory)
        self.assertIn(response.status_code, [413, 500])
        data = json.loads(response.data)
        self.assertIn('error', data)


class TestIntegration(unittest.TestCase):
    """Integrační testy"""
    
    def setUp(self):
        """Nastavení před každým testem"""
        self.app = app.test_client()
        self.app.testing = True

    def test_full_workflow(self):
        """Test kompletního workflow"""
        # 1. Health check
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        # 2. Config check
        response = self.app.get('/config',
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        self.assertEqual(response.status_code, 200)
        
        # 3. List files (může selhat, ale ne kvůli autentifikaci)
        response = self.app.get('/list',
            headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
        # Status může být 200 nebo 500 (podle WebDAV dostupnosti)
        self.assertIn(response.status_code, [200, 500])


class TestSecurity(unittest.TestCase):
    """Bezpečnostní testy"""
    
    def setUp(self):
        """Nastavení před každým testem"""
        self.app = app.test_client()
        self.app.testing = True

    def test_path_traversal_protection(self):
        """Test ochrany proti path traversal"""
        malicious_names = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\config\\sam',
            '/etc/shadow',
            'script<>.exe',
            'file|with|pipes.txt'
        ]
        
        for filename in malicious_names:
            test_data = {
                'filename': filename,
                'data': base64.b64encode(b'Test content').decode()
            }
            
            response = self.app.post('/upload',
                json=test_data,
                headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
            
            # Mělo by být buď odmítnuto (400) nebo název sanitizován (200)
            if response.status_code == 200:
                data = json.loads(response.data)
                # Sanitizovaný název nesmí obsahovat nebezpečné znaky
                self.assertNotIn('..', data.get('filename', ''))
                self.assertNotIn('/', data.get('filename', ''))
                self.assertNotIn('\\', data.get('filename', ''))

    def test_sql_injection_attempts(self):
        """Test pokusů o SQL injection"""
        malicious_usernames = [
            "admin'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin' UNION SELECT * FROM passwords --"
        ]
        
        for username in malicious_usernames:
            auth_string = base64.b64encode(f"{username}:password".encode()).decode()
            response = self.app.get('/config',
                headers={'Authorization': f'Basic {auth_string}'})
            
            # Mělo by být odmítnuto
            self.assertEqual(response.status_code, 401)

    def test_xss_prevention(self):
        """Test prevence XSS útoků"""
        xss_payloads = [
            '<script>alert("xss")</script>',
            'javascript:alert(1)',
            '"><script>alert(document.cookie)</script>'
        ]
        
        for payload in xss_payloads:
            test_data = {
                'filename': f'{payload}.txt',
                'data': base64.b64encode(b'Test content').decode()
            }
            
            response = self.app.post('/upload',
                json=test_data,
                headers={'Authorization': f'Basic {base64.b64encode(b"perplexity:secure-password-123").decode()}'})
            
            if response.status_code == 200:
                data = json.loads(response.data)
                filename = data.get('filename', '')
                # Filename nesmí obsahovat script tagy
                self.assertNotIn('<script>', filename.lower())
                self.assertNotIn('javascript:', filename.lower())


def run_tests():
    """Spustí všechny testy"""
    # Vytvoření test suite
    test_suite = unittest.TestSuite()
    
    # Přidání testů
    test_suite.addTest(unittest.makeSuite(TestWebDAVUploader))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestSecurity))
    
    # Spuštění testů
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Výsledky
    print(f"\n{'='*50}")
    print(f"VÝSLEDKY TESTŮ")
    print(f"{'='*50}")
    print(f"Spuštěno testů: {result.testsRun}")
    print(f"Chyby: {len(result.errors)}")
    print(f"Selhání: {len(result.failures)}")
    print(f"Úspěšnost: {((result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun * 100):.1f}%")
    
    if result.errors:
        print(f"\nCHYBY:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print(f"\nSELHÁNÍ:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 Spouštím testy WebDAV Uploader...")
    success = run_tests()
    
    if success:
        print("\n✅ Všechny testy prošly!")
        exit(0)
    else:
        print("\n❌ Některé testy selhaly!")
        exit(1)