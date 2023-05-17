from fastapi import Depends, HTTPException, Response, status, APIRouter
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/")
def vote(vote_data: schemas.Vote, db: Session = Depends(database.get_db),
         current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote_data.post_id).first()

    # If the post does not exist raise a 404 error
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {vote_data.post_id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.user_id == current_user.id, 
                                     models.Vote.post_id == vote_data.post_id)
    found_vote = vote_query.first()

    if (vote_data.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"user {current_user.id} has already voted on post {vote_data.post_id}")
    
        new_vote = models.Vote(post_id=vote_data.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {"message": "sucessfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Vote does not exit")   
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "sucessfully deleted vote"}
