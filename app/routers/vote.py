from os import stat
from typing import List, Optional

from sqlalchemy.sql.functions import mode, user
from sqlalchemy.sql.sqltypes import REAL
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session

router = APIRouter(
    prefix = "/vote",
    tags = ['Vote']
)

@router.post("/{post_id}", response_model=schema.Votes)
def vote(response:Response, post_id:int, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user), vote:int = 1):

    user_id = current_user.id;
    #check if post exists 
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with id not found")
    
    vote_obj = db.query(models.Votes).filter(models.Votes.post_id == post_id).filter(models.Votes.user_id == user_id)
    vote_obj_first = vote_obj.first()
    if vote_obj_first and vote:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "status": "Post already liked",
            "details": vote_obj_first
        }

    if vote_obj_first and not vote:
        vote_obj.delete(synchronize_session=False)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT
        return {
            "status": "Post unliked",
            "details": vote_obj_first
        }

    if not vote_obj_first and vote:
        #create the like
        vote_val = {
            "post_id": post_id,
            "user_id": user_id
        }
        vote_post = models.Votes(**vote_val)
        db.add(vote_post)
        db.commit()
        db.refresh(vote_post)
        response.status_code = status.HTTP_201_CREATED
        return {
            "status": "Post liked successfully", 
            "details": vote_post
        }

    if not vote_obj_first and not vote:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "status": "Post not liked",
        }
    return 
