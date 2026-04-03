from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.contact import ContactCreate, ContactUpdate, ContactResponse
from services.db import find_one, insert_one, update_one, delete_one, find_many
from services.jwt_service import JWTService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user ID"""
    token = credentials.credentials
    payload = JWTService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user_id

@router.get("/", response_model=list[ContactResponse])
async def get_contacts(user_id: str = Depends(get_current_user_id)):
    """Get all emergency contacts for the current user"""
    try:
        contacts = await find_many(
            "emergency_contacts", 
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        # Convert ObjectId to string and format response
        response_contacts = []
        for contact in contacts:
            response_contacts.append({
                "id": str(contact["_id"]),
                "user_id": contact["user_id"],
                "name": contact["name"],
                "phone": contact["phone"],
                "relationship": contact["relationship"],
                "is_primary": contact.get("is_primary", False),
                "created_at": contact["created_at"]
            })
        
        return response_contacts
        
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contacts"
        )

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate, user_id: str = Depends(get_current_user_id)):
    """Add a new emergency contact"""
    try:
        # Check if contact with this phone already exists for this user
        existing_contact = await find_one("emergency_contacts", {
            "user_id": user_id,
            "phone": contact_data.phone
        })
        
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this phone number already exists"
            )
        
        # If this is marked as primary, unmark all other contacts
        if contact_data.is_primary:
            await update_one(
                "emergency_contacts",
                {"user_id": user_id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )
        
        # Create contact record
        contact_record = {
            "user_id": user_id,
            "name": contact_data.name,
            "phone": contact_data.phone,
            "relationship": contact_data.relationship.value,
            "is_primary": contact_data.is_primary,
            "created_at": datetime.utcnow()
        }
        
        contact_id = await insert_one("emergency_contacts", contact_record)
        if not contact_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create contact"
            )
        
        logger.info(f"Contact created for user {user_id}: {contact_data.name}")
        return {
            "id": contact_id,
            "user_id": user_id,
            "name": contact_data.name,
            "phone": contact_data.phone,
            "relationship": contact_data.relationship,
            "is_primary": contact_data.is_primary,
            "created_at": contact_record["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contact"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str, user_id: str = Depends(get_current_user_id)):
    """Get a specific emergency contact"""
    try:
        contact = await find_one("emergency_contacts", {
            "_id": contact_id,
            "user_id": user_id
        })
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        return {
            "id": str(contact["_id"]),
            "user_id": contact["user_id"],
            "name": contact["name"],
            "phone": contact["phone"],
            "relationship": contact["relationship"],
            "is_primary": contact.get("is_primary", False),
            "created_at": contact["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contact"
        )

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: str, contact_data: ContactUpdate, 
                       user_id: str = Depends(get_current_user_id)):
    """Update an emergency contact"""
    try:
        # Check if contact exists and belongs to user
        existing_contact = await find_one("emergency_contacts", {
            "_id": contact_id,
            "user_id": user_id
        })
        
        if not existing_contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Check if phone number conflicts with another contact
        if contact_data.phone:
            conflict_contact = await find_one("emergency_contacts", {
                "user_id": user_id,
                "phone": contact_data.phone,
                "_id": {"$ne": contact_id}
            })
            
            if conflict_contact:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Another contact with this phone number already exists"
                )
        
        # If setting as primary, unmark all other contacts
        if contact_data.is_primary and not existing_contact.get("is_primary", False):
            await update_one(
                "emergency_contacts",
                {"user_id": user_id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )
        
        # Prepare update data
        update_data = {}
        if contact_data.name is not None:
            update_data["name"] = contact_data.name
        if contact_data.phone is not None:
            update_data["phone"] = contact_data.phone
        if contact_data.relationship is not None:
            update_data["relationship"] = contact_data.relationship.value
        if contact_data.is_primary is not None:
            update_data["is_primary"] = contact_data.is_primary
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            success = await update_one(
                "emergency_contacts",
                {"_id": contact_id},
                {"$set": update_data}
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update contact"
                )
        
        # Get updated contact
        updated_contact = await find_one("emergency_contacts", {"_id": contact_id})
        
        logger.info(f"Contact updated for user {user_id}: {contact_id}")
        return {
            "id": str(updated_contact["_id"]),
            "user_id": updated_contact["user_id"],
            "name": updated_contact["name"],
            "phone": updated_contact["phone"],
            "relationship": updated_contact["relationship"],
            "is_primary": updated_contact.get("is_primary", False),
            "created_at": updated_contact["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact"
        )

@router.delete("/{contact_id}")
async def delete_contact(contact_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete an emergency contact"""
    try:
        # Check if contact exists and belongs to user
        contact = await find_one("emergency_contacts", {
            "_id": contact_id,
            "user_id": user_id
        })
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Delete contact
        success = await delete_one("emergency_contacts", {"_id": contact_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete contact"
            )
        
        logger.info(f"Contact deleted for user {user_id}: {contact_id}")
        return {"message": "Contact deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact"
        )

@router.get("/primary/summary")
async def get_primary_contacts_summary(user_id: str = Depends(get_current_user_id)):
    """Get summary of primary emergency contacts for quick SOS"""
    try:
        primary_contacts = await find_many(
            "emergency_contacts",
            {"user_id": user_id, "is_primary": True},
            sort=[("created_at", 1)]
        )
        
        # If no primary contacts, get all contacts
        if not primary_contacts:
            primary_contacts = await find_many(
                "emergency_contacts",
                {"user_id": user_id},
                sort=[("created_at", 1)]
            )
        
        summary = []
        for contact in primary_contacts[:5]:  # Limit to 5 for SOS
            summary.append({
                "id": str(contact["_id"]),
                "name": contact["name"],
                "phone": contact["phone"],
                "relationship": contact["relationship"]
            })
        
        return {
            "contacts": summary,
            "total_count": len(summary)
        }
        
    except Exception as e:
        logger.error(f"Error fetching primary contacts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch primary contacts"
        )
