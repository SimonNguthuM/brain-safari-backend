from db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from utils import update_leaderboard 
# user model
class User(db.Model, UserMixin, SerializerMixin): 
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    leaderboard_entry = db.relationship('Leaderboard', back_populates='user', uselist=False)
    feedback = db.relationship('Feedback', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')
    replies = db.relationship('Reply', back_populates='user')
    enrolled_paths = db.relationship('UserLearningPath', back_populates='user')
    contributed_paths = db.relationship('LearningPath', back_populates='contributor')
    challenges = db.relationship('UserChallenge', back_populates='user')
    achievements = db.relationship('UserAchievement', back_populates='user')
    quiz_submissions = db.relationship('QuizSubmission', back_populates='user')

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the provided password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def add_points(self, points):
        """Add points to the user's score and update the leaderboard."""
        self.points += points
        db.session.commit()
        update_leaderboard(db, Leaderboard, self.id, self.points)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "points": self.points,
            "date_joined": self.date_joined.isoformat(),
            "leaderboard_entry_id": self.leaderboard_entry.id if self.leaderboard_entry else None
        }

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class LearningPath(db.Model, SerializerMixin):
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)

    modules = db.relationship('Module', back_populates='learning_path')
    enrolled_users = db.relationship('UserLearningPath', back_populates='learning_path')
    contributor = db.relationship('User', back_populates='contributed_paths')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "contributor_id": self.contributor_id,
            "rating": self.rating
        }

    def __repr__(self):
        return f"<LearningPath(id={self.id}, title={self.title})>"


class Module(db.Model, SerializerMixin):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))

    learning_path = db.relationship('LearningPath', back_populates='modules')
    resources = db.relationship('ModuleResource', back_populates='module')
    challenges = db.relationship('Challenge', back_populates='module')
    quiz_content = db.relationship('QuizContent', back_populates='module')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "learning_path_id": self.learning_path_id
        }

    def __repr__(self):
        return f"<Module(id={self.id}, title={self.title})>"


class Resource(db.Model, SerializerMixin):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    type = db.Column(db.Enum('Video', 'Article', 'Tutorial', name='resource_type'))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    feedbacks = db.relationship('Feedback', back_populates='resource')
    modules = db.relationship('ModuleResource', back_populates='resource')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "type": self.type,
            "description": self.description,
            "contributor_id": self.contributor_id
        }

    def __repr__(self):
        return f"<Resource(id={self.id}, title={self.title})>"


class Feedback(db.Model, SerializerMixin):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    user = db.relationship("User", back_populates="feedback")
    resource = db.relationship("Resource", back_populates="feedbacks")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "resource_id": self.resource.id,
            "comment": self.comment,
            "rating": self.rating
        }

    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, rating={self.rating})>"


class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="comments")
    replies = db.relationship("Reply", back_populates="comment")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Comment(id={self.id}, content='{self.content[:20]}...')>"


class Reply(db.Model, SerializerMixin):
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="replies")
    comment = db.relationship("Comment", back_populates="replies")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "comment_id": self.comment.id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Reply(id={self.id}, content='{self.content[:20]}...')>"


class Challenge(db.Model, SerializerMixin):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    points_reward = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))

    module = db.relationship("Module", back_populates="challenges")
    users = db.relationship("UserChallenge", back_populates="challenge")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "points_reward": self.points_reward,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "module_id": self.module_id
        }

    def __repr__(self):
        return f"<Challenge(id={self.id}, title={self.title})>"


class Achievement(db.Model, SerializerMixin):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(200))
    points_required = db.Column(db.Integer)

    users = db.relationship("UserAchievement", back_populates="achievement")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "points_required": self.points_required
        }

    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name})>"


class Leaderboard(db.Model, SerializerMixin):
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)

    user = db.relationship("User", back_populates="leaderboard_entry")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "score": self.score
        }

    def __repr__(self):
        return f"<Leaderboard(id={self.id}, score={self.score})>"


class ModuleResource(db.Model, SerializerMixin):
    __tablename__ = 'module_resources'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship("Module", back_populates="resources")
    resource = db.relationship("Resource", back_populates="modules")

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "resource_id": self.resource_id,
            "added_at": self.added_at.isoformat()
        }

    def __repr__(self):
        return f"<ModuleResource(id={self.id})>"


class UserAchievement(db.Model, SerializerMixin):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="achievements")
    achievement = db.relationship("Achievement", back_populates="users")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "achievement_id": self.achievement.id,
            "earned_at": self.earned_at.isoformat()
        }

    def __repr__(self):
        return f"<UserAchievement(id={self.id})>"


class UserLearningPath(db.Model, SerializerMixin):
    __tablename__ = 'user_learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))
    progress_percentage = db.Column(db.Integer)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="enrolled_paths")
    learning_path = db.relationship("LearningPath", back_populates="enrolled_users")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "learning_path_id": self.learning_path.id,
            "progress_percentage": self.progress_percentage,
            "last_accessed": self.last_accessed.isoformat(),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f"<UserLearningPath(id={self.id})>"


class UserChallenge(db.Model, SerializerMixin):
    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="challenges")
    challenge = db.relationship("Challenge", back_populates="users")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "challenge_id": self.challenge.id,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f"<UserChallenge(id={self.id})>"


class QuizContent(db.Model, SerializerMixin):
    __tablename__ = 'quiz_content'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'))
    type = db.Column(db.String, nullable=False)
    content_text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean)

    module = db.relationship("Module", back_populates="quiz_content")
    parent = db.relationship("QuizContent", remote_side=[id], back_populates="children")
    children = db.relationship("QuizContent", back_populates="parent")

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "parent_id": self.parent_id,
            "type": self.type,
            "content_text": self.content_text,
            "points": self.points,
            "is_correct": self.is_correct
        }

    def __repr__(self):
        return f"<QuizContent(id={self.id})>"


class QuizSubmission(db.Model, SerializerMixin):
    __tablename__ = 'quiz_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'))
    score = db.Column(db.Integer)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="quiz_submissions")
    quiz = db.relationship("QuizContent")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "quiz_id": self.quiz.id,
            "score": self.score,
            "submitted_at": self.submitted_at.isoformat()
        }

    def __repr__(self):
        return f"<QuizSubmission(id={self.id})>"
