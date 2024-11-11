from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship

















class QuizContent(db.Model):
    __tablename__ = 'quiz_content'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True) 
    parent_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=True)  # Self-referencing foreign key
    type = db.Column(db.String, nullable=False)  # "quiz", "question", or "option"
    content_text = db.Column(db.Text, nullable=False)  # Quiz title, question text, or option text
    points = db.Column(db.Integer, nullable=True)  # Points for questions; NULL for quizzes and options
    is_correct = db.Column(db.Boolean, nullable=True)  # Only for options; true if correct, null otherwise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship('QuizContent', remote_side=[id], back_populates='children')  # Self-referential relationship
    children = relationship('QuizContent', back_populates='parent')  # Allows nesting (questions under quizzes)

    def __repr__(self):
        return f"<QuizContent(id={self.id}, type={self.type}, content_text='{self.content_text[:20]}...', points={self.points})>"


class QuizSubmission(db.Model):
    __tablename__ = 'quiz_submission'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=False)  # Refers to a quiz in QuizContent
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='quiz_submissions')  
    quiz = relationship('QuizContent', back_populates='submissions', foreign_keys=[quiz_id])

    def __repr__(self):
        return f"<QuizSubmission(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score})>"
