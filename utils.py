def update_leaderboard(db, Leaderboard, user_id, new_score):
    """Update the leaderboard score for the given user."""
    leaderboard_entry = Leaderboard.query.filter_by(user_id=user_id).first()
    if leaderboard_entry:
        leaderboard_entry.score = new_score  
    else:
        leaderboard_entry = Leaderboard(user_id=user_id, score=new_score)  # Create new entry if not exists
        db.session.add(leaderboard_entry)
    db.session.commit()
