import os
import google.generativeai as genai
from flask import Blueprint, request, jsonify, stream_template
import json
import time

# Load environment variables only in development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in production, which is fine
    pass

chat_bp = Blueprint('chat', __name__)

# Configure Google Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    # Debug: Print available environment variables for troubleshooting
    print("Available environment variables:")
    for key in sorted(os.environ.keys()):
        if 'GEMINI' in key or 'API' in key or 'RAILWAY' in key:
            print(f"  {key}: {'*' * len(os.environ[key]) if os.environ[key] else 'None'}")
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Store chat sessions in memory (in production, use a database)
chat_sessions = {}

@chat_bp.route('/chat/start', methods=['POST'])
def start_chat():
    """Start a new chat session"""
    try:
        data = request.get_json()
        story_prompt = data.get('prompt', '')
        
        # Create a new chat session
        chat = model.start_chat(history=[])
        
        # Generate session ID
        session_id = str(int(time.time() * 1000))
        
        # Initial system prompt for storytelling
        system_prompt = f"""Você é um narrador mestre especializado em ficção interativa. Sua função é criar e conduzir narrativas envolventes e imersivas.

Diretrizes:
- Seja criativo, descritivo e imaginativo
- Adapte-se ao tom e gênero da história
- Responda às ações do usuário de forma coerente e interessante
- Mantenha a narrativa fluindo naturalmente
- Ofereça escolhas e possibilidades interessantes
- Use linguagem rica e evocativa
- Seja flexível e aceite ações inesperadas dos usuários

{f"Contexto inicial: {story_prompt}" if story_prompt else "Crie uma introdução envolvente para uma nova aventura."}

Comece a narrativa agora:"""

        # Get initial response
        response = chat.send_message(system_prompt)
        
        # Store the chat session
        chat_sessions[session_id] = {
            'chat': chat,
            'history': [
                {'role': 'user', 'content': system_prompt},
                {'role': 'assistant', 'content': response.text}
            ]
        }
        
        return jsonify({
            'session_id': session_id,
            'message': response.text,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@chat_bp.route('/chat/send', methods=['POST'])
def send_message():
    """Send a message to an existing chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '')
        
        if not session_id or session_id not in chat_sessions:
            return jsonify({
                'error': 'Invalid session ID',
                'success': False
            }), 400
        
        if not message.strip():
            return jsonify({
                'error': 'Message cannot be empty',
                'success': False
            }), 400
        
        # Get the chat session
        session = chat_sessions[session_id]
        chat = session['chat']
        
        # Send message to Gemini
        response = chat.send_message(message)
        
        # Update history
        session['history'].extend([
            {'role': 'user', 'content': message},
            {'role': 'assistant', 'content': response.text}
        ])
        
        return jsonify({
            'message': response.text,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        if session_id not in chat_sessions:
            return jsonify({
                'error': 'Session not found',
                'success': False
            }), 404
        
        history = chat_sessions[session_id]['history']
        
        return jsonify({
            'history': history,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@chat_bp.route('/chat/sessions', methods=['GET'])
def list_sessions():
    """List all active chat sessions"""
    try:
        sessions = []
        for session_id, session_data in chat_sessions.items():
            # Get the first few messages to create a preview
            history = session_data['history']
            preview = ""
            if len(history) > 1:
                preview = history[1]['content'][:100] + "..." if len(history[1]['content']) > 100 else history[1]['content']
            
            sessions.append({
                'session_id': session_id,
                'preview': preview,
                'message_count': len(history),
                'last_activity': session_id  # Using session_id as timestamp for now
            })
        
        return jsonify({
            'sessions': sessions,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@chat_bp.route('/chat/delete/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    try:
        if session_id in chat_sessions:
            del chat_sessions[session_id]
            return jsonify({
                'message': 'Session deleted successfully',
                'success': True
            })
        else:
            return jsonify({
                'error': 'Session not found',
                'success': False
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

