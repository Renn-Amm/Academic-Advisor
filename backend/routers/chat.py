from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, ChatMessage
from backend.schemas import ChatQuery, ChatResponse
from backend.auth import get_current_active_user
from backend.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    chat_query: ChatQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a chat message and get AI response"""
    service = RecommendationService(db)
    
    # Process the query
    courses, explanations, ai_response = service.get_personalized_recommendations(
        user=current_user,
        query=chat_query.message,
        limit=6
    )
    
    # Save chat message
    chat_message = ChatMessage(
        user_id=current_user.id,
        message=chat_query.message,
        response=ai_response,
        query_type=chat_query.query_type
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    return {
        "message": chat_query.message,
        "response": ai_response,
        "timestamp": chat_message.timestamp,
        "recommended_courses": courses
    }


@router.get("/history")
async def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for current user"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    
    return {
        "total": len(messages),
        "messages": [
            {
                "id": msg.id,
                "message": msg.message,
                "response": msg.response,
                "timestamp": msg.timestamp,
                "query_type": msg.query_type
            }
            for msg in messages
        ]
    }


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear chat history for current user"""
    db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {"message": "Chat history cleared successfully"}
