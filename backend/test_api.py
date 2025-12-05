"""
Tests d'intégration API pour le chatbot Toyota Auris
"""
import pytest
import json
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from api import app


@pytest.fixture
def client():
    """Créer un client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIHealth:
    """Tests de santé de l'API"""
    
    def test_health_endpoint(self, client):
        """Vérifie que l'endpoint /api/health fonctionne"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'chatbot_ready' in data
        assert 'documents_count' in data
    
    def test_health_has_documents(self, client):
        """Vérifie que des documents sont chargés"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['documents_count'] > 0


class TestAPISuggestions:
    """Tests des suggestions de questions"""
    
    def test_suggestions_endpoint(self, client):
        """Vérifie que l'endpoint /api/suggestions fonctionne"""
        response = client.get('/api/suggestions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'suggestions' in data
        assert len(data['suggestions']) > 0
    
    def test_suggestions_format(self, client):
        """Vérifie le format des suggestions"""
        response = client.get('/api/suggestions')
        data = json.loads(response.data)
        
        for suggestion in data['suggestions']:
            assert 'id' in suggestion
            assert 'text' in suggestion
            assert 'category' in suggestion


class TestAPIChatVehicle:
    """Tests du chat pour les questions véhicules"""
    
    def test_chat_endpoint_exists(self, client):
        """Vérifie que l'endpoint /api/chat existe"""
        response = client.post('/api/chat', 
                              json={'message': 'test'},
                              content_type='application/json')
        # Ne devrait pas retourner 404
        assert response.status_code != 404
    
    def test_chat_requires_message(self, client):
        """Vérifie que le message est requis"""
        response = client.post('/api/chat', 
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_vehicle_question(self, client):
        """Vérifie la réponse à une question véhicule"""
        response = client.post('/api/chat',
                              json={'message': "Quelle est la capacité du réservoir de l'Auris?"},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        assert len(data['response']) > 0
        # Ne devrait pas être un refus
        assert "🚫" not in data['response']
    
    def test_chat_maintenance_question(self, client):
        """Vérifie la réponse à une question d'entretien"""
        response = client.post('/api/chat',
                              json={'message': "Quand faut-il changer les plaquettes de frein?"},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        assert len(data['response']) > 0


class TestAPIChatNonVehicle:
    """Tests du chat pour les questions hors-sujet"""
    
    def test_chat_rejects_cooking(self, client):
        """Vérifie le rejet des questions cuisine"""
        response = client.post('/api/chat',
                              json={'message': "Comment faire une tarte aux pommes?"},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        # Devrait être un refus poli
        assert "🚫" in data['response'] or "spécialisé" in data['response'].lower()
    
    def test_chat_rejects_politics(self, client):
        """Vérifie le rejet des questions politiques"""
        response = client.post('/api/chat',
                              json={'message': "Qui est le président de la France?"},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'response' in data
        assert "🚫" in data['response'] or "spécialisé" in data['response'].lower()


class TestAPIHistory:
    """Tests de l'historique de conversation"""
    
    def test_history_endpoint(self, client):
        """Vérifie que l'endpoint /api/history fonctionne"""
        response = client.get('/api/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert isinstance(data['history'], list)
    
    def test_clear_history_endpoint(self, client):
        """Vérifie que l'endpoint /api/clear fonctionne"""
        response = client.post('/api/clear')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestAPICORS:
    """Tests de configuration CORS"""
    
    def test_cors_headers(self, client):
        """Vérifie les headers CORS sur les requêtes OPTIONS"""
        response = client.options('/api/chat')
        # CORS devrait permettre les requêtes
        assert response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
