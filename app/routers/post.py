from typing import List, Optional
from fastapi import Depends, HTTPException, Response, status, APIRouter
from ..database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from .. import models, schemas, oauth2, database

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=List[schemas.PostResponse])
@router.get("/", response_model=List[schemas.VoteResponse])
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 5, skip: int = 0, search: Optional[str] = ''):
    """Get all the posts"""
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post, func.count(models.Vote.user_id).label("vote_count"))\
                          .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
                          .filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    """Create a new post"""
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchall()
    # conn.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    print(current_user.id)

    post_dict = post.dict()
    # post_dict.update({"owner_id": f"{user.id}"})

    new_post = models.Post(owner_id=current_user.id, **post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.VoteResponse)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    """Get a single post of given id"""
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    
    post = db.query(models.Post, func.count(models.Vote.user_id).label("vote_count"))\
                          .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
                          .filter(models.Post.id == id).first()

    # Raise an error if the returned post is null
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found.")
    
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # """Deleted row of the given id"""
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    # removed_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    
    # If database returns nothing raise 404 error
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    """Update fields for given id"""
    # Using sql to update the change and sql alchemy to query the data because sql alchemy was buggy when updating 
    # data without updating `created_at` field
    returned_post = database.cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                   (updated_post.title, updated_post.content, updated_post.published, str(id)))
    updated_post = database.cursor.fetchone()

    # print(updated_post)

    # Converting data to dictionary to access `owner_id` field
    updated_post_dict = dict(updated_post)
    
    #  database returns nothing raise 404 error
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    if updated_post_dict["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")


    # post_quey.update(updated_post.dict(), synchronize_session=False)

    # db.commit()
    database.conn.commit()

    # print(main.cursor.fetchone())

    # Fetching the latest change
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()


    return post
 