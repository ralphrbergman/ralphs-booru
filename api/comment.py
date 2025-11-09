from db import Comment, Post, User, db

def create_comment(content: str, author: User, post: Post) -> Comment:
    """
    Creates and returns comment object.

    Args:
        content (str): Comment content
        author (User)
        post (Post)
    """
    comment = Comment()

    comment.author = author
    comment.post = post
    comment.content = content

    db.session.add(comment)
    db.session.commit()

    return comment
