from typing import List, Optional

from sqlalchemy import func
from .. import models, schema, utils, oauth
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session

router = APIRouter(
    prefix = "/posts",
    tags = ['posts']
)


#get all posts
@router.get("/", response_model=List[schema.PostOut])
# @router.get("/")
def get_posts(response:Response, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user), limit:int = 10, skip:int = 0, q: Optional[str] = ""):
    # query = "SELECT * FROM posts"
    # cursor.execute(query)
    # posts = cursor.fetchone()
    # print(current_user.email)

    # print(limit)

    # user_id = current_user.id
    # posts = db.query(models.Post).filter(models.Post.title.contains(q)).limit(limit).offset(skip).all()
    posts = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Post.id == models.Votes.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(q)).limit(limit).offset(skip).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    response.status_code = status.HTTP_200_OK
    return posts

#get one post
@router.get("/{id}", response_model=schema.PostOut)
def get_post(id: int, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    # query = f"SELECT * FROM posts WHERE id = {id}"
    # cursor.execute(query)
    # post = cursor.fetchone()
    user_id = current_user.id
    post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Post.id == models.Votes.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).filter(models.Post.user_id == user_id).first()
    # post = db.query(models.Post).filter(models.Post.id == id).filter(models.Post.user_id == user_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

#create a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_post(payload: schema.CreatePost, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    post = payload.dict()
    # query = f"INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *"
    # cursor.execute(query, (payload.title, payload.content, payload.published))
    # post = cursor.fetchone()
    # conn.commit()
    post["user_id"] = current_user.id

    # post = models.Post(title=payload.title, content=payload.content, published=payload.published)
    post = models.Post(**post)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

#delete a post
@router.delete("/{id}")
def delete_post(id: int, response:Response, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    # query = "DELETE FROM posts WHERE id = %s RETURNING *"
    # cursor.execute(query, (str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    user_id = current_user.id
    post = db.query(models.Post).filter(models.Post.id == id).filter(models.Post.user_id == user_id)
    if not post.first():
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"data": {
            "status": "failed", 
            "details": "Post was not found"
        }}
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
#update a post
@router.put("/{id}", response_model=schema.Post)
def update_post(id:int, payload:schema.CreatePost, response:Response, db: session = Depends(get_db), current_user=Depends(oauth.get_current_user)):

    # query = "UPDATE posts SET title = %s, content = %s, published = %s WHERE ID = %s RETURNING *"
    # cursor.execute(query, (payload.title, payload.content, payload.published, str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    user_id = current_user.id
    post = db.query(models.Post).filter(models.Post.id == id).filter(models.Post.user_id == user_id)
    post_check = post.first()
    if not post_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.update(payload.dict(), synchronize_session=False)

    db.commit()
    respnse = status.HTTP_200_OK
    
    return post.first()
