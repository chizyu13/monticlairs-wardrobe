from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import ChatSession, ChatMessage
from home.models import Product


@require_http_methods(["POST"])
@csrf_exempt
def start_chat(request, product_id=None):
    """Start a new chat session"""
    try:
        data = json.loads(request.body)
        
        # Get or create session
        if request.user.is_authenticated:
            session, created = ChatSession.objects.get_or_create(
                user=request.user,
                is_closed=False,
                defaults={'product_id': product_id}
            )
        else:
            # Guest chat
            guest_name = data.get('guest_name', 'Guest')
            guest_email = data.get('guest_email', '')
            
            session = ChatSession.objects.create(
                guest_name=guest_name,
                guest_email=guest_email,
                product_id=product_id
            )
            created = True
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'created': created
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def send_message(request, session_id):
    """Send a message in a chat session"""
    try:
        session = ChatSession.objects.get(id=session_id)
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Determine sender name
        if request.user.is_authenticated:
            sender_name = request.user.get_full_name() or request.user.username
        else:
            sender_name = session.guest_name or 'Guest'
        
        # Create message
        message = ChatMessage.objects.create(
            session=session,
            sender=request.user if request.user.is_authenticated else None,
            sender_name=sender_name,
            message=message_text,
            is_admin=False
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Chat session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def get_messages(request, session_id):
    """Get messages from a chat session"""
    try:
        session = ChatSession.objects.get(id=session_id)
        last_message_id = request.GET.get('last_message_id', 0)
        
        # Get messages after the last one
        messages = ChatMessage.objects.filter(
            session=session,
            id__gt=last_message_id
        ).values(
            'id', 'sender_name', 'message', 'is_admin', 'created_at'
        ).order_by('created_at')
        
        return JsonResponse({
            'success': True,
            'messages': list(messages)
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Chat session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def close_chat(request, session_id):
    """Close a chat session"""
    try:
        session = ChatSession.objects.get(id=session_id)
        session.is_closed = True
        session.save()
        
        return JsonResponse({
            'success': True
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Chat session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
