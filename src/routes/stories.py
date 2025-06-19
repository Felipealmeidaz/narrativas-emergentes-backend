from flask import Blueprint, request, jsonify
import json
import time

stories_bp = Blueprint('stories', __name__)

# Mock data for stories (in production, use a database)
mock_stories = [
    {
        'id': '1',
        'title': 'A Floresta Encantada',
        'description': 'Uma aventura mágica através de uma floresta cheia de criaturas místicas e segredos antigos.',
        'participants': ['Você', 'Ana', 'Carlos'],
        'lastActivity': '2 horas atrás',
        'messageCount': 47,
        'status': 'active',
        'genre': 'Fantasia',
        'createdAt': '2025-01-15',
        'session_id': 'session_1'
    },
    {
        'id': '2',
        'title': 'Mistério na Estação Espacial',
        'description': 'Um thriller de ficção científica onde a tripulação precisa resolver um mistério antes que seja tarde demais.',
        'participants': ['Você', 'Marina'],
        'lastActivity': '1 dia atrás',
        'messageCount': 23,
        'status': 'paused',
        'genre': 'Ficção Científica',
        'createdAt': '2025-01-10',
        'session_id': 'session_2'
    },
    {
        'id': '3',
        'title': 'O Último Cavaleiro',
        'description': 'Uma épica medieval sobre honra, coragem e a busca pelo Santo Graal.',
        'participants': ['Você'],
        'lastActivity': '3 dias atrás',
        'messageCount': 15,
        'status': 'completed',
        'genre': 'Medieval',
        'createdAt': '2025-01-05',
        'session_id': 'session_3'
    },
    {
        'id': '4',
        'title': 'Detetive em Neo-Tokyo',
        'description': 'Um noir cyberpunk nas ruas neon de uma metrópole futurista.',
        'participants': ['Você', 'Alex', 'Sam', 'Jordan'],
        'lastActivity': '5 horas atrás',
        'messageCount': 89,
        'status': 'active',
        'genre': 'Cyberpunk',
        'createdAt': '2025-01-12',
        'session_id': 'session_4'
    }
]

@stories_bp.route('/stories', methods=['GET'])
def get_stories():
    """Get all stories with optional filtering"""
    try:
        # Get query parameters
        status_filter = request.args.get('status', 'all')
        search_term = request.args.get('search', '').lower()
        
        # Filter stories
        filtered_stories = mock_stories.copy()
        
        # Apply status filter
        if status_filter != 'all':
            filtered_stories = [s for s in filtered_stories if s['status'] == status_filter]
        
        # Apply search filter
        if search_term:
            filtered_stories = [
                s for s in filtered_stories 
                if search_term in s['title'].lower() or 
                   search_term in s['description'].lower() or 
                   search_term in s['genre'].lower()
            ]
        
        return jsonify({
            'stories': filtered_stories,
            'total': len(filtered_stories),
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@stories_bp.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story by ID"""
    try:
        story = next((s for s in mock_stories if s['id'] == story_id), None)
        
        if not story:
            return jsonify({
                'error': 'Story not found',
                'success': False
            }), 404
        
        return jsonify({
            'story': story,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@stories_bp.route('/stories', methods=['POST'])
def create_story():
    """Create a new story"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'genre']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    'error': f'Field {field} is required',
                    'success': False
                }), 400
        
        # Create new story
        new_story = {
            'id': str(len(mock_stories) + 1),
            'title': data['title'],
            'description': data['description'],
            'participants': ['Você'],
            'lastActivity': 'Agora',
            'messageCount': 0,
            'status': 'active',
            'genre': data['genre'],
            'createdAt': time.strftime('%Y-%m-%d'),
            'session_id': f"session_{len(mock_stories) + 1}"
        }
        
        mock_stories.append(new_story)
        
        return jsonify({
            'story': new_story,
            'success': True
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@stories_bp.route('/stories/<story_id>', methods=['PUT'])
def update_story(story_id):
    """Update an existing story"""
    try:
        story = next((s for s in mock_stories if s['id'] == story_id), None)
        
        if not story:
            return jsonify({
                'error': 'Story not found',
                'success': False
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'status', 'genre']
        for field in allowed_fields:
            if field in data:
                story[field] = data[field]
        
        return jsonify({
            'story': story,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@stories_bp.route('/stories/<story_id>', methods=['DELETE'])
def delete_story(story_id):
    """Delete a story"""
    try:
        story_index = next((i for i, s in enumerate(mock_stories) if s['id'] == story_id), None)
        
        if story_index is None:
            return jsonify({
                'error': 'Story not found',
                'success': False
            }), 404
        
        deleted_story = mock_stories.pop(story_index)
        
        return jsonify({
            'message': 'Story deleted successfully',
            'story': deleted_story,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@stories_bp.route('/stories/stats', methods=['GET'])
def get_stories_stats():
    """Get statistics about stories"""
    try:
        total_stories = len(mock_stories)
        active_stories = len([s for s in mock_stories if s['status'] == 'active'])
        completed_stories = len([s for s in mock_stories if s['status'] == 'completed'])
        paused_stories = len([s for s in mock_stories if s['status'] == 'paused'])
        total_messages = sum(s['messageCount'] for s in mock_stories)
        
        stats = {
            'total_stories': total_stories,
            'active_stories': active_stories,
            'completed_stories': completed_stories,
            'paused_stories': paused_stories,
            'total_messages': total_messages
        }
        
        return jsonify({
            'stats': stats,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

